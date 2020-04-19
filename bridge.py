import abc


class AdMobBridge(abc.ABC):
    @abc.abstractmethod
    def __init__(self, app_id):
        pass

    @abc.abstractmethod
    def add_test_device(self, test_id):
        pass

    @abc.abstractmethod
    def is_interstitial_loaded(self):
        return False

    @abc.abstractmethod
    def new_banner(self, unit_id, top_pos=True):
        pass

    @abc.abstractmethod
    def new_interstitial(self, unit_id):
        pass

    @abc.abstractmethod
    def request_banner(self, options):
        pass

    @abc.abstractmethod
    def request_interstitial(self, options):
        pass

    @abc.abstractmethod
    def show_banner(self):
        pass

    @abc.abstractmethod
    def show_interstitial(self):
        pass

    @abc.abstractmethod
    def destroy_banner(self):
        pass

    @abc.abstractmethod
    def destroy_interstitial(self):
        pass

    @abc.abstractmethod
    def hide_banner(self):
        pass

    @abc.abstractmethod
    def set_rewarded_ad_listener(self, listener):
        pass

    @abc.abstractmethod
    def load_rewarded_ad(self, unit_id):
        pass

    @abc.abstractmethod
    def show_rewarded_ad(self):
        pass
