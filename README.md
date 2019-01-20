![KivMob](https://raw.githubusercontent.com/MichaelStott/KivMob/master/demo/assets/kivmob-title.png)

[![Build Status](https://travis-ci.com/MichaelStott/KivMob.svg?branch=master)](https://travis-ci.com/MichaelStott/KivMob)
[![Python 2.7](https://img.shields.io/badge/python-2.7-green.svg)](https://www.python.org/downloads/release/python-270/)
[![Downloads](https://pepy.tech/badge/kivmob)](https://pepy.tech/project/kivmob)
[![Maintainability](https://api.codeclimate.com/v1/badges/add8cd9bd9600d898b79/maintainability)](https://codeclimate.com/github/MichaelStott/KivMob/maintainability)

Allows developers to monetize their [Kivy] mobile applications using [Google AdMob].

  - No need to change internal Android project manifest templates or Java code.
  - Supports banner, interstitial, and rewarded video ads.


### Installation

You can install KivMob with the following command.
```sh
$ pip install  git+https://github.com/MichaelStott/KivMob
```

### Demo Screenshot
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
android.meta_data = com.google.android.gms.ads.APPLICATION_ID=ca-app-pub-3940256099942544~3347511713
```

Finally, build and launch the application.

```sh
$ buildozer android debug deploy run
```

### App Showcase

_Please contact me via pull request or project issue if you would like your KivMob app featured in this README and the documentation._

<!-- List alphabetically please.  -->
| App | Play Store Link | Author |
| ------ | ------ | ------ |
| Gloworld | https://play.google.com/store/apps/details?id=com.worldglowfree.dom.com.world.glowfree | Prozee Games, [thegameguy] |

### Other 

KivMob is an open source project not associated with AdMob. Please abide by their policies when designing and testing your application.

<!-- Links pertinent to README -->
[Google AdMob]: <https://www.google.com/admob/>
[Kivy]: <https://kivy.org/>
[Buildozer]: <https://github.com/kivy/buildozer>

<!-- App showcase author links -->
[thegameguy]: <https://github.com/thegameguy>
