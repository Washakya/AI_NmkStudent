#モジュールのインポート
import os
import tweepy
import time
import random
import datetime
import math
import re
import MeCab
import markovify

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
following = api_S.get_friends(screen_name = "AI_GetTweetsMys")

for u in following:
    #それぞれのアカウントから最新の200ツイートを取得
    for t in api_S.user_timeline(screen_name = u.screen_name, count = 200):
        #本人以外へのリプを取得
        if not t.in_reply_to_status_id == None and not t.in_reply_to_screen_name == t.user.screen_name:
            #リンク付きツイートはリンク・メンションを削除
            tweets.append(t.text.strip(re.search(r'@(.+) ',t.text).group(0)).partition("http")[0])

#生成中の文字を入れておくやつ
SplittedTweets = ""

#ツイートのリストを分かち書きの単一テキストにする
mecab = MeCab.Tagger("-Owakati")
for s in tweets:
    SplittedTweets += mecab.parse(s)

#単語ブラックリスト読み込み
with open("BlackList.txt", encoding="utf-8") as f:
    lines = f.readlines()
BlackList = [line.rstrip('\n') for line in lines]

#各種記号・文字の削除
for w in BlackList:
    SplittedTweets = re.sub(w, "", SplittedTweets)
SplittedTweets = re.sub(r"[（）「」『』｛｝【】＠”’！？｜～・]", '', SplittedTweets)
SplittedTweets = re.sub(r"[()\[\]{}\'\"|~-]", "", SplittedTweets)
SplittedTweets = re.sub("\u3000", "", SplittedTweets)

#おみくじの中身を設定
kuji = ["凶","末吉","小吉","中吉","吉","大吉","https://ja.wikipedia.org/wiki/おみくじ"]

#おみくじの結果を返す
def mikuji():
    return kuji[random.randint(0,6)]

#返信を生成
def reply():
    #モデル生成
    text_model = markovify.NewlineText(SplittedTweets, state_size=2, well_formed=False)
    #文章作成(10文字から60文字)
    sentence = text_model.make_sentence(tries=random.randint(10,60))
    #分かち書きの単語間スペースを消す
    sentence = "".join(sentence.split())
    return sentence

#認証オブジェクトの作成(返信用)
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

#実行時刻になるまで待つ
while True:
    if StartTime == datetime.datetime.now().hour:
        break

#停止と言うor時間になるまで繰り返し
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
            api_P.update_status(status="@"+t.user.screen_name+" "+reply(), in_reply_to_status_id = t.id)
            lastID = t.id
            print(t.text)
    #クールタイム
    time.sleep(60)
#終了通知
print("停止")
