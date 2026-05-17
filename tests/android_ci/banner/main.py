"""Minimal banner-ad app for Android CI (Google test units)."""

import os

os.environ.setdefault("KIVY_NO_ARGS", "1")

from kivy.app import App
from kivy.logger import Logger
from kivy.uix.label import Label

from kivmob import KivMob, TestIds


class BannerAdCiApp(App):
    def build(self):
        Logger.info("CI_TEST:banner_init")
        self.ads = KivMob(TestIds.APP)
        self.ads.new_banner(TestIds.BANNER, top_pos=True)
        self.ads.request_banner()
        self.ads.show_banner()
        Logger.info("CI_TEST:banner_shown")
        return Label(text="KivMob CI — banner")


if __name__ == "__main__":
    BannerAdCiApp().run()
