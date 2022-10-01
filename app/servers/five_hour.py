from flask import request, abort, Blueprint ,current_app
import subprocess

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError, LineBotApiError
)
from linebot.models import (
    MessageEvent, TextMessage, ImageMessage, VideoMessage, StickerMessage
)
import os

from servers.bin.disreq import message_find,img_message,download

app2 = Blueprint("app2",__name__)

servers_name=os.environ['SERVER_NAME']
server_list=servers_name.split(",")

server_name=server_list[1]

line_bot_api = LineBotApi(os.environ[f'{server_name}_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ[f'{server_name}_CHANNEL_SECRET'])

@app2.route(f"/{server_name}", methods=['POST'])
def callbacks():
	logger = current_app.logger
    # get X-Line-Signature header value
	signature = request.headers['X-Line-Signature']

    # get request body as text
	body = request.get_data(as_text=True)
	logger.info("Request body: " + body)
	#app2.logger.info("Request body: " + body)

    # handle webhook body
	try:
		handler.handle(body, signature)
	except InvalidSignatureError:
		print("Invalid signature. Please check your channel access token/channel secret.")
		abort(400)

	return 'OK'


@handler.add(MessageEvent, message=[TextMessage,ImageMessage,VideoMessage,StickerMessage])
def handle_message(event:MessageEvent):
    event_type=event.message.type
    try:
        profile = line_bot_api.get_profile(event.source.user_id)
    except LineBotApiError:
        profile = line_bot_api.get_group_member_profile(os.environ[f"{server_name}_GROUP_ID"],event.source.user_id)

    if event_type=='text':
        message_text=event.message.text
    if event_type=='sticker':
        message_text=f"https://stickershop.line-scdn.net/stickershop/v1/sticker/{event.message.sticker_id}/iPhone/sticker_key@2x.png"
    if event_type=='image':
        # message_idから画像のバイナリデータを取得
        message_content = line_bot_api.get_message_content(event.message.id).content
        message_text=img_message(message_content)
    if event_type=='video':
        message_content = line_bot_api.get_message_content(event.message.id)
        download(message_content)
        youtube_id = subprocess.run(['python', 'upload_video.py', f'--title="{profile.display_name}の動画"','--description="LINEからの動画"'], capture_output=True)
        message_text = f"https://youtu.be/{youtube_id.stdout.decode()}"
    message_find(
        message_text,
        os.environ[f"{server_name}_GUILD_ID"],
        os.environ[f"{server_name}_TEMPLE_ID"],
        profile
    )