// Define the package name. This must match the folder structure we created.
package org.kivmob.wrapper;

// Import required Android and AdMob libraries
import android.app.Activity;
import androidx.annotation.NonNull;
import com.google.android.gms.ads.AdRequest;
import com.google.android.gms.ads.LoadAdError;
import com.google.android.gms.ads.AdError;
import com.google.android.gms.ads.interstitial.InterstitialAd;
import com.google.android.gms.ads.interstitial.InterstitialAdLoadCallback;
import com.google.android.gms.ads.FullScreenContentCallback;

public class KivmobInterstitial {
    
    // 1. CREATE A SIMPLE INTERFACE FOR PYTHON
    // Python (pyjnius) can easily understand this simple interface.
    // It acts as a messenger between Java and Python.
    public interface InterstitialListener {
        void onAdLoaded();
        void onAdFailedToLoad(int errorCode);
        void onAdDismissedFullScreenContent();
        void onAdFailedToShowFullScreenContent(int errorCode);
        void onAdShowedFullScreenContent();
    }

    // Variables to hold the ad, the app screen (Activity), and our messenger
    private InterstitialAd mInterstitialAd;
    private Activity mActivity;
    private InterstitialListener mListener;

    // Constructor: Runs when we initialize this class from Python
    public KivmobInterstitial(Activity activity, InterstitialListener listener) {
        this.mActivity = activity;
        this.mListener = listener;
    }

    // 2. FUNCTION TO LOAD THE AD
    public void loadAd(String adUnitId, AdRequest adRequest) {
        // UI operations must run on the main UI thread
        mActivity.runOnUiThread(new Runnable() {
            @Override
            public void run() {
                // Tell Google AdMob to load the Interstitial ad
                InterstitialAd.load(mActivity, adUnitId, adRequest,
                    new InterstitialAdLoadCallback() {
                        
                        // Called when the ad is successfully loaded from the internet
                        @Override
                        public void onAdLoaded(@NonNull InterstitialAd interstitialAd) {
                            mInterstitialAd = interstitialAd; // Save the loaded ad
                            
                            // Now set up callbacks for when the ad is shown on screen
                            mInterstitialAd.setFullScreenContentCallback(new FullScreenContentCallback(){
                                
                                // Called when the user clicks the 'X' button and closes the ad
                                @Override
                                public void onAdDismissedFullScreenContent() {
                                    mInterstitialAd = null; // Clear the ad from memory
                                    if(mListener != null) mListener.onAdDismissedFullScreenContent(); // Tell Python
                                }
                                
                                // Called if the ad fails to show on screen
                                @Override
                                public void onAdFailedToShowFullScreenContent(AdError adError) {
                                    mInterstitialAd = null;
                                    if(mListener != null) mListener.onAdFailedToShowFullScreenContent(adError.getCode()); // Tell Python
                                }
                                
                                // Called when the ad is successfully visible to the user
                                @Override
                                public void onAdShowedFullScreenContent() {
                                    if(mListener != null) mListener.onAdShowedFullScreenContent(); // Tell Python
                                }
                            });
                            
                            // Tell Python that the ad is ready to be shown
                            if(mListener != null) mListener.onAdLoaded();
                        }

                        // Called if the ad fails to load from the internet (e.g., no connection, bad ID)
                        @Override
                        public void onAdFailedToLoad(@NonNull LoadAdError loadAdError) {
                            mInterstitialAd = null;
                            if(mListener != null) mListener.onAdFailedToLoad(loadAdError.getCode()); // Tell Python
                        }
                    });
            }
        });
    }

    // 3. FUNCTION TO CHECK IF AD IS READY
    // Returns true if ad is downloaded and ready, false otherwise
    public boolean isLoaded() {
        return mInterstitialAd != null;
    }

    // 4. FUNCTION TO SHOW THE AD ON SCREEN
    public void show() {
        if (mInterstitialAd != null) {
            mActivity.runOnUiThread(new Runnable() {
                @Override
                public void run() {
                    mInterstitialAd.show(mActivity); // Show the ad to the user
                }
            });
        }
    }
}
