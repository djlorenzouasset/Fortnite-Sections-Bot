# [DEPRECATED] Fortnite Shop Sections Bot

> ⚠️ This repository is deprecated since Epic Games doesn't update the sections endpoint anymore.

A bot that automatically post <b>shop sections</b> in your twitter account.


# How to use:
- Make sure you have [Python](https://www.python.org/downloads/) installed on your computer (>= 3.9).
- Open `build.bat` for install all requirements that the program need to run.
- Open the file `settings.json` and set your data for run the bot [see guide here](https://github.com/djlorenzouasset/Fortnite-Sections-Bot#Set-Configuration). Remember that this program work with Epic Games API, so you need an account for create device auths. If you dont know ho do that, just use [DeviceAuthGenerator](https://github.com/xMistt/DeviceAuthGenerator) made by [xMistt](https://github.com/xMistt).
- Open `start.bat` and make sure that the program dont generate any error.


# Set Configuration:

- `language`: The language of the sections. Default to en.
+ `seconds_per_task`: Seconds for the task, you can decide how often the bot have to check new sections. Default to 50, recommended is >= 50.
- `auth`: The data you get from [DeviceAuthGenerator](https://github.com/xMistt/DeviceAuthGenerator)
+ `twitter`: The data you get from [Twitter Developer](https://developer.twitter.com/en). You can disactivate it by changing `enabled` to `false` or `true` for enable it.
- `sections`: Here you have to set the post text. You can set an image for the tweet with replacing `image` with the path of the image (local file). You can choose if show sections that have only one tab like `(x1)` or not with the `show_if_one` value. If enabled the bot will show sections like this `Daily (x1)`. If not enabled the section will shown like this `Daily`. The `title` and `footer` are customizables as you want.


## Example
```jsonc
{
    "language": "en",
    "seconds_per_task": 50,
    "auth": {
        "device_id": "your_device_id",
        "account_id": "your_account_id",
        "secret": "your_secret_token"
    },
    "twitter": {
        "enabled": false,
        "apiKey": "twitter_api_key",
        "apiSecret": "twitter_key_secret",
        "accessToken": "twitter_access_token",
        "accessTokenSecret": "twitter_token_secret"
    },
    "sections": {
        "image": false,
        "show_if_one": true,
        "title": "New #Fortnite shop sections:",
        "footer": ""
    }
}
```

## Support

If you need support you can contact me on [Discord](https://discord.com/users/584349337497108480)
