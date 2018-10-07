from setuptools import setup

setup(name='kivmob',
      version='1.1',
      description='Provides AdMob support for Kivy.',
      url='http://github.com/MichaelStott/KivMob',
      author='Michael Stott',
      license='MIT',
      py_modules=['kivmob'],
      install_requires=[
          'kivy',
          'Click'
      ],
      zip_safe=False)
