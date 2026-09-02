"""Cross-platform browser engine abstraction for TikTok Live Auto Liker.

Supports:
- macOS: Apple WebKit (WKWebView) via PyObjC with native hardware H.264/HEVC/AAC decoding.
- Windows: Microsoft Edge WebView2 (qtwebview2) with low-memory configuration.
- Linux: PyQt6-WebEngine (QWebEngineView) with DocumentCreation codec shims.
"""

import sys
import os
import json
from ctypes import c_void_p
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QMainWindow
from PyQt6.QtCore import Qt, QUrl, pyqtSignal, QObject, QTimer

# Detection of available backends
HAS_MAC_WEBKIT = False
HAS_WIN_WEBVIEW2 = False
HAS_QT_WEBENGINE = False

if sys.platform == "darwin":
    try:
        import objc
        import WebKit
        import AppKit
        HAS_MAC_WEBKIT = True
    except ImportError:
        HAS_MAC_WEBKIT = False

if sys.platform == "win32":
    try:
        from qtwebview2.widget import QtWebView2Widget
        HAS_WIN_WEBVIEW2 = True
    except ImportError:
        HAS_WIN_WEBVIEW2 = False

try:
    from PyQt6.QtWebEngineWidgets import QWebEngineView
    from PyQt6.QtWebEngineCore import QWebEngineScript, QWebEngineProfile, QWebEnginePage
    HAS_QT_WEBENGINE = True
except ImportError:
    HAS_QT_WEBENGINE = False


TAPPER_IN_PAGE_SCRIPT = """
(function() {
    if (window.__tiktokAutoTapperInstalled) {
        return;
    }
    window.__tiktokAutoTapperInstalled = true;

    var state = {
        enabled: true,
        baseDelay: 100,
        randomization: 50,
        timerId: null,
        cleanupTimerId: null
    };

    function getNextDelay() {
        return Math.max(50, state.baseDelay + Math.floor(Math.random() * (state.randomization + 1)));
    }

    function triggerTap() {
        if (!state.enabled) return;

        // 1. Dispatch 'L' key with proper bubbling
        try {
            var kd = new KeyboardEvent('keydown', {
                key: 'l', code: 'KeyL', keyCode: 76, which: 76, bubbles: true, cancelable: true
            });
            var ku = new KeyboardEvent('keyup', {
                key: 'l', code: 'KeyL', keyCode: 76, which: 76, bubbles: true, cancelable: true
            });
            document.dispatchEvent(kd);
            document.dispatchEvent(ku);
        } catch(e) {}

        // 2. Double-click video container as fallback
        try {
            var likeArea = document.querySelector('[data-e2e="live-video"]') || 
                           document.querySelector('.tiktok-web-player') ||
                           document.querySelector('video');
            if (likeArea) {
                var dbl = new MouseEvent('dblclick', {
                    view: window,
                    bubbles: true,
                    cancelable: true
                });
                likeArea.dispatchEvent(dbl);
            }
        } catch(e) {}

        // Schedule next tap with natural jitter
        if (state.enabled) {
            state.timerId = setTimeout(triggerTap, getNextDelay());
        }
    }

    function pruneDOM() {
        try {
            // Prune floating like animations & heart containers to prevent unbounded DOM growth
            var selectors = [
                '[class*="LikeAnimation"]', '[class*="like-animation"]',
                '[class*="DiggContainer"]', '[class*="digg-container"]',
                '[class*="GiftEffect"]', '[class*="gift-effect"]',
                '[class*="GiftAnimation"]', '[class*="gift-animation"]',
                '[class*="GiftOverlay"]', '[class*="gift-overlay"]',
                '[class*="EffectContainer"]', '[class*="effect-container"]',
                '[class*="GiftPanel"]', '[class*="gift-panel"]'
            ];
            document.querySelectorAll(selectors.join(',')).forEach(function(el) {
                el.remove();
            });

            // Keep chat messages bounded to 40 max
            var chatLists = document.querySelectorAll(
                '[class*="ChatMessageList"], [class*="chat-list"], [data-e2e="chat-list"], [class*="webcast-chatroom"]'
            );
            chatLists.forEach(function(c) {
                while (c.children.length > 40) {
                    c.removeChild(c.children[0]);
                }
            });
        } catch(e) {}
    }

    window.__tiktokStartTapper = function(base, rand, enabled) {
        if (typeof base === 'number') state.baseDelay = base;
        if (typeof rand === 'number') state.randomization = rand;
        if (enabled !== undefined) state.enabled = !!enabled;

        if (state.timerId) clearTimeout(state.timerId);
        if (state.cleanupTimerId) clearInterval(state.cleanupTimerId);

        if (state.enabled) {
            state.timerId = setTimeout(triggerTap, getNextDelay());
        }
        // Run DOM pruning every 3 seconds
        state.cleanupTimerId = setInterval(pruneDOM, 3000);
    };

    window.__tiktokSetTapperSpeed = function(base, rand) {
        state.baseDelay = base;
        state.randomization = rand;
    };

    window.__tiktokSetTapperEnabled = function(enabled) {
        state.enabled = !!enabled;
        if (state.enabled && !state.timerId) {
            state.timerId = setTimeout(triggerTap, getNextDelay());
        } else if (!state.enabled && state.timerId) {
            clearTimeout(state.timerId);
            state.timerId = null;
        }
    };

    window.__tiktokStopTapper = function() {
        state.enabled = false;
        if (state.timerId) clearTimeout(state.timerId);
        if (state.cleanupTimerId) clearInterval(state.cleanupTimerId);
        state.timerId = null;
        state.cleanupTimerId = null;
    };
})();
"""


