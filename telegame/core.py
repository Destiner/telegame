import urllib3

urllib3.disable_warnings()
http = urllib3.PoolManager()

def get_updates(token, offset):
    method = 'getUpdates'
    params = 'offset={0}'.format(offset)
    update_url = get_method_url(token, method, params)
    response = http.request('GET', update_url)
    return response

def send_message(token, chat_id, text, reply_markup=None):
    method = 'sendMessage'
    params = 'chat_id={0}&text={1}'.format(chat_id, text)
    if reply_markup:
        params += '&reply_markup={0}'.format(reply_markup)
    send_url = get_method_url(token, method, params)
    http.request('POST', send_url)

def send_game(token, chat_id, game_short_name):
    method = 'sendGame'
    params = 'chat_id={0}&game_short_name={1}'.format(chat_id, game_short_name)
    send_url = get_method_url(token, method, params)
    http.request('POST', send_url)

def answer_callback_query(token, callback_query_id, url):
    method = 'answerCallbackQuery'
    params = 'callback_query_id={0}&url={1}'.format(callback_query_id, url)
    answer_url = get_method_url(token, method, params)
    http.request('POST', answer_url)

def answer_inline_query(token, inline_query_id, results):
    method = 'answerInlineQuery'
    params = 'inline_query_id={0}&results={1}'.format(inline_query_id, results)
    answer_url = get_method_url(token, method, params)
    http.request('POST', answer_url)

def get_method_url(token, method, params):
    api_url = 'https://api.telegram.org/bot{0}/{1}?{2}'
    answer_url = api_url.format(token, method, params)
    return answer_url
