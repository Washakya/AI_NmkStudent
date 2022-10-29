#モジュールのインポート
import tweepy
import MeCab
import markovify
import demoji
import re
import random
import os

#各種キー設定
API_KEY = os.environ.get("API_KEY")
API_KEY_SECRET = os.environ.get("API_KEY_SECRET")
ACCESS_TOKEN_S = os.environ.get("ACCESS_TOKEN_S")
ACCESS_TOKEN_SECRET_S = os.environ.get("ACCESS_TOKEN_SECRET_S")
ACCESS_TOKEN_P = os.environ.get("ACCESS_TOKEN_P")
ACCESS_TOKEN_SECRET_P = os.environ.get("ACCESS_TOKEN_SECRET_P")

#APIの認証オブジェクト作成(収集用)
auth = tweepy.OAuthHandler(API_KEY, API_KEY_SECRET)
auth.set_access_token(ACCESS_TOKEN_S, ACCESS_TOKEN_SECRET_S)
api = tweepy.API(auth, wait_on_rate_limit=True)

#ツイートのリストを入れておくやつ
tweets = []

#フォロー中のアカウント取得
following = api.get_friends(screen_name = "AI_GetTweetsMys")

for u in following:
    #それぞれのアカウントから最新の200ツイートを取得
    for t in api.user_timeline(screen_name = u.screen_name, count = 200):
        #RT・メンション・リプを除外
        if not "@" in t.text and not "RT" in t.text and t.in_reply_to_status_id == None:
            #リンク付きツイートはリンクを削除
            if not "http" in t.text:
                tweets.append(t.text)
            else:
                tweets.append(t.text.partition("http")[0])

#生成中の文字を入れておくやつ
SplittedTweets = ""

#ツイートのリストを分かち書きの単一テキストにする
mecab = MeCab.Tagger("-Owakati")
for s in tweets:
    SplittedTweets += mecab.parse(s)

#各種記号・文字の削除
SplittedTweets = re.sub(r"匿名質問募集中|咲太郎|飯田清","", SplittedTweets)
SplittedTweets = re.sub(r"[（）「」『』｛｝【】＠”’！？｜～・]", '', SplittedTweets)
SplittedTweets = re.sub(r"[()\[\]{}\'\"|~-]", "", SplittedTweets)
SplittedTweets = re.sub(r"\u3000", "", SplittedTweets)

#絵文字の削除
SplittedTweets = demoji.replace(string=SplittedTweets, repl="")

#AIモデル作成(精度2)
text_model = markovify.NewlineText(SplittedTweets, state_size=2, well_formed=False)

#文章作成(10文字から100文字)
sentence = text_model.make_sentence(tries=random.randint(10,100))

#分かち書きの単語間スペースを消す
sentence = "".join(sentence.split())

#APIの認証オブジェクト作成(投稿用)
auth.set_access_token(ACCESS_TOKEN_P, ACCESS_TOKEN_SECRET_P)
api = tweepy.API(auth, wait_on_rate_limit=True)

print(sentence)

#ツイート送信
api.update_status(sentence)
