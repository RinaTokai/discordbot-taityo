from flask import Flask,request,abort
from threading import Thread

import os
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

from servers.five_hour import app2
from servers.bin.disreq import message_find,img_message,download

app = Flask(__name__)

app.register_blueprint(app2)

# 環境変数SERVER_NAMEをカンマ区切りでlistに格納。
servers_name=os.environ['SERVER_NAME']
server_list=servers_name.split(",")

# SERVER_NAMEの先頭を代入。
server_name=server_list[0]

# LINEBotのアクセストークンとチャネルシークレットを格納
line_bot_api = LineBotApi(os.environ[f'{server_name}_ACCESS_TOKEN'])
handler = WebhookHandler(os.environ[f'{server_name}_CHANNEL_SECRET'])

# POSTリクエストが来た場合(エンドポイントはserver_list[0])
@app.route(f"/{server_name}", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

# LINEからテキストメッセージ、画像、動画、スタンプが送信された場合
@handler.add(MessageEvent, message=[TextMessage,ImageMessage,VideoMessage,StickerMessage])
def handle_message(event:MessageEvent):

    # メッセージタイプを検出
    event_type=event.message.type

    # LINEのプロフィールを取得(友達登録している場合)
    try:
        profile = line_bot_api.get_profile(event.source.user_id)
    # ない場合、グループから取得(グループに所属しているが、友達登録していない場合)
    except LineBotApiError:
        profile = line_bot_api.get_group_member_profile(os.environ[f"{server_name}_GROUP_ID"],event.source.user_id)

    if event_type=='text':
        message_text=event.message.text
    if event_type=='sticker':
        message_text=f"https://stickershop.line-scdn.net/stickershop/v1/sticker/{event.message.sticker_id}/iPhone/sticker_key@2x.png"
    if event_type=='image':
        # message_idから画像のバイナリデータを取得
        message_content = line_bot_api.get_message_content(event.message.id).content

        # Gyazoにアップロードし、URLも取得
        message_text=img_message(message_content)
    if event_type=='video':
        # message_idから動画のデータをクラスごと取得
        message_content = line_bot_api.get_message_content(event.message.id)

        # ローカルにmp4として保存
        download(message_content)

        # subprocessでupload_video.pyを実行、動画がYouTubeに限定公開でアップロードされる
        youtube_id = subprocess.run(['python', 'upload_video.py', f'--title="{profile.display_name}の動画"','--description="LINEからの動画"'], capture_output=True)
        # 出力されたidを当てはめ、YouTubeの限定公開リンクを作成
        message_text = f"https://youtu.be/{youtube_id.stdout.decode()}"

    # LINEのメッセージをDiscordにアップロード
    message_find(
        message_text,
        os.environ[f"{server_name}_GUILD_ID"],
        os.environ[f"{server_name}_TEMPLE_ID"],
        profile
    )

if __name__ == "__main__":
    app.run("0.0.0.0", port=8080)

def run():
  app.run("0.0.0.0", port=8080, threaded=True)

def keep_alive():
  t = Thread(target=run)
  t.start()