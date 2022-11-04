#モジュールのインポート
import tweepy
import MeCab
import markovify
import os
import requests
import json
import time
import random
import datetime
import math
import re

#各種キーの取得
API_KEY = os.environ.get("API_KEY")
API_KEY_SECRET = os.environ.get("API_KEY_SECRET")
ACCESS_TOKEN_S = os.environ.get("ACCESS_TOKEN_S")
ACCESS_TOKEN_SECRET_S = os.environ.get("ACCESS_TOKEN_SECRET_S")
ACCESS_TOKEN_P = os.environ.get("ACCESS_TOKEN_P")
ACCESS_TOKEN_SECRET_P = os.environ.get("ACCESS_TOKEN_SECRET_P")

#認証オブジェクトの作成(収集用)
auth = tweepy.OAuthHandler(API_KEY, API_KEY_SECRET)
auth.set_access_token(ACCESS_TOKEN_S, ACCESS_TOKEN_SECRET_S)
api_S = tweepy.API(auth)

#ツイートのリストを入れておくやつ
tweets = []

#フォロー中のアカウント取得
following = api_S.get_friend_ids(screen_name = "AI_GetTweetsMys")

for u in following:
    #それぞれのアカウントから最新の200ツイートを取得
    for t in api_S.user_timeline(user_id = u, count = 200):
        #本人以外へのリプを取得
        if not t.in_reply_to_status_id == None and not t.in_reply_to_screen_name == t.user.screen_name:
            #リンク付きツイートはリンク・メンションを削除
            tweets.append(t.text.strip(re.search(r'@(.+) ',t.text).group(0)).partition("http")[0])

#ツイートを一文にしたやつを入れるやつ
OneSentenceTweets = ""

#ツイートリストを一文化
for t in tweets:
    OneSentenceTweets += t

#人名を入れとくリスト
HumanName = []

#人名の取得
mecab = MeCab.Tagger("-Ochasen")
node = mecab.parseToNode(OneSentenceTweets).next
while node:
    nodeFeature = node.feature.split(",")
    if nodeFeature[0] == "名詞" and nodeFeature[1] == "固有名詞" and nodeFeature[2] == "人名":
        HumanName.append(node.surface)
    node = node.next

#単語ブラックリスト読み込み
with open("BlackList.txt", encoding="utf-8") as f:
    lines = f.readlines()
    BlackList = [line.rstrip('\n') for line in lines]

#人名リストをブラックリストに追加
BlackList.extend(set(HumanName))

#ブラックリストの単語を含むツイートを削除
for w in BlackList:
    tweets = ([t for t in tweets if not w in t])

#単語削除リスト読み込み
with open("DeleteList.txt", encoding="utf-8") as f:
    lines = f.readlines()
    DeleteList = [line.rstrip('\n') for line in lines]

#単語削除リストに含まれる単語を部分削除
for w in DeleteList:
    for t in tweets:
        tweets[tweets.index(t)] = re.sub(w, "", t)

#生成中の文字を入れておくやつ
SplittedTweets = ""

#ツイートのリストを分かち書きの単一テキストにする
mecab = MeCab.Tagger("-Owakati")
for s in tweets:
    SplittedTweets += mecab.parse(s)

#各種記号・文字の削除
for w in BlackList:
    SplittedTweets = re.sub(w, "", SplittedTweets)
SplittedTweets = re.sub(r"[（）「」『』｛｝【】＠”’！？｜～・]", "", SplittedTweets)
SplittedTweets = re.sub(r"[()\[\]{}\'\"|~-]", "", SplittedTweets)
SplittedTweets = re.sub("\u3000", "", SplittedTweets)

#おみくじ
def mikuji():
    #おみくじの中身を設定
    kuji = ["凶","末吉","小吉","中吉","吉","大吉","https://ja.wikipedia.org/wiki/おみくじ"]
    #結果を返す
    return kuji[random.randint(0,6)]

#ラッキーアイテム
def LuckyItem():
    #アイテムを入れとくリスト
    items = []
    #名詞(人名を除く)の取得
    node = mecab.parseToNode(OneSentenceTweets).next
    #名詞のみを取り出す
    while node:
        nodeFeature = node.feature.split(",")
        if nodeFeature[0] == "名詞" and nodeFeature[1] == "一般" or nodeFeature[1] == "固有名詞" and not node.surface in BlackList:
            items.append(node.surface)
        node = node.next
    #重複を削除
    items = list(set(items))
    #結果を返す
    return items[random.randint(0,len(items)-1)]

