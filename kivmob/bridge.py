"""Shared AdMob bridge contract and helpers."""


def _normalize_options(options):
    return {} if options is None else options


def _ad_load_callback_current(active_generation, load_generation):
    """True when an ad callback belongs to the current load (not destroyed/superseded)."""
    return active_generation == load_generation


class AdMobBridge:
    def __init__(self, appID):
        pass

    def add_test_device(self, testID):
        pass

    def is_interstitial_loaded(self):
        return False

    def is_rewarded_loaded(self):
        return False

    def new_banner(self, unitID, top_pos=True):
        pass

    def new_interstitial(self, unitID):
        pass

    def request_banner(self, options):
        pass

    def request_interstitial(self, options):
        pass

    def show_banner(self):
        pass

    def show_interstitial(self):
        pass

    def destroy_banner(self):
        pass

    def destroy_interstitial(self):
        pass

    def hide_banner(self):
        pass

    def set_rewarded_ad_listener(self, listener):
        pass

    def load_rewarded_ad(self, unitID):
        pass

    def show_rewarded_ad(self):
        pass

    def destroy_rewarded_video_ad(self):
        pass


class RewardedListenerInterface:
    """Interface for objects that handle rewarded video ad callback functions.

    On Android, ``on_rewarded_video_ad_left_application`` is not invoked by the
    current Mobile Ads SDK bridge (no equivalent callback in Play Services Ads
    25.x). ``on_rewarded_video_ad_completed`` is called on dismiss when the user
    earned a reward during that ad session.

    ``set_rewarded_ad_listener()`` may be called before load or while an ad is
    showing; the active listener is updated and in-flight reward state is kept.
    """

    def on_rewarded(self, reward_name, reward_amount):
        pass

    def on_rewarded_video_ad_left_application(self):
        """Not called on Android with the current Play Services Ads bridge."""
        pass

    def on_rewarded_video_ad_closed(self):
        pass

    def on_rewarded_video_ad_failed_to_load(self, error_code):
        pass

    def on_rewarded_video_ad_loaded(self):
        pass

    def on_rewarded_video_ad_opened(self):
        pass

    def on_rewarded_video_ad_started(self):
        pass

    def on_rewarded_video_ad_completed(self):
        pass
