import os
import requests

from linebot.models import Profile,Content

# DiscordAPIを直接叩いてLINEのメッセージを変換
"""
mes:str
    テキストメッセージ
guild_id
    DiscordのサーバーID
temple_id
    送信する規定のテキストチャンネルのID
profile
    LINEのprofileデータ
"""
def message_find(
        mes:str,
        guild_id:int,
        temple_id:int,
        profile:Profile
    ):

    # DiscordBotのトークンとリクエスト上限
    token=os.environ["TOKEN"]
    limit=os.environ["USER_LIMIT"]

    headers = {
    	'Authorization': f'Bot {token}',
		'Content-Type': 'application/x-www-form-urlencoded',
	}

    # テキストメッセージに「#member」が含まれている場合
    if mes.find('#member')>=0:
        
        # Discordサーバーのメンバー一覧を定めた上限まで取得
        res = requests.get(f'https://discordapp.com/api/guilds/{guild_id}/members?limit={limit}', headers=headers)

        # for文でメンバーを一人一人参照
        for rs in res.json():
            # 「@ユーザー名#member」が含まれている場合、メンションと判断
            if mes.find(f'@{rs["user"]["username"]}#member')>=0:
                # Discordでのメンションの形式にテキストを変換
                mes=mes.replace(f'@{rs["user"]["username"]}#member',f'<@{rs["user"]["id"]}>')

    # テキストメッセージに「#role」が含まれている場合
    if mes.find('#role')>=0:

        # Discordサーバーのロール一覧を取得
        res = requests.get(f'https://discordapp.com/api/guilds/{guild_id}/roles', headers=headers)

        # for文でロールを一つ一つ参照
        for rs in res.json():
            # 「@ロール#role」が含まれている場合、ロールメンションと判断
            if mes.find(f'@{rs["name"]}#role')>=0:
                # Discordでのメンションの形式にテキストを変換
                mes=mes.replace(f'@{rs["name"]}#role',f'<@&{rs["id"]}>')

    # テキストメッセージの最初が「/」の場合
    if mes.find('/')==0:

        # Discordチャンネル一覧を取得
        response = requests.get(f'https://discordapp.com/api/guilds/{guild_id}/channels', headers=headers)

        # 取得したデータをjsonで展開
        r = response.json()

        # for文でチャンネルを一つ一つ参照
        for res in r:

            # type=0(テキストチャンネル)の場合
            if res["type"]==0:
                print(f"{res['name']} {res['type']} {res['id']}")

                # テキストメッセージの最初に「/チャンネル名」と書かれている場合
                if mes.find(f'/{res["name"]}')==0:

                    # 「/チャンネル名」をテキストから削除
                    mes=mes.lstrip(f'/{res["name"]}')
                    # 「LINEのユーザー名 「テキストメッセージ」」の形式でDiscordに送信
                    data = {"content":f'{profile.display_name}\n「 {mes} 」'}
                    ress=requests.post(f'https://discordapp.com/api/channels/{res["id"]}/messages', headers=headers, data=data)
                    print(ress)
                    return "dmc"

        # 該当するチャンネルがなかった場合、そのまま送信
        data = {"content":f'{profile.display_name}\n「 {mes} 」'}
        ress=requests.post(f'https://discordapp.com/api/channels/{res["id"]}/messages', headers=headers, data=data)
    else:
        data = {"content":f'{profile.display_name}\n「 {mes} 」'}
        response = requests.post(f'https://discordapp.com/api/channels/{temple_id}/messages', headers=headers, data=data)  

# 画像が送信された場合、Gyazoにアップロード
def img_message(image:bytes):
    headers = {
        'Authorization': f"Bearer "+os.environ["GYAZO_TOKEN"]
    }
    files = {
        'imagedata': image
    }
    # Gyazoにヘッダとファイルを送信
    r=requests.request('post', "https://upload.gyazo.com/api/upload", headers=headers, files=files) 
    
    # 受け取ったjsonファイルを展開し、idと拡張子でURLを生成
    res=r.json()
    return f"https://i.gyazo.com/{res['image_id']}.{res['type']}"

# 動画が送信された場合、動画を保存
def download(message_content:Content):

    # mp4で保存
	with open(".\movies\a.mp4", 'wb') as fd:
		for chunk in message_content.iter_content():
			fd.write(chunk)