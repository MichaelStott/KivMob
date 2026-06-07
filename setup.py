import sys
from pathlib import Path

from setuptools import setup

sys.path.insert(0, str(Path(__file__).resolve().parent / "scripts"))
from version import get_version

setup(
    name="kivmob",
    version=get_version("kivmob"),
    description="Provides AdMob support for Kivy.",
    url="http://github.com/MichaelStott/KivMob",
    author="Michael Stott",
    license="MIT",
    py_modules=["kivmob"],
    install_requires=["kivy"],
    zip_safe=False,
)
