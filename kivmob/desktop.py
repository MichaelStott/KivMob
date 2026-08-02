"""Desktop (no-op) AdMob bridge."""

from .bridge import AdMobBridge


class DesktopBridge(AdMobBridge):
    """No-op AdMob bridge for desktop (and Android when AdMob fails to load)."""

    pass
