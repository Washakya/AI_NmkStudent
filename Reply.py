#モジュールのインポート
import os
import tweepy
import datetime
import random
import time
import math

#各種キーの取得
API_KEY = os.environ.get("API_KEY")
API_KEY_SECRET = os.environ.get("API_KEY_SECRET")
ACCESS_TOKEN_P = os.environ.get("ACCESS_TOKEN_P")
ACCESS_TOKEN_SECRET_P = os.environ.get("ACCESS_TOKEN_SECRET_P")

#認証オブジェクトの作成
auth = tweepy.OAuthHandler(API_KEY, API_KEY_SECRET)
auth.set_access_token(ACCESS_TOKEN_P, ACCESS_TOKEN_SECRET_P)
api_P = tweepy.API(auth)

#最後のメンションを取得
lastID = api_P.mentions_timeline()[0].id

#おみくじの中身を設定
kuji = ["凶","末吉","小吉","中吉","吉","大吉","https://ja.wikipedia.org/wiki/おみくじ"]

#おみくじの結果を返す
def mikuji():
    return kuji[random.randint(0,6)]

#ステータスの読み込み
with open("ReplyStatus.txt",mode="r",encoding="utf-8") as f:
    status = f.read().strip("\n")

#ステータスの判定
if status == "稼働中":
    #実行をオンに
    flg = True
else:
    #実行をオフに
    flg = False

#開始時間の取得
StartTime = (math.floor(datetime.datetime.now().hour / 4) * 4 + 4) % 24

#実行時刻になるまで待つ
while True:
    if StartTime == datetime.datetime.now().hour:
        break

#停止と言うまで繰り返し
while flg and not datetime.datetime.now().hour == (StartTime + 4) % 24:
    #最新のメンションを取得
    results = api_P.mentions_timeline(since_id=lastID)
    for t in results:
        #停止するやつ
        if "停止" in t.text and t.user.screen_name == "Moyashi_Utteru":
            api_P.update_status(status="@"+t.user.screen_name+" "+"停止しました", in_reply_to_status_id = t.id)
            flg = False
            with open("ReplyStatus.txt",mode="w",encoding="utf-8") as f:
                f.write("停止中\n")
            break
        #おみくじ返信するやつ
        elif "おみくじ" in t.text:
            api_P.update_status(status="@"+t.user.screen_name+" "+mikuji(), in_reply_to_status_id = t.id)
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
