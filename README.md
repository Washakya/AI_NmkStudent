# AI_NmkStudent
## 概要
並木生のツイートから学習・文章生成をし、AIの並木生を作ろうという試み

* AI並木中等生([@AI_NmkStudent](https://twitter.com/AI_NmkStudent))
* 学習用([@AI_GetTweetsMys](https://twitter.com/AI_GetTweetsMys))

## 使用言語・パッケージ
__Python__
* tweepy
* MeCab
* markovify

## 約束事項
* 学習用アカウントのフォロー外のアカウントから学習することはありません。
* 学習用アカウントのフォローは本人の承認のもと行います。

## 機能
### 定刻ツイート
1. 一定時間フォロー中のアカウントからツイートを最大200件ずつ取得
1. 単語ごとに分解(形態素解析)
1. マルコフ連鎖による文章生成
1. ツイートを送信

〇実行間隔
* 平日:6-7時,17-24時 (1日計10回)
1時間おきに実行
* 休日:6-24時 (1日計19回)
1時間おきに実行


### リプライ
1. フォロー中のアカウントから返信ツイートのみを取得
1. 定刻ツイート同様にマルコフ連鎖で返信生成する関数reply()の作成
1. おみくじ返信関数の作成mikuji()の生成
1. 定期的にメンションを取得・返信(プログラム停止まで繰り返し)
#### リプライコマンドまとめ
* *"おみくじ"*　おみくじを返信
* ※その他の返信 AI生成の文章を返信

〇実行間隔
* 24時間稼働中


### フォローバック
1. フォロー中のアカウント、フォローされているアカウントを取得
1. フォローされているアカウントのうち、フォローしていないアカウントをフォローバック

〇実行間隔
* 平日・休日:0-23時 (1日計24回)
1時間おきに実行

## アップデート履歴
* 2022 10/24 (月) -アカウント始動
* 2022 10/30 (日) -自動フォローバック実装
* 2022 11/01 (火) -自動リプライβ実装
