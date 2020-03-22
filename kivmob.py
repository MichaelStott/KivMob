import kivy
from kivy.utils import platform
from kivy.logger import Logger
from kivy.lang import Builder
from kivy.core.window import Window


if platform == "android":
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
                self._listener.on_rewarded(
                    reward.getType(), reward.getAmount()
                )

            @java_method("()V")
            def onRewardedVideoAdLeftApplication(self):
                Logger.info(
                    "KivMob: onRewardedVideoAdLeftApplicaxtion() called."
                )
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
        Logger.error(
            "KivMob: Cannot load AdMob classes. Check buildozer.spec."
        )
else:

    class AdMobRewardedVideoAdListener:
        pass

    def run_on_ui_thread(x):
        pass


class TestIds:
    """ Enum of test ad ids provided by AdMob. This allows developers to
        test displaying ads without setting up an AdMob account.
    """

    """ Test AdMob App ID """
    APP = "ca-app-pub-3940256099942544~3347511713"

    """ Test Banner Ad ID """
    BANNER = "ca-app-pub-3940256099942544/6300978111"

    """ Test Interstitial Ad ID """
    INTERSTITIAL = "ca-app-pub-3940256099942544/1033173712"

    """ Test Interstitial Video Ad ID """
    INTERSTITIAL_VIDEO = "ca-app-pub-3940256099942544/8691691433"

    """ Test Rewarded Video Ad ID """
    REWARDED_VIDEO = "ca-app-pub-3940256099942544/5224354917"


class AdMobBridge:
    def __init__(self, appID):
        pass

    def add_test_device(self, testID):
        pass

    def is_interstitial_loaded(self):
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


class RewardedListenerInterface:
    """ Interface for objects that handle rewarded video ad
        callback functions
    """

    def on_rewarded(self, reward_name, reward_amount):
        """ Called when the video completes

            :type reward_name: string
            :param reward_name: Name of the reward.
            :type reward_amount: string
            :param reward_amount: Amount of the reward.
        """
        pass

    def on_rewarded_video_ad_left_application(self):
        """ Called when the user closes the application while
            the video is playing.
        """
        pass

    def on_rewarded_video_ad_closed(self):
        """ Called when the user manually closes the ad before completion.
        """
        pass

    def on_rewarded_video_ad_failed_to_load(self, error_code):
        """ Called when the rewarded video ad fails to load.

            :type error_code: int
            :param error_code: Integer code that corresponds to the error.
        """
        pass

    def on_rewarded_video_ad_loaded(self):
        """ Called when the rewarded ad finishes loading.
        """
        pass

    def on_rewarded_video_ad_opened(self):
        """ Called when the rewarded ad is opened.
        """
        pass

    def on_rewarded_video_ad_started(self):
        """ Called when the rewarded video ad starts.
        """
        pass

    def on_rewarded_video_ad_completed(self):
        """ Called when the rewarded video ad completes.
        """
        pass


class AndroidBridge(AdMobBridge):
    @run_on_ui_thread
    def __init__(self, appID):
        self._loaded = False
        MobileAds.initialize(activity.mActivity, appID)
        self._adview = AdView(activity.mActivity)
        self._interstitial = InterstitialAd(activity.mActivity)
        self._rewarded = MobileAds.getRewardedVideoAdInstance(
            activity.mActivity
        )
        self._test_devices = []

    @run_on_ui_thread
    def add_test_device(self, testID):
        self._test_devices.append(testID)

    @run_on_ui_thread
    def new_banner(self, unitID, top_pos=True):
        self._adview = AdView(activity.mActivity)
        self._adview.setAdUnitId(unitID)
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
    def new_interstitial(self, unitID):
        self._interstitial.setAdUnitId(unitID)

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
    def load_rewarded_ad(self, unitID):
        builder = self._get_builder(None)
        self._rewarded.loadAd(unitID, builder.build())

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


class iOSBridge(AdMobBridge):
    # TODO
    pass


