from kivy.core.window import Window
from kivy.logger import Logger
from kivy.metrics import dp
from kivy.utils import platform

if platform == "android":
    try:
        from jnius import autoclass, cast, PythonJavaClass, java_method
        from android.runnable import run_on_ui_thread

        activity = autoclass("org.kivy.android.PythonActivity")
        AdRequest = autoclass("com.google.android.gms.ads.AdRequest")
        AdRequestBuilder = autoclass("com.google.android.gms.ads.AdRequest$Builder")
        AdSize = autoclass("com.google.android.gms.ads.AdSize")
        AdView = autoclass("com.google.android.gms.ads.AdView")
        Gravity = autoclass("android.view.Gravity")
        LayoutParams = autoclass("android.view.ViewGroup$LayoutParams")
        LinearLayout = autoclass("android.widget.LinearLayout")
        MobileAds = autoclass("com.google.android.gms.ads.MobileAds")
        View = autoclass("android.view.View")
        ArrayList = autoclass("java.util.ArrayList")
        RequestConfigurationBuilder = autoclass("com.google.android.gms.ads.RequestConfiguration$Builder")
        
        # OUR JAVA BRIDGES
        KivmobInterstitial = autoclass("org.kivmob.wrapper.KivmobInterstitial")
        KivmobRewarded = autoclass("org.kivmob.wrapper.KivmobRewarded") # NEWLY ADDED

        # INTERSTITIAL AD LISTENER
        class InterstitialListener(PythonJavaClass):
            __javainterfaces__ = ["org.kivmob.wrapper.KivmobInterstitial$InterstitialListener"]
            __javacontext__ = "app"
            def __init__(self, bridge):
                super().__init__()
                self.bridge = bridge
            @java_method("()V")
            def onAdLoaded(self):
                Logger.info("KivMob: Interstitial Ad LOADED!")
                self.bridge._interstitial_loaded = True
            @java_method("(I)V")
            def onAdFailedToLoad(self, errorCode):
                self.bridge._interstitial_loaded = False
            @java_method("()V")
            def onAdDismissedFullScreenContent(self):
                self.bridge._interstitial_loaded = False
            @java_method("(I)V")
            def onAdFailedToShowFullScreenContent(self, errorCode):
                self.bridge._interstitial_loaded = False
            @java_method("()V")
            def onAdShowedFullScreenContent(self):
                pass

        # REWARDED AD LISTENER (NEWLY ADDED)
        class RewardedListener(PythonJavaClass):
            __javainterfaces__ = ["org.kivmob.wrapper.KivmobRewarded$RewardedListener"]
            __javacontext__ = "app"
            def __init__(self, bridge):
                super().__init__()
                self.bridge = bridge
            @java_method("()V")
            def onAdLoaded(self):
                Logger.info("KivMob: Rewarded Ad LOADED!")
                self.bridge._rewarded_loaded = True
                if self.bridge._custom_rewarded_listener:
                    self.bridge._custom_rewarded_listener.on_rewarded_video_ad_loaded()
            @java_method("(I)V")
            def onAdFailedToLoad(self, errorCode):
                self.bridge._rewarded_loaded = False
                if self.bridge._custom_rewarded_listener:
                    self.bridge._custom_rewarded_listener.on_rewarded_video_ad_failed_to_load(errorCode)
            @java_method("()V")
            def onAdDismissedFullScreenContent(self):
                self.bridge._rewarded_loaded = False
                if self.bridge._custom_rewarded_listener:
                    self.bridge._custom_rewarded_listener.on_rewarded_video_ad_closed()
            @java_method("(I)V")
            def onAdFailedToShowFullScreenContent(self, errorCode):
                self.bridge._rewarded_loaded = False
            @java_method("()V")
            def onAdShowedFullScreenContent(self):
                if self.bridge._custom_rewarded_listener:
                    self.bridge._custom_rewarded_listener.on_rewarded_video_ad_opened()
            @java_method("(Ljava/lang/String;I)V")
            def onUserEarnedReward(self, rewardType, rewardAmount):
                Logger.info(f"KivMob: REWARD EARNED! Amount: {rewardAmount} {rewardType}")
                if self.bridge._custom_rewarded_listener:
                    self.bridge._custom_rewarded_listener.on_rewarded(rewardType, rewardAmount)

    except BaseException as e:
        Logger.error(f"KivMob: AdMob classes could not be loaded. {e}")
else:
    def run_on_ui_thread(x): pass


class TestIds:
    APP = "ca-app-pub-3940256099942544~3347511713"
    BANNER = "ca-app-pub-3940256099942544/6300978111"
    INTERSTITIAL = "ca-app-pub-3940256099942544/1033173712"
    REWARDED_VIDEO = "ca-app-pub-3940256099942544/5224354917"

class RewardedListenerInterface:
    def on_rewarded(self, reward_name, reward_amount): pass
    def on_rewarded_video_ad_closed(self): pass
    def on_rewarded_video_ad_failed_to_load(self, error_code): pass
    def on_rewarded_video_ad_loaded(self): pass
    def on_rewarded_video_ad_opened(self): pass

