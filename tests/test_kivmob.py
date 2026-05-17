"""Unit tests for the ``kivmob`` library (desktop / no-op Android path)."""

from unittest.mock import MagicMock, patch

import pytest
from kivy.metrics import dp

import kivmob
from kivmob import (
    AdMobBridge,
    KivMob,
    RewardedListenerInterface,
    TestIds,
)


def test_test_ids_are_google_sample_ad_units():
    assert TestIds.APP.endswith("3347511713")
    assert "/6300978111" in TestIds.BANNER
    assert "/1033173712" in TestIds.INTERSTITIAL
    assert "/8691691433" in TestIds.INTERSTITIAL_VIDEO
    assert "/5224354917" in TestIds.REWARDED_VIDEO


def test_admob_bridge_noop_defaults():
    bridge = AdMobBridge("dummy-app-id")
    assert bridge.is_interstitial_loaded() is False
    assert bridge.is_rewarded_loaded() is False
    # Smoke: methods exist and do not raise.
    bridge.add_test_device("DEVICE_HASH")
    bridge.new_banner(TestIds.BANNER)
    bridge.request_banner({})
    bridge.show_banner()
    bridge.hide_banner()
    bridge.destroy_banner()
    bridge.new_interstitial(TestIds.INTERSTITIAL)
    bridge.request_interstitial({})
    bridge.show_interstitial()
    bridge.destroy_interstitial()
    bridge.set_rewarded_ad_listener(None)
    bridge.load_rewarded_ad(TestIds.REWARDED_VIDEO)
    bridge.show_rewarded_ad()
    bridge.destroy_rewarded_video_ad()


@pytest.mark.parametrize(
    ("window_height", "expected_dp"),
    [
        (dp(300), 32),
        (dp(500), 50),
        (dp(800), 90),
    ],
)
def test_determine_banner_height(window_height, expected_dp):
    with patch.object(kivmob, "Window") as mock_window:
        mock_window.height = window_height
        km = KivMob("")
        assert km.determine_banner_height() == dp(expected_dp)


def test_kivmob_uses_admob_bridge_on_non_mobile():
    km = KivMob(TestIds.APP)
    assert isinstance(km.bridge, AdMobBridge)


def test_kivmob_forwards_calls_to_bridge():
    km = KivMob("")
    km.bridge = MagicMock()
    km.add_test_device("abc")
    km.new_banner("unit", top_pos=False)
    km.request_banner({"children": True})
    km.show_banner()
    km.hide_banner()
    km.destroy_banner()
    km.new_interstitial("int-unit")
    km.request_interstitial({})
    km.show_interstitial()
    km.destroy_interstitial()
    km.set_rewarded_ad_listener(None)
    km.load_rewarded_ad("rw-unit")
    km.show_rewarded_ad()
    km.bridge.add_test_device.assert_called_once_with("abc")
    km.bridge.new_banner.assert_called_once_with("unit", False)
    km.bridge.request_banner.assert_called_once_with({"children": True})
    km.bridge.show_banner.assert_called_once()
    km.bridge.hide_banner.assert_called_once()
    km.bridge.destroy_banner.assert_called_once()
    km.bridge.new_interstitial.assert_called_once_with("int-unit")
    km.bridge.request_interstitial.assert_called_once_with({})
    km.bridge.show_interstitial.assert_called_once()
    km.bridge.destroy_interstitial.assert_called_once()
    km.bridge.set_rewarded_ad_listener.assert_called_once_with(None)
    km.bridge.load_rewarded_ad.assert_called_once_with("rw-unit")
    km.bridge.show_rewarded_ad.assert_called_once()


def test_rewarded_listener_interface_defaults_are_callable():
    listener = RewardedListenerInterface()
    listener.on_rewarded("coins", "10")
    listener.on_rewarded_video_ad_left_application()
    listener.on_rewarded_video_ad_closed()
    listener.on_rewarded_video_ad_failed_to_load(2)
    listener.on_rewarded_video_ad_loaded()
    listener.on_rewarded_video_ad_opened()
    listener.on_rewarded_video_ad_started()
    listener.on_rewarded_video_ad_completed()
