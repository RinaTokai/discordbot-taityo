import requests,json
import os
import random

from cogs.bin.daylimit import PushLimit


def day_signal(name_list:list,text:str):
    
    for name in name_list:
        print(name)
        limit=PushLimit(name=name)
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
                残り送信上限が{limit.templelimit()}以上の場合、<#{os.environ[f"{name}_TEMPLE_ID"]}>以外のメッセージも送信されます。(閲覧注意チャンネルは除く。)
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

def angry_signal(limit:PushLimit,text:str,server_name:str):
    angry_text = os.environ.get("ANGRY_TEXT")
    if angry_text == None:
        text+="push上限やぞ！！！！！！！！！！！！！！いい加減にしたらどうだVAVA！！！"
    else:
        angry_list=angry_text.split(",")
        text+=random.choice(angry_list)

    embed=[
            {
                'description': f"""
                一か月分のプッシュ上限                  {limit.pushlimit()}件\n
                今月分のプッシュ数                          {limit.aftertotal()}件\n
                本日分のプッシュ上限                      {limit.onedaypush()}\n
                本日のプッシュ数                               {limit.afterpush()}\n
                1送信につき消費するプッシュ数   {limit.consumption()}
                """,
                'color': 15146762,
                'image': {
                    'url': 'https://1.bp.blogspot.com/-k7FaT97oySE/WKFi-oaehjI/AAAAAAABBrQ/-Kb-SuhCJHUqqZwCA37rv7I9Fs0KIDxVACLcB/s800/face_angry_man4.png'
                }
            }
    ]
    content = {
            'username': '怒りのLINE連携',
            'avatar_url': 'https://1.bp.blogspot.com/-k7FaT97oySE/WKFi-oaehjI/AAAAAAABBrQ/-Kb-SuhCJHUqqZwCA37rv7I9Fs0KIDxVACLcB/s800/face_angry_man4.png',
            'content': text,
            'embeds': embed
    }
    headers = {'Content-Type': 'application/json'}
    requests.post(os.environ.get(f"{server_name}_WEBHOOK"),json.dumps(content), headers=headers) 