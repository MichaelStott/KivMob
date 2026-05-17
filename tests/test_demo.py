"""Unit tests for demo application helpers (no full App/window lifecycle)."""

from unittest.mock import MagicMock, patch

import pytest

pytest.importorskip("kivymd")

import demo.main as demo_main


def test_configure_window_for_desktop_preview_sets_size_on_linux():
    with patch.object(demo_main, "Config") as mock_cfg, patch.object(demo_main, "Window") as mock_win:
        demo_main._configure_window_for_desktop_preview("linux")
        mock_cfg.set.assert_called_once_with("graphics", "resizable", "0")
        assert mock_win.size == (400, 600)


def test_configure_window_for_desktop_preview_skips_mobile():
    with patch.object(demo_main, "Config") as mock_cfg, patch.object(demo_main, "Window") as mock_win:
        demo_main._configure_window_for_desktop_preview("android")
        mock_cfg.set.assert_not_called()
        assert not mock_win.mock_calls


def test_configure_window_for_desktop_preview_skips_ios():
    with patch.object(demo_main, "Config") as mock_cfg:
        demo_main._configure_window_for_desktop_preview("ios")
        mock_cfg.set.assert_not_called()


def test_rewards_handler_on_rewarded_updates_points():
    app = MagicMock()
    app.Points = 0
    handler = demo_main.Rewards_Handler(app)
    handler.on_rewarded("gems", "5")
    assert handler.Reward == "gems"
    assert handler.Reward_Amount == "5"
    assert app.Points == 5


def test_rewards_handler_on_rewarded_video_ad_completed_replays_last_reward():
    app = MagicMock()
    app.Points = 1
    handler = demo_main.Rewards_Handler(app)
    handler.Reward = "x"
    handler.Reward_Amount = "3"
    handler.on_rewarded_video_ad_completed()
    assert app.Points == 4


def test_rewards_handler_on_rewarded_video_ad_started_loads_video():
    app = MagicMock()
    handler = demo_main.Rewards_Handler(app)
    handler.on_rewarded_video_ad_started()
    app.load_video.assert_called_once()


def test_rewards_handler_left_application_no_crash():
    app = MagicMock()
    handler = demo_main.Rewards_Handler(app)
    handler.on_rewarded_video_ad_left_application()


def test_kivmob_demo_ui_switch_to_screen_and_back():
    ui = demo_main.KivMobDemoUI.__new__(demo_main.KivMobDemoUI)
    ui.ids = MagicMock()
    ui.ids.title_lbl = MagicMock()
    ui.ids.back_btn = MagicMock()
    ui.ids.scr_mngr = MagicMock()

    demo_main.KivMobDemoUI.switch_to_screen(ui, "banner", "Banners")
    assert ui.ids.title_lbl.text == "Banners"
    assert ui.ids.back_btn.opacity == 1
    assert ui.ids.back_btn.disabled is False
    assert ui.ids.scr_mngr.transition.direction == "left"
    assert ui.ids.scr_mngr.current == "banner"

    demo_main.KivMobDemoUI.back_to_menu(ui)
    assert ui.ids.scr_mngr.transition.direction == "right"
    assert ui.ids.scr_mngr.current == "menu"
    assert ui.ids.title_lbl.text == "KivMob 2.0"
    assert ui.ids.back_btn.opacity == 0
    assert ui.ids.back_btn.disabled is True


def test_kivmob_demo_toggle_banner_toggles_ads_and_flag():
    demo = demo_main.KivMobDemo.__new__(demo_main.KivMobDemo)
    demo.ads = MagicMock()
    demo.show_banner = False

    demo_main.KivMobDemo.toggle_banner(demo)
    assert demo.show_banner is True
    demo.ads.show_banner.assert_called_once()

    demo_main.KivMobDemo.toggle_banner(demo)
    assert demo.show_banner is False
    demo.ads.hide_banner.assert_called_once()


def test_kivmob_demo_ui_show_and_hide_interstitial_msg_and_open_dialog():
    ui = demo_main.KivMobDemoUI.__new__(demo_main.KivMobDemoUI)
    demo_main.KivMobDemoUI.show_interstitial_msg(ui)
    demo_main.KivMobDemoUI.hide_interstitial_msg(ui)
    demo_main.KivMobDemoUI.open_dialog(ui)


def test_kivmob_demo_build_and_load_video():
    with patch.object(demo_main, "KivMob") as mock_kivmob_cls:
        ads = MagicMock()
        mock_kivmob_cls.return_value = ads
        app = demo_main.KivMobDemo()
        root = app.build()

        assert isinstance(root, demo_main.KivMobDemoUI)
        mock_kivmob_cls.assert_called_once_with(demo_main.TestIds.APP)
        ads.new_banner.assert_called_once_with(demo_main.TestIds.BANNER, False)
        ads.new_interstitial.assert_called_once_with(demo_main.TestIds.INTERSTITIAL)
        ads.request_banner.assert_called_once()
        ads.request_interstitial.assert_called_once()
        ads.set_rewarded_ad_listener.assert_called_once_with(app.rewards)
        ads.load_rewarded_ad.assert_called_once_with(demo_main.TestIds.REWARDED_VIDEO)

        demo_main.KivMobDemo.load_video(app)
        assert ads.load_rewarded_ad.call_count == 2
        ads.load_rewarded_ad.assert_called_with(demo_main.TestIds.REWARDED_VIDEO)


def test_avatar_icon_widget_can_be_constructed():
    w = demo_main.AvatarIconWidget()
    assert w is not None
