import json
import time
import random

from telegame import core


class Bot:
    actions = {'category': 'Categories', 'random_game': 'Random Game', 'play_with_friends': 'Play with friends'}

    def __init__(self, token):
        self.token = token
        self.last_update_id = 0
        self.buttons = {}
        self.messages = {}
        self.games = None
        self.base_url = ''

    def set_games(self, games):
        """
        Sets games
        :param games: JSON-like object
        :return: Bot object
        """
        self.games = games
        return self

    def set_base_url(self, base_url):
        """
        Sets base url for game location. Bot uses it if url was not specified for each game.
        :param games: URL string
        :return: Bot object
        """
        self.base_url = base_url
        return self

    def enable_category_button(self):
        """
        Shows category button in the main menu
        :return: Bot object
        """
        self.buttons['category'] = True
        return self

    def enable_random_game_button(self):
        """
        Shows random_game button in the main menu
        :return: Bot object
        """
        self.buttons['random_game'] = True
        return self

    def enable_play_with_friends_button(self):
        """
        Shows play_with_friends button in the main menu
        :return: Bot object
        """
        self.buttons['play_with_friends'] = True
        return self

    def set_greeting_message(self, greeting_message):
        """
        Sets greeting message. Bot will use this message each time user sends '/start' command.
        :return: Bot object
        """
        self.messages['greeting'] = greeting_message
        return self

    def start(self):
        """
        Starts the bot.
        """
        self._set_categories()
        self._start_polling()

    def _set_categories(self):
        self.categories = {}
        for game in self.games:
            game_info = self.games[game]
            if 'category' not in game_info:
                continue
            category_name = game_info['category']
            if category_name not in self.categories:
                self.categories[category_name] = []
            category = self.categories[category_name]
            category.append(game)

    def _start_polling(self):
        while True:
            offset = self.last_update_id + 1
            response = core.get_updates(self.token, offset)
            if response.status != 200:
                continue
            data_str = response.data.decode('utf-8')
            data_json = json.loads(data_str)
            if not data_json['ok']:
                continue
            updates = data_json['result']
            self._handle_updates(updates)
            time.sleep(0.1)

    def _handle_updates(self, updates):
        if len(updates) == 0:
            return
        for update in updates:
            if 'message' not in update:
                self._handle_non_message_update(update)
                continue
            message = update['message']
            chat_id = update['message']['chat']['id']
            if 'text' not in message:
                continue
            text = update['message']['text']
            self._handle_text_update(chat_id, text)
        self.last_update_id = updates[-1]['update_id']

    def _handle_non_message_update(self, update):
        if 'inline_query' in update:
            inline_query = update['inline_query']
            inline_query_id = inline_query['id']
            query_text = inline_query['query']
            games = self._find_games(query_text)
            self._show_found_games(inline_query_id, games)
            return
        if 'callback_query' in update:
            callback_query = update['callback_query']
            callback_query_id = callback_query['id']
            game_short_name = callback_query['game_short_name']
            url = self._get_url_by_short_name(game_short_name)
            core.answer_callback_query(self.token, callback_query_id, url)
            return

    def _handle_text_update(self, chat_id, text):
        if text == '/start':
            self._greet(chat_id)
        if text == 'Random Game':
            game_short_name = self._random_game()
            core.send_game(self.token, chat_id, game_short_name)
            return
        if text == 'Categories':
            self._send_categories(chat_id)
            return
        if text == 'Play with friends':
            self._send_play_friends_message(chat_id)
        if text == 'Back':
            self._greet(chat_id)
            return
        if self._is_category(text):
            self._send_games(chat_id, text)
            return
        if self._is_game(text):
            game_short_name = self._get_game_by_name(text)
            core.send_game(self.token, chat_id, game_short_name)

    def _greet(self, chat_id):
        greet_text = 'Hello my friend! Would you like to play some games?'
        if 'greeting' in self.messages:
            greet_text = self.messages['greeting']
        reply_markup = self._get_main_reply_markup()
        core.send_message(self.token, chat_id, greet_text, reply_markup=reply_markup)

    def _random_game(self):
        game_list = list(self.games.keys())
        return random.choice(game_list)

    def _find_games(self, query):
        query = query.lower()
        results = []
        for game in self.games:
            game_name = self.games[game]['name'].lower()
            if game_name.startswith(query):
                results.append(game)
        return results

    def _show_found_games(self, inline_query_id, games):
        games_json = ''
        for game in games:
            game_json = '{{"type": "{0}", "id": "{1}", "game_short_name": "{1}"}}'.format('game', game)
            games_json += game_json + ','
        if len(games) > 0:
            games_json = games_json[:-1]
        games_json = '[' + games_json + ']'
        core.answer_inline_query(self.token, inline_query_id, games_json)

    def _send_categories(self, chat_id):
        text = 'Select category, please.'
        reply_markup = self._get_category_reply_markup()
        core.send_message(self.token, chat_id, text, reply_markup)

    def _send_games(self, chat_id, category):
        text = 'Select game, please.'
        reply_markup = self._get_games_reply_markup(category)
        core.send_message(self.token, chat_id, text, reply_markup)

    def _send_play_friends_message(self, chat_id):
        text = 'Just mention me in any chat and get ready to play!'
        reply_markup = self._get_share_bot_reply_markup()
        core.send_message(self.token, chat_id, text, reply_markup=reply_markup)

    def _notify_error(self, chat_id):
        error_text = 'Sorry, I can not understand you. Please pick on of the options below.'
        reply_markup = self._get_main_reply_markup()
        core.send_message(self.token, chat_id, error_text, reply_markup=reply_markup)

    def _get_url_by_short_name(self, game_short_name):
        game_info = self.games[game_short_name]
        if 'url' in game_info:
            return game_info['url']
        if self.base_url is not None:
            return self.base_url + '/' + game_short_name
        return ''

    def _get_main_reply_markup(self):
        actions_json = ''
        # Add button for each action
        for button in self.buttons:
            # If button was enabled
            if self.buttons[button]:
                action_title = Bot.actions[button]
                action_json = '["{0}"]'.format(action_title)
                actions_json += action_json + ','
        # Removes last comma if any (otherwise leaves string empty)
        actions_json = actions_json[:-1]
        actions_json = '[' + actions_json + ']'
        reply_markup = '{{"keyboard": {0}}}'.format(actions_json)
        return reply_markup

    def _get_category_reply_markup(self):
        categories_json = ''
        # Add button for each category
        for category in self.categories:
            category_json = '["{0}"]'.format(category)
            categories_json += category_json + ','
        # Add back button
        categories_json += '["Back"]'
        categories_json = '[' + categories_json + ']'
        reply_markup = '{{"keyboard": {0}}}'.format(categories_json)
        return reply_markup

    def _get_games_reply_markup(self, category):
        games = self.categories[category]
        games_json = ''
        # Add button for each category
        for game in games:
            game_name = self.games[game]['name']
            game_json = '["{0}"]'.format(game_name)
            games_json += game_json + ','
        # Add back button
        games_json += '["Back"]'
        games_json = '[' + games_json + ']'
        reply_markup = '{{"keyboard": {0}}}'.format(games_json)
        return reply_markup

    @staticmethod
    def _get_share_bot_reply_markup():
        share_bot_button_json = '{"text": "Play with friends", "switch_inline_query": ""}'
        row_json = '[' + share_bot_button_json + ']'
        keyboard_json = '[' + row_json + ']'
        reply_markup = '{{"inline_keyboard": {0}}}'.format(keyboard_json)
        return reply_markup

    def _is_category(self, text):
        for category in self.categories:
            if text == category:
                return True
        return False

    def _is_game(self, text):
        for game in self.games:
            game_name = self.games[game]['name']
            if text == game_name:
                return True
        return False

    def _get_game_by_name(self, name):
        for game in self.games:
            game_name = self.games[game]['name']
            if name == game_name:
                return game
        return None
