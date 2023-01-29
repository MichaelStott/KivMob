Tutorial
========

Installation
-----------------

KivMob is available for download from the Python Package Index using *pip*:

.. code-block:: sh

    $ pip3 install kivmob

Alternatively, you can install it from the source via setup.py

.. code-block:: sh

    $ python3 setup.py install --user

Android Configuration
---------------------

Modify buildozer.spec as such:

.. code-block:: sh

    requirements = python3, kivy, android, jnius, kivmob
    ...
    android.permissions = INTERNET, ACCESS_NETWORK_STATE
    android.api = 33
    android.minapi = 21
    android.sdk = 33
    android.ndk = 25b
    android.gradle_dependencies = 'com.google.firebase:firebase-ads:21.4.0'
    android.enable_androidx = True
    p4a.branch = master
    # For test ads, use application ID ca-app-pub-3940256099942544~3347511713
    android.meta_data = com.google.android.gms.ads.APPLICATION_ID={ADMOB_APP_ID_HERE}

Banners
-----------------

Banner ads are rectangular image or text ads that take up a portion of the app screen. KivMob allows banner ads
to be positioned on the top or bottom of the page.

.. code-block:: python

    from kivmob import KivMob, TestIds

    from kivy.app import App
    from kivy.uix.label import Label

    class BannerTest(App):
        """ Displays a banner ad at top of the screen.
        """

        def build(self):
            self.ads = KivMob(TestIds.APP)
            self.ads.new_banner(TestIds.BANNER, top_pos=True)
            self.ads.request_banner()
            self.ads.show_banner()
            return Label(text='Banner Ad Demo')

    if __name__ == "__main__":
        BannerTest().run()

The banner location can be changed to the bottom of the screen by setting *top_pos* to *False*.

Interstitials
-----------------

Interstitial ads are full-screen ads that cover the entire app until dismissed by the user.

.. code-block:: python

    from kivmob import KivMob, TestIds

    from kivy.app import App
    from kivy.uix.button import Button

    class InterstitialTest(App):
        """ Display an interstitial ad on button release.
        """

        def build(self):
            self.ads = KivMob(TestIds.APP)
            self.ads.new_interstitial(TestIds.INTERSTITIAL)
            self.ads.request_interstitial()
            return Button(text='Show Interstitial',
                          on_release=lambda a:self.ads.show_interstitial())
                        
        def on_resume(self):
            self.ads.request_interstitial()

    if __name__ == "__main__":
        InterstitialTest().run()

Rewarded Video
-------------------

Ads the user may view in exchange for in-app rewards. Callback
functionality can be handled with a class implementing RewardedListenerInterface.

.. code-block:: python

    from kivmob import KivMob, TestIds, RewardedListenerInterface

    from kivy.app import App
    from kivy.uix.button import Button

    class RewardedVideoTest(App):
        """ Display a rewarded video ad on button release.
        """

        def build(self):
            self.ads = KivMob(TestIds.APP)
            self.ads.load_rewarded_ad(TestIds.REWARDED_VIDEO)
            # Add any callback functionality to this class.
            self.ads.set_rewarded_ad_listener(RewardedListenerInterface())
            return Button(text='Show Rewarded Ad',
                          on_release=lambda a:self.ads.show_rewarded_ad())
                        
        def on_resume(self):
            self.ads.load_rewarded_ad(TestIds.REWARDED_VIDEO)

    if __name__ == "__main__":
        RewardedVideoTest().run()
