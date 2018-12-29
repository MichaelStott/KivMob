from kivy.utils import platform
from kivy.logger import Logger

if platform == 'android':
    try:
        from jnius import autoclass, cast, PythonJavaClass, java_method
        from android.runnable import run_on_ui_thread
        activity = autoclass('org.kivy.android.PythonActivity')
        AdListener = autoclass('com.google.android.gms.ads.AdListener')
        AdMobAdapter = autoclass('com.google.ads.mediation.admob.AdMobAdapter')
        AdRequest = autoclass('com.google.android.gms.ads.AdRequest')
        AdRequestBuilder = autoclass('com.google.android.gms.ads.AdRequest$Builder')
        AdSize = autoclass('com.google.android.gms.ads.AdSize')
        AdView = autoclass('com.google.android.gms.ads.AdView')
        Bundle = autoclass('android.os.Bundle')
        Gravity = autoclass('android.view.Gravity')
        InterstitialAd = autoclass('com.google.android.gms.ads.InterstitialAd')
        LayoutParams = autoclass('android.view.ViewGroup$LayoutParams') 
        LinearLayout = autoclass('android.widget.LinearLayout')
        MobileAds = autoclass('com.google.android.gms.ads.MobileAds')
        RewardedVideoAd = autoclass('com.google.android.gms.ads.reward.RewardedVideoAd')
        View = autoclass('android.view.View')

        class RewardedVideoAdListener(PythonJavaClass):

            __javainterfaces__ = ['com/google/android/gms/ads/reward/RewardedVideoAdListener']

            @java_method('()Z')
            def onRewarded(reward):
                pass

            @java_method('()Z')
            def onRewardedVideoAdLeftApplication():
                pass

            @java_method('()Z')
            def onRewardedVideoAdClosed():
                pass

            @java_method('()Z')
            def onRewardedVideoAdFailedToLoad():
                pass

            @java_method('()Z')
            def onRewardedVideoAdLoaded():
                pass

            @java_method('()Z')
            def onRewardedVideoAdOpened():
                pass

            @java_method('()Z')
            def onRewardedVideoStarted():
                pass

            @java_method('()Z')
            def onRewardedVideoCompleted():
                pass
    except:
        Logger.info('KivMob: Cannot load AdMob classes. Check buildozer.spec configuration.')
else:
    class RewardedVideoAdListener():
        pass

    def run_on_ui_thread(x):
        pass
        

class TestIds():
    """ Enum of test ad ids provided by AdMob. This allows developers to test displaying ads
        without setting up an AdMob account.

        App ID Source: https://developers.google.com/admob/android/quick-start
        Ad IDs Source: https://developers.google.com/admob/android/test-ads
    """

    APP = "ca-app-pub-3940256099942544~3347511713"
    BANNER =  "ca-app-pub-3940256099942544/6300978111"
    INTERSTITIAL = "ca-app-pub-3940256099942544/1033173712"
    INTERSTITIAL_VIDEO = "ca-app-pub-3940256099942544/8691691433"
    REWARDED_VIDEO = "ca-app-pub-3940256099942544/5224354917"
    

class AdMobBridge():
    """ Interface for communicating with native AdMob library.
    """

    def __init__(self, appID):
        """ Initialize platform specific features here.
        """
        Logger.info('KivMob: __init__ called.')
        
    def add_test_device(self, testID):
        """ Add a test device.
        """
        Logger.info('KivMob: add_test_device() called.')

    def is_interstitial_loaded(self):
        """ Add a test device.
        """
        Logger.info('KivMob: is_interstitial_loaded() called.')
        return False
        
    def new_banner(self, unitID, top_pos=True):
        """ Create a new banner ad.
        """
        Logger.info('KivMob: new_banner() called.')

    def new_interstitial(self, unitID):
        """ Create a new interstitial ad.
        """
        Logger.info('KivMob: new_interstitial() called.')
    
    def request_banner(self, options):
        """ Requests new banner ad.
        """
        Logger.info('KivMob: request_banner() called.')

    def request_interstitial(self, options):
        """ Requests new interstitial ad.
        """
        Logger.info('KivMob: request_interstitial() called.')
        
    def show_banner(self):
        """ If possible, show banner ad.

            NOTE: You must call request_banner() beforehand!
        """
        Logger.info('KivMob: show_banner() called.')

    def show_interstitial(self):
        """ If possible, show interstitial ad.

            NOTE: You must call request_interstitial() beforehand!
        """
        Logger.info('KivMob: show_interstitial() called.')
    
    def destroy_banner(self):
        """ Destory current banner ad.
        """
        Logger.info('KivMob: destroy_banner() called.')

    def destroy_interstitial(self):
        """ Destroy interstitial ad.
        """
        Logger.info('KivMob: destroy_interstitial() called.')

    def hide_banner(self):
        """ Hide banner ad.
        """
        Logger.info('KivMob: hide_banner() called.')

    def load_rewarded_ad(self, unitID):
        ''' Load rewarded ad.
        '''
        Logger.info('KivMob: load_rewarded_ad() called.')

    def show_rewarded_ad(self):
        ''' If possible, show rewardeed video app.
        '''
        Logger.info('KivMob: show_rewarded_ad() called.')

