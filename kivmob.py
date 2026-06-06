from kivy.core.window import Window
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.utils import platform

try:
    from importlib.metadata import version as _package_version

    __version__ = _package_version("kivmob")
except Exception:
    __version__ = "0.0.0"

if platform == "android":
    try:
        from jnius import autoclass, java_method, PythonJavaClass
        from android.runnable import run_on_ui_thread

        activity = autoclass("org.kivy.android.PythonActivity")
        AdRequest = autoclass("com.google.android.gms.ads.AdRequest")
        AdRequestBuilder = autoclass("com.google.android.gms.ads.AdRequest$Builder")
        AdSize = autoclass("com.google.android.gms.ads.AdSize")
        AdView = autoclass("com.google.android.gms.ads.AdView")
        Bundle = autoclass("android.os.Bundle")
        Gravity = autoclass("android.view.Gravity")
        KivMobAdsBridge = autoclass("org.kivmob.kivmob.KivMobAdsBridge")
        LayoutParams = autoclass("android.view.ViewGroup$LayoutParams")
        LinearLayout = autoclass("android.widget.LinearLayout")
        MobileAds = autoclass("com.google.android.gms.ads.MobileAds")
        View = autoclass("android.view.View")
        AdMobAdapter = autoclass("com.google.ads.mediation.admob.AdMobAdapter")

    except BaseException as exc:
        Logger.error(
            "KivMob: Cannot load AdMob classes. Check buildozer.spec. %s" % exc
        )
        activity = None
        _ANDROID_ADS_OK = False
    else:
        _ANDROID_ADS_OK = True

        # --- JNI callbacks: Mobile Ads SDK bridge callbacks ---

        class KivOnInitCompleteListener(PythonJavaClass):
            __javainterfaces__ = [
                "com/google/android/gms/ads/initialization/OnInitializationCompleteListener"
            ]
            __javacontext__ = "app"

            def __init__(self, bridge):
                super().__init__()
                self._bridge = bridge

            @java_method(
                "(Lcom/google/android/gms/ads/initialization/InitializationStatus;)V"
            )
            def onInitializationComplete(self, _status):
                self._bridge._on_ads_initialized()

        class KivInterstitialBridgeListener(PythonJavaClass):
            __javainterfaces__ = ["org/kivmob/kivmob/KivMobInterstitialListener"]
            __javacontext__ = "app"

            def __init__(self, bridge):
                super().__init__()
                self._bridge = bridge

            @java_method("()V")
            def onInterstitialDismissed(self):
                Logger.info("KivMob: interstitial dismissed")
                self._bridge._interstitial_ad = None
                self._bridge._interstitial_loaded = False

            @java_method("(Ljava/lang/String;I)V")
            def onInterstitialFailed(self, message, _code):
                Logger.warning("KivMob: interstitial failed: %s" % message)
                self._bridge._interstitial_ad = None
                self._bridge._interstitial_loaded = False

            @java_method("()V")
            def onInterstitialLoaded(self):
                Logger.info("KivMob: interstitial loaded.")
                self._bridge._interstitial_loaded = True
                self._bridge._interstitial_ad = True

            @java_method("()V")
            def onInterstitialShown(self):
                Logger.info("KivMob: interstitial shown")

        class KivRewardedBridgeListener(PythonJavaClass):
            __javainterfaces__ = ["org/kivmob/kivmob/KivMobRewardedListener"]
            __javacontext__ = "app"

            def __init__(self, bridge, user_listener):
                super().__init__()
                self._bridge = bridge
                self._user = user_listener

            @java_method("()V")
            def onRewardedDismissed(self):
                Logger.info("KivMob: rewarded ad dismissed")
                if self._user is not None:
                    self._user.on_rewarded_video_ad_closed()
                self._bridge._rewarded_ad = None
                self._bridge._rewarded_loaded = False

            @java_method("(Ljava/lang/String;I)V")
            def onRewardedFailed(self, message, code):
                Logger.info("KivMob: rewarded ad failed: %s" % message)
                if self._user is not None:
                    self._user.on_rewarded_video_ad_failed_to_load(code)
                self._bridge._rewarded_ad = None
                self._bridge._rewarded_loaded = False

            @java_method("()V")
            def onRewardedShown(self):
                Logger.info("KivMob: rewarded ad shown")
                if self._user is not None:
                    self._user.on_rewarded_video_ad_opened()
                    self._user.on_rewarded_video_ad_started()

            @java_method("()V")
            def onRewardedLoaded(self):
                Logger.info("KivMob: rewarded ad loaded.")
                self._bridge._rewarded_ad = True
                self._bridge._rewarded_loaded = True
                if self._user is not None:
                    self._user.on_rewarded_video_ad_loaded()

            @java_method("(Ljava/lang/String;I)V")
            def onUserEarnedReward(self, reward_type, reward_amount):
                if self._user is not None:
                    self._user.on_rewarded(str(reward_type), str(reward_amount))

