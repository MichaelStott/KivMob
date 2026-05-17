from kivmob import KivMob, TestIds, RewardedListenerInterface

import kivy.utils
from kivymd.app import MDApp
from kivy.lang import Builder
from kivy.config import Config
from kivy.utils import platform
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager
from kivy.uix.image import Image
from kivy.properties import NumericProperty
from kivy.logger import Logger


def _configure_window_for_desktop_preview(platform_name):
    """Resize window on desktop only (unit-test both branches without faking imports)."""
    if platform_name not in ("android", "ios"):
        # Approximate dimensions of mobile phone.
        Config.set("graphics", "resizable", "0")
        Window.size = (400, 600)


_configure_window_for_desktop_preview(platform)

__version__ = "1.0"

from kivymd.theming import ThemeManager
from kivymd.uix.list import ILeftBody
from kivymd.uix.list import OneLineListItem
from kivymd.uix.list import TwoLineListItem
from kivymd.uix.list import ThreeLineListItem

Builder.load_string(
"""
#:import kivy kivy
#.import Snackbar kivymd.uix.snackbar.Snackbar
#:import MDList kivymd.uix.list.MDList
#:import OneLineListItem kivymd.uix.list.OneLineListItem
#:import TwoLineListItem kivymd.uix.list.TwoLineListItem
#:import ThreeLineListItem kivymd.uix.list.ThreeLineListItem

#:import webbrowser webbrowser

<KivMobDemoUI>:
    BoxLayout:
        orientation: 'vertical'
        BoxLayout:
            size_hint_y: None
            height: "56dp"
            padding: "8dp", 0
            spacing: "8dp"
            canvas.before:
                Color:
                    rgba: app.theme_cls.primary_color
                Rectangle:
                    pos: self.pos
                    size: self.size
            Button:
                id: back_btn
                text: "<"
                size_hint_x: None
                width: "48dp"
                opacity: 0
                disabled: True
                on_release: root.back_to_menu()
            Label:
                id: title_lbl
                text: "KivMob 2.0"
                color: 1, 1, 1, 1
                halign: "left"
                valign: "middle"
                text_size: self.size
        ScreenManager:
            id: scr_mngr
            Screen:
                name: 'menu'
                ScrollView:
                    do_scroll_x: False
                    MDList:
                        ThreeLineAvatarListItem:
                            type: "three-line"
                            text: "Banners"
                            secondary_text: "Rectangular image or text ads that occupy a spot within an app's layout."
                            on_press: app.root.switch_to_screen("banner", "Banners")
                            AvatarIconWidget:
                                source: './assets/banner.png'
                        ThreeLineAvatarListItem:
                            type: "three-line"
                            text: "Interstitial"
                            secondary_text: "Full-screen ads that cover the interface of an app until closed by the user."
                            on_press: app.root.switch_to_screen("interstitial", "Interstitial")
                            AvatarIconWidget:
                                source: './assets/interstitial.png'
                        ThreeLineAvatarListItem:
                            type: "three-line"
                            text: "Rewarded Video"
                            secondary_text: "Video ads that users may watch in exchange for in-app rewards."
                            on_press: app.root.switch_to_screen("rewarded", "Rewarded Video Ad")
                            AvatarIconWidget:
                                source: './assets/rewarded.png'
                        ThreeLineAvatarListItem:
                            type: "three-line"
                            text: "Documentation"
                            secondary_text: "Learn how to utilize KivMob within a mobile Kivy application."
                            on_press: webbrowser.open("https://kivmob.com")
                            AvatarIconWidget:
                                source: './assets/documentation.png'
                        ThreeLineAvatarListItem:
                            type: "three-line"
                            text: "Source Code"
                            secondary_text: "Checkout, fork, and follow the KivMob project on GitHub."
                            on_press: webbrowser.open("https://github.com/MichaelStott/KivMob")
                            AvatarIconWidget:
                                source: './assets/github.png'
                        ThreeLineAvatarListItem:
                            type: "three-line"
                            text: "About"
                            secondary_text: "Software licensing, credits, and other KivMob information."
                            on_press: webbrowser.open("https://github.com/MichaelStott/KivMob")
                            AvatarIconWidget:
                                source: './assets/about.png'
            Screen:
                name: "banner"
                on_pre_leave:
                    app.ads.hide_banner()
                    app.show_banner = False
                MDRaisedButton:
                    text: "Toggle Banner Ad"
                    elevation_normal: 2
                    opposite_colors: True
                    pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                    on_press: app.toggle_banner()
            Screen:
                name: "interstitial"
                MDRaisedButton:
                    text: "Show Interstitial"
                    elevation_normal: 2
                    opposite_colors: True
                    pos_hint: {'center_x': 0.5, 'center_y': 0.5}
                    on_press: app.ads.show_interstitial() if app.ads.is_interstitial_loaded() else app.root.show_interstitial_msg()
            Screen:
                name: 'rewarded'
                BoxLayout:
                    MDLabel:
                        font_style: 'H1'
                        theme_text_color: 'Primary'
                        text: "Points: "+str(app.Points)
                        halign: 'center'
                        pos_hint: {'center_x': 0.5, 'center_y': 0.75}
                MDFloatingActionButton:
                    icon: 'plus'
                    elevation_normal: 2
                    pos_hint: {'center_x': 0.5, 'center_y': 0.25}
                    on_press: app.ads.show_rewarded_ad()
"""
)