# ---------------------------------------------------------------------------
# macOS Native WebKit (WKWebView) Backend
# ---------------------------------------------------------------------------
if HAS_MAC_WEBKIT:
    class _MacNavDelegate(AppKit.NSObject):
        """Bridge WKNavigationDelegate events to PyQt signals."""
        def initWithOwner_(self, owner):
            self = objc.super(_MacNavDelegate, self).init()
            if self is not None:
                self._owner = owner
            return self

        def webView_didFinishNavigation_(self, webview, navigation):
            if self._owner is not None:
                url = str(webview.URL().absoluteString()) if webview.URL() else ""
                self._owner._on_nav_finished(True, url)

        def webView_didFailNavigation_withError_(self, webview, navigation, error):
            if self._owner is not None:
                url = str(webview.URL().absoluteString()) if webview.URL() else ""
                self._owner._on_nav_finished(False, url)

        def webView_didFailProvisionalNavigation_withError_(self, webview, navigation, error):
            if self._owner is not None:
                url = str(webview.URL().absoluteString()) if webview.URL() else ""
                self._owner._on_nav_finished(False, url)

        def webView_decidePolicyForNavigationAction_decisionHandler_(self, webview, action, handler):
            url_obj = action.request().URL()
            scheme = str(url_obj.scheme()).lower() if url_obj and url_obj.scheme() else ""
            if scheme in ("http", "https", "about", "data", "blob", ""):
                handler(WebKit.WKNavigationActionPolicyAllow)
            else:
                # Safely ignore app links/custom protocols (e.g. tiktok://) without crashing
                handler(WebKit.WKNavigationActionPolicyCancel)


    class _MacUIDelegate(AppKit.NSObject):
        """Handle new window/popup requests (window.open, target=_blank)."""
        def webView_createWebViewWithConfiguration_forNavigationAction_windowFeatures_(self, webview, config, action, features):
            # Load popups and blank targets directly in the current webview
            if action.targetFrame() is None:
                webview.loadRequest_(action.request())
            return None


    class MacWKWebViewWidget(QWidget):
        navigation_completed = pyqtSignal(bool, str)
        source_changed = pyqtSignal(str)

        def __init__(self, parent=None, user_data_folder=None, url=None, lazyload=False, init_settings_hook=None, is_headless=False):
            super().__init__(parent)
            self._is_headless = is_headless
            self._is_muted = True
            self._last_url = ""
            self._dev_tools_window = None

            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            self.setLayout(layout)

            config = WebKit.WKWebViewConfiguration.alloc().init()
            config.setMediaTypesRequiringUserActionForPlayback_(WebKit.WKAudiovisualMediaTypeNone)

            if hasattr(config, '_setMediaDataLoadsAutomatically_'):
                try: config._setMediaDataLoadsAutomatically_(True)
                except Exception: pass
            if hasattr(config, '_setRequiresUserActionForVideoPlayback_'):
                try: config._setRequiresUserActionForVideoPlayback_(False)
                except Exception: pass
            if hasattr(config, '_setRequiresUserActionForAudioPlayback_'):
                try: config._setRequiresUserActionForAudioPlayback_(False)
                except Exception: pass

            pref = config.preferences()
            if hasattr(pref, '_setAllowsInlineMediaPlayback_'):
                try: pref._setAllowsInlineMediaPlayback_(True)
                except Exception: pass
            if hasattr(pref, '_setRequiresUserGestureForVideoPlayback_'):
                try: pref._setRequiresUserGestureForVideoPlayback_(False)
                except Exception: pass
            if hasattr(pref, '_setRequiresUserGestureForAudioPlayback_'):
                try: pref._setRequiresUserGestureForAudioPlayback_(False)
                except Exception: pass
            if hasattr(pref, '_setMediaSourceEnabled_'):
                try: pref._setMediaSourceEnabled_(True)
                except Exception: pass

            # Persistent website data store
            if hasattr(WebKit, 'WKWebsiteDataStore'):
                data_store = WebKit.WKWebsiteDataStore.defaultDataStore()
                config.setWebsiteDataStore_(data_store)

            # Developer tools access
            try:
                config.preferences().setValue_forKey_(True, "developerExtrasEnabled")
            except Exception:
                pass

            if is_headless:
                self.wk = WebKit.WKWebView.alloc().initWithFrame_configuration_(AppKit.NSZeroRect, config)
            else:
                self.ns_container = objc.objc_object(c_void_p=int(self.winId()))
                self.wk = WebKit.WKWebView.alloc().initWithFrame_configuration_(self.ns_container.bounds(), config)
                self.wk.setAutoresizingMask_(AppKit.NSViewWidthSizable | AppKit.NSViewHeightSizable)
                self.ns_container.addSubview_(self.wk)

            # Standard macOS Safari User-Agent to ensure TikTok serves desktop video feeds
            if hasattr(self.wk, 'setCustomUserAgent_'):
                self.wk.setCustomUserAgent_(
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.3 Safari/605.1.15"
                )

            # Allow Safari inspection on modern macOS
            if hasattr(self.wk, 'setInspectable_'):
                try:
                    self.wk.setInspectable_(True)
                except Exception:
                    pass

            self._delegate = _MacNavDelegate.alloc().initWithOwner_(self)
            self.wk.setNavigationDelegate_(self._delegate)
            self._ui_delegate = _MacUIDelegate.alloc().init()
            self.wk.setUIDelegate_(self._ui_delegate)

            # Periodic URL poll to detect SPA client-side router navigation
            self._url_poll_timer = QTimer(self)
            self._url_poll_timer.timeout.connect(self._check_url_change)
            self._url_poll_timer.start(500)

            if init_settings_hook:
                try:
                    init_settings_hook(self)
                except Exception:
                    pass

            if url and not lazyload:
                self.load_url(url)

        def _check_url_change(self):
            if not getattr(self, 'wk', None):
                return
            try:
                ns_url = self.wk.URL()
                if ns_url:
                    current = str(ns_url.absoluteString())
                    if current and current != self._last_url:
                        self._last_url = current
                        self.source_changed.emit(current)
            except Exception:
                pass

        def _on_nav_finished(self, success, url):
            if url and url != self._last_url:
                self._last_url = url
                self.source_changed.emit(url)
            self.navigation_completed.emit(success, url)

        def load_url(self, url_str):
            if not getattr(self, 'wk', None) or not url_str:
                return
            self._last_url = url_str
            ns_url = AppKit.NSURL.URLWithString_(url_str)
            req = AppKit.NSURLRequest.requestWithURL_(ns_url)
            self.wk.loadRequest_(req)

        def load_html(self, html_str):
            if getattr(self, 'wk', None):
                self.wk.loadHTMLString_baseURL_(html_str, None)

        def evaluate_js(self, js_code, callback=None):
            if not getattr(self, 'wk', None):
                return
            clean_js = js_code.strip()
            if clean_js.startswith("return "):
                clean_js = clean_js[7:].strip()
            def handler(res, err):
                if callback:
                    callback({'result': res})
            self.wk.evaluateJavaScript_completionHandler_(clean_js, handler)

        def set_muted(self, muted):
            self._is_muted = muted
            # Mute all media elements inside the DOM
            js = f"document.querySelectorAll('video, audio').forEach(function(v) {{ v.muted = {'true' if muted else 'false'}; }});"
            self.evaluate_js(js)

        def set_background_mode(self, is_background):
            """Reduce video rendering and media buffer allocation in background tabs."""
            if is_background:
                js = """
                (function() {
                    if (document.getElementById('__autoliker_bg_mode__')) return;
                    var style = document.createElement('style');
                    style.id = '__autoliker_bg_mode__';
                    style.textContent = 'video { visibility: hidden !important; height: 1px !important; width: 1px !important; position: absolute !important; }';
                    document.head.appendChild(style);
                })();
                """
            else:
                js = """
                (function() {
                    var el = document.getElementById('__autoliker_bg_mode__');
                    if (el) el.remove();
                })();
                """
            self.evaluate_js(js)

        def inject_in_page_tapper(self, base_ms=100, rand_ms=50, enabled=True):
            """Injects the tapping engine and starts the loop natively inside the browser."""
            setup_call = f"window.__tiktokStartTapper({base_ms}, {rand_ms}, {'true' if enabled else 'false'});"
            full_js = TAPPER_IN_PAGE_SCRIPT + "\n" + setup_call
            self.evaluate_js(full_js)

        def set_tapper_rate(self, base_ms, rand_ms):
            self.evaluate_js(f"if (window.__tiktokSetTapperSpeed) window.__tiktokSetTapperSpeed({base_ms}, {rand_ms});")

        def set_tapper_enabled(self, enabled):
            self.evaluate_js(f"if (window.__tiktokSetTapperEnabled) window.__tiktokSetTapperEnabled({'true' if enabled else 'false'});")

        def stop_tapper(self):
            self.evaluate_js("if (window.__tiktokStopTapper) window.__tiktokStopTapper();")

        def reload(self):
            if getattr(self, 'wk', None):
                self.wk.reload()

        def open_dev_tools(self):
            """Open developer inspection."""
            # Modern WKWebView supports Safari Develop menu inspection out of the box when inspectable=True
            self.evaluate_js("console.log('TikTok Live Auto-Liker: DevTools active for this tab.');")

        def resizeEvent(self, event):
            super().resizeEvent(event)
            if not self._is_headless and getattr(self, 'wk', None) and getattr(self, 'ns_container', None):
                try:
                    self.wk.setFrame_(self.ns_container.bounds())
                except Exception:
                    pass

        def cleanup(self):
            if hasattr(self, '_url_poll_timer'):
                self._url_poll_timer.stop()
            self.stop_tapper()
            if getattr(self, 'wk', None):
                try:
                    self.wk.stopLoading()
                    self.wk.setNavigationDelegate_(None)
                    self.wk.setUIDelegate_(None)
                except Exception:
                    pass
                if not self._is_headless:
                    try:
                        self.wk.removeFromSuperview()
                    except Exception:
                        pass
                self.wk = None
            self._delegate = None
            self._ui_delegate = None