else:
    _ANDROID_ADS_OK = False

    def run_on_ui_thread(f):
        return f


class TestIds:
    """Enum of test ad ids provided by AdMob. This allows developers to
    test displaying ads without setting up an AdMob account.
    """

    APP = "ca-app-pub-3940256099942544~3347511713"
    BANNER = "ca-app-pub-3940256099942544/6300978111"
    INTERSTITIAL = "ca-app-pub-3940256099942544/1033173712"
    INTERSTITIAL_VIDEO = "ca-app-pub-3940256099942544/8691691433"
    REWARDED_VIDEO = "ca-app-pub-3940256099942544/5224354917"


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
    """Interface for objects that handle rewarded video ad callback functions."""

    def on_rewarded(self, reward_name, reward_amount):
        pass

    def on_rewarded_video_ad_left_application(self):
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


if platform == "android" and _ANDROID_ADS_OK:

    class AndroidBridge(AdMobBridge):
        @run_on_ui_thread
        def __init__(self, appID):
            self._app_id = appID
            self._adview = None
            self._banner_layout = None
            self._interstitial_ad = None
            self._interstitial_unit = None
            self._interstitial_loaded = False
            self._rewarded_ad = None
            self._rewarded_unit = None
            self._rewarded_loaded = False
            self._reward_listener = None
            self._interstitial_bridge_listener = KivInterstitialBridgeListener(self)
            self._rewarded_bridge_listener = KivRewardedBridgeListener(
                self, self._reward_listener
            )
            self._test_devices = []
            self._ads_initialized = False
            self._pending_banner_options = None
            self._pending_interstitial_options = None
            self._pending_rewarded_unit = None
            m_activity = activity.mActivity
            try:
                MobileAds.initialize(m_activity, KivOnInitCompleteListener(self))
            except Exception as e:
                Logger.error("KivMob: MobileAds.initialize failed: %s" % e)
            if appID and str(appID).strip():
                Logger.info(
                    "KivMob: App ID (also set com.google.android.gms.ads.APPLICATION_ID in buildozer): %s"
                    % (appID,)
                )

        @run_on_ui_thread
        def _on_ads_initialized(self):
            Logger.info("KivMob: Mobile Ads initialized.")
            self._ads_initialized = True
            if self._pending_banner_options is not None:
                options = self._pending_banner_options
                self._pending_banner_options = None
                self._load_banner(options)
            if self._pending_interstitial_options is not None:
                options = self._pending_interstitial_options
                self._pending_interstitial_options = None
                self._load_interstitial(options)
            if self._pending_rewarded_unit is not None:
                unit_id = self._pending_rewarded_unit
                self._pending_rewarded_unit = None
                self._load_rewarded(unit_id)

        @run_on_ui_thread
        def add_test_device(self, testID):
            self._test_devices.append(testID)

        def _banner_ad_size(self):
            dm = activity.mActivity.getResources().getDisplayMetrics()
            w_dp = int(dm.widthPixels / float(dm.density))
            try:
                return AdSize.getCurrentOrientationAnchoredAdaptiveBannerAdSize(
                    activity.mActivity, w_dp
                )
            except Exception:
                return AdSize.BANNER

        @run_on_ui_thread
        def new_banner(self, unitID, top_pos=True):
            if self._adview is not None:
                self._adview.destroy()
                self._adview = None
            self._banner_layout = None
            self._adview = AdView(activity.mActivity)
            self._adview.setAdUnitId(unitID)
            self._adview.setAdSize(self._banner_ad_size())
            self._adview.setVisibility(View.GONE)
            ad_layout = LayoutParams(
                LayoutParams.MATCH_PARENT, LayoutParams.WRAP_CONTENT
            )
            self._adview.setLayoutParams(ad_layout)
            layout = LinearLayout(activity.mActivity)
            if not top_pos:
                layout.setGravity(Gravity.BOTTOM)
            layout.addView(self._adview)
            outer = LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.MATCH_PARENT)
            layout.setLayoutParams(outer)
            self._banner_layout = layout
            activity.mActivity.addContentView(layout, outer)

        def _load_banner(self, options):
            if self._adview is not None:
                self._adview.loadAd(self._get_builder(options).build())

        @run_on_ui_thread
        def request_banner(self, options={}):
            if not self._ads_initialized:
                self._pending_banner_options = options
                return
            self._load_banner(options)

        @run_on_ui_thread
        def show_banner(self):
            if self._adview is not None:
                self._adview.setVisibility(View.VISIBLE)
                if self._banner_layout is not None:
                    self._banner_layout.bringToFront()

        @run_on_ui_thread
        def hide_banner(self):
            if self._adview is not None:
                self._adview.setVisibility(View.GONE)

        @run_on_ui_thread
        def new_interstitial(self, unitID):
            self._interstitial_unit = unitID
            self._interstitial_ad = None
            self._interstitial_loaded = False

        def _load_interstitial(self, options):
            if not self._interstitial_unit:
                Logger.error("KivMob: call new_interstitial(unit_id) first.")
                return
            self._interstitial_ad = None
            self._interstitial_loaded = False
            try:
                KivMobAdsBridge.loadInterstitial(
                    activity.mActivity,
                    self._interstitial_unit,
                    self._get_builder(options).build(),
                    self._interstitial_bridge_listener,
                )
            except Exception as exc:
                Logger.warning("KivMob: interstitial load disabled: %s" % exc)
                self._interstitial_ad = None
                self._interstitial_loaded = False

        @run_on_ui_thread
        def request_interstitial(self, options={}):
            if not self._ads_initialized:
                self._pending_interstitial_options = options
                return
            self._load_interstitial(options)

        def is_interstitial_loaded(self):
            try:
                loaded = bool(KivMobAdsBridge.isInterstitialLoaded())
            except Exception:
                loaded = False
            return self._interstitial_loaded and loaded

        @run_on_ui_thread
        def show_interstitial(self):
            try:
                KivMobAdsBridge.showInterstitial(activity.mActivity)
            except Exception as exc:
                Logger.warning("KivMob: show_interstitial failed: %s" % exc)

        @run_on_ui_thread
        def set_rewarded_ad_listener(self, listener):
            self._reward_listener = listener
            self._rewarded_bridge_listener = KivRewardedBridgeListener(
                self, self._reward_listener
            )

        def _load_rewarded(self, unitID):
            self._rewarded_unit = unitID
            self._rewarded_ad = None
            self._rewarded_loaded = False
            if not unitID:
                return
            try:
                KivMobAdsBridge.loadRewarded(
                    activity.mActivity,
                    unitID,
                    self._get_builder(None).build(),
                    self._rewarded_bridge_listener,
                )
            except Exception as exc:
                Logger.warning("KivMob: rewarded load disabled: %s" % exc)
                self._rewarded_ad = None
                self._rewarded_loaded = False

        @run_on_ui_thread
        def load_rewarded_ad(self, unitID):
            if not self._ads_initialized:
                self._pending_rewarded_unit = unitID
                return
            self._load_rewarded(unitID)

        def is_rewarded_loaded(self):
            try:
                loaded = bool(KivMobAdsBridge.isRewardedLoaded())
            except Exception:
                loaded = False
            return self._rewarded_loaded and loaded

        @run_on_ui_thread
        def show_rewarded_ad(self):
            try:
                KivMobAdsBridge.showRewarded(activity.mActivity)
            except Exception as exc:
                Logger.warning("KivMob: show_rewarded_ad failed: %s" % exc)

        @run_on_ui_thread
        def destroy_banner(self):
            if self._adview is not None:
                self._adview.destroy()
                self._adview = None

        @run_on_ui_thread
        def destroy_interstitial(self):
            self._interstitial_ad = None
            self._interstitial_loaded = False

        @run_on_ui_thread
        def destroy_rewarded_video_ad(self):
            self._rewarded_ad = None
            self._rewarded_loaded = False

        def _get_builder(self, options):
            builder = AdRequestBuilder()
            if options is not None:
                if "children" in options:
                    builder.tagForChildDirectedTreatment(options["children"])
                if "family" in options:
                    extras = Bundle()
                    extras.putBoolean("is_designed_for_families", options["family"])
                    try:
                        builder.addNetworkExtrasBundle(AdMobAdapter, extras)
                    except Exception as e:
                        Logger.warning("KivMob: addNetworkExtrasBundle: %s" % e)
            for test_device in self._test_devices:
                if len(self._test_devices) != 0:
                    builder.addTestDevice(test_device)
            return builder


