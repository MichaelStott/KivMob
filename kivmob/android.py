"""Android AdMob bridge (JNI listeners + Mobile Ads SDK)."""

from kivy.logger import Logger
from kivy.utils import platform

from .bridge import (
    AdMobBridge,
    _ad_load_callback_current,
    _normalize_options,
)

ANDROID_ADS_OK = False


class _AdLoadState:
    """Tracks load generations so stale JNI callbacks are ignored."""

    __slots__ = ("load_gen", "active_gen", "loaded")

    def __init__(self):
        self.load_gen = 0
        self.active_gen = 0
        self.loaded = False

    def begin(self):
        self.load_gen += 1
        self.active_gen = self.load_gen

    def invalidate(self):
        self.load_gen += 1
        self.loaded = False

    def is_current(self):
        return _ad_load_callback_current(self.active_gen, self.load_gen)


if platform == "android":
    try:
        from jnius import autoclass, java_method, PythonJavaClass
        from android.runnable import run_on_ui_thread

        activity = autoclass("org.kivy.android.PythonActivity")
        AdRequest = autoclass("com.google.android.gms.ads.AdRequest")
        AdRequestBuilder = autoclass("com.google.android.gms.ads.AdRequest$Builder")
        AdSize = autoclass("com.google.android.gms.ads.AdSize")
        AdView = autoclass("com.google.android.gms.ads.AdView")
        Bundle = autoclass("android.os.Bundle")
        Gravity = autoclass("android.view.Gravity")
        KivMobAdsBridge = autoclass("org.kivmob.kivmob.KivMobAdsBridge")
        LayoutParams = autoclass("android.view.ViewGroup$LayoutParams")
        LinearLayout = autoclass("android.widget.LinearLayout")
        MobileAds = autoclass("com.google.android.gms.ads.MobileAds")
        RequestConfigurationBuilder = autoclass(
            "com.google.android.gms.ads.RequestConfiguration$Builder"
        )
        View = autoclass("android.view.View")
        AdMobAdapter = autoclass("com.google.ads.mediation.admob.AdMobAdapter")
        ArrayList = autoclass("java.util.ArrayList")

    except Exception as exc:
        Logger.error(
            "KivMob: Cannot load AdMob classes. Check buildozer.spec. %s" % exc
        )
        activity = None
    else:
        ANDROID_ADS_OK = True

        # --- JNI callbacks: Mobile Ads SDK bridge callbacks ---

        class KivOnInitCompleteListener(PythonJavaClass):
            __javainterfaces__ = [
                "com/google/android/gms/ads/initialization/OnInitializationCompleteListener"
            ]
            __javacontext__ = "app"

            def __init__(self, bridge):
                super().__init__()
                self._bridge = bridge

            @java_method(
                "(Lcom/google/android/gms/ads/initialization/InitializationStatus;)V"
            )
            def onInitializationComplete(self, _status):
                self._bridge._on_ads_initialized()

        class KivInterstitialBridgeListener(PythonJavaClass):
            __javainterfaces__ = ["org/kivmob/kivmob/KivMobInterstitialListener"]
            __javacontext__ = "app"

            def __init__(self, bridge):
                super().__init__()
                self._bridge = bridge

            def _is_current(self):
                return self._bridge._interstitial.is_current()

            @java_method("()V")
            def onInterstitialDismissed(self):
                if not self._is_current():
                    return
                Logger.info("KivMob: interstitial dismissed")
                self._bridge._interstitial.loaded = False

            @java_method("(Ljava/lang/String;I)V")
            def onInterstitialFailed(self, message, _code):
                if not self._is_current():
                    return
                Logger.warning("KivMob: interstitial failed: %s" % message)
                self._bridge._interstitial.loaded = False

            @java_method("()V")
            def onInterstitialLoaded(self):
                if not self._is_current():
                    return
                Logger.info("KivMob: interstitial loaded.")
                self._bridge._interstitial.loaded = True

            @java_method("()V")
            def onInterstitialShown(self):
                if not self._is_current():
                    return
                Logger.info("KivMob: interstitial shown")

        class KivRewardedBridgeListener(PythonJavaClass):
            __javainterfaces__ = ["org/kivmob/kivmob/KivMobRewardedListener"]
            __javacontext__ = "app"

            def __init__(self, bridge, user_listener):
                super().__init__()
                self._bridge = bridge
                self._user = user_listener
                self._reward_earned = False

            def _is_current(self):
                return self._bridge._rewarded.is_current()

            @java_method("()V")
            def onRewardedDismissed(self):
                if not self._is_current():
                    return
                Logger.info("KivMob: rewarded ad dismissed")
                if self._user is not None:
                    if self._reward_earned:
                        self._user.on_rewarded_video_ad_completed()
                    self._user.on_rewarded_video_ad_closed()
                self._reward_earned = False
                self._bridge._rewarded.loaded = False

            @java_method("(Ljava/lang/String;I)V")
            def onRewardedFailed(self, message, code):
                if not self._is_current():
                    return
                Logger.info("KivMob: rewarded ad failed: %s" % message)
                if self._user is not None:
                    self._user.on_rewarded_video_ad_failed_to_load(code)
                self._reward_earned = False
                self._bridge._rewarded.loaded = False

            @java_method("()V")
            def onRewardedShown(self):
                if not self._is_current():
                    return
                Logger.info("KivMob: rewarded ad shown")
                if self._user is not None:
                    self._user.on_rewarded_video_ad_opened()
                    self._user.on_rewarded_video_ad_started()

            @java_method("()V")
            def onRewardedLoaded(self):
                if not self._is_current():
                    return
                Logger.info("KivMob: rewarded ad loaded.")
                self._reward_earned = False
                self._bridge._rewarded.loaded = True
                if self._user is not None:
                    self._user.on_rewarded_video_ad_loaded()

            @java_method("(Ljava/lang/String;I)V")
            def onUserEarnedReward(self, reward_type, reward_amount):
                if not self._is_current():
                    return
                self._reward_earned = True
                if self._user is not None:
                    self._user.on_rewarded(str(reward_type), str(reward_amount))

        class AndroidBridge(AdMobBridge):
            @run_on_ui_thread
            def __init__(self, appID):
                self._app_id = appID
                self._adview = None
                self._banner_layout = None
                self._interstitial_unit = None
                self._interstitial = _AdLoadState()
                self._rewarded_unit = None
                self._rewarded = _AdLoadState()
                self._reward_listener = None
                self._interstitial_bridge_listener = KivInterstitialBridgeListener(self)
                self._rewarded_bridge_listener = KivRewardedBridgeListener(
                    self, self._reward_listener
                )
                self._test_devices = []
                self._ads_initialized = False
                self._pending_after_init = {}
                m_activity = activity.mActivity
                try:
                    MobileAds.initialize(m_activity, KivOnInitCompleteListener(self))
                except Exception as e:
                    Logger.error("KivMob: MobileAds.initialize failed: %s" % e)
                if appID and str(appID).strip():
                    Logger.info(
                        "KivMob: App ID (also set com.google.android.gms.ads.APPLICATION_ID in buildozer): %s"
                        % (appID,)
                    )

            def _run_or_defer(self, key, action):
                """Run ``action`` now, or queue it until Mobile Ads init completes."""
                if not self._ads_initialized:
                    self._pending_after_init[key] = action
                    return
                action()

            @run_on_ui_thread
            def _on_ads_initialized(self):
                Logger.info("KivMob: Mobile Ads initialized.")
                self._ads_initialized = True
                pending = self._pending_after_init
                self._pending_after_init = {}
                for action in pending.values():
                    action()

            @run_on_ui_thread
            def add_test_device(self, testID):
                self._test_devices.append(testID)
                self._apply_test_device_config()

            def _apply_test_device_config(self):
                if not self._test_devices:
                    return
                ids = ArrayList()
                for device_id in self._test_devices:
                    ids.add(device_id)
                config = RequestConfigurationBuilder().setTestDeviceIds(ids).build()
                MobileAds.setRequestConfiguration(config)

            def _banner_ad_size(self):
                dm = activity.mActivity.getResources().getDisplayMetrics()
                w_dp = int(dm.widthPixels / float(dm.density))
                try:
                    return AdSize.getCurrentOrientationAnchoredAdaptiveBannerAdSize(
                        activity.mActivity, w_dp
                    )
                except Exception:
                    return AdSize.BANNER

            def _clear_banner(self):
                if self._adview is not None:
                    self._adview.destroy()
                    self._adview = None
                self._banner_layout = None

            @run_on_ui_thread
            def new_banner(self, unitID, top_pos=True):
                self._clear_banner()
                self._adview = AdView(activity.mActivity)
                self._adview.setAdUnitId(unitID)
                self._adview.setAdSize(self._banner_ad_size())
                self._adview.setVisibility(View.GONE)
                ad_layout = LayoutParams(
                    LayoutParams.MATCH_PARENT, LayoutParams.WRAP_CONTENT
                )
                self._adview.setLayoutParams(ad_layout)
                layout = LinearLayout(activity.mActivity)
                if not top_pos:
                    layout.setGravity(Gravity.BOTTOM)
                layout.addView(self._adview)
                outer = LayoutParams(
                    LayoutParams.MATCH_PARENT, LayoutParams.MATCH_PARENT
                )
                layout.setLayoutParams(outer)
                self._banner_layout = layout
                activity.mActivity.addContentView(layout, outer)

            def _load_banner(self, options):
                if self._adview is not None:
                    self._adview.loadAd(self._get_builder(options).build())

            @run_on_ui_thread
            def request_banner(self, options=None):
                options = _normalize_options(options)
                self._run_or_defer("banner", lambda: self._load_banner(options))

            @run_on_ui_thread
            def show_banner(self):
                if self._adview is not None:
                    self._adview.setVisibility(View.VISIBLE)
                    if self._banner_layout is not None:
                        self._banner_layout.bringToFront()

            @run_on_ui_thread
            def hide_banner(self):
                if self._adview is not None:
                    self._adview.setVisibility(View.GONE)

            @run_on_ui_thread
            def new_interstitial(self, unitID):
                self._interstitial.invalidate()
                self._interstitial_unit = unitID

            def _load_interstitial(self, options):
                if not self._interstitial_unit:
                    Logger.error("KivMob: call new_interstitial(unit_id) first.")
                    return
                self._interstitial.begin()
                try:
                    KivMobAdsBridge.loadInterstitial(
                        activity.mActivity,
                        self._interstitial_unit,
                        self._get_builder(options).build(),
                        self._interstitial_bridge_listener,
                    )
                except Exception as exc:
                    Logger.warning("KivMob: interstitial load disabled: %s" % exc)
                    self._interstitial.invalidate()

            @run_on_ui_thread
            def request_interstitial(self, options=None):
                options = _normalize_options(options)
                self._run_or_defer(
                    "interstitial", lambda: self._load_interstitial(options)
                )

            def is_interstitial_loaded(self):
                try:
                    loaded = bool(KivMobAdsBridge.isInterstitialLoaded())
                except Exception:
                    loaded = False
                return self._interstitial.loaded and loaded

            @run_on_ui_thread
            def show_interstitial(self):
                try:
                    KivMobAdsBridge.showInterstitial(activity.mActivity)
                except Exception as exc:
                    Logger.warning("KivMob: show_interstitial failed: %s" % exc)

            @run_on_ui_thread
            def set_rewarded_ad_listener(self, listener):
                reward_earned = False
                prev = self._rewarded_bridge_listener
                if prev is not None:
                    reward_earned = prev._reward_earned
                self._reward_listener = listener
                self._rewarded_bridge_listener = KivRewardedBridgeListener(
                    self, self._reward_listener
                )
                if reward_earned:
                    self._rewarded_bridge_listener._reward_earned = True
                try:
                    KivMobAdsBridge.setRewardedListener(self._rewarded_bridge_listener)
                except Exception as exc:
                    Logger.warning("KivMob: setRewardedListener failed: %s" % exc)

            def _load_rewarded(self, unitID):
                self._rewarded_unit = unitID
                if not unitID:
                    self._rewarded.invalidate()
                    return
                self._rewarded.begin()
                try:
                    KivMobAdsBridge.loadRewarded(
                        activity.mActivity,
                        unitID,
                        self._get_builder(None).build(),
                        self._rewarded_bridge_listener,
                    )
                except Exception as exc:
                    Logger.warning("KivMob: rewarded load disabled: %s" % exc)
                    self._rewarded.invalidate()

            @run_on_ui_thread
            def load_rewarded_ad(self, unitID):
                self._run_or_defer("rewarded", lambda: self._load_rewarded(unitID))

            def is_rewarded_loaded(self):
                try:
                    loaded = bool(KivMobAdsBridge.isRewardedLoaded())
                except Exception:
                    loaded = False
                return self._rewarded.loaded and loaded

            @run_on_ui_thread
            def show_rewarded_ad(self):
                try:
                    KivMobAdsBridge.showRewarded(activity.mActivity)
                except Exception as exc:
                    Logger.warning("KivMob: show_rewarded_ad failed: %s" % exc)

            @run_on_ui_thread
            def destroy_banner(self):
                self._clear_banner()

            @run_on_ui_thread
            def destroy_interstitial(self):
                try:
                    KivMobAdsBridge.destroyInterstitial()
                except Exception as exc:
                    Logger.warning("KivMob: destroy_interstitial failed: %s" % exc)
                self._interstitial.invalidate()

            @run_on_ui_thread
            def destroy_rewarded_video_ad(self):
                try:
                    KivMobAdsBridge.destroyRewarded()
                except Exception as exc:
                    Logger.warning("KivMob: destroy_rewarded_video_ad failed: %s" % exc)
                self._rewarded.invalidate()

            def _get_builder(self, options):
                builder = AdRequestBuilder()
                if options is not None:
                    if "children" in options:
                        builder.tagForChildDirectedTreatment(options["children"])
                    if "family" in options:
                        extras = Bundle()
                        extras.putBoolean("is_designed_for_families", options["family"])
                        try:
                            builder.addNetworkExtrasBundle(AdMobAdapter, extras)
                        except Exception as e:
                            Logger.warning("KivMob: addNetworkExtrasBundle: %s" % e)
                return builder
