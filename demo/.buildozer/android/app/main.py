from kivmob import KivMob, TestIds

import kivy.utils
from kivy.app import App
from kivy.lang import Builder
from kivy.config import Config
from kivy.utils import platform
from kivy.core.window import Window
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image

if platform not in ('android', 'ios'):
    # Approximate dimensions of mobile phone.
    Config.set('graphics', 'resizable', '0')
    Window.size = (400, 600)
import webbrowser

__version__ = "1.0"

from kivymd.label import MDLabel
from kivymd.theming import ThemeManager
from kivymd.list import ILeftBody

Builder.load_string("""
#:import kivy kivy

#:import Toolbar kivymd.toolbar.Toolbar
#:import MDCard kivymd.card.MDCard
#:import MDSeparator kivymd.card.MDSeparator
#:import MDList kivymd.list.MDList
#:import OneLineListItem kivymd.list.OneLineListItem
#:import TwoLineListItem kivymd.list.TwoLineListItem
#:import ThreeLineListItem kivymd.list.ThreeLineListItem

<KivMobDemoUI>:

    BoxLayout:
        orientation: 'vertical'
        Toolbar:
            id: toolbar
            title: 'KivMob'
            md_bg_color: app.theme_cls.primary_color
            #left_action_items: None # [['menu', lambda x: app.root.toggle_nav_drawer()]]
        ScreenManager:
            Screen:
                name: 'list'
                ScrollView:
                    do_scroll_x: False
                    MDList:
                        ThreeLineAvatarListItem:
                            type: "three-line"
                            text: "Banners"
                            secondary_text: "Rectangular image or text ads that occupy a spot within an app's layout."
                            AvatarSampleWidget:
                                source: './assets/banner.png'
                        ThreeLineAvatarListItem:
                            type: "three-line"
                            text: "Interstitial"
                            secondary_text: "Full-screen ads that cover the interface of an app until closed by the user."
                            AvatarSampleWidget:
                                source: './assets/interstitial.png'
                        ThreeLineAvatarListItem:
                            type: "four-line"
                            text: "Rewarded Video"
                            secondary_text: "Video ads that users may watch in exchange for in-app rewards."
                            AvatarSampleWidget:
                                source: './assets/rewarded.png'
                        ThreeLineAvatarListItem:
                            type: "three-line"
                            text: "Native"
                            secondary_text: "Customize the way assets and calls to action are presented in your apps."
                            AvatarSampleWidget:
                                source: './assets/native.png'
                        ThreeLineAvatarListItem:
                            type: "three-line"
                            text: "Documentation"
                            secondary_text: "Learn how to utilize KivMob within a mobile Kivy application."
                            AvatarSampleWidget:
                                source: './assets/documentation.png'
                        ThreeLineAvatarListItem:
                            type: "three-line"
                            text: "Source Code"
                            secondary_text: "Checkout, fork, and follow the KivMob project on GitHub."
                            AvatarSampleWidget:
                                source: './assets/github.png'
                        ThreeLineAvatarListItem:
                            type: "three-line"
                            text: "About"
                            secondary_text: "Credits, software licensing information, and other information."
                            AvatarSampleWidget:
                                source: './assets/about.png'
""")


class AvatarSampleWidget(ILeftBody, Image):
    pass


class KivMobDemoUI(FloatLayout):
    pass

        
class KivMobDemo(App):
    
    theme_cls = ThemeManager()

    def build(self):
        #self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = 'Indigo'
        self.ads = KivMob(TestIds.APP)
        self.ads.new_banner(TestIds.BANNER)
        self.ads.new_interstitial(TestIds.INTERSTITIAL_VIDEO)
        self.ads.request_banner()
        self.ads.request_interstitial()
        self.toggled = False
        return KivMobDemoUI()

if __name__ == "__main__":
    KivMobDemo().run()
