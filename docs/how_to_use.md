Here is the documentation and the example Kivy application for the Pull Request. 

### `HOW_TO_USE.md`

```markdown
# KivMob: AdMob Support for Kivy (Updated for SDK v20+)

Welcome to the updated KivMob! Due to architecture changes in Google AdMob SDK v20+, simple Java Interfaces have been replaced with Abstract Classes (such as `InterstitialAdLoadCallback`). Because `pyjnius` cannot directly implement Java Abstract Classes, we have introduced a custom Java Wrapper bridge (`KivmobInterstitial.java` and `KivmobRewarded.java`) to safely connect Python back to AdMob[cite: 1, 2, 3].

This guide will walk you through the setup, including critical configurations required to prevent your app from crashing.

## 1. Project Directory Structure
To use the new Java wrappers, you must include them in your project structure. Create a `java_src` folder in your project root and map out the exact package path for the wrappers[cite: 4]:

```text
your_project/
│
├── main.py
├── kivmob.py
├── buildozer.spec
└── java_src/
    └── org/
        └── kivmob/
            └── wrapper/
                ├── KivmobInterstitial.java
                └── KivmobRewarded.java
```

## 2. CRITICAL: `buildozer.spec` Gotchas
During testing, we discovered specific requirements for `buildozer.spec`. **If you ignore these, your app will crash or fail to show ads with a 403 Error.**

*   **Add Java Sources:** You MUST tell Buildozer to compile our new Java wrappers by setting the source directory[cite: 4].
    ```ini
    android.add_src = java_src
    
```
*   **Update Gradle Dependencies:** You MUST use the latest AdMob SDK[cite: 4].
    ```ini
    android.gradle_dependencies = com.google.android.gms:play-services-ads:25.2.0
    
```
*   **Package Domain (403 Error Fix):** Google AdMob strictly blocks `org.test` (e.g., `org.test.myapp`) and will throw a 403 Error. You must use a real-looking package name[cite: 4].
    ```ini
    # DO NOT USE org.test
    package.domain = org.mycoolapp 
    
```
*   **Application ID Meta-data:** Ensure your AdMob App ID is correctly placed in the meta-data[cite: 4].
    ```ini
    android.meta_data = com.google.android.gms.ads.APPLICATION_ID=ca-app-pub-3940256099942544~3347511713
    
```

## 3. Initializing KivMob & Test Devices
Test Device IDs are no longer added via the old builder. The new architecture leverages `RequestConfigurationBuilder` under the hood[cite: 1]. You must add your test devices directly using the `add_test_device` method.

```python
from kivmob import KivMob, TestIds

# Initialize KivMob with your App ID
ads = KivMob(TestIds.APP)

# Add your test device ID to prevent invalid traffic bans
ads.add_test_device("YOUR_TEST_DEVICE_HASH_ID")
```

## 4. Setting Up Rewarded Ads
Because Rewarded Ads grant users items (like coins or extra lives), you must implement the `RewardedListenerInterface` to catch the reward data passed back from our Java wrapper[cite: 1, 2].

```python
from kivmob import RewardedListenerInterface

class MyRewardedListener(RewardedListenerInterface):
    def on_rewarded(self, reward_name, reward_amount):
        print(f"User earned {reward_amount} {reward_name}!")
```

## 5. Requesting and Showing Ads
Once initialized, the lifecycle for displaying ads remains simple.

*   **Banner Ads:**
    ```python
    ads.new_banner(TestIds.BANNER, top_pos=False)
    ads.request_banner()
    ads.show_banner()
    
```
*   **Interstitial Ads:**
    ```python
    ads.new_interstitial(TestIds.INTERSTITIAL)
    ads.request_interstitial()
    # Wait for the ad to load, then show:
    if ads.is_interstitial_loaded():
        ads.show_interstitial()
    
```
*   **Rewarded Ads:**
    ```python
    ads.set_rewarded_ad_listener(MyRewardedListener())
    ads.load_rewarded_ad(TestIds.REWARDED_VIDEO)
    # Wait for the ad to load, then show:
    if ads.is_rewarded_loaded():
        ads.show_rewarded_ad()
    ```
```

---
