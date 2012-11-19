# ash
ash is **a sh**ll.

- You can control Android device from PC using keyboard and mouse.
- You can control PC from Android using Android device's touchscreen, Motion sensor, etc.
- You can control PC from other PC.

ash is a device control environment that makes **ash installed devices** able to **control each other**.

ash can be installed on any devices like _Android_ / _PC_ and control other devices ash installed using various user interfaces(CLI, GUI, or something else).

If your PCs and Android devices has installed ash for them, You can control them with one of them.

ash defines a simple language based on ash's simple syntax.
You can command ash to control other devices with that language from prompt.

Or, You can use convenient GUI control applications using ash.
It's just an _user interface_.

Anybody can make their interface for ash conveniently.
Or, You can make _application_ based on ash's language, too. Just use ash as device control facility.

ashdi and [AshFa](https://github.com/sjp38/AshFa)'s PC control feature is one good example for ash interface layer application.

Anybody can implement ash using any language, any platform, if and only if they support ash language syntax and basic operations properly.
This ash implementation is for linux. You can get an **ash for Android(AshFa)** from [Here](https://github.com/sjp38/AshFa).

AshFa just works, but, not complete as an ash. AshFa is just an example. You can make your ash for Android and publish it anywhere.

# News
 - ash 2.0 have announced from [Google HackFair, Korea](http://googlekoreablog.blogspot.kr/2012/11/google-hackfair_6.html) and released by 19th, November 2012(EST).

 - Next minor version update will be done by few months.

# License
GPL v3.
Anyone can use code of Ash everywhere. But, should follow limitation of GPL v3.(http://www.gnu.org/licenses/gpl-3.0.html)


# System requirements
Just works on _Ubuntu 12.04_ with _JRE_ and _Android SDK tools_.

May works well with little effort on other platforms. But, no guarantee.

# How to use
You should install _JRE_ and _Android SDK tools_. _Android SDK tools_ directory path should be exist in your PATH.

If you are expert,

`$ ./ash.py`

If you have _Galaxy Nexus_ and want to control it from PC, install [_AshFa_](https://github.com/sjp38/AshFa) to your _Galaxy Nexus_ and start it. then,

`$ ./ash.py init_di_maguro.ash`


# Version
2.0.0.0

2.0 is still *not stable*. But, better than 1.0

# Author
SeongJae Park (sj38.park@gmail.com)
