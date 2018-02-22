import sys
import os
import errno
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
    SourceUser,
    ButtonsTemplate,
    MessageTemplateAction, URITemplateAction,
    TemplateSendMessage
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
    # declare functions to use in dict:
    def get_profile():
        if isinstance(event.source, SourceUser):
            profile = line_bot_api.get_profile(event.source.user_id)
            # log in terminal:
            app.logger.info('Display name: ' + str(profile.display_name) + 
                            '\nUser id: ' + str(profile.user_id) +
                            '\nPicture: ' + str(profile.picture_url) +
                            '\nStatus: ' + str(profile.status_message))
            # end of log
            # reply msg:
            line_bot_api.reply_message(
                event.reply_token,
                [
                    TextSendMessage(text='Your Display Name: ' + str(profile.display_name)),
                    TextSendMessage(text='Your Status msg: ' + str(profile.status_message))
                ]
            )
        else:
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text='Invalid user id'))
    def send_buttons():
        buttons_template = ButtonsTemplate(
            thumbnail_image_url='https://is4-ssl.mzstatic.com/image/thumb/Purple111/v4/59/bc/39/59bc3937-cf92-451d-50ce-bb33b95ebe85/source/1200x630bb.jpg',
            image_aspect_ratio='square',
            image_size='contain',
            image_background_color='#F4429B',
            title='Test Menu',
            text='Please select',
            actions=[
                MessageTemplateAction(
                    label='Message',
                    text='Selected Message'
                ),
                URITemplateAction(
                    label='URI',
                    uri='https://www.google.com'
                )
            ]
        )
        template_message = TemplateSendMessage(
            alt_text='alt text for buttons',
            template=buttons_template
        )
        line_bot_api.reply_message(
            event.reply_token,
            template_message
        )

    def nBest_buttons():
        buttons_template = ButtonsTemplate(
            # thumbnail_image_url='https://is4-ssl.mzstatic.com/image/thumb/Purple111/v4/59/bc/39/59bc3937-cf92-451d-50ce-bb33b95ebe85/source/1200x630bb.jpg',
            # image_aspect_ratio='square',
            # image_size='contain',
            # image_background_color='#F4429B',
            title='What do you think?',
            text='คิดว่าน้องเบสเป็นคนยังไง?',
            actions=[
                MessageTemplateAction(
                    label='เคี่ยว',
                    text='ใช่เลยยย !!'
                ),
                MessageTemplateAction(
                    label='เจิดจรัสดั่งพระอาทิตย์',
                    text='เห็นด้วยที่สุด !!'
                ),
                MessageTemplateAction(
                    label='น่ารัก',
                    text='ไม่จริงอ่ะ !!'
                ),
            ]
        )
        template_message = TemplateSendMessage(
            alt_text='alt text for buttons',
            template=buttons_template
        )
        line_bot_api.reply_message(
            event.reply_token,
            template_message
        )

    # detect an user's sent message:
    text = event.message.text
    
    case = {
        'profile': get_profile,
        'button': send_buttons,
        'are you happy?': lambda: line_bot_api.reply_message(
            event.reply_token,
            [TextSendMessage(text = 'Yes Im very happy, and you?')]
        ),
        'best': nBest_buttons,
        'เบส': nBest_buttons,
        'pob': lambda: line_bot_api.reply_message(
            event.reply_token,
            [TextSendMessage(text = 'อุ๊ย คนนี้หล่อจุง <3')]
        ),
        'ภพ': lambda: line_bot_api.reply_message(
            event.reply_token,
            [TextSendMessage(text = 'คนดีๆแบบนี้ จะหาได้ที่ไหนอีก')]
        ),
    }

    if text in case:
        case[text]()
    else:
        line_bot_api.reply_message(
            event.reply_token,
            [TextSendMessage(text = 'See ya')]
        )
    