class iOSBridge(AdMobBridge):
    pass


class KivMob:
    """Allows access to AdMob functionality on Android devices."""

    def __init__(self, appID):
        Logger.info("KivMob: __init__ called.")
        self._banner_top_pos = True
        if platform == "android" and _ANDROID_ADS_OK:
            Logger.info("KivMob: Android platform detected.")
            self.bridge = AndroidBridge(appID)
        elif platform == "ios":
            Logger.warning("KivMob: iOS not yet supported.")
            self.bridge = iOSBridge(appID)
        else:
            if platform == "android":
                Logger.error("KivMob: AdMob failed to load; no-op mode.")
            else:
                Logger.warning("KivMob: Ads will not be shown.")
            self.bridge = AdMobBridge(appID)

    def add_test_device(self, device):
        Logger.info("KivMob: add_test_device() called.")
        self.bridge.add_test_device(device)

    def new_banner(self, unitID, top_pos=True):
        Logger.info("KivMob: new_banner() called.")
        self.bridge.new_banner(unitID, top_pos)

    def new_interstitial(self, unitID):
        Logger.info("KivMob: new_interstitial() called.")
        self.bridge.new_interstitial(unitID)

    def is_interstitial_loaded(self):
        Logger.info("KivMob: is_interstitial_loaded() called.")
        return self.bridge.is_interstitial_loaded()

    def is_rewarded_loaded(self):
        return self.bridge.is_rewarded_loaded()

    def request_banner(self, options={}):
        Logger.info("KivMob: request_banner() called.")
        self.bridge.request_banner(options)

    def request_interstitial(self, options={}):
        Logger.info("KivMob: request_interstitial() called.")
        self.bridge.request_interstitial(options)

    def show_banner(self):
        Logger.info("KivMob: show_banner() called.")
        self.bridge.show_banner()

    def show_interstitial(self):
        Logger.info("KivMob: show_interstitial() called.")
        self.bridge.show_interstitial()

    def destroy_banner(self):
        Logger.info("KivMob: destroy_banner() called.")
        self.bridge.destroy_banner()

    def destroy_interstitial(self):
        Logger.info("KivMob: destroy_interstitial() called.")
        self.bridge.destroy_interstitial()

    def hide_banner(self):
        Logger.info("KivMob: hide_banner() called.")
        self.bridge.hide_banner()

    def set_rewarded_ad_listener(self, listener):
        Logger.info("KivMob: set_rewarded_ad_listener() called.")
        self.bridge.set_rewarded_ad_listener(listener)

    def load_rewarded_ad(self, unitID):
        Logger.info("KivMob: load_rewarded_ad() called.")
        self.bridge.load_rewarded_ad(unitID)

    def show_rewarded_ad(self):
        Logger.info("KivMob: show_rewarded_ad() called.")
        self.bridge.show_rewarded_ad()

    def determine_banner_height(self):
        height = dp(32)
        upper_bound = dp(720)
        if Window.height > upper_bound:
            height = dp(90)
        elif dp(400) < Window.height <= upper_bound:
            height = dp(50)
        return height


if __name__ == "__main__":
    print(
        "\033[92m  _  ___       __  __       _\n"
        " | |/ (_)_   _|  \\/  | ___ | |__\n"
        " | ' /| \\ \\ / / |\\/| |/ _ \\| '_ \\\n"
        " | . \\| |\\ V /| |  | | (_) | |_) |\n"
        " |_|\\_\\_| \\_/ |_|  |_|\\___/|_.__/\n\033[0m"
    )
    print(" AdMob support for Kivy\n")
    print(" Michael Stott, 2019\n")
