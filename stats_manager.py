import os
import json
import time
import uuid
import threading
from datetime import datetime, timezone


class StatsManager:
    """
    Manages verified like statistics, stream session lifecycles,
    aggregated streamer metrics, and daily time-series analytics.
    Thread-safe and persistent to disk.
    """

    def __init__(self, data_dir: str = "."):
        self.data_dir = data_dir
        self.stats_file = os.path.join(self.data_dir, "stats.json")
        self._lock = threading.RLock()
        self._active_sessions = {}  # session_id -> dict
        self._save_timer = None

        self.data = {
            "version": 1,
            "all_time": {
                "verified_likes": 0,
                "taps_dispatched": 0,
                "total_sessions": 0,
                "total_duration_seconds": 0
            },
            "streamers": {},       # username -> { verified_likes, taps_dispatched, sessions_count, total_duration_seconds, last_active }
            "sessions": [],        # list of session dicts
            "daily_summary": {},   # YYYY-MM-DD -> { verified_likes, taps_dispatched, duration_seconds, sessions_count }
            "updated_at": time.time()
        }
        self._load()

    def _load(self):
        with self._lock:
            if os.path.exists(self.stats_file):
                try:
                    with open(self.stats_file, "r", encoding="utf-8") as f:
                        loaded = json.load(f)
                    if isinstance(loaded, dict):
                        self.data["all_time"] = loaded.get("all_time", self.data["all_time"])
                        self.data["streamers"] = loaded.get("streamers", {})
                        self.data["sessions"] = loaded.get("sessions", [])
                        self.data["daily_summary"] = loaded.get("daily_summary", {})
                        self.data["updated_at"] = loaded.get("updated_at", time.time())
                except Exception as e:
                    print(f"[StatsManager] Error loading stats: {e}")

    def save_now(self):
        with self._lock:
            self.data["updated_at"] = time.time()
            try:
                os.makedirs(self.data_dir, exist_ok=True)
                temp_file = f"{self.stats_file}.tmp_{os.getpid()}"
                with open(temp_file, "w", encoding="utf-8") as f:
                    json.dump(self.data, f, indent=2, ensure_ascii=False)
                os.replace(temp_file, self.stats_file)
            except Exception as e:
                print(f"[StatsManager] Error saving stats: {e}")

    def _debounce_save(self, delay=2.0):
        with self._lock:
            if self._save_timer is not None:
                self._save_timer.cancel()
            self._save_timer = threading.Timer(delay, self.save_now)
            self._save_timer.daemon = True
            self._save_timer.start()

    # --- Session Management ---

    def start_session(self, username: str, room_likes_start: int = 0) -> str:
        with self._lock:
            now = time.time()
            session_id = f"sess_{int(now)}_{uuid.uuid4().hex[:6]}_{username}"
            session = {
                "session_id": session_id,
                "username": username,
                "started_at": now,
                "ended_at": None,
                "duration_seconds": 0,
                "verified_likes": 0,
                "taps_dispatched": 0,
                "failed_requests": 0,
                "room_likes_start": int(room_likes_start or 0),
                "room_likes_end": int(room_likes_start or 0),
                "status": "active"
            }
            self._active_sessions[session_id] = session
            return session_id

    def record_progress(self, session_id: str, verified_likes: int, taps_dispatched: int, failed: int = 0, room_likes: int = 0):
        with self._lock:
            if session_id not in self._active_sessions:
                return
            sess = self._active_sessions[session_id]
            sess["verified_likes"] = max(sess["verified_likes"], int(verified_likes or 0))
            sess["taps_dispatched"] = max(sess["taps_dispatched"], int(taps_dispatched or 0))
            sess["failed_requests"] = max(sess["failed_requests"], int(failed or 0))
            if room_likes > 0:
                sess["room_likes_end"] = int(room_likes)
            sess["duration_seconds"] = max(0, int(time.time() - sess["started_at"]))

    def end_session(self, session_id: str, reason: str = "completed"):
        with self._lock:
            if session_id not in self._active_sessions:
                return
            sess = self._active_sessions.pop(session_id)
            now = time.time()
            sess["ended_at"] = now
            sess["duration_seconds"] = max(1, int(now - sess["started_at"]))
            sess["status"] = reason

            # Only commit sessions where duration > 3s or some likes were tapped/sent
            if sess["duration_seconds"] >= 3 or sess["taps_dispatched"] > 0 or sess["verified_likes"] > 0:
                self._commit_session(sess)
                self.save_now()

    def _commit_session(self, sess: dict):
        with self._lock:
            # Check if session is already recorded
            for idx, existing in enumerate(self.data["sessions"]):
                if existing.get("session_id") == sess.get("session_id"):
                    self.data["sessions"][idx] = sess
                    self._recalculate_aggregates()
                    return

            self.data["sessions"].append(sess)
            # Keep sessions bounded to 1000 most recent
            if len(self.data["sessions"]) > 1000:
                self.data["sessions"] = self.data["sessions"][-1000:]
            self._recalculate_aggregates()

    def _recalculate_aggregates(self):
        with self._lock:
            total_verified = 0
            total_taps = 0
            total_duration = 0
            streamers = {}
            daily = {}

            for s in self.data["sessions"]:
                v = int(s.get("verified_likes") or 0)
                t = int(s.get("taps_dispatched") or 0)
                d = int(s.get("duration_seconds") or 0)
                u = str(s.get("username") or "unknown")

                total_verified += v
                total_taps += t
                total_duration += d

                # Streamer totals
                st = streamers.setdefault(u, {
                    "verified_likes": 0,
                    "taps_dispatched": 0,
                    "sessions_count": 0,
                    "total_duration_seconds": 0,
                    "last_active": 0
                })
                st["verified_likes"] += v
                st["taps_dispatched"] += t
                st["sessions_count"] += 1
                st["total_duration_seconds"] += d
                end_time = s.get("ended_at") or s.get("started_at") or 0
                if end_time > st["last_active"]:
                    st["last_active"] = end_time

                # Daily aggregation
                started = s.get("started_at") or 0
                if started > 0:
                    day_key = datetime.fromtimestamp(started, tz=timezone.utc).strftime("%Y-%m-%d")
                    dt = daily.setdefault(day_key, {
                        "verified_likes": 0,
                        "taps_dispatched": 0,
                        "duration_seconds": 0,
                        "sessions_count": 0
                    })
                    dt["verified_likes"] += v
                    dt["taps_dispatched"] += t
                    dt["duration_seconds"] += d
                    dt["sessions_count"] += 1

            self.data["all_time"] = {
                "verified_likes": total_verified,
                "taps_dispatched": total_taps,
                "total_sessions": len(self.data["sessions"]),
                "total_duration_seconds": total_duration
            }
            self.data["streamers"] = streamers
            self.data["daily_summary"] = daily

    # --- Query APIs for UI & Dashboard ---

    def get_kpis(self) -> dict:
        with self._lock:
            all_time = self.data["all_time"]
            v = all_time.get("verified_likes", 0)
            t = all_time.get("taps_dispatched", 0)

            # Include live active sessions in current totals
            active_v = sum(s["verified_likes"] for s in self._active_sessions.values())
            active_t = sum(s["taps_dispatched"] for s in self._active_sessions.values())
            active_d = sum(s["duration_seconds"] for s in self._active_sessions.values())

            disp_total_v = v + active_v
            disp_total_t = t + active_t
            disp_total_d = all_time.get("total_duration_seconds", 0) + active_d

            rate = round((disp_total_v / max(1, disp_total_t)) * 100.0, 1) if disp_total_t > 0 else 100.0

            return {
                "total_verified_likes": disp_total_v,
                "total_taps_dispatched": disp_total_t,
                "total_sessions": all_time.get("total_sessions", 0) + len(self._active_sessions),
                "total_duration_seconds": disp_total_d,
                "confirmation_rate_pct": min(100.0, rate),
                "active_sessions_count": len(self._active_sessions)
            }

    def get_streamer_leaderboard(self, limit: int = 10) -> list:
        with self._lock:
            res = []
            for user, data in self.data["streamers"].items():
                v = data.get("verified_likes", 0)
                t = data.get("taps_dispatched", 0)
                rate = round((v / max(1, t)) * 100.0, 1) if t > 0 else 100.0
                res.append({
                    "username": user,
                    "verified_likes": v,
                    "taps_dispatched": t,
                    "sessions_count": data.get("sessions_count", 0),
                    "total_duration_seconds": data.get("total_duration_seconds", 0),
                    "confirmation_rate": min(100.0, rate),
                    "last_active": data.get("last_active", 0)
                })
            res.sort(key=lambda x: x["verified_likes"], reverse=True)
            return res[:limit]

    def get_daily_chart_data(self, days: int = 14) -> dict:
        with self._lock:
            # Generate continuous day sequence for last N days
            today = datetime.now(timezone.utc).date()
            labels = []
            likes = []
            durations = []

            for i in range(days - 1, -1, -1):
                from datetime import timedelta
                day = today - timedelta(days=i)
                day_str = day.strftime("%Y-%m-%d")
                label_str = day.strftime("%b %d")
                labels.append(label_str)

                entry = self.data["daily_summary"].get(day_str, {})
                likes.append(entry.get("verified_likes", 0))
                durations.append(round(entry.get("duration_seconds", 0) / 60.0, 1))

            return {
                "labels": labels,
                "verified_likes": likes,
                "duration_minutes": durations
            }

    def get_recent_sessions(self, limit: int = 50) -> list:
        with self._lock:
            # Combine active sessions and past sessions, sorted newest first
            active = list(self._active_sessions.values())
            past = list(self.data["sessions"])
            all_sess = active + past
            all_sess.sort(key=lambda s: s.get("started_at", 0), reverse=True)
            return all_sess[:limit]

    def export_csv(self) -> str:
        with self._lock:
            lines = ["Session ID,Streamer,Start Time,End Time,Duration (s),Verified Likes,Taps Dispatched,Room Start,Room End,Status"]
            for s in sorted(self.data["sessions"], key=lambda x: x.get("started_at", 0), reverse=True):
                st = datetime.fromtimestamp(s.get("started_at", 0), tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S") if s.get("started_at") else ""
                et = datetime.fromtimestamp(s.get("ended_at", 0), tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S") if s.get("ended_at") else ""
                lines.append(
                    f"{s.get('session_id')},{s.get('username')},{st},{et},{s.get('duration_seconds')},"
                    f"{s.get('verified_likes')},{s.get('taps_dispatched')},{s.get('room_likes_start')},"
                    f"{s.get('room_likes_end')},{s.get('status')}"
                )
            return "\n".join(lines)

    # --- Multi-Device Sync Helpers ---

    def get_sync_payload(self) -> dict:
        with self._lock:
            return {
                "sessions": self.data["sessions"],
                "updated_at": self.data.get("updated_at", time.time())
            }

    def merge_external_sessions(self, remote_sessions: list) -> bool:
        if not isinstance(remote_sessions, list):
            return False
        with self._lock:
            changed = False
            existing_ids = {s.get("session_id"): idx for idx, s in enumerate(self.data["sessions"]) if s.get("session_id")}

            for r in remote_sessions:
                if not isinstance(r, dict) or not r.get("session_id"):
                    continue
                sid = r["session_id"]
                if sid not in existing_ids:
                    self.data["sessions"].append(r)
                    changed = True
                else:
                    idx = existing_ids[sid]
                    # If remote has higher verified likes, update
                    curr_v = self.data["sessions"][idx].get("verified_likes", 0)
                    rem_v = r.get("verified_likes", 0)
                    if rem_v > curr_v:
                        self.data["sessions"][idx] = r
                        changed = True

            if changed:
                self._recalculate_aggregates()
                self.save_now()
            return changed
