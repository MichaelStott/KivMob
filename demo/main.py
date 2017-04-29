from kivmob import KivMob

import kivy.utils
from kivy.app import App
from kivy.lang import Builder
from kivy.config import Config
from kivy.properties import ListProperty
from kivy.utils import platform
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.core.window import Window
if platform not in ('android', 'ios'):
    # Approximate dimensions of mobile phone.
    Config.set('graphics', 'resizable', '0')
    Window.size = (320, 420)
import webbrowser

__version__ = "1.0"

Builder.load_string("""
#:import kivy kivy

<KivMobDemoUI>:
    canvas.before:
        Color:
            rgba: kivy.utils.get_color_from_hex("f5f5f5")
        Rectangle:
            pos: self.pos
            size: self.size
    FloatLayout:
        Image:
            source: "assets/kivmob-title.png"
    BoxLayout:
        orientation: "vertical"
        AnchorLayout:
            CustomButton:
                text: "Toggle Banner"
                size_hint: 0.8, 0.2
                on_release: app.toggle_banner()
        AnchorLayout:
            CustomButton:
                text: "Show Interstitial"
                size_hint: 0.8, 0.2
                on_release: app.show_interstitial()

<CustomButton>:
    canvas.before:
        Color:
            rgba: self.box_color
        RoundedRectangle:
            pos: self.pos
            size: self.size
    color: (1, 1, 1, 1)
    bold: True
    text_size: self.width, None
    height: self.texture_size[1]+size_hint_y: None
    text_size: self.width, None
    height: self.texture_size[1] + sp(20)
    halign: 'center'
    valign: 'middle'
""")

class KivMobDemoUI(FloatLayout):
    pass

class CustomButton(ButtonBehavior, Label):
    """Custom button used by applicatiod rather than default kivy
    button.
    
    Attributes:
        box_color -- Button color.
        prv_color -- Stores original box color.
    """
    
    box_color = ListProperty(kivy.utils.get_color_from_hex("56b669"))
    prv_color = ListProperty(kivy.utils.get_color_from_hex("56b669"))
    
    def __init__(self, **kwargs):
        super(CustomButton, self).__init__(**kwargs)
        self.always_release = True
        
    def on_press(self):
        self.prv_color = self.box_color
        self.box_color = (self.box_color[0] * 0.5,\
                          self.box_color[1] * 0.5,\
                          self.box_color[2] * 0.5,\
                          self.box_color[3])

    def on_release(self):
        self.box_color = self.prv_color
        
class KivMobDemo(App):

    APP_ID = "ca-app-pub-COPY APP ID HERE"
    BANNER_ID = "ca-app-pub-COPY BANNER ID HERE"
    INTERSTITIAL_ID = "ca-app-pub-COPY INTERSTITIAL ID HERE"
    TEST_DEVICE_ID = "COPY DEVICE ID HERE"
    
    def build(self):
        self.ads = KivMob(APP_ID)
        self.ads.add_test_device(TEST_DEVICE_ID)
        self.ads.new_banner({"unitID":BANNER_ID})
        self.ads.new_interstitial(INTERSTITIAL_ID)
        self.ads.request_banner()
        self.ads.request_interstitial()
        self.toggled = False
        return KivMobDemoUI()

    def on_start(self):
        """Called on application start.
        """
        if platform not in ("android", "ios"):
            self.desktop_warning()
            
    def desktop_warning(self):
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text='KivMob will not display ads on ' +\
                          'nonmobile platforms. You must build an ' +\
                          'Android project to demo ads. (iOS not yet ' +\
                          'supported)',
                          size_hint_y=1,
                          text_size=(250,  None),
                          halign='left',
                          valign='middle'))
        button_layout = BoxLayout()
        button1=Button(text="Open Build Steps", size_hint=(0.8, 0.2))
        button1.bind(on_release = lambda x :
                     webbrowser.open("https://www.google.com"))
        button_layout.add_widget(button1)
        button2=Button(text="Close", size_hint=(0.8, 0.2))
        button2.bind(on_release = lambda x : popup.dismiss())
        button_layout.add_widget(button2)
        layout.add_widget(button_layout)
        popup = Popup(title='KivMob Demo Alert',
                      content=layout,
                      size_hint=(0.9, 0.9))
        popup.open()

    def interstitial_warning(self):
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(Label(text="Ad has not loaded. " +\
                                    "Wait a few seconds and then " +\
                                    "try again.",
                                    size_hint_y=1,
                                    text_size=(250,  None),
                                    halign='left',
                                    valign='middle'))
        button_layout = BoxLayout()
        close=Button(text="Close", size_hint=(0.8, 0.2))
        close.bind(on_release = lambda x : popup.dismiss())
        button_layout.add_widget(close)
        layout.add_widget(button_layout)
        popup = Popup(title='KivMob Demo Alert',
                      content=layout,
                      size_hint=(0.9, 0.9))
        popup.open()

    def on_pause(self):
        """Android specific method. Save important app data on pause.
        """
        return True

    def on_resume(self):
        """Android specific method. Resume paused app.
        """
        self.ads.request_interstitial()
    
    def toggle_banner(self):
        if not self.toggled:
            self.ads.show_banner()
        else:
            self.ads.hide_banner()
        self.toggled = not self.toggled

    def show_interstitial(self):
        if self.ads.is_interstitial_loaded():
            self.ads.show_interstitial()
        else:
            self.interstitial_warning()
            

if __name__ == "__main__":
    KivMobDemo().run()
