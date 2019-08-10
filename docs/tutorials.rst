Tutorial
========

Installation
-----------------

kivmob is available for download using pip:

.. code-block:: sh

    $ pip3 install kivmob

Alternatively, you can install it from the master branch via setup.py

.. code-block:: sh

    python3 setup.py install --user

Banner Ads
-----------------

Banner ads are rectangular text or image ads that take up a portion of the app screen. KivMob allows positioning
on the top or bottom of the page.

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

The banner ad position can be changed to the bottom of the screen by setting top_pos to False.

Interstitial Ads
-----------------

Interstitial ads full-screen ads that cover the entire app screen until dismissed by the app user.

.. code-block:: python

    from kivmob import KivMob, TestIds

    from kivy.app import App
    from kivy.uix.button import Button

    class InterstitialTest(App):
        """ Display an interstitial ad on button press.
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

Rewarded Video Ads
-------------------

Rewarded video ads can be watched by the user in exchange for in-app rewards. Callback
functionality can be handled with a class that implements the RewardedListenerInterface.

.. code-block:: python

    from kivmob import KivMob, TestIds

    from kivy.app import App
    from kivy.uix.button import Button

    class RewardedVideoTest(App):
        """ Display an interstitial ad on button press.
        """

        def build(self):
            self.ads = KivMob(TestIds.APP)
            self.ads.load_rewarded_ad(TestIds.REWARDED_VIDEO)
            self.ads.set_rewarded_ad_listener(RewardedListenerInterface())
            return Button(text='Show Rewarded Ad',
                          on_release=lambda a:self.ads.show_rewarded_ad())
                        
        def on_resume(self):
            self.ads.request_interstitial()

    if __name__ == "__main__":
        RewardedVideoTest().run()