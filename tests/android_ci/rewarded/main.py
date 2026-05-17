"""Minimal rewarded-video app for Android CI (Google test units)."""

import os

os.environ.setdefault("KIVY_NO_ARGS", "1")

from kivy.app import App
from kivy.logger import Logger
from kivy.uix.label import Label

from kivmob import KivMob, RewardedListenerInterface, TestIds


class _CiRewardedListener(RewardedListenerInterface):
    def __init__(self, ads):
        self._ads = ads

    def on_rewarded_video_ad_loaded(self):
        Logger.info("CI_TEST:rewarded_show")
        self._ads.show_rewarded_ad()

    def on_rewarded(self, reward_name, reward_amount):
        Logger.info(
            "CI_TEST:rewarded_earned %s %s" % (reward_name, reward_amount)
        )


class RewardedAdCiApp(App):
    def build(self):
        Logger.info("CI_TEST:rewarded_init")
        self.ads = KivMob(TestIds.APP)
        self.ads.set_rewarded_ad_listener(_CiRewardedListener(self.ads))
        self.ads.load_rewarded_ad(TestIds.REWARDED_VIDEO)
        return Label(text="KivMob CI — rewarded")


if __name__ == "__main__":
    RewardedAdCiApp().run()
