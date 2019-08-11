Architecture
====================

.. image:: kivmob-arch.png
    :align: center

KivMob leverages the bridge design pattern to handle platform-specific instantiation. This allows
developers to import the module without breaking applications on non-mobile platforms. The Android and iOS
implementations should both implement the AdMobBridge interface. 



