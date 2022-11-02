#モジュールのインポート
import tweepy
import MeCab
import markovify
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
api_S = tweepy.API(auth, wait_on_rate_limit=True)

#ツイートのリストを入れておくやつ
tweets = []

#フォロー中のアカウント取得
following = api_S.get_friend_ids(screen_name = "AI_GetTweetsMys")

for u in following:
    #それぞれのアカウントから最新の200ツイートを取得
    for t in api_S.user_timeline(user_id = u, include_rts=True, trim_user=True, count = 200):
        #RT・メンション・リプを除外
        if not "@" in t.text and t.in_reply_to_status_id == None:
            #リンク付きツイートはリンクを削除
            tweets.append(t.text.partition("http")[0])

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
SplittedTweets = re.sub(r"[（）「」『』｛｝【】＠”’！？｜～・]", "", SplittedTweets)
SplittedTweets = re.sub(r"[()\[\]{}\'\"|~-]", "", SplittedTweets)
SplittedTweets = re.sub("\u3000", "", SplittedTweets)

#AIモデル作成(精度2)
text_model = markovify.NewlineText(SplittedTweets, state_size=2, well_formed=False)

#ツイート作成関数
def MakeTwet():
    #文章作成(10文字から100文字)
    sentence = text_model.make_sentence(tries=random.randint(10,100))

    #分かち書きの単語間スペースを消す
    sentence = "".join(sentence.split())

    #作成した文章を返す
    return sentence


#APIの認証オブジェクト作成(投稿用)
auth.set_access_token(ACCESS_TOKEN_P, ACCESS_TOKEN_SECRET_P)
api_P = tweepy.API(auth, wait_on_rate_limit=True)

#作成したツイートを取得
PostTweet = MakeTwet()

#ログに出力
print(PostTweet)

#Twitterに投稿
api_P.update_status(PostTweet)
