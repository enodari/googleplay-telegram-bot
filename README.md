Google Play Telegram Bot
============
A Telegram Bot that let you download .apk from Google Play

## Credits
This project uses a custom and updated version of the [Google Play Unofficial Python API](https://github.com/egirault/googleplay-api).

## Requirements
* [Python 2.7](http://www.python.org)
* [Protocol Buffers](http://code.google.com/p/protobuf/)
* [Requests](http://docs.python-requests.org/)
* [Telepot](https://github.com/nickoala/telepot)

## Configuration
You must edit `config.py` before running the bot.

You need to provide:
* a valid [Telegram Bot](https://core.telegram.org/bots) authentication token
* your phone's `androidID`
* your Google Play Store login and password, or a valid subAuthToken

To get your `androidID`, use `*#*#8255#*#*` on your phone to start *Gtalk Monitor*. The hex string listed after `aid` is your `androidID`.

## Quick Start

When the configuration is complete you can install the dependencies with:

    $ pip install protobuf requests telepot

And run the bot with:

    $ python bot.py

## Usage
With the bot running you can send him a text with the **package name** (i.e. _*org.telegram.messenger*_) and it will respond with the requested .apk file.

I only tested with free apps, but I guess it should work as well with non-free as soon as you have enough money on your Google account.

## License
This project is licensed under the terms of the **MIT** license.