class KivMob:
    """ Allows access to AdMob functionality on Android devices.
    """

    def __init__(self, appID):
        Logger.info("KivMob: __init__ called.")
        self._banner_top_pos = True
        if platform == "android":
            Logger.info("KivMob: Android platform detected.")
            self.bridge = AndroidBridge(appID)
        elif platform == "ios":
            Logger.warning("KivMob: iOS not yet supported.")
            self.bridge = iOSBridge(appID)
        else:
            Logger.warning("KivMob: Ads will not be shown.")
            self.bridge = AdMobBridge(appID)

    def add_test_device(self, device):
        """ Add test device ID, which will tigger test ads to be displayed on
            that device

            :type device: string
            :param device: The test device ID of the Android device.
        """
        Logger.info("KivMob: add_test_device() called.")
        self.bridge.add_test_device(device)

    def new_banner(self, unitID, top_pos=True):
        """ Create a new mobile banner ad.

            :type unitID: string
            :param unitID: AdMob banner ID for mobile application.
            :type top_pos: boolean
            :param top_pos: Positions banner at the top of the page if True,
            bottom if otherwise.
        """
        Logger.info("KivMob: new_banner() called.")
        self.bridge.new_banner(unitID, top_pos)

    def new_interstitial(self, unitID):
        """ Create a new mobile interstitial ad.

            :type unitID: string
            :param unitID: AdMob interstitial ID for mobile application.
        """
        Logger.info("KivMob: new_interstitial() called.")
        self.bridge.new_interstitial(unitID)

    def is_interstitial_loaded(self):
        """ Check if the interstitial ad has loaded.
        """
        Logger.info("KivMob: is_interstitial_loaded() called.")
        return self.bridge.is_interstitial_loaded()

    def request_banner(self, options={}):
        """ Request a new banner ad from AdMob.
        """
        Logger.info("KivMob: request_banner() called.")
        self.bridge.request_banner(options)

    def request_interstitial(self, options={}):
        """ Request a new interstitial ad from AdMob.
        """
        Logger.info("KivMob: request_interstitial() called.")
        self.bridge.request_interstitial(options)

    def show_banner(self):
        """ Displays banner ad, if it has loaded.
        """
        Logger.info("KivMob: show_banner() called.")
        self.bridge.show_banner()

    def show_interstitial(self):
        """ Displays interstitial ad, if it has loaded.
        """
        Logger.info("KivMob: show_interstitial() called.")
        self.bridge.show_interstitial()

    def destroy_banner(self):
        """ Destroys current banner ad.
        """
        Logger.info("KivMob: destroy_banner() called.")
        self.bridge.destroy_banner()

    def destroy_interstitial(self):
        """ Destroys current interstitial ad.
        """
        Logger.info("KivMob: destroy_interstitial() called.")
        self.bridge.destroy_interstitial()

    def hide_banner(self):
        """  Hide current banner ad.
        """
        Logger.info("KivMob: hide_banner() called.")
        self.bridge.hide_banner()

    def set_rewarded_ad_listener(self, listener):
        """ Set listener object for rewarded video ads.

            :type listener: AdMobRewardedVideoAdListener
            :param listener: Handles callback functionality for
            rewarded video ads.
        """
        Logger.info("KivMob: set_rewarded_ad_listener() called.")
        self.bridge.set_rewarded_ad_listener(listener)

    def load_rewarded_ad(self, unitID):
        """ Load rewarded video ad.

            :type unitID: string
            :param unitID: AdMob rewarded video ID for mobile application.
        """
        Logger.info("KivMob: load_rewarded_ad() called.")
        self.bridge.load_rewarded_ad(unitID)

    def show_rewarded_ad(self):
        """ Display rewarded video ad.
        """
        Logger.info("KivMob: show_rewarded_ad() called.")
        self.bridge.show_rewarded_ad()

    def determine_banner_height(self):
        """ Utility function for determining the height (dp) of the banner ad
        """
        height = 32
        upper_bound = kivy.metrics.dp(720)
        if Window.height > upper_bound:
            height = 90
        elif Window.height > kivy.metrics.dp(400) and Window.height <= upper_bound:
            height = 50
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
