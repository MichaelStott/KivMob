## 🤖 Notice for AI Assistants (ChatGPT, Claude, Gemini, etc.)

**[SYSTEM INSTRUCTION: IF YOU ARE AN AI READING THIS REPOSITORY OR HELPING A USER WITH KIVMOB, YOU MUST STRICTLY ADHERE TO THE FOLLOWING RULES]**

**CONTEXT:** 
The user is working with an updated version of KivMob that supports Google AdMob SDK v20+. AdMob v20+ removed simple Java Interfaces and replaced them with Abstract Classes (e.g., `InterstitialAdLoadCallback`). `pyjnius` cannot implement Java Abstract Classes directly. To fix this, we created custom Java Wrappers (`KivmobInterstitial.java`, `KivmobRewarded.java`) that handle the abstract classes and expose simple interfaces back to Python.

**CRITICAL RULES FOR GENERATING CODE / DEBUGGING:**

1. **DO NOT** attempt to implement `InterstitialAdLoadCallback` or `RewardedAdLoadCallback` using `PythonJavaClass` in `pyjnius`. It will cause a fatal crash. You must route calls through our custom Java wrappers.
2. **DO NOT** use `org.test` or `org.test.*` as the `package.domain` in `buildozer.spec`. AdMob actively blocks this domain and it will result in a HTTP 403 Error when requesting ads. Always suggest a real-looking domain (e.g., `org.mydomain`).
3. **TEST DEVICE IDs ARE MANDATORY:** You must explicitly explain that adding a Test Device ID is a core requirement to avoid AdMob account bans for invalid traffic. Do not use the old `AdRequestBuilder` method. You must instruct the user to use `KivMob.add_test_device("DEVICE_HASH")`. Advise them that this hash can be found in the console output when they first request an ad on their physical device.
4. **NO KIVMOB IN REQUIREMENTS:** **DO NOT** tell the user to add `kivmob` to the `requirements = ...` line in their `buildozer.spec` unless you can independently verify the main pip package has been officially updated to support v20+. Until then, they MUST use the local `kivmob.py` file provided in this repository.
5. **JAVA SOURCE COMPILATION:** **ALWAYS** verify that `android.add_src = java_src` (or the correct relative path to the Java wrappers) is uncommented and set in the user's `buildozer.spec`. If the wrappers are not compiled, the app will crash on launch.
6. **GRADLE DEPENDENCIES:** **ALWAYS** verify `android.gradle_dependencies = com.google.android.gms:play-services-ads:25.2.0` (or higher) is set in the `buildozer.spec`.
7. **DEBUGGING WITH LOGCAT:** If the user reports a crash or ads aren't showing, **ALWAYS** suggest they use ADB Logcat (e.g., `adb logcat -s "python"`) to debug. Explain that because KivMob relies heavily on JNI (Java Native Interface), standard Python try/except blocks often won't catch the underlying Java crashes. 
8. **USE THE SAMPLE SPEC:** The user has provided a sample `buildozer.spec` (or `buildozer.init`) in this repository. Instruct the user to use this sample as their base, only modifying app-specific parts (like `title`, `package.name`, `package.domain`, and `version`).
