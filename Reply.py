#モジュールのインポート
import os
import tweepy
import datetime
import random
import time

#各種キーの取得
API_KEY = os.environ.get("API_KEY")
API_KEY_SECRET = os.environ.get("API_KEY_SECRET")
ACCESS_TOKEN_P = os.environ.get("ACCESS_TOKEN_P")
ACCESS_TOKEN_SECRET_P = os.environ.get("ACCESS_TOKEN_SECRET_P")

#認証オブジェクトの作成
auth = tweepy.OAuthHandler(API_KEY, API_KEY_SECRET)
auth.set_access_token(ACCESS_TOKEN_P, ACCESS_TOKEN_SECRET_P)
api_P = tweepy.API(auth)

#各終了時刻
StopTime = [0,4,8,12,16,20]

#終了時刻リストから現在時刻を削除
if datetime.datetime.now().hour == 23:
    StopTime.remove(0)
    StartTime = 0
else:
    StopTime.remove(datetime.datetime.now().hour + 1)
    StartTime = datetime.datetime.now().hour + 1

#実行時刻になるまで待つ
while True:
    if StartTime == datetime.datetime.now().hour:
        break


#最後のメンションを取得
lastID = api_P.mentions_timeline()[0].id

#おみくじの中身を設定
kuji = ["凶","末吉","小吉","中吉","吉","大吉"]

#繰り返しをオンに
flg = True

#停止と言うまで繰り返し
while flg or datetime.datetime.now().hour in StopTime:
    #最新のメンションを取得
    results = api_P.mentions_timeline(since_id=lastID)
    for t in results:
        #停止するやつ
        if "停止" in t.text and t.user.screen_name == "Moyashi_Utteru":
            api_P.update_status(status="@"+t.user.screen_name+" "+"停止しました", in_reply_to_status_id = t.id)
            flg = False
            break
        #おみくじ返信するやつ
        elif "おみくじ" in t.text:
            api_P.update_status(status="@"+t.user.screen_name+" "+kuji[random.randint(0,5)], in_reply_to_status_id = t.id)
            lastID = t.id
            print(t.text)
        #クッソうざい返信
        else:
            api_P.update_status(status="@"+t.user.screen_name+" "+"一理ある", in_reply_to_status_id = t.id)
            lastID = t.id
            print(t.text)
    #クールタイム
    time.sleep(60)

#終了通知
print("停止")
