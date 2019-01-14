![KivMob](https://raw.githubusercontent.com/MichaelStott/KivMob/master/demo/assets/kivmob-title.png)

Allows developers to monetize their [Kivy] mobile applications using [Google AdMob].

  - No need to change internal Android project manifest templates, Java code, or manually add external libraries.
  - Banner, interstitial, and rewarded video ads (WIP).


### Installation

You can install KivMob with the following command.
```sh
$ pip install  git+https://github.com/MichaelStott/KivMob
```

### Demo Screenshot (WIP)
<p align="center">
  <img src="https://raw.githubusercontent.com/MichaelStott/KivMob/master/demo/assets/demo_screenshotv2.png">
</p>

### Quickstart

Create an new folder containing main.py and buildozer.spec.
```sh
$ mkdir kivmob-quickstart
$ cd kivmob-quickstart
$ touch main.py
$ buildozer init
```

Copy the following into main.py.
```python
from kivmob import KivMob, TestIds
from kivy.app import App
from kivy.uix.button import Button

class KivMobTest(App):
    
    def build(self):
        ads = KivMob(TestIds.APP)
        ads.new_interstitial(TestIds.INTERSTITIAL)
        ads.request_interstitial()
        return Button(text='Show Interstitial',
                      on_release= lambda a:ads.show_interstitial())

KivMobTest().run()
```

Make the following modifications to your buildozer.spec file.

```
android.permissions = INTERNET, ACCESS_NETWORK_STATE
android.api = 27
android.minapi = 21
android.sdk = 24
android.ndk = 17b
android.gradle_dependencies = 'com.google.firebase:firebase-ads:10.2.0'
p4a.branch = master
# You will need to place your actual app ID here. The below ID corresponds to kivmob.TestIds.APP.
android.meta_data = com.google.android.gms.ads.APPLICATION_ID=ca-app-pub-3940256099942544~3347511713
```

Finally, build and launch the application.

```sh
$ buildozer android debug deploy run
```

### Apps using KivMob

Please contact me via pull request or project issue if you would like your KivMob app featured in this README and/or the documentation.

### Other

KivMob is an open source project not associated with AdMob. Please abide by their policies when designing your application.

[Google AdMob]: <https://www.google.com/admob/>
[Kivy]: <https://kivy.org/>
[Buildozer]: <https://github.com/kivy/buildozer>
