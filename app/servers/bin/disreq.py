import os
import requests

def message_find(mes,guild_id,temple_id,profile):
    token=os.environ["TOKEN"]
    limit=os.environ["USER_LIMIT"]

    headers = {
    	'Authorization': f'Bot {token}',
		'Content-Type': 'application/x-www-form-urlencoded',
	}
    response = requests.get(f'https://discordapp.com/api/guilds/{guild_id}/channels', headers=headers)

    if mes.find('#member')>=0:
        res = requests.get(f'https://discordapp.com/api/guilds/{guild_id}/members?limit={limit}', headers=headers)
        for rs in res.json():
            if mes.find(f'@{rs["user"]["username"]}#member')>=0:
                mes=mes.replace(f'@{rs["user"]["username"]}#member',f'<@{rs["user"]["id"]}>')

    if mes.find('#role')>=0:
        res = requests.get(f'https://discordapp.com/api/guilds/{guild_id}/roles', headers=headers)

        for rs in res.json():
            if mes.find(f'@{rs["name"]}#role')>=0:
                mes=mes.replace(f'@{rs["name"]}#role',f'<@&{rs["id"]}>')

    response = requests.get(f'https://discordapp.com/api/guilds/{guild_id}/channels', headers=headers)
    print(response)
    if mes.find('/')==0:
        r = response.json()
        for res in r:
            if res["type"]==0:
                print(f"{res['name']} {res['type']} {res['id']}")
                if mes.find(f'/{res["name"]}')==0:
                    mes=mes.lstrip(f'/{res["name"]}')
                    data = {"content":f'{profile.display_name}\n「 {mes} 」'}
                    ress=requests.post(f'https://discordapp.com/api/channels/{res["id"]}/messages', headers=headers, data=data)
                    print(ress)
                    return "dmc"
        ress=requests.post(f'https://discordapp.com/api/channels/{res["id"]}/messages', headers=headers, data=data)
    else:
        data = {"content":f'{profile.display_name}\n「 {mes} 」'}
        response = requests.post(f'https://discordapp.com/api/channels/{temple_id}/messages', headers=headers, data=data)  

def img_message(image):
    headers = {
        'Authorization': f"Bearer "+os.environ["GYAZO_TOKEN"]
    }
    files = {
        'imagedata': image
    }
    r=requests.request('post', "https://upload.gyazo.com/api/upload", headers=headers, files=files) 
    res=r.json()
    return f"https://i.gyazo.com/{res['image_id']}.{res['type']}"

def download(message_content):

	with open(".\movies\a.mp4", 'wb') as fd:
		for chunk in message_content.iter_content():
			fd.write(chunk)