# ---------------------------------------------------------------------------
# Windows WebView2 (qtwebview2) Backend
# ---------------------------------------------------------------------------
if HAS_WIN_WEBVIEW2:
    class WindowsWebView2Widget(QWidget):
        navigation_completed = pyqtSignal(bool, str)
        source_changed = pyqtSignal(str)

        def __init__(self, parent=None, user_data_folder=None, url=None, lazyload=False, init_settings_hook=None, is_headless=False):
            super().__init__(parent)
            self._is_muted = True
            self._core_wv2 = None
            self._nav_handler = None
            self._source_handler = None

            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            self.setLayout(layout)

            self.wv2 = QtWebView2Widget(
                url=url if not lazyload else None,
                lazyload=lazyload,
                user_data_folder=user_data_folder or "./userdata",
                init_settings_hook=self._on_core_init
            )
            layout.addWidget(self.wv2)
            self._custom_init_hook = init_settings_hook

        def _on_core_init(self, core_wv2):
            self._core_wv2 = core_wv2

            # Set low memory mode flags on inactive or headless workers
            try:
                core_wv2.IsMuted = self._is_muted
            except Exception:
                pass

            def on_nav_done(sender, args):
                url = str(sender.Source) if sender and hasattr(sender, 'Source') else ""
                self.navigation_completed.emit(bool(args.IsSuccess), url)

            def on_src_changed(sender, args):
                url = str(sender.Source) if sender and hasattr(sender, 'Source') else ""
                self.source_changed.emit(url)

            self._nav_handler = on_nav_done
            self._source_handler = on_src_changed

            try:
                core_wv2.NavigationCompleted += self._nav_handler
                core_wv2.SourceChanged += self._source_handler
            except Exception:
                pass

            if self._custom_init_hook:
                try:
                    self._custom_init_hook(core_wv2)
                except Exception:
                    pass

        def load_url(self, url_str):
            if self.wv2:
                self.wv2.load_url(url_str)

        def load_html(self, html_str):
            if self.wv2:
                self.wv2.load_html(html_str)

        def evaluate_js(self, js_code, callback=None):
            if self.wv2:
                self.wv2.evaluate_js(js_code, callback)

        def set_muted(self, muted):
            self._is_muted = muted
            if self._core_wv2:
                try:
                    self._core_wv2.IsMuted = muted
                except Exception:
                    pass
            js = f"document.querySelectorAll('video, audio').forEach(function(v) {{ v.muted = {'true' if muted else 'false'}; }});"
            self.evaluate_js(js)

        def set_background_mode(self, is_background):
            if is_background:
                js = """
                (function() {
                    if (document.getElementById('__autoliker_bg_mode__')) return;
                    var style = document.createElement('style');
                    style.id = '__autoliker_bg_mode__';
                    style.textContent = 'video { visibility: hidden !important; height: 1px !important; width: 1px !important; position: absolute !important; }';
                    document.head.appendChild(style);
                })();
                """
                if self._core_wv2:
                    try:
                        self._core_wv2.MemoryUsageTargetLevel = 1  # Low
                    except Exception:
                        pass
            else:
                js = """
                (function() {
                    var el = document.getElementById('__autoliker_bg_mode__');
                    if (el) el.remove();
                })();
                """
                if self._core_wv2:
                    try:
                        self._core_wv2.MemoryUsageTargetLevel = 0  # Normal
                    except Exception:
                        pass
            self.evaluate_js(js)

        def inject_in_page_tapper(self, base_ms=100, rand_ms=50, enabled=True):
            setup_call = f"window.__tiktokStartTapper({base_ms}, {rand_ms}, {'true' if enabled else 'false'});"
            full_js = TAPPER_IN_PAGE_SCRIPT + "\n" + setup_call
            self.evaluate_js(full_js)

        def set_tapper_rate(self, base_ms, rand_ms):
            self.evaluate_js(f"if (window.__tiktokSetTapperSpeed) window.__tiktokSetTapperSpeed({base_ms}, {rand_ms});")

        def set_tapper_enabled(self, enabled):
            self.evaluate_js(f"if (window.__tiktokSetTapperEnabled) window.__tiktokSetTapperEnabled({'true' if enabled else 'false'});")

        def stop_tapper(self):
            self.evaluate_js("if (window.__tiktokStopTapper) window.__tiktokStopTapper();")

        def reload(self):
            if self.wv2:
                self.wv2.reload()

        def open_dev_tools(self):
            if self._core_wv2:
                try:
                    self._core_wv2.OpenDevToolsWindow()
                except Exception:
                    pass

        def cleanup(self):
            self.stop_tapper()
            if self._core_wv2:
                try:
                    if self._nav_handler:
                        self._core_wv2.NavigationCompleted -= self._nav_handler
                    if self._source_handler:
                        self._core_wv2.SourceChanged -= self._source_handler
                except Exception:
                    pass
                self._core_wv2 = None
            self._nav_handler = None
            self._source_handler = None
            if self.wv2:
                try:
                    self.wv2.close()
                    self.wv2.deleteLater()
                except Exception:
                    pass
                self.wv2 = None


