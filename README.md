# Pluie
Discord bot playing rainwave.cc music

## Installation

You'll need : 

* [discord.py](https://discordpy.readthedocs.io/en/stable/intro.html#installing) with voice support
* [requests](https://pypi.org/project/requests/)

You also need to get a [rainwave.cc](https://rainwave.cc/) api key and user id. You just have to register/login in the site, and get it [here](https://rainwave.cc/keys/)

You have to edit the `config.json.sample` file, fill the fields, and rename it `config.sample`

You are now ready to go.

## How to use

* `!play [station_id]` play the channel you want. 

| Music Type | Staton Id |
|------------|-----------|
| Game       |     1     |
| OcRemix    |     2     |
| Covers     |     3     |
| Chiptune   |     4     |
| All        |     5     |

* `!info` get info on the current music playing
* `!stop` stop the music
