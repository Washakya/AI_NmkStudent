#モジュールのインポート
import os
import tweepy

#APIのセットアップ
API_KEY = os.environ.get("API_KEY")
API_KEY_SECRET = os.environ.get("API_KEY_SECRET")
ACCESS_TOKEN_P = os.environ.get("ACCESS_TOKEN_P")
ACCESS_TOKEN_SECRET_P = os.environ.get("ACCESS_TOKEN_SECRET_P")

# APIの認証オブジェクト作成
auth = tweepy.OAuthHandler(API_KEY, API_SECRET)
auth.set_access_token(ACCESS_TOKEN_P, ACCESS_TOKEN_SECRET_P)
api_P = tweepy.API(auth, wait_on_rate_limit=True)

#フォロワーの取得
followers = api_P.get_follower_ids(screen_name = "AI_NmkStudent")

#フォロー中アカウントの取得
following = api_P.get_friend_ids(screen_name = "AI_NmkStudent")

#フォロバチェック・フォロバ
for u in followers:
    if not u in following:
        api_P.create_friendship(user_id = u)

#りむーぶ^^
for u in following:
    if not u in followers:
        api_P.destroy_friendship(user_id= u)
