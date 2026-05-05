from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.logger import Logger

# Import our updated KivMob module[cite: 1]
from kivmob import KivMob, TestIds, RewardedListenerInterface

class MyRewardedListener(RewardedListenerInterface):
    """
    This class handles events coming back from the KivmobRewarded.java wrapper[cite: 2].
    """
    def on_rewarded(self, reward_name, reward_amount):
        # This is triggered by the Java bridge when the user finishes the video[cite: 1, 2]
        print(f"REWARD GRANTED: You received {reward_amount} {reward_name}!")
        Logger.info(f"KivMob: User earned {reward_amount} {reward_name}")

    def on_rewarded_video_ad_loaded(self):
        print("Rewarded Ad: Ready to show!")

    def on_rewarded_video_ad_failed_to_load(self, error_code):
        print(f"Rewarded Ad: Failed to load. Error: {error_code}")


class AdTestLayout(BoxLayout):
    def __init__(self, ads, **kwargs):
        super().__init__(orientation='vertical', padding=30, spacing=20, **kwargs)
        self.ads = ads

        self.add_widget(Label(text="KivMob AdMob v20+ Tester", font_size='20sp', size_hint_y=0.2))

        # --- BANNER SECTION ---
        # Banners load and show immediately in this example[cite: 1]
        btn_banner = Button(text="Show/Refresh Banner", background_color=(0.2, 0.6, 1, 1))
        btn_banner.bind(on_release=lambda x: self.test_banner())
        self.add_widget(btn_banner)

        # --- INTERSTITIAL SECTION ---
        btn_load_interstitial = Button(text="Load Interstitial")
        btn_load_interstitial.bind(on_release=lambda x: self.load_interstitial())
        self.add_widget(btn_load_interstitial)

        btn_show_interstitial = Button(text="Show Interstitial")
        btn_show_interstitial.bind(on_release=lambda x: self.show_interstitial())
        self.add_widget(btn_show_interstitial)

        # --- REWARDED SECTION ---
        btn_load_rewarded = Button(text="Load Rewarded Ad")
        btn_load_rewarded.bind(on_release=lambda x: self.load_rewarded())
        self.add_widget(btn_load_rewarded)

        btn_show_rewarded = Button(text="Show Rewarded Ad", background_color=(0.2, 0.8, 0.2, 1))
        btn_show_rewarded.bind(on_release=lambda x: self.show_rewarded())
        self.add_widget(btn_show_rewarded)

    def test_banner(self):
        print("Action: Requesting Banner...")
        self.ads.new_banner(TestIds.BANNER, top_pos=False) #[cite: 1]
        self.ads.request_banner() #[cite: 1]
        self.ads.show_banner() #[cite: 1]

    def load_interstitial(self):
        print("Action: Loading Interstitial...")
        self.ads.new_interstitial(TestIds.INTERSTITIAL) #[cite: 1]
        self.ads.request_interstitial() #[cite: 1]

    def show_interstitial(self):
        if self.ads.is_interstitial_loaded(): #[cite: 1]
            print("Action: Showing Interstitial.")
            self.ads.show_interstitial() #[cite: 1]
        else:
            print("Status: Interstitial not loaded yet. Click Load first.")

    def load_rewarded(self):
        print("Action: Loading Rewarded Ad...")
        self.ads.load_rewarded_ad(TestIds.REWARDED_VIDEO) #[cite: 1]

    def show_rewarded(self):
        if self.ads.is_rewarded_loaded(): #[cite: 1]
            print("Action: Showing Rewarded Ad.")
            self.ads.show_rewarded_ad() #[cite: 1]
        else:
            print("Status: Rewarded Ad not loaded yet. Click Load first.")


class KivMobTestApp(App):
    def build(self):
        # 1. Initialize with App ID[cite: 1]
        self.ads = KivMob(TestIds.APP) 
        
        # 2. Add Test Device ID (Required for modern AdMob testing)[cite: 1]
        # Replace with your actual device ID hash from logcat
        self.ads.add_test_device("YOUR_DEVICE_HASH_ID") 

        # 3. Set the listener for Rewarded Video rewards[cite: 1]
        self.ads.set_rewarded_ad_listener(MyRewardedListener()) 

        return AdTestLayout(self.ads)

if __name__ == "__main__":
    KivMobTestApp().run()