class AdMobBridge:
    def __init__(self, appID): pass
    def add_test_device(self, testID): pass
    def is_interstitial_loaded(self): return False
    def is_rewarded_loaded(self): return False
    def new_banner(self, unitID, top_pos=True): pass
    def new_interstitial(self, unitID): pass
    def request_banner(self, options): pass
    def request_interstitial(self, options): pass
    def show_banner(self): pass
    def show_interstitial(self): pass
    def destroy_banner(self): pass
    def hide_banner(self): pass
    def set_rewarded_ad_listener(self, listener): pass
    def load_rewarded_ad(self, unitID): pass
    def show_rewarded_ad(self): pass


if platform == "android":
    class AndroidBridge(AdMobBridge):
        @run_on_ui_thread
        def __init__(self, appID):
            self._interstitial_loaded = False
            self._rewarded_loaded = False
            self._test_devices = []
            self._custom_rewarded_listener = None
            
            try: MobileAds.initialize(activity.mActivity)
            except ValueError as error: print(error)
                
            self._adview = AdView(activity.mActivity)
            
            # INTERSTITIAL BRIDGE
            self._interstitial_listener = InterstitialListener(self)
            self._interstitial_wrapper = KivmobInterstitial(activity.mActivity, self._interstitial_listener)
            self._interstitial_unit_id = None
            
            # REWARDED BRIDGE
            self._rewarded_listener = RewardedListener(self)
            self._rewarded_wrapper = KivmobRewarded(activity.mActivity, self._rewarded_listener)

        @run_on_ui_thread
        def add_test_device(self, testID):
            self._test_devices.append(testID)
            try:
                test_devices_list = ArrayList()
                for device in self._test_devices: test_devices_list.add(device)
                req_builder = RequestConfigurationBuilder()
                req_builder.setTestDeviceIds(test_devices_list)
                MobileAds.setRequestConfiguration(req_builder.build())
            except Exception as e: print(e)

        # BANNER AND INTERSTITIAL CODES (SAME AS BEFORE)
        @run_on_ui_thread
        def new_banner(self, unitID, top_pos=True):
            self._adview = AdView(activity.mActivity)
            self._adview.setAdUnitId(unitID)
            self._adview.setAdSize(AdSize.BANNER)
            self._adview.setVisibility(View.GONE)
            adLayoutParams = LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.WRAP_CONTENT)
            self._adview.setLayoutParams(adLayoutParams)
            layout = LinearLayout(activity.mActivity)
            if not top_pos: layout.setGravity(Gravity.BOTTOM)
            layout.addView(self._adview)
            layoutParams = LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.MATCH_PARENT)
            layout.setLayoutParams(layoutParams)
            activity.mActivity.addContentView(layout, layoutParams)

        @run_on_ui_thread
        def request_banner(self, options={}):
            self._adview.loadAd(self._get_builder(options).build())

        @run_on_ui_thread
        def show_banner(self): self._adview.setVisibility(View.VISIBLE)

        @run_on_ui_thread
        def hide_banner(self): self._adview.setVisibility(View.GONE)

        @run_on_ui_thread
        def destroy_banner(self): self._adview.destroy()

        @run_on_ui_thread
        def new_interstitial(self, unitID):
            self._interstitial_unit_id = unitID

        @run_on_ui_thread
        def request_interstitial(self, options={}):
            if self._interstitial_unit_id:
                builder = self._get_builder(options)
                self._interstitial_wrapper.loadAd(self._interstitial_unit_id, builder.build())

        def is_interstitial_loaded(self): return self._interstitial_loaded

        @run_on_ui_thread
        def show_interstitial(self): self._interstitial_wrapper.show()

        # REWARDED AD METHODS
        def set_rewarded_ad_listener(self, listener):
            self._custom_rewarded_listener = listener

        @run_on_ui_thread
        def load_rewarded_ad(self, unitID):
            builder = self._get_builder(None)
            self._rewarded_wrapper.loadAd(unitID, builder.build())
            
        def is_rewarded_loaded(self):
            return self._rewarded_loaded

        @run_on_ui_thread
        def show_rewarded_ad(self):
            self._rewarded_wrapper.show()

        def _get_builder(self, options):
            builder = AdRequestBuilder()
            return builder
else:
    class iOSBridge(AdMobBridge): pass

class KivMob:
    def __init__(self, appID):
        self._banner_top_pos = True
        if platform == "android": self.bridge = AndroidBridge(appID)
        elif platform == "ios": self.bridge = iOSBridge(appID)
        else: self.bridge = AdMobBridge(appID)

    def add_test_device(self, device): self.bridge.add_test_device(device)
    def new_banner(self, unitID, top_pos=True): self.bridge.new_banner(unitID, top_pos)
    def new_interstitial(self, unitID): self.bridge.new_interstitial(unitID)
    def is_interstitial_loaded(self): return self.bridge.is_interstitial_loaded()
    def is_rewarded_loaded(self): return self.bridge.is_rewarded_loaded()
    def request_banner(self, options={}): self.bridge.request_banner(options)
    def request_interstitial(self, options={}): self.bridge.request_interstitial(options)
    def show_banner(self): self.bridge.show_banner()
    def show_interstitial(self): self.bridge.show_interstitial()
    def destroy_banner(self): self.bridge.destroy_banner()
    def hide_banner(self): self.bridge.hide_banner()
    def set_rewarded_ad_listener(self, listener): self.bridge.set_rewarded_ad_listener(listener)
    def load_rewarded_ad(self, unitID): self.bridge.load_rewarded_ad(unitID)
    def show_rewarded_ad(self): self.bridge.show_rewarded_ad()

if __name__ == "__main__":
    pass
