package org.kivy.android;

import java.util.ArrayList;
import android.os.Bundle;
import android.os.Handler;
import android.os.Message;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.FrameLayout;
import com.google.android.gms.ads.AdListener;
import com.google.android.gms.ads.AdRequest;
import com.google.android.gms.ads.InterstitialAd;
import com.google.android.gms.ads.MobileAds;
import com.google.android.gms.ads.AdSize;
import com.google.android.gms.ads.AdView;
import com.google.ads.mediation.admob.AdMobAdapter;

public class KivMobAdMobAdapter {

    private static AdView adView = null;
    private static InterstitialAd interstitialAd = null;
    private static ArrayList<String> testDevices = new ArrayList<String>();
    public static enum AdCmd { INIT_ADS,
                               ADD_TEST_DEVICE,
                               NEW_BANNER,
                               NEW_INTERSTITIAL,
                               REQ_BANNER,
                               REQ_INTERSTITIAL,
                               SHOW_BANNER,
                               SHOW_INTERSTITIAL,
                               HIDE_BANNER
                             };

    // Handles all comunication to ad threads.
    public static Handler adHandler = new Handler() {
	@Override
	public void handleMessage(Message msg) {
        AdRequest.Builder builder = new AdRequest.Builder();
	    switch (AdCmd.values()[msg.what]) {
            case INIT_ADS:
                MobileAds.initialize(PythonActivity.mActivity, msg.getData().getString("appID"));
                break;
            case ADD_TEST_DEVICE:
                testDevices.add(msg.getData().getString("deviceID"));
                break;
            case NEW_BANNER:
                FrameLayout.LayoutParams lp = new FrameLayout.LayoutParams(
                    FrameLayout.LayoutParams.WRAP_CONTENT,
                    FrameLayout.LayoutParams.WRAP_CONTENT,
                    Gravity.BOTTOM|Gravity.CENTER_HORIZONTAL);
                adView = new AdView(PythonActivity.mActivity);
                adView.setAdSize(AdSize.SMART_BANNER);
                adView.setAdUnitId(msg.getData().getString("unitID"));
                adView.setLayoutParams(lp);
                adView.setVisibility(View.GONE);
                adView.setAdListener(new AdListener() {});
                ViewGroup layout = getLayout();
                layout.addView(adView);
                break;
            case NEW_INTERSTITIAL:
                interstitialAd = new InterstitialAd(PythonActivity.mActivity);
                interstitialAd.setAdUnitId(msg.getData().getString("unitID"));
                interstitialAd.setAdListener(new AdListener() {
                    @Override
                    public void onAdClosed() {}
                });
                break;
            case REQ_BANNER: 
                for (String device : testDevices) {
                    builder.addTestDevice(device);
                }
                builder.addTestDevice(AdRequest.DEVICE_ID_EMULATOR);
                AdRequest bannRequest = builder.build();
                adView.loadAd(bannRequest);
                break;
            case REQ_INTERSTITIAL:
                if (msg.getData().containsKey("child")) {
                    builder.tagForChildDirectedTreatment(msg.getData().getBoolean("child"));
                }
                if (msg.getData().containsKey("family")) { 
                    Bundle extras = new Bundle();
                    extras.putBoolean("is_designed_for_families",
                        msg.getData().getBoolean("family"));
                    builder.addNetworkExtrasBundle(AdMobAdapter.class, extras);
                }
                builder.addTestDevice(AdRequest.DEVICE_ID_EMULATOR);
                for (String device : testDevices) {
                    builder.addTestDevice(device);
                }
                AdRequest interRequest = builder.build();
                interstitialAd.loadAd(interRequest);
                break;
            case SHOW_BANNER:
                adView.setVisibility(View.VISIBLE);
                break;
            case SHOW_INTERSTITIAL:
                if (interstitialAd.isLoaded()) { interstitialAd.show(); }
                break;
            case HIDE_BANNER:
                adView.setVisibility(View.GONE);
                break;
            default:
                break;
	    }
	}
    };

    public static boolean isLoaded() {
        return interstitialAd.isLoaded();
    }
}