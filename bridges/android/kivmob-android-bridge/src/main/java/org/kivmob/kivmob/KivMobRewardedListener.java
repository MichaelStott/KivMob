package org.kivmob.kivmob;

public interface KivMobRewardedListener {
    void onRewardedLoaded();
    void onRewardedFailed(String message, int code);
    void onRewardedShown();
    void onRewardedDismissed();
    void onUserEarnedReward(String rewardType, int rewardAmount);
}
