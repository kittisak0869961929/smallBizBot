import sys
import os
import errno
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage
)

app = Flask(__name__)
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)

if channel_secret is None:
    print('Specify LINE_CHANNEL_SECRET as an environment variable.')
    sys.exit(1)
if channel_access_token is None:
    print('Specify LINE_CHANNEL_ACCESS_TOKEN as an environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)

static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')

# for creating tmp dir for downloaded contents:
def make_static_tmp_dir():
    try:
        os.makedirs(static_tmp_path)
    except OSError as exc:
        if exc.errno == errno.EEXIST and os.path.isdir(static_tmp_path):
            pass
        else:
            print(exc.strerror)
            raise


@app.route('/')
def index():
    return '<h1 style="color:red">Pob\'s BOT</h1>'

@app.route('/send', methods = ['POST'])
def send():
    # get X-Line-Signature from header
    signature = request.headers['X-Line-Signature']

    # get request body as text and log it to shell
    body = request.get_data(as_text=True)
    app.logger.info('Request body: ' + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    text = event.message.text

    if text == 'pob' or text == 'metz':
        line_bot_api.reply_message(
            event.reply_token,
            [
                TextSendMessage(text='Whatsup, Im {} jaaa'.format(text.upper())),
                TextSendMessage(text='How can I help you?')
            ]
        )
