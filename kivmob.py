import kivy
from kivy.utils import platform
from kivy.logger import Logger
from kivy.lang import Builder
from kivy.core.window import Window


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


class KivMob:
    """ Allows access to AdMob functionality on Android devices.
    """

    def __init__(self, app_id):
        Logger.info("KivMob: __init__ called.")
        self._banner_top_pos = True
        if platform == "android":
            Logger.info("KivMob: Android platform detected.")
            from bridge.android import AndroidBridge

            self.bridge = AndroidBridge(app_id)
        elif platform == "ios":
            Logger.warning("KivMob: iOS not yet supported.")
            # self.bridge = iOSBridge(app_id)
        else:
            Logger.info(
                "KivMob: Desktop platform detected. Ads will not be shown."
            )
            from bridge.desktop import DesktopBridge

            self.bridge = DesktopBridge(app_id)

    def add_test_device(self, device):
        """ Add test device ID, which will trigger test ads to be displayed on
            that device

            :type device: string
            :param device: The test device ID of the Android device.
        """
        Logger.info("KivMob: add_test_device() called.")
        self.bridge.add_test_device(device)

    def new_banner(self, unit_id, top_pos=True):
        """ Create a new mobile banner ad.

            :type unit_id: string
            :param unit_id: AdMob banner ID for mobile application.
            :type top_pos: boolean
            :param top_pos: Positions banner at the top of the page if True,
            bottom if otherwise.
        """
        Logger.info("KivMob: new_banner() called.")
        self.bridge.new_banner(unit_id, top_pos)

    def new_interstitial(self, unit_id):
        """ Create a new mobile interstitial ad.

            :type unit_id: string
            :param unit_id: AdMob interstitial ID for mobile application.
        """
        Logger.info("KivMob: new_interstitial() called.")
        self.bridge.new_interstitial(unit_id)

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

    def load_rewarded_ad(self, unit_id):
        """ Load rewarded video ad.

            :type unit_id: string
            :param unit_id: AdMob rewarded video ID for mobile application.
        """
        Logger.info("KivMob: load_rewarded_ad() called.")
        self.bridge.load_rewarded_ad(unit_id)

    def show_rewarded_ad(self):
        """ Display rewarded video ad.
        """
        Logger.info("KivMob: show_rewarded_ad() called.")
        self.bridge.show_rewarded_ad()

    def determine_banner_height(self):
        """ Utility function for determining the height (dp) of the banner ad.

            :return height: Height of banner ad in dp.
        """
        height = 32
        upper_bound = kivy.metrics.dp(720)
        if Window.height > upper_bound:
            height = 90
        elif (
            Window.height > kivy.metrics.dp(400)
            and Window.height <= upper_bound
        ):
            height = 50
        return height


if __name__ == "__main__":
    KivMob(TestIds.APP)
    print(
        "\033[92m  _  ___       __  __       _\n"
        " | |/ (_)_   _|  \\/  | ___ | |__\n"
        " | ' /| \\ \\ / / |\\/| |/ _ \\| '_ \\\n"
        " | . \\| |\\ V /| |  | | (_) | |_) |\n"
        " |_|\\_\\_| \\_/ |_|  |_|\\___/|_.__/\n\033[0m"
    )
    print(" AdMob support for Kivy\n")
    print(" Michael Stott, 2019\n")
