from bridge.bridge import AdMobBridge


class DesktopBridge(AdMobBridge):
    def __init__(self, app_id):
        pass

    def add_test_device(self, test_id):
        pass

    def is_interstitial_loaded(self):
        return False

    def new_banner(self, unit_id, top_pos=True):
        pass

    def new_interstitial(self, unit_id):
        pass

    def request_banner(self, options):
        pass

    def request_interstitial(self, options):
        pass

    def show_banner(self):
        pass

    def show_interstitial(self):
        pass

    def destroy_banner(self):
        pass

    def destroy_interstitial(self):
        pass

    def hide_banner(self):
        pass

    def set_rewarded_ad_listener(self, listener):
        pass

    def load_rewarded_ad(self, unit_id):
        pass

    def show_rewarded_ad(self):
        pass
