import datetime
import requests
import calendar
import os
import math

def linereq(url,token,jsonkey):

    return (requests.request(
		"get",
		url=url,
		headers={
            'Authorization': 'Bearer ' + token
		}
	)).json()[jsonkey]

class DayGet:
    def __init__(self,name:str):
        self.token=os.environ.get(f'{name}_ACCESS_TOKEN')
        self.group_id=os.environ.get(f"{name}_GROUP_ID")    #グループIDなしの場合、None
		
    # 0
    def totalpush(self):
        return linereq(
            "https://api.line.me/v2/bot/message/quota/consumption",
            self.token,
            "totalUsage"
            )
    
    # 1
    def friend(self):
        # グループIDなしの場合、友達数をカウント
        if self.group_id == None:
            if datetime.datetime.now().strftime('%H') == '00':
                url="https://api.line.me/v2/bot/insight/followers?date="+(datetime.date.today()+datetime.timedelta(days=-1)).strftime('%Y%m%d')
            else:
                url="https://api.line.me/v2/bot/insight/followers?date="+datetime.date.today().strftime('%Y%m%d')
            return linereq(
                url,
                self.token,
                "followers"
            )
        else:
            return linereq(
				"https://api.line.me/v2/bot/group/"+self.group_id+"/members/count",
				self.token,
				"count"
			)
    # 1000
    def pushlimit(self):
        return linereq(
            "https://api.line.me/v2/bot/message/quota",
            self.token,
            "value"
            )
    def today_time(self):
        return datetime.datetime.now()
    def today(self):
        return datetime.datetime.now().day
    def endmonth(self):
        return calendar.monthrange(datetime.datetime.now().year, datetime.datetime.now().month)[1]

class Limit(DayGet):
    def __init__(self,name:str):
        super().__init__(name)
    
    # 1000/30=33.3333
    def onedaypush(self):
        return super().pushlimit()/super().endmonth()
    
    # 0/1
    def todaypush(self):
        return super().totalpush()/super().today()
    
    # (0+1)/1
    def afterpush(self):
        return (super().totalpush()+super().friend())/super().today()

    # 0+1
    def aftertotal(self):
        return super().totalpush()+super().friend()

class Push(Limit):
	def __init__(self,name:str):
		super().__init__(name)
		
    # 1-0
	def consumption(self):
		return super().afterpush()-super().todaypush()

class PushLimit(Push):
    def __init__(self,name:str):
        super().__init__(name)
	
    # (33.333-0)/1
    def daylimit(self):
        return math.ceil((super().onedaypush()-super().afterpush())/super().consumption())
    
    def templelimit(self):
        return math.ceil(super().onedaypush()/super().friend())

if __name__=="main":
    limit=PushLimit(name='')

    print(f"一か月分のプッシュ上限 {limit.pushlimit()}")
    print(f"今月分のプッシュ数 {limit.totalpush()}")
    print(f"1送信につき消費するプッシュ数（botの友達数) {limit.friend()}")
    print(f"本日分のプッシュ上限 {limit.onedaypush()}")
    print(f"本日のプッシュ数 {limit.todaypush()}")
    print(f"1送信につき消費するプッシュ数 {limit.consumption()}")
    print(f"残り送信上限 {limit.daylimit()}")