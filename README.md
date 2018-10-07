![KivMob](https://raw.githubusercontent.com/MichaelStott/KivMob/master/demo/assets/kivmob-title.png)

Framework which enables ad monitization for [Kivy]-based Android applications.

  - Automates Android project configuration through CLI tool.
  - Video, interstitial, and banner ads.
  - Google AdMob support.

### Demo Screenshot

<p align="center">
  <img src="https://raw.githubusercontent.com/MichaelStott/KivMob/master/demo/assets/demo-screenshot-github.png">
</p>

### Installation

You can install KivMob with the following command.
```sh
$ pip install kivmob
```
### Quick Tutorial

This tutorial assumes you are familiar with AdMob. Additionally, be sure that you have the latest version of [Buildozer] installed, as KivMob uses the android_new toolchain.

Create a new directory. Copy the following and paste it into a new main.py file. Be sure to include your AdMob app ID, your test device ID, and interstitial ID.

```python
from kivmob import KivMob
from kivy.app import App
from kivy.uix.button import Button

class KivMobTest(App):
    
    def build(self):
        ads = KivMob("APP_ID")
        ads.add_test_device("TEST_DEVICE_ID")
        ads.new_interstitial("INTERSTITIAL_ID")
        ads.request_interstitial()
        return Button(text='Show Interstitial',
                      on_release= lambda a:ads.show_interstitial())

KivMobTest().run()
```

In the same directory, generate buildozer.spec and make the following changes.

```sh
requirements = kivy, hostpython2, android, kivmob
android.permissions = INTERNET, ACCESS_NETWORK_STATE
android.bootstrap = sdl2-admob
```

To build and deploy the project, run the following command. Wait a few moments for the ad to load before pressing the button.

```sh
$ buildozer android debug deploy
```

<p align="center">
  <img src="https://raw.githubusercontent.com/MichaelStott/KivMob/master/demo/assets/tutorial-screenshot.png">
</p>

Look under the demo folder for a more extensive example.

### Todo
 - Finish remaining unimplemented methods in AdMobBridge interface.
 - Write documentation.
 - Develop Buildozer recipe for KivMob that would make changes to Android project, download AdMob library, and provide Java backend. (Eliminating need for python-for-android-admob)

### Future Work
 - Layout that repositions widgets when banner ad is displayed.
 - iOS support.

[Google Admob]: <https://www.google.com/admob/>
[Kivy]: <https://kivy.org/>
[Buildozer]: <https://github.com/kivy/buildozer>
