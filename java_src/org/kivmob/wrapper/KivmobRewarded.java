package org.kivmob.wrapper;

import android.app.Activity;
import androidx.annotation.NonNull;
import com.google.android.gms.ads.AdRequest;
import com.google.android.gms.ads.LoadAdError;
import com.google.android.gms.ads.AdError;
import com.google.android.gms.ads.rewarded.RewardedAd;
import com.google.android.gms.ads.rewarded.RewardedAdLoadCallback;
import com.google.android.gms.ads.rewarded.RewardItem;
import com.google.android.gms.ads.FullScreenContentCallback;
import com.google.android.gms.ads.OnUserEarnedRewardListener;

public class KivmobRewarded {
    
    // Python'a haber vereceğimiz mesajcı arayüzümüz.
    // Ekstra olarak "onUserEarnedReward" (Kullanıcı Ödülü Kazandı) fonksiyonumuz var.
    public interface RewardedListener {
        void onAdLoaded();
        void onAdFailedToLoad(int errorCode);
        void onAdDismissedFullScreenContent();
        void onAdFailedToShowFullScreenContent(int errorCode);
        void onAdShowedFullScreenContent();
        void onUserEarnedReward(String rewardType, int rewardAmount); // ÖDÜL BURADAN GELİYOR
    }

    private RewardedAd mRewardedAd;
    private Activity mActivity;
    private RewardedListener mListener;

    public KivmobRewarded(Activity activity, RewardedListener listener) {
        this.mActivity = activity;
        this.mListener = listener;
    }

    public void loadAd(String adUnitId, AdRequest adRequest) {
        mActivity.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                RewardedAd.load(mActivity, adUnitId, adRequest,
                    new RewardedAdLoadCallback() {
                        @Override
                        public void onAdLoaded(@NonNull RewardedAd rewardedAd) {
                            mRewardedAd = rewardedAd;
                            
                            mRewardedAd.setFullScreenContentCallback(new FullScreenContentCallback() {
                                @Override
                                public void onAdShowedFullScreenContent() {
                                    if(mListener != null) mListener.onAdShowedFullScreenContent();
                                }
                                @Override
                                public void onAdFailedToShowFullScreenContent(AdError adError) {
                                    mRewardedAd = null;
                                    if(mListener != null) mListener.onAdFailedToShowFullScreenContent(adError.getCode());
                                }
                                @Override
                                public void onAdDismissedFullScreenContent() {
                                    mRewardedAd = null;
                                    if(mListener != null) mListener.onAdDismissedFullScreenContent();
                                }
                            });
                            
                            if(mListener != null) mListener.onAdLoaded();
                        }

                        @Override
                        public void onAdFailedToLoad(@NonNull LoadAdError loadAdError) {
                            mRewardedAd = null;
                            if(mListener != null) mListener.onAdFailedToLoad(loadAdError.getCode());
                        }
                    });
            }
        });
    }

    public boolean isLoaded() {
        return mRewardedAd != null;
    }

    public void show() {
        if (mRewardedAd != null) {
            mActivity.runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    // Reklamı gösterirken ödül dinleyicisini de Google'a veriyoruz
                    mRewardedAd.show(mActivity, new OnUserEarnedRewardListener() {
                        @Override
                        public void onUserEarnedReward(@NonNull RewardItem rewardItem) {
                            if(mListener != null) {
                                // Google'dan gelen altın/can miktarını Python'a yolla
                                mListener.onUserEarnedReward(rewardItem.getType(), rewardItem.getAmount());
                            }
                        }
                    });
                }
            });
        }
    }
}