# ---------------------------------------------------------------------------
# Cross-Platform PyQt6-WebEngine (QWebEngineView) Backend (Linux & Fallback)
# ---------------------------------------------------------------------------
if HAS_QT_WEBENGINE:
    class QtWebEngineWebViewWidget(QWidget):
        navigation_completed = pyqtSignal(bool, str)
        source_changed = pyqtSignal(str)

        _shared_profile = None

        @classmethod
        def get_profile(cls, storage_path=None):
            if cls._shared_profile is None:
                cls._shared_profile = QWebEngineProfile("TikTokAutoLikerProfile")
                if storage_path:
                    abs_path = os.path.abspath(storage_path)
                    os.makedirs(abs_path, exist_ok=True)
                    cls._shared_profile.setPersistentStoragePath(abs_path)
                cls._shared_profile.setPersistentCookiesPolicy(
                    QWebEngineProfile.PersistentCookiesPolicy.ForcePersistentCookies
                )
            return cls._shared_profile

        def __init__(self, parent=None, user_data_folder=None, url=None, lazyload=False, init_settings_hook=None, is_headless=False):
            super().__init__(parent)
            self._is_muted = True
            self._dev_tools_window = None

            layout = QVBoxLayout(self)
            layout.setContentsMargins(0, 0, 0, 0)
            self.setLayout(layout)

            profile = self.get_profile(user_data_folder)
            self.web = QWebEngineView(self)
            page = QWebEnginePage(profile, self.web)
            self.web.setPage(page)

            # Codec shim injected at DocumentCreation so TikTok Live mounts the player
            script = QWebEngineScript()
            script.setName("tiktok_codec_shim")
            script.setInjectionPoint(QWebEngineScript.InjectionPoint.DocumentCreation)
            script.setWorldId(QWebEngineScript.ScriptWorldId.MainWorld)
            script.setSourceCode("""
            (function() {
                var origCanPlay = HTMLMediaElement.prototype.canPlayType;
                HTMLMediaElement.prototype.canPlayType = function(type) {
                    if (type && (type.includes('mp4') || type.includes('avc1') || type.includes('mp4a') || type.includes('h264'))) {
                        return 'probably';
                    }
                    return origCanPlay.call(this, type);
                };
                if (window.MediaSource) {
                    var origIsSupported = MediaSource.isTypeSupported;
                    MediaSource.isTypeSupported = function(type) {
                        if (type && (type.includes('mp4') || type.includes('avc1') || type.includes('mp4a') || type.includes('h264'))) {
                            return true;
                        }
                        return origIsSupported.call(this, type);
                    };
                }
            })();
            """)
            page.scripts().insert(script)
            layout.addWidget(self.web)

            self.web.urlChanged.connect(lambda qurl: self.source_changed.emit(qurl.toString()))
            self.web.loadFinished.connect(lambda ok: self.navigation_completed.emit(ok, self.web.url().toString()))

            if init_settings_hook:
                try:
                    init_settings_hook(self)
                except Exception:
                    pass

            if url and not lazyload:
                self.load_url(url)

        def load_url(self, url_str):
            if self.web and url_str:
                self.web.setUrl(QUrl(url_str))

        def load_html(self, html_str):
            if self.web:
                self.web.setHtml(html_str)

        def evaluate_js(self, js_code, callback=None):
            if not self.web or not self.web.page():
                return
            clean_js = js_code.strip()
            if clean_js.startswith("return "):
                clean_js = clean_js[7:].strip()
            def cb(res):
                if callback:
                    callback({'result': res})
            self.web.page().runJavaScript(clean_js, cb if callback else lambda _: None)

        def set_muted(self, muted):
            self._is_muted = muted
            if self.web and self.web.page():
                self.web.page().setAudioMuted(muted)
            js = f"document.querySelectorAll('video, audio').forEach(function(v) {{ v.muted = {'true' if muted else 'false'}; }});"
            self.evaluate_js(js)

        def set_background_mode(self, is_background):
            if is_background:
                js = """
                (function() {
                    if (document.getElementById('__autoliker_bg_mode__')) return;
                    var style = document.createElement('style');
                    style.id = '__autoliker_bg_mode__';
                    style.textContent = 'video { visibility: hidden !important; height: 1px !important; width: 1px !important; position: absolute !important; }';
                    document.head.appendChild(style);
                })();
                """
                if hasattr(QWebEnginePage, 'LifecycleState'):
                    try:
                        self.web.page().setLifecycleState(QWebEnginePage.LifecycleState.Passive)
                    except Exception:
                        pass
            else:
                js = """
                (function() {
                    var el = document.getElementById('__autoliker_bg_mode__');
                    if (el) el.remove();
                })();
                """
                if hasattr(QWebEnginePage, 'LifecycleState'):
                    try:
                        self.web.page().setLifecycleState(QWebEnginePage.LifecycleState.Active)
                    except Exception:
                        pass
            self.evaluate_js(js)

        def inject_in_page_tapper(self, base_ms=100, rand_ms=50, enabled=True):
            setup_call = f"window.__tiktokStartTapper({base_ms}, {rand_ms}, {'true' if enabled else 'false'});"
            full_js = TAPPER_IN_PAGE_SCRIPT + "\n" + setup_call
            self.evaluate_js(full_js)

        def set_tapper_rate(self, base_ms, rand_ms):
            self.evaluate_js(f"if (window.__tiktokSetTapperSpeed) window.__tiktokSetTapperSpeed({base_ms}, {rand_ms});")

        def set_tapper_enabled(self, enabled):
            self.evaluate_js(f"if (window.__tiktokSetTapperEnabled) window.__tiktokSetTapperEnabled({'true' if enabled else 'false'});")

        def stop_tapper(self):
            self.evaluate_js("if (window.__tiktokStopTapper) window.__tiktokStopTapper();")

        def reload(self):
            if self.web:
                self.web.reload()

        def open_dev_tools(self):
            if self._dev_tools_window is None or not self._dev_tools_window.isVisible():
                self._dev_tools_window = QMainWindow(self)
                self._dev_tools_window.setWindowTitle("Developer Tools")
                self._dev_tools_window.resize(800, 600)
                dt_view = QWebEngineView(self._dev_tools_window)
                self.web.page().setDevToolsPage(dt_view.page())
                self._dev_tools_window.setCentralWidget(dt_view)
            self._dev_tools_window.show()
            self._dev_tools_window.raise_()

        def cleanup(self):
            self.stop_tapper()
            if self.web:
                try:
                    self.web.stop()
                    self.web.close()
                    self.web.deleteLater()
                except Exception:
                    pass
                self.web = None


