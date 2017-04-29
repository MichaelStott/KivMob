![KivMob](https://raw.githubusercontent.com/MichaelStott/KivMob/master/demo/assets/kivmob-title.png)

Provides interface for Kivy applications to access [Google Admob] functionalty on Android devices.

  - No need to change internal Android project manifest templates, Java code, or manually add external libraries.
  - Support for interstitial and banner ads.

### Demo Screenshot

<p align="center">
  <img src="https://raw.githubusercontent.com/MichaelStott/KivMob/master/demo/assets/demo-screenshot-github.png">
</p>

### Installation

Download python-for-android-admob and install KivMob using the following commands.
```sh
$ git clone https://github.com/MichaelStott/python-for-android-admob.git
$ pip install kivmob
```
### Tutorial

Make the following changes in buildozer.spec.
```sh
requirements = kivy, hostpython2, android, kivmob
android.permissions = INTERNET, ACCESS_NETWORK_STATE
android.p4a_dir = # dir/to/python-for-android-admob/
android.bootstrap = sdl2-admob
```

### Todos
 - Buildozer recipe for KivMob that would make changes to Android project, download AdMob library, and provide Java backend. (Eliminating need for python-for-android-admob)
 - iOS support.

### Future Work
 - Layout that repositions widgets when banner ad is displayed.

[Google Admob]: <https://www.google.com/admob/>
