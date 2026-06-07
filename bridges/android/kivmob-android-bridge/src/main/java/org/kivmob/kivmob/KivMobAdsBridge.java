package org.kivmob.kivmob;

import android.app.Activity;
import android.util.Log;

import com.google.android.gms.ads.AdError;
import com.google.android.gms.ads.AdRequest;
import com.google.android.gms.ads.FullScreenContentCallback;
import com.google.android.gms.ads.LoadAdError;
import com.google.android.gms.ads.interstitial.InterstitialAd;
import com.google.android.gms.ads.interstitial.InterstitialAdLoadCallback;
import com.google.android.gms.ads.rewarded.RewardItem;
import com.google.android.gms.ads.rewarded.RewardedAd;
import com.google.android.gms.ads.rewarded.RewardedAdLoadCallback;

public final class KivMobAdsBridge {
    private static final String TAG = "KivMobAdsBridge";

    private static InterstitialAd interstitialAd;
    private static RewardedAd rewardedAd;
    private static KivMobRewardedListener rewardedListener;

    private KivMobAdsBridge() {}

    public static void loadInterstitial(
            Activity activity,
            String unitId,
            AdRequest adRequest,
            KivMobInterstitialListener listener) {
        interstitialAd = null;
        InterstitialAd.load(
                activity,
                unitId,
                adRequest,
                new InterstitialAdLoadCallback() {
                    @Override
                    public void onAdLoaded(InterstitialAd ad) {
                        interstitialAd = ad;
                        ad.setFullScreenContentCallback(
                                new FullScreenContentCallback() {
                                    @Override
                                    public void onAdShowedFullScreenContent() {
                                        if (listener != null) {
                                            listener.onInterstitialShown();
                                        }
                                    }

                                    @Override
                                    public void onAdDismissedFullScreenContent() {
                                        interstitialAd = null;
                                        if (listener != null) {
                                            listener.onInterstitialDismissed();
                                        }
                                    }

                                    @Override
                                    public void onAdFailedToShowFullScreenContent(AdError adError) {
                                        interstitialAd = null;
                                        if (listener != null) {
                                            listener.onInterstitialFailed(adError.getMessage(), adError.getCode());
                                        }
                                    }
                                });
                        if (listener != null) {
                            listener.onInterstitialLoaded();
                        }
                    }

                    @Override
                    public void onAdFailedToLoad(LoadAdError error) {
                        interstitialAd = null;
                        if (listener != null) {
                            listener.onInterstitialFailed(error.getMessage(), error.getCode());
                        }
                    }
                });
    }

    public static boolean isInterstitialLoaded() {
        return interstitialAd != null;
    }

    public static void showInterstitial(Activity activity) {
        if (interstitialAd != null) {
            interstitialAd.show(activity);
        } else {
            Log.d(TAG, "showInterstitial called with no loaded ad");
        }
    }

    public static void destroyInterstitial() {
        interstitialAd = null;
    }

    public static void loadRewarded(
            Activity activity,
            String unitId,
            AdRequest adRequest,
            KivMobRewardedListener listener) {
        rewardedAd = null;
        rewardedListener = listener;
        RewardedAd.load(
                activity,
                unitId,
                adRequest,
                new RewardedAdLoadCallback() {
                    @Override
                    public void onAdLoaded(RewardedAd ad) {
                        rewardedAd = ad;
                        ad.setFullScreenContentCallback(
                                new FullScreenContentCallback() {
                                    @Override
                                    public void onAdShowedFullScreenContent() {
                                        if (rewardedListener != null) {
                                            rewardedListener.onRewardedShown();
                                        }
                                    }

                                    @Override
                                    public void onAdDismissedFullScreenContent() {
                                        rewardedAd = null;
                                        if (rewardedListener != null) {
                                            rewardedListener.onRewardedDismissed();
                                        }
                                    }

                                    @Override
                                    public void onAdFailedToShowFullScreenContent(AdError adError) {
                                        rewardedAd = null;
                                        if (rewardedListener != null) {
                                            rewardedListener.onRewardedFailed(adError.getMessage(), adError.getCode());
                                        }
                                    }
                                });
                        if (rewardedListener != null) {
                            rewardedListener.onRewardedLoaded();
                        }
                    }

                    @Override
                    public void onAdFailedToLoad(LoadAdError error) {
                        rewardedAd = null;
                        if (rewardedListener != null) {
                            rewardedListener.onRewardedFailed(error.getMessage(), error.getCode());
                        }
                    }
                });
    }

    public static boolean isRewardedLoaded() {
        return rewardedAd != null;
    }

    public static void showRewarded(Activity activity) {
        if (rewardedAd == null) {
            Log.d(TAG, "showRewarded called with no loaded ad");
            return;
        }
        rewardedAd.show(
                activity,
                (RewardItem rewardItem) -> {
                    if (rewardedListener != null) {
                        rewardedListener.onUserEarnedReward(
                                rewardItem.getType(),
                                rewardItem.getAmount());
                    }
                });
    }

    public static void destroyRewarded() {
        rewardedAd = null;
    }
}
