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

if platform not in ("android", "ios"):
    # Approximate dimensions of mobile phone.
    Config.set("graphics", "resizable", "0")
    Window.size = (400, 600)

__version__ = "1.0"

from kivymd.theming import ThemeManager
from kivymd.uix.list import ILeftBody
from kivymd.uix.list import OneLineListItem
from kivymd.uix.list import TwoLineListItem
from kivymd.uix.list import ThreeLineListItem
from kivymd.uix.snackbar import Snackbar

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
        MDToolbar:
            id: toolbar
            title: 'KivMob 2.0'
            md_bg_color: app.theme_cls.primary_color
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
                            on_press: webbrowser.open("https://github.com/MichaelStott/KivMob")
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
                        text: "Counter: 0"
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
        self.ids.toolbar.title = title
        self.ids.toolbar.left_action_items = [
            ["chevron-left", lambda x: self.back_to_menu()]
        ]
        self.ids.scr_mngr.transition.direction = "left"
        self.ids.scr_mngr.current = name
        self.interstitial_snack = Snackbar(
            text="Interstitial has not yet loaded."
        )

    def back_to_menu(self):
        self.ids.scr_mngr.transition.direction = "right"
        self.ids.scr_mngr.current = "menu"
        self.ids.toolbar.title = "KivMob 2.0"
        self.ids.toolbar.left_action_items = []

    def show_interstitial_msg(self):
        self.interstitial_snack.show()

    def hide_interstitial_msg(self):
        self.interstitial_snack.hide()

    def open_dialog(self):
        pass


class KivMobDemo(MDApp):
    def __init__(self, **kwargs):
        self.theme_cls.theme_style = "Dark"
        super().__init__(**kwargs)

    show_banner = False

    def build(self):
        self.ads = KivMob(TestIds.APP)
        self.ads.new_banner(TestIds.BANNER, False)
        self.ads.new_interstitial(TestIds.INTERSTITIAL)
        self.ads.request_banner()
        self.ads.request_interstitial()
        self.ads.set_rewarded_ad_listener(RewardedListenerInterface())
        self.ads.load_rewarded_ad(TestIds.REWARDED_VIDEO)
        self.toggled = False
        return KivMobDemoUI()

    def toggle_banner(self):
        self.show_banner = not self.show_banner
        if self.show_banner:
            self.ads.show_banner()
        else:
            self.ads.hide_banner()


if __name__ == "__main__":
    KivMobDemo().run()
