# telegame
This library allows to create a bot that distribute your HTML5 based games. It is simple and convinient.

```
pip install telegame
```

## Features
* Add any number of games
* Game categories (e. g. Sport, Strategy)
* Inline search support
* 'Play with friends' button (share game to any chat)
* 'Random game' button

## Guide

### Adding games to the bot
This part may look tricky at the start, but actually it is not so hard. Bot expects ```dict```, where keys are short names 
that you have sent to BotFather and values are the Game objects defined as follows:

Key | Required | Description
--- | --- | ---
name | yes | Name of the game. Will be used in search and in game list
category | no | Category. If set, the game will be shown in the list of the specified category
url | no | Url of the game. If not set, bot will use following url: base_url + '/' + game_short_name

Some examples:
```
'hockey': {'name': 'Cool Hockey', 'category': 'Sports'}
'go_game': {'name': 'Go'}
'lumberjack': {'name': 'Lumberjack', 'url': 'https://tbot.xyz/lumber/', 'category': 'Action'}
```

### Managing categories
If you set category for each (or some) of your games, it is a good idea to make list of your games grouped by categories. 
Telegame can do that for you: just add ```bot.enable_category_button()``` to your bot configuration.

### Other features
If you did not specify url for each game, you should add base url. 
The url of the game will be a concatenation of base_url and game_short_name. 
As example, if the base URL is ```https://mycoolgamez.com``` and game short name is ```hockey```, 
the bot will open ```https://mycoolgamez.com/hockey``` for your game.
You can set base URL as following: ```bot.set_base_url(base_url)```

Bot can send random game to the user. Type ```bot.enable_random_game_button()```. This will add 'Random game' button to the main menu.  
To add share button, type ```bot.enable_play_with_friends_button()```.

To customize greeting message (first message from the bot that user will see), use ```bot.set_greeting_message(greeting_message)```.
Default message is "Hello my friend! Would you like to play some games?"

### Starting bot
When you configured your bot, just type ```bot.start()``` to start it. Note that this is a blocking method that runs endless loop.


## Example
```python
import telegame

token = 'SOME_LONG_TOKEN'
games = {
    'checkers': {'name': 'Checkers', 'category': 'Strategic games'},
    'chess': {'name': 'Chess', 'category': 'Strategic games'},
    'go_game': {'name': 'Go', 'category': 'Strategic games'},
    'snakes_and_ladders': {'name': 'Snakes and Ladders', 'category': 'Games with dice'},
    'risk': {'name': 'Risk', 'category': 'Games with dice'}
}
base_url = 'https://destiner.github.io/FlatBoard'
greeting_message = 'Hello my friend! Would you like to play some games?'

bot = telegame.Bot(token)
bot \
    .set_games(games) \
    .set_base_url(base_url) \
    .enable_category_button() \
    .enable_random_game_button() \
    .enable_play_with_friends_button() \
    .set_greeting_message(greeting_message) \
    .start()

```

