import discord
from discord.ext import tasks
import os
import datetime
import traceback
import requests,json

from cogs.bin.daylimit import PushLimit

class DBot(discord.AutoShardedBot):
    def __init__(self, token, intents):
        self.token = token
        super().__init__(intents = intents)
        self.load_cogs()

    async def on_ready(self):
        print('起動しました')
        await self.change_presence(activity=discord.Game(name="senran kagura"))
        self.signal.start()

    def load_cogs(self):
        for file in os.listdir("./cogs"): 
            if file.endswith(".py"): 
                cog = file[:-3] 
                self.load_extension(f"cogs.{cog}")
                print(cog + "をロードしました")

    @tasks.loop(seconds=60)
    async def signal(self):
        now = datetime.datetime.now().strftime('%H:%M')
        if now == '00:00':
            print(now)
            servers_name=os.environ['SERVER_NAME']
            server_list=servers_name.split(",")

            for name in server_list:
                print(name)
                limit=PushLimit(name=name)
                text="@here 日付が変更されました。本日の上限をお伝えいたします。"
                embed=[
                    {
                        'description': f"""
                        日付        {limit.today()}日\n
                        月末日          {limit.endmonth()}日\n
                        実行時刻            {limit.today_time()}\n
                        一か月分のプッシュ上限                  {limit.pushlimit()}件\n
                        今月分のプッシュ数                          {limit.totalpush()}件\n
                        本日分のプッシュ上限                      {limit.onedaypush()}\n
                        本日のプッシュ数                               {limit.todaypush()}\n
                        botの友達数（グループの人数）   {limit.friend()}\n
                        1送信につき消費するプッシュ数   {limit.consumption()}\n
                        ***残り送信上限                                           {limit.daylimit()}***\n
                        残り送信上限が{limit.templelimit()}以上の場合、テンプレチャンネル以外のメッセージも送信されます。(閲覧注意チャンネルは除く。)
                        """,
                        'color': 15146762,
                        'image': {
                            'url': 'https://1.bp.blogspot.com/-k5TkNAwyxTE/XwP7r7zmMeI/AAAAAAABZ6M/g0eGM0WVPWgG3pT0bFleMisy_DzenRkZQCNcBGAsYHQ/s1600/smartphone_earphone_man.png'
                        }
                    }
                ]
                content = {
                    'username': '時報するLINE連携',
                    'avatar_url': 'https://1.bp.blogspot.com/-k5TkNAwyxTE/XwP7r7zmMeI/AAAAAAABZ6M/g0eGM0WVPWgG3pT0bFleMisy_DzenRkZQCNcBGAsYHQ/s1600/smartphone_earphone_man.png',
                    'content': text,
                    'embeds': embed
                }
                headers = {'Content-Type': 'application/json'}
                requests.post(os.environ.get(f"{name}_WEBHOOK"),json.dumps(content), headers=headers)

    # 起動用の補助関数です
    def run(self):
        try:
            self.loop.run_until_complete(self.start(self.token))
        except discord.LoginFailure:
            print("Discord Tokenが不正です")
        except KeyboardInterrupt:
            print("終了します")
            self.loop.run_until_complete(self.logout())
        except discord.HTTPException as e:
            traceback.print_exc()
            if e.status == 429:
                main_content = {'content': '<@&855749835096195124> DiscordBot 429エラー\n直ちにDockerファイルを再起動してください。'}
                headers      = {'Content-Type': 'application/json'}

                response     = requests.post(os.environ["WEBHOOK"], json.dumps(main_content), headers=headers)
                
        except:
            traceback.print_exc()