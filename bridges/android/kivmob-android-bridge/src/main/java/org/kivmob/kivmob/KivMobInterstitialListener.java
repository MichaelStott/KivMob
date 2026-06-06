package org.kivmob.kivmob;

public interface KivMobInterstitialListener {
    void onInterstitialLoaded();
    void onInterstitialFailed(String message, int code);
    void onInterstitialShown();
    void onInterstitialDismissed();
}
