import discord
import os
from typing import List

from cogs.bin.daylimit import PushLimit
from core.signal import day_signal,angry_signal

from linebot import (
    LineBotApi
)

from linebot.models import (
    TextSendMessage, ImageSendMessage, VideoSendMessage
)

from discord.ext import commands
from core.start import DBot

class mst_line(commands.Cog):
    def __init__(self, bot : DBot):
        self.bot = bot      

    # テストコマンド
    @commands.slash_command(description="LINEの利用状況を確認します")
    async def test_signal(self,ctx:discord.ApplicationContext):

        # 環境変数から所属しているサーバー名一覧を取得し、配列に格納
        servers_name=os.environ['SERVER_NAME']
        server_list=servers_name.split(",")
        for server_name in server_list:
            # コマンドを打ったサーバーと環境変数にあるサーバーが一致した場合、利用状況を送信
            if int(os.environ[f"{server_name}_GUILD_ID"])==int(ctx.guild.id):
                await ctx.respond("LINE連携の利用状況です。")
                day_signal([server_name],f"<@{ctx.author.id}>\nテストコマンド 現在の上限です")
                angry_signal(PushLimit(server_name),f"<@{ctx.author.id}>\n",server_name)
                

    # DiscordからLINEへ
    @commands.Cog.listener(name='on_message')
    async def on_message(self, message:discord.Message):

        # メッセージがbot、閲覧注意チャンネル、ピン止め、ボイスチャンネルの場合終了
        if (message.author.bot is True or
            message.channel.nsfw is True or
            message.type == discord.MessageType.pins_add or
            message.channel.type == discord.ChannelType.voice):
            return

        # FIVE_SECONDs,FIVE_HOUR
        # ACCESS_TOKEN,GUILD_ID,TEMPLE_ID (それぞれ最低限必要な環境変数)
        servers_name=os.environ['SERVER_NAME']
        server_list=servers_name.split(",")

        # LINEに送信するメッセージのリスト
        messagelist=[]

        # テキストメッセージ
        messagetext=f"{message.channel.name}にて、{message.author.name}"

        if message.type == discord.MessageType.new_member:
            messagetext=f"{message.author.name}が参加しました。"

        if message.type == discord.MessageType.premium_guild_subscription:
            messagetext=f"{message.author.name}がサーバーブーストしました。"
        
        if message.type == discord.MessageType.premium_guild_tier_1:
            messagetext=f"{message.author.name}がサーバーブーストし、レベル1になりました！！！！！！！！"
        
        if message.type == discord.MessageType.premium_guild_tier_2:
            messagetext=f"{message.author.name}がサーバーブーストし、レベル2になりました！！！！！！！！！"
        
        if message.type == discord.MessageType.premium_guild_tier_3:
            messagetext=f"{message.author.name}がサーバーブーストし、レベル3になりました！！！！！！！！！！！"

        # 送付ファイルがあった場合
        if message.attachments:
            # 画像か動画であるかをチェック
            messagelist,imgcnt,videocnt=file_checker(message.attachments)

            messagetext+="が、"

            # 送信された動画と画像の数を格納
            if imgcnt>0:
                messagetext+=f"画像を{imgcnt}枚、"

            if videocnt>0:
                messagetext+=f"動画を{videocnt}個"

            # 画像と動画以外のファイルがある場合、urlを直接書き込む
            if (imgcnt+videocnt)<len(message.attachments):
                for attachment in message.attachments:
                    messagetext+=f"\n{attachment.url} "

            messagetext+="送信しました。"

        # メッセージ本文を書き込む
        messagetext+=f"「 {message.clean_content} 」"

        # スタンプが送付されている場合
        if message.stickers:
            # 動くスタンプは送信不可のため終了
            if message.stickers[0].url.endswith(".json"):
                return
            # 画像として送信
            else:
                messagelist,imgcnt,videocnt=file_checker(message.stickers)
                messagelist.insert(0,TextSendMessage(text=f"{messagetext} スタンプ:{message.stickers[0].name}"))
        else:
            # テキストメッセージをlistの先頭に格納
            messagelist.insert(0,TextSendMessage(text=messagetext))

        
        for server_name in server_list:
            # メッセージが送られたサーバーを探す
            if int(os.environ[f"{server_name}_GUILD_ID"])==int(message.guild.id):
                # LINEBot側のステータスを取得
                limit=PushLimit(name=server_name)

                """
                LINE上限対策

                LINE側には1か月1000件のメッセージ送信条件があります。
                また、1回の送信につき、送信した人数ごとに送信件数が消費されます。
                例:友達数=10の場合
                1回に送信されるメッセージの数が10件なので、1か月の上限は
                1000/10=100件
                となります。

                これにより、

                1回に送信するメッセージ件数=友達数
                
                となります。

                1日の上限=メッセージ上限/月末日
                残りの上限=メッセージ送信数/本日の日付

                1日の上限>残りの上限
                当月分のメッセージの送信数+友達数>メッセージ上限
                本日分の送信上限が1日あたりの上限未満かつTEMPLE_IDからのメッセージではない場合

                いずれかの条件を満たした場合、LINEへメッセージは送信されません。

                =================================================================

                メッセージ上限(無料プラン)=1000
                LINE側の友達(グループ)数=10
                例:6月の場合
                6月の月末日=30

                1000/30=33.333333


                メッセージ送信数が1日の時点で10の場合
                10/1=10

                1日の上限>残りの上限
                33.333..>10

                条件が成立するので送信されます。


                メッセージ送信数が4日の時点で140の場合
                140/4=35

                1日の上限>残りの上限
                33.333..<35

                条件が成立しないので送信されません。


                友達数=11
                送信数=990の場合

                990+11>1000

                1000件を超えてしまうので送信されません。


                残り送信上限=3
                1日あたりの上限=4

                3<4

                テキストチャンネルのIDが環境変数のTEMPLE_IDと一致している場合は送信されますが、
                それ以外のチャンネルの場合送信されません。

                """
                if (limit.todaypush()>limit.onedaypush() or
                    limit.aftertotal()>limit.pushlimit() or
                    (limit.daylimit()<limit.templelimit() and 
                    int(message.channel.id)!=int(os.environ[f"{server_name}_TEMPLE_ID"]))):
                    return

                # 送信NGのチャンネル名の場合、終了
                ng_channel=os.environ.get(f"{server_name}_NG_CHANNEL").split(",")
                for ng in ng_channel:
                    if ng == message.channel.name:
                        return

                # メッセージを送信することにより、本日分の上限を超える場合
                if limit.afterpush()>limit.onedaypush():

                    # 警告メッセージを送信する
                    angry_signal(
                        limit,
                        f"<@{message.author.id}>\n",
                        server_name
                    )
                    
                name_tmp=str(server_name)
                line_bot_api = LineBotApi(os.environ[f"{name_tmp}_ACCESS_TOKEN"])
                # グループIDが存在する場合、グループに送信
                if os.environ.get(f"{name_tmp}_GROUP_ID")!=None:
                    return line_bot_api.push_message(to=os.environ[f"{name_tmp}_GROUP_ID"],messages=messagelist)
                # そうでない場合、友達全員に送信
                else:
                    return line_bot_api.broadcast(messagelist)
            
