"""Minimal interstitial-ad app for Android CI (Google test units)."""

import os

os.environ.setdefault("KIVY_NO_ARGS", "1")

from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger
from kivy.uix.label import Label

from kivmob import KivMob, TestIds


class InterstitialAdCiApp(App):
    def build(self):
        Logger.info("CI_TEST:interstitial_init")
        self.ads = KivMob(TestIds.APP)
        self.ads.new_interstitial(TestIds.INTERSTITIAL)
        self.ads.request_interstitial()
        Clock.schedule_interval(self._poll_loaded, 1.0)
        return Label(text="KivMob CI — interstitial")

    def _poll_loaded(self, _dt):
        if self.ads.is_interstitial_loaded():
            Logger.info("CI_TEST:interstitial_show")
            self.ads.show_interstitial()
            return False
        return True


if __name__ == "__main__":
    InterstitialAdCiApp().run()