#AI返信
def reply():
    text_model = markovify.NewlineText(SplittedTweets, state_size=2, well_formed=False)
    #文章作成(10文字から30文字)
    sentence = text_model.make_sentence(tries=random.randint(10,30))
    #分かち書きの単語間スペースを消す
    sentence = "".join(sentence.split())
    #結果を返す
    return sentence

def weather(day = 0):
    # 気象庁データの取得
    jma_json = requests.get("https://www.jma.go.jp/bosai/forecast/data/forecast/080000.json").json()

    #降水確率の取得
    RainyPercent = jma_json[0]["timeSeries"][1]["areas"][1]["pops"]
    #リストの空欄に-を置く
    for i in range(8-len(RainyPercent)):
        RainyPercent.insert(0,"-")

    #最高気温と最低気温の取得
    MaxAndMin = jma_json[0]["timeSeries"][2]["areas"][1]["temps"]
    #リストの空欄に-を置く
    for i in range(4-len(MaxAndMin)):
        MaxAndMin.insert(0,"-")

    #天気のデータを取得
    DayWeather = jma_json[0]["timeSeries"][0]["areas"][1]["weathers"][day]
    # 全角スペースの削除
    DayWeather = DayWeather.replace("\u3000", "")

    #日にちの取得
    date = jma_json[0]["timeSeries"][0]["timeDefines"][day][:10]
    if day == 1:
        date = "明日 "+date[0:4]+"年"+date[5:7]+"月"+date[8:10]+"日"+" の予報\n"
    else:
        date = "今日 "+date[0:4]+"年"+date[5:7]+"月"+date[8:10]+"日"+" の予報\n"

    #文章にまとめて返す
    return date + "【天気】"+DayWeather+"\n【降水確率】"+RainyPercent[day*4]+"/"+RainyPercent[day*4+1]+"/"+RainyPercent[day*4+2]+"/"+RainyPercent[day*4+3]+"%\n【気温】Max:"+MaxAndMin[day*2]+"℃/Min:" + MaxAndMin[day*2+1]+"℃\n\n気象庁より"

#認証オブジェクトの作成
auth = tweepy.OAuthHandler(API_KEY, API_KEY_SECRET)
auth.set_access_token(ACCESS_TOKEN_P, ACCESS_TOKEN_SECRET_P)
api_P = tweepy.API(auth)

#最後のメンションを取得
lastID = api_P.mentions_timeline()[0].id

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

#回答済みリストの作成(バグ防止)
answered = []

#準備完了
print("準備完了")

#実行時刻になるまで待つ
while True:
    if StartTime == datetime.datetime.now().hour:
        print("始動at" +str(StartTime) + ":00")
        break

#停止と言うまで繰り返し
while flg and not datetime.datetime.now().hour == (StartTime + 4) % 24:

    #最新のメンションを取得
    results = api_P.mentions_timeline(since_id=lastID)

    for t in results:
        if not t.id in answered:
            #停止するやつ
            if "停止" in t.text and t.user.screen_name == "Moyashi_Utteru":
                api_P.update_status(status="@"+t.user.screen_name+" "+"停止しました", in_reply_to_status_id = t.id)
                flg = False
                with open("ReplyStatus.txt",mode="w",encoding="utf-8") as f:
                    f.write("停止中\n")
                break

            #天気
            elif "天気" in t.text:
                if "明日" in t.text:
                    api_P.update_status(status="@"+t.user.screen_name+" "+weather(1), in_reply_to_status_id = t.id)
                else:
                    api_P.update_status(status="@"+t.user.screen_name+" "+weather(0), in_reply_to_status_id = t.id)
                answered.append(t.id)
                lastID = t.id

            #おみくじ
            elif "おみくじ" in t.text:
                api_P.update_status(status="@"+t.user.screen_name+" "+mikuji(), in_reply_to_status_id = t.id)
                answered.append(t.id)
                lastID = t.id

            #ラッキーアイテム
            elif "ラッキーアイテム" in t.text:
                api_P.update_status(status="@"+t.user.screen_name+" "+LuckyItem(), in_reply_to_status_id = t.id)
                answered.append(t.id)
                lastID = t.id
            
            #クッソうざい返信
            else:
                api_P.update_status(status="@"+t.user.screen_name+" "+reply(), in_reply_to_status_id = t.id)
                answered.append(t.id)
                lastID = t.id
    #クールタイム
    time.sleep(15)

#終了通知
print("停止at" + str(StartTime + 4) + ":00")