# ファイルの拡張子から画像か動画かを識別
def file_checker(attachments:List[discord.Attachment]):

    # 画像を識別
    image=[".jpg",".png",".JPG",".PNG",".jpeg",".gif",".GIF"]
    eventsdata=[]
    imgcnt=0
    videocnt=0
    for attachment in attachments:
        for file in image:
            iurl=str(attachment.url)
            if iurl.endswith(file):
                eventsdata.append(ImageSendMessage(
                    original_content_url=iurl,
                    preview_image_url=iurl))
                imgcnt+=1

    # 動画を識別
    video=[".mp4",".MP4",".MOV",".mov",".mpg",".avi",".wmv"]
    for attachment in attachments:
        for file in video:
            iurl=str(attachment.url)
            if iurl.endswith(file):
                eventsdata.append(VideoSendMessage(
                    original_content_url=iurl,
                    preview_image_url="https://cdn.discordapp.com/attachments/943046430711480402/987284460070404106/ohime.JPG"))
                videocnt+=1

    # print(eventsdata,flush=True)
   
    return eventsdata,imgcnt,videocnt


def voice_checker(attachments):
    voice=[".wav",".mp3",".flac",".aif",".m4a",".oga",".ogg"]
    eventsdata=[]
    cnt=0
    for attachment in attachments:
        for file in voice:
            iurl=str(attachment.url)
            if iurl.endswith(file):
                eventsdata.append({f"voice{cnt}": iurl})
                cnt+=1
   
    return eventsdata

def setup(bot:DBot):
    return bot.add_cog(mst_line(bot))