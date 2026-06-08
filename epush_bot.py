import telebot
import os
from config import *
from flask import Flask, request
server = Flask(__name__)

import importdir
importdir.do("features", globals())

# Explicitly load operations sub-module (importdir doesn't recurse into subdirs)
from features.operations import *

from features.promotions import start_scheduler

@server.route('/'+ TOKEN, methods=['POST'])
def getMessage():
    request_object = request.stream.read().decode("utf-8")
    update_to_json = [telebot.types.Update.de_json(request_object)]
    bot.process_new_updates(update_to_json)
    return "got Message bro"

@server.route('/hook')
def webhook():
    url=URL
    bot.remove_webhook()
    bot.set_webhook(url + TOKEN)
    return f"Webhook set to {url}"

@server.route('/')
def thanks():
    url=URL
    return f"Thanks you've reach chukwudi bot {url}"


if DEBUG==True:
    bot.remove_webhook()
    start_scheduler()

    # Start Flask health check in background thread for Railway
    import threading
    port = int(os.environ.get('PORT', 5000))
    t = threading.Thread(target=server.run, kwargs={'host': '0.0.0.0', 'port': port}, daemon=True)
    t.start()

    while True:
        try:
            bot.polling()
        except Exception as e:
            print(f"Polling error: {e}")
            continue
else:
    if __name__ == "__main__":
        server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))