# ---------------------------------------------------------------------------
# Factory / Dispatcher: Select Best Engine For Current Platform
# ---------------------------------------------------------------------------
def get_best_engine_class():
    if sys.platform == "darwin" and HAS_MAC_WEBKIT:
        return MacWKWebViewWidget
    if sys.platform == "win32" and HAS_WIN_WEBVIEW2:
        return WindowsWebView2Widget
    if HAS_QT_WEBENGINE:
        return QtWebEngineWebViewWidget
    if HAS_MAC_WEBKIT:
        return MacWKWebViewWidget
    if HAS_WIN_WEBVIEW2:
        return WindowsWebView2Widget
    raise RuntimeError("No compatible browser engine installed. Please install PyQt6-WebEngine or platform prerequisites.")


class UniversalWebView(QWidget):
    """Universal browser widget that proxies all calls to the best available platform backend."""

    navigation_completed = pyqtSignal(bool, str)
    source_changed = pyqtSignal(str)

    def __init__(self, parent=None, user_data_folder=None, url=None, lazyload=False, init_settings_hook=None, is_headless=False):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

        engine_cls = get_best_engine_class()
        self._engine = engine_cls(
            parent=self,
            user_data_folder=user_data_folder,
            url=url,
            lazyload=lazyload,
            init_settings_hook=init_settings_hook,
            is_headless=is_headless
        )
        layout.addWidget(self._engine)

        self._engine.navigation_completed.connect(self.navigation_completed.emit)
        self._engine.source_changed.connect(self.source_changed.emit)

    def load_url(self, url_str):
        self._engine.load_url(url_str)

    def load_html(self, html_str):
        self._engine.load_html(html_str)

    def evaluate_js(self, js_code, callback=None):
        self._engine.evaluate_js(js_code, callback)

    def set_muted(self, muted):
        self._engine.set_muted(muted)

    def set_background_mode(self, is_background):
        self._engine.set_background_mode(is_background)

    def inject_in_page_tapper(self, base_ms=100, rand_ms=50, enabled=True):
        self._engine.inject_in_page_tapper(base_ms, rand_ms, enabled)

    def set_tapper_rate(self, base_ms, rand_ms):
        self._engine.set_tapper_rate(base_ms, rand_ms)

    def set_tapper_enabled(self, enabled):
        self._engine.set_tapper_enabled(enabled)

    def stop_tapper(self):
        self._engine.stop_tapper()

    def reload(self):
        self._engine.reload()

    def open_dev_tools(self):
        self._engine.open_dev_tools()

    def cleanup(self):
        if getattr(self, '_engine', None):
            self._engine.cleanup()
            self._engine = None
