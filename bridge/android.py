from kivy.logger import Logger

try:
    from jnius import autoclass, cast, PythonJavaClass, java_method
    from android.runnable import run_on_ui_thread

    activity = autoclass("org.kivy.android.PythonActivity")
    AdListener = autoclass("com.google.android.gms.ads.AdListener")
    AdMobAdapter = autoclass("com.google.ads.mediation.admob.AdMobAdapter")
    AdRequest = autoclass("com.google.android.gms.ads.AdRequest")
    AdRequestBuilder = autoclass(
        "com.google.android.gms.ads.AdRequest$Builder"
    )
    AdSize = autoclass("com.google.android.gms.ads.AdSize")
    AdView = autoclass("com.google.android.gms.ads.AdView")
    Bundle = autoclass("android.os.Bundle")
    Gravity = autoclass("android.view.Gravity")
    InterstitialAd = autoclass("com.google.android.gms.ads.InterstitialAd")
    LayoutParams = autoclass("android.view.ViewGroup$LayoutParams")
    LinearLayout = autoclass("android.widget.LinearLayout")
    MobileAds = autoclass("com.google.android.gms.ads.MobileAds")
    RewardItem = autoclass("com.google.android.gms.ads.reward.RewardItem")
    RewardedVideoAd = autoclass(
        "com.google.android.gms.ads.reward.RewardedVideoAd"
    )
    RewardedVideoAdListener = autoclass(
        "com.google.android.gms.ads.reward.RewardedVideoAdListener"
    )
    View = autoclass("android.view.View")

    class AdMobRewardedVideoAdListener(PythonJavaClass):

        __javainterfaces__ = (
            "com.google.android.gms.ads.reward.RewardedVideoAdListener",
        )
        __javacontext__ = "app"

        def __init__(self, listener):
            self._listener = listener

        @java_method("(Lcom/google/android/gms/ads/reward/RewardItem;)V")
        def onRewarded(self, reward):
            Logger.info("KivMob: onRewarded() called.")
            self._listener.on_rewarded(reward.getType(), reward.getAmount())

        @java_method("()V")
        def onRewardedVideoAdLeftApplication(self):
            Logger.info("KivMob: onRewardedVideoAdLeftApplicaxtion() called.")
            self._listener.on_rewarded_video_ad_left_application()

        @java_method("()V")
        def onRewardedVideoAdClosed(self):
            Logger.info("KivMob: onRewardedVideoAdClosed() called.")
            self._listener.on_rewarded_video_ad_closed()

        @java_method("(I)V")
        def onRewardedVideoAdFailedToLoad(self, errorCode):
            Logger.info("KivMob: onRewardedVideoAdFailedToLoad() called.")
            # Logger.info('KivMob: ErrorCode ' + str(errorCode))
            self._listener.on_rewarded_video_ad_failed_to_load(errorCode)

        @java_method("()V")
        def onRewardedVideoAdLoaded(self):
            Logger.info("KivMob: onRewardedVideoAdLoaded() called.")
            self._listener.on_rewarded_video_ad_loaded()

        @java_method("()V")
        def onRewardedVideoAdOpened(self):
            Logger.info("KivMob: onRewardedVideoAdOpened() called.")
            self._listener.on_rewarded_video_ad_opened()

        @java_method("()V")
        def onRewardedVideoStarted(self):
            Logger.info("KivMob: onRewardedVideoStarted() called.")
            self._listener.on_rewarded_video_ad_started()

        @java_method("()V")
        def onRewardedVideoCompleted(self):
            Logger.info("KivMob: onRewardedVideoCompleted() called.")
            self._listener.on_rewarded_video_ad_completed()


except BaseException:
    Logger.error("KivMob: Cannot load AdMob classes. Check buildozer.spec.")

from bridge.bridge import AdMobBridge


class AndroidBridge(AdMobBridge):
    @run_on_ui_thread
    def __init__(self, app_id):
        self._loaded = False
        MobileAds.initialize(activity.mActivity, app_id)
        self._adview = AdView(activity.mActivity)
        self._interstitial = InterstitialAd(activity.mActivity)
        self._rewarded = MobileAds.getRewardedVideoAdInstance(
            activity.mActivity
        )
        self._test_devices = []

    @run_on_ui_thread
    def add_test_device(self, test_id):
        self._test_devices.append(test_id)

    @run_on_ui_thread
    def new_banner(self, unit_id, top_pos=True):
        self._adview = AdView(activity.mActivity)
        self._adview.setAdUnitId(unit_id)
        self._adview.setAdSize(AdSize.SMART_BANNER)
        self._adview.setVisibility(View.GONE)
        adLayoutParams = LayoutParams(
            LayoutParams.MATCH_PARENT, LayoutParams.WRAP_CONTENT
        )
        self._adview.setLayoutParams(adLayoutParams)
        layout = LinearLayout(activity.mActivity)
        if not top_pos:
            layout.setGravity(Gravity.BOTTOM)
        layout.addView(self._adview)
        layoutParams = LayoutParams(
            LayoutParams.MATCH_PARENT, LayoutParams.MATCH_PARENT
        )
        layout.setLayoutParams(layoutParams)
        activity.addContentView(layout, layoutParams)

    @run_on_ui_thread
    def request_banner(self, options={}):
        self._adview.loadAd(self._get_builder(options).build())

    @run_on_ui_thread
    def show_banner(self):
        self._adview.setVisibility(View.VISIBLE)

    @run_on_ui_thread
    def hide_banner(self):
        self._adview.setVisibility(View.GONE)

    @run_on_ui_thread
    def new_interstitial(self, unit_id):
        self._interstitial.setAdUnitId(unit_id)

    @run_on_ui_thread
    def request_interstitial(self, options={}):
        self._interstitial.loadAd(self._get_builder(options).build())

    @run_on_ui_thread
    def _is_interstitial_loaded(self):
        self._loaded = self._interstitial.isLoaded()

    def is_interstitial_loaded(self):
        self._is_interstitial_loaded()
        return self._loaded

    @run_on_ui_thread
    def show_interstitial(self):
        if self.is_interstitial_loaded():
            self._interstitial.show()

    @run_on_ui_thread
    def set_rewarded_ad_listener(self, listener):
        self._listener = AdMobRewardedVideoAdListener(listener)
        self._rewarded.setRewardedVideoAdListener(self._listener)

    @run_on_ui_thread
    def load_rewarded_ad(self, unit_id):
        builder = self._get_builder(None)
        self._rewarded.loadAd(unit_id, builder.build())

    @run_on_ui_thread
    def show_rewarded_ad(self):
        if self._rewarded.isLoaded():
            self._rewarded.show()

    @run_on_ui_thread
    def destroy_banner(self):
        self._adview.destroy()

    @run_on_ui_thread
    def destroy_interstitial(self):
        self._interstitial.destroy()

    @run_on_ui_thread
    def destroy_rewarded_video_ad(self):
        self._rewarded.destroy()

    def _get_builder(self, options):
        builder = AdRequestBuilder()
        if options is not None:
            if "children" in options:
                builder.tagForChildDirectedTreatment(options["children"])
            if "family" in options:
                extras = Bundle()
                extras.putBoolean(
                    "is_designed_for_families", options["family"]
                )
                builder.addNetworkExtrasBundle(AdMobAdapter, extras)
        for test_device in self._test_devices:
            builder.addTestDevice(test_device)
        return builder
