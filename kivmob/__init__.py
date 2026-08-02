"""AdMob support for Kivy."""

from kivy.core.window import Window
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.utils import platform

from .bridge import (
    AdMobBridge,
    RewardedListenerInterface,
    _ad_load_callback_current,
)
from .desktop import DesktopBridge
from .ios import iOSBridge

try:
    from importlib.metadata import version as _package_version

    __version__ = _package_version("kivmob")
except Exception:
    __version__ = "0.0.0"


class TestIds:
    """Enum of test ad ids provided by AdMob. This allows developers to
    test displaying ads without setting up an AdMob account.
    """

    APP = "ca-app-pub-3940256099942544~3347511713"
    BANNER = "ca-app-pub-3940256099942544/6300978111"
    INTERSTITIAL = "ca-app-pub-3940256099942544/1033173712"
    INTERSTITIAL_VIDEO = "ca-app-pub-3940256099942544/8691691433"
    REWARDED_VIDEO = "ca-app-pub-3940256099942544/5224354917"


def _create_bridge(app_id):
    """Return the platform-appropriate AdMob bridge instance."""
    if platform == "android":
        from . import android as android_bridge

        if android_bridge.ANDROID_ADS_OK:
            Logger.info("KivMob: Android platform detected.")
            return android_bridge.AndroidBridge(app_id)
        Logger.error("KivMob: AdMob failed to load; no-op mode.")
        return DesktopBridge(app_id)
    if platform == "ios":
        Logger.warning("KivMob: iOS not yet supported.")
        return iOSBridge(app_id)
    Logger.warning("KivMob: Ads will not be shown.")
    return DesktopBridge(app_id)


class KivMob:
    """Allows access to AdMob functionality on Android devices."""

    def __init__(self, appID):
        Logger.info("KivMob: __init__ called.")
        self._banner_top_pos = True
        self.bridge = _create_bridge(appID)

    def add_test_device(self, device):
        Logger.debug("KivMob: add_test_device() called.")
        self.bridge.add_test_device(device)

    def new_banner(self, unitID, top_pos=True):
        Logger.debug("KivMob: new_banner() called.")
        self.bridge.new_banner(unitID, top_pos)

    def new_interstitial(self, unitID):
        Logger.debug("KivMob: new_interstitial() called.")
        self.bridge.new_interstitial(unitID)

    def is_interstitial_loaded(self):
        Logger.debug("KivMob: is_interstitial_loaded() called.")
        return self.bridge.is_interstitial_loaded()

    def is_rewarded_loaded(self):
        Logger.debug("KivMob: is_rewarded_loaded() called.")
        return self.bridge.is_rewarded_loaded()

    def request_banner(self, options=None):
        Logger.debug("KivMob: request_banner() called.")
        self.bridge.request_banner(options)

    def request_interstitial(self, options=None):
        Logger.debug("KivMob: request_interstitial() called.")
        self.bridge.request_interstitial(options)

    def show_banner(self):
        Logger.debug("KivMob: show_banner() called.")
        self.bridge.show_banner()

    def show_interstitial(self):
        Logger.debug("KivMob: show_interstitial() called.")
        self.bridge.show_interstitial()

    def destroy_banner(self):
        Logger.debug("KivMob: destroy_banner() called.")
        self.bridge.destroy_banner()

    def destroy_interstitial(self):
        Logger.debug("KivMob: destroy_interstitial() called.")
        self.bridge.destroy_interstitial()

    def destroy_rewarded_video_ad(self):
        Logger.debug("KivMob: destroy_rewarded_video_ad() called.")
        self.bridge.destroy_rewarded_video_ad()

    def hide_banner(self):
        Logger.debug("KivMob: hide_banner() called.")
        self.bridge.hide_banner()

    def set_rewarded_ad_listener(self, listener):
        Logger.debug("KivMob: set_rewarded_ad_listener() called.")
        self.bridge.set_rewarded_ad_listener(listener)

    def load_rewarded_ad(self, unitID):
        Logger.debug("KivMob: load_rewarded_ad() called.")
        self.bridge.load_rewarded_ad(unitID)

    def show_rewarded_ad(self):
        Logger.debug("KivMob: show_rewarded_ad() called.")
        self.bridge.show_rewarded_ad()

    def determine_banner_height(self):
        height = dp(32)
        upper_bound = dp(720)
        if Window.height > upper_bound:
            height = dp(90)
        elif dp(400) < Window.height <= upper_bound:
            height = dp(50)
        return height


__all__ = [
    "AdMobBridge",
    "DesktopBridge",
    "KivMob",
    "RewardedListenerInterface",
    "TestIds",
    "iOSBridge",
    "_ad_load_callback_current",
    "_create_bridge",
    "__version__",
]
