![KivMob](https://raw.githubusercontent.com/MichaelStott/KivMob/master/demo/assets/kivmob-title.png)

Provides interface for Kivy applications to access [Google Admob] functionalty on Android devices.

  - No need to change internal Android project manifest templates, Java code, or manually add external libraries.
  - Support for interstitial and banner ads.

### Installation

Download python-for-android-admob and install KivMob using the following commands.
```sh
$ git clone https://github.com/MichaelStott/python-for-android-admob.git
$ pip install kivmob
```
### Tutorial

Make the following changes in buildozer.spec.
```sh
requirements = kivy, hostpython2, android
android.permissions = INTERNET, ACCESS_NETWORK_STATE
android.p4a_dir = # dir/to/python-for-android-admob/
android.bootstrap = sdl2-admob
```

### Todos
 - iOS support.
 - Layout that repositions widgets when banner ad is displayed.

### Future Work
 - Buildozer recipe for KivMob that would make changes to Android project, download AdMob library, and Java backend. (Eliminating need for python-for-android-admob)

[Google Admob]: <https://www.google.com/admob/>
