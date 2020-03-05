<p align="center">
  <img src="https://raw.githubusercontent.com/MichaelStott/KivMob/master/demo/assets/kivmob-title.png">
</p>
<h2 align="center">AdMob support for Kivy</h2>
<p align="center">
  <a href="https://travis-ci.com/MichaelStott/KivMob"><img alt="Build Status" src="https://travis-ci.com/MichaelStott/KivMob.svg?branch=master"></a>
  <a href="https://badge.fury.io/py/kivmob"><img alt="pypi" src="https://badge.fury.io/py/kivmob.svg"></a>
  <a href="https://www.python.org/downloads/release/python-270/"><img alt="Python Version" src="https://img.shields.io/badge/python-2.7|3.7-green.svg"></a>
  <a href="https://pepy.tech/project/kivmob"><img alt="Code Climate" src="https://pepy.tech/badge/kivmob"></a>
  <a href="https://codeclimate.com/github/MichaelStott/KivMob/maintainability"><img alt="Code Climate" src="https://api.codeclimate.com/v1/badges/add8cd9bd9600d898b79/maintainability"></a>
  <a href="https://github.com/python/black"><img alt="Code style: black" src="https://img.shields.io/badge/code%20style-black-000000.svg"></a>
  <a href="http://kivmob.com"><img alt="docs" src="https://img.shields.io/static/v1?label=s3-hosted-docs&message=passing&color=blue"/></a>
</p>

Allows developers to monetize their [Kivy] mobile applications using [Google AdMob].

  - No need to change internal Android project manifest templates or Java code.
  - Supports banner, interstitial, and rewarded video ads.

For more information, please read the official [documentation].

### Installation

You can install KivMob with the following command.
```sh
$ pip3 install kivmob
```

### Demo Screenshot
<p align="center">
  <img src="https://raw.githubusercontent.com/MichaelStott/KivMob/master/demo/assets/demo_screenshotv2.png">
</p>

### Quickstart

Create a new folder containing main.py and buildozer.spec.

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
        self.ads = KivMob(TestIds.APP)
        self.ads.new_interstitial(TestIds.INTERSTITIAL)
        self.ads.request_interstitial()
        return Button(text='Show Interstitial',
                      on_release=lambda a:self.ads.show_interstitial())
                      
    def on_resume(self):
        self.ads.request_interstitial()

KivMobTest().run()
```

Make the following modifications to your buildozer.spec file.

```
requirements = kivy, android, jnius, kivmob
...
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

_Please open a pull request or project issue if you would like your KivMob app featured in this README and the documentation._

<!-- List alphabetically please.  -->
| App | Play Store Link | Author |
| ------ | ------ | ------ |
| Gloworld : The Marbles game | https://play.google.com/store/apps/details?id=com.worldglowfree.dom.com.world.glowfree&hl=en | [thegameguy] |
| MIUI Hidden Settings | https://play.google.com/store/apps/details?id=com.ceyhan.sets | [Yunus Ceyhan] |
| PyTool USB Serial Free |  https://play.google.com/store/apps/details?id=com.quanlin.pytoolusbserialfree | [Quan Lin] |

### Other 

KivMob is an open source project not associated with AdMob. Please abide by their policies when designing and testing your application.

<!-- Links pertinent to README -->
[Google AdMob]: <https://www.google.com/admob/>
[Kivy]: <https://kivy.org/>
[Buildozer]: <https://github.com/kivy/buildozer>
[documentation]: <http://kivmob.com>

<!-- App showcase author links -->
[Quan Lin]: <https://github.com/jacklinquan>
[thegameguy]: <https://github.com/thegameguy>
[Yunus Ceyhan]: <https://github.com/yunus-ceyhan>