class AndroidBridge(AdMobBridge):

    @run_on_ui_thread
    def __init__(self, appID):
        self._loaded = False
        self._adview = AdView(activity.mActivity)
        self._interstitial = InterstitialAd(activity.mActivity)
        MobileAds.initialize(activity.mActivity, appID)
        self._rewarded = MobileAds.getRewardedVideoAdInstance(activity.mActivity)

    @run_on_ui_thread
    def new_banner(self, unitID, top_pos=True):
        self._adview = AdView(activity.mActivity)
        self._adview.setAdUnitId(unitID)
        self._adview.setAdSize(AdSize.SMART_BANNER)
        self._adview.setVisibility(View.GONE)
        adLayoutParams = LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.WRAP_CONTENT)
        self._adview.setLayoutParams(adLayoutParams)
        layout = LinearLayout(activity.mActivity)
        if not top_pos:
            layout.setGravity(Gravity.BOTTOM)
        layout.addView(self._adview)
        layoutParams = LayoutParams(LayoutParams.MATCH_PARENT, LayoutParams.MATCH_PARENT)
        layout.setLayoutParams(layoutParams)
        activity.addContentView(layout, layoutParams)
        

    @run_on_ui_thread
    def request_banner(self, options={}):
        self._adview.loadAd(AdRequestBuilder().build())

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
        builder = AdRequestBuilder()
        if "children" in options:
            builder.tagForChildDirectedTreatment(options["children"])
        if "family" in options:
            extras = Bundle()
            extras.putBoolean("is_designed_for_families", options['family'])
            builder.addNetworkExtrasBundle(AdMobAdapter, extras)
        self._interstitial.loadAd(builder.build())

    @run_on_ui_thread
    def _is_interstitial_loaded(self):
        self._loaded = self._interstitial.isLoaded()

    def is_interstitial_loaded(self):
        # Values returned from run_on_ui_thread appear as
        # NoneType. Setting the result to private variable
        # self._loaded before returning solves this issue.
        self._is_interstitial_loaded()
        return self._loaded

    @run_on_ui_thread
    def show_interstitial(self):
        if self.is_interstitial_loaded():
            self._interstitial.show()

    @run_on_ui_thread
    def load_rewarded_ad(self, unitID):
        self._rewarded.loadAd(unitID, AdRequestBuilder().build())

    @run_on_ui_thread
    def show_rewarded_ad(self):
        self._rewarded.show()


class iOSBridge(AdMobBridge):
    # TODO
    pass


class KivMob():

    def __init__(self, appID):
        if platform == 'android':
            Logger.info('KivMob: Android platform detected.')
            self.bridge = AndroidBridge(appID)
        elif platform == 'ios':
            Logger.warning('KivMob: iOS not yet supported.')
            self.bridge = iOSBridge(appID)
        else:
            Logger.warning('KivMob: Ads will not be shown.')
            self.bridge = AdMobBridge(appID)

    def add_test_device(self, device):
        self.bridge.add_test_device(device)
        
    def new_banner(self, unitID, top_pos=True):
        self.bridge.new_banner(unitID, top_pos)

    def new_interstitial(self, options={}):
        self.bridge.new_interstitial(options)

    def is_interstitial_loaded(self):
        return self.bridge.is_interstitial_loaded()

    def request_banner(self, options={}):
        self.bridge.request_banner(options)
        
    def request_interstitial(self, options={}):
        self.bridge.request_interstitial(options)
        
    def show_banner(self):
        self.bridge.show_banner()

    def show_interstitial(self):
        self.bridge.show_interstitial()

    def destroy_banner(self):
        self.bridge.destroy_banner()

    def destroy_interstitial(self):
        self.bridge.destroy_interstitial()

    def hide_banner(self):
        self.bridge.hide_banner()

    def load_rewarded_ad(self, unitID):
        self.bridge.load_rewarded_ad(unitID)

    def show_rewarded_ad(self):
        self.bridge.show_rewarded_ad()


if __name__ == '__main__':
    print("\033[92m  _  ___       __  __       _\n" +\
          " | |/ (_)_   _|  \/  | ___ | |__\n" +\
          " | ' /| \ \ / / |\/| |/ _ \| '_ \\\n" +\
          " | . \| |\ V /| |  | | (_) | |_) |\n" +\
          " |_|\_\_| \_/ |_|  |_|\___/|_.__/\n\033[0m")
    print(" Michael Stott, 2017\n")
    