class AvatarIconWidget(ILeftBody, Image):
    pass

class KivMobDemoUI(FloatLayout):
    def switch_to_screen(self, name, title):
        self.ids.title_lbl.text = title
        self.ids.back_btn.opacity = 1
        self.ids.back_btn.disabled = False
        self.ids.scr_mngr.transition.direction = "left"
        self.ids.scr_mngr.current = name

    def back_to_menu(self):
        self.ids.scr_mngr.transition.direction = "right"
        self.ids.scr_mngr.current = "menu"
        self.ids.title_lbl.text = "KivMob 2.0"
        self.ids.back_btn.opacity = 0
        self.ids.back_btn.disabled = True

    def show_interstitial_msg(self):
        Logger.info("KivMobDemo: Interstitial has not yet loaded.")

    def hide_interstitial_msg(self):
        pass

    def open_dialog(self):
        pass

class KivMobDemo(MDApp):

    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.theme_cls.theme_style = "Dark"
        self.rewards = Rewards_Handler(self)

    Points = NumericProperty(0)
    show_banner = False

    def build(self):
        self.ads = KivMob(TestIds.APP)
        self.ads.new_banner(TestIds.BANNER, False)
        self.ads.new_interstitial(TestIds.INTERSTITIAL)
        self.ads.request_banner()
        self.ads.request_interstitial()
        self.ads.set_rewarded_ad_listener(self.rewards)
        self.ads.load_rewarded_ad(TestIds.REWARDED_VIDEO)
        self.toggled = False
        return KivMobDemoUI()

    def toggle_banner(self):
        self.show_banner = not self.show_banner
        if self.show_banner:
            self.ads.show_banner()
        else:
            self.ads.hide_banner()

    def load_video(self):
        self.ads.load_rewarded_ad(TestIds.REWARDED_VIDEO)

class Rewards_Handler(RewardedListenerInterface):

    def __init__(self,other):
        self.AppObj = other

    Reward = "None"
    Reward_Amount = "None"

    def on_rewarded(self, reward_name, reward_amount):
        self.Reward = reward_name
        self.Reward_Amount = reward_amount
        self.AppObj.Points += int(reward_amount)

    def on_rewarded_video_ad_completed(self):
        self.on_rewarded(self.Reward,self.Reward_Amount)

    def on_rewarded_video_ad_started(self):
        self.AppObj.load_video()

    def on_rewarded_video_ad_left_application(self):
        self.AppObj.Points += 0

if __name__ == "__main__":  # pragma: no cover
    KivMobDemo().run()
