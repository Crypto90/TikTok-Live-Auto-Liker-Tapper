"""Live status lookups through TikTok's web API, without a browser.

One small JSON request (~10 KB, ~250 ms) per creator replaces loading the creator's full live page,
video included, in a hidden browser and guessing from the page markup.
"""

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass

API_URL = "https://www.tiktok.com/api-live/user/room/?aid=1988&sourceType=54&uniqueId={}"
USER_AGENT = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
              "Chrome/130.0.0.0 Safari/537.36")
ROOM_STATUS_LIVE = 2  # observed: 2 while live, 4 once the stream has ended
STATUS_USER_NOT_FOUND = 19881007


class LiveStatusError(Exception):
    """The API gave no trustworthy answer; check the live page instead.

    `blocked` means TikTok refused the request or answered with something that isn't the API,
    so it's pointless to keep asking for a while.
    """

    def __init__(self, message: str, blocked: bool = False):
        super().__init__(message)
        self.blocked = blocked


@dataclass
class LiveStatus:
    is_live: bool
    avatar_url: str = ""
    exists: bool = True


def fetch_live_status(username: str, timeout: float = 10.0, opener=urllib.request.urlopen) -> LiveStatus:
    request = urllib.request.Request(
        API_URL.format(urllib.parse.quote(username)),
        headers={"User-Agent": USER_AGENT, "Accept": "application/json", "Referer": "https://www.tiktok.com/"},
    )
    try:
        with opener(request, timeout=timeout) as response:
            body = response.read()
    except urllib.error.HTTPError as exc:
        raise LiveStatusError(f"HTTP {exc.code}", blocked=exc.code in (403, 429)) from exc
    except OSError as exc:
        raise LiveStatusError(f"network error: {exc}") from exc

    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, ValueError) as exc:
        raise LiveStatusError("response is not JSON (captcha or block page?)", blocked=True) from exc
    if not isinstance(payload, dict):
        raise LiveStatusError("unexpected response shape", blocked=True)

    code = payload.get("statusCode", payload.get("status_code"))
    if code == STATUS_USER_NOT_FOUND:
        return LiveStatus(is_live=False, exists=False)
    if code != 0:
        raise LiveStatusError(f"statusCode {code}: {payload.get('message', '')}")

    data = payload.get("data") or {}
    user = data.get("user") or {}
    room_status = (data.get("liveRoom") or {}).get("status", user.get("status"))
    if not isinstance(room_status, int):
        raise LiveStatusError("response has no room status", blocked=True)
    avatar = user.get("avatarThumb") or user.get("avatarMedium") or user.get("avatarLarger") or ""
    return LiveStatus(is_live=room_status == ROOM_STATUS_LIVE, avatar_url=str(avatar))
