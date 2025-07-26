import discord
from discord.ext import tasks, commands
import datetime
import os
from flask import Flask
from threading import Thread

# --- 設定項目 ---
# Renderなどの環境変数からトークンを読み込む
# 環境変数にDISCORD_BOT_TOKENという名前でトークンを設定してください
BOT_TOKEN = os.environ.get("DISCORD_BOT_TOKEN")
# 通知を送信したいチャンネルのID
# チャンネルを右クリックして「IDをコピー」で取得できます
CHANNEL_ID = 1145938488483655761

# --- トークンが設定されているか確認 ---
if BOT_TOKEN is None:
    print("エラー: Discord Botのトークンが設定されていません。")
    print("RenderのEnvironment VariablesなどにDISCORD_BOT_TOKENを設定してください。")
    exit() # トークンがない場合はプログラムを終了

# --- Webサーバー機能（Renderのスリープ防止用）---
app = Flask('')

@app.route('/')
def home():
    return "Botは正常に起動しています。"

def run():
  app.run(host='0.0.0.0', port=8080)

def start_web_server():
    t = Thread(target=run)
    t.start()
# --- Webサーバー機能ここまで ---


# --- Discord Bot本体のコード ---

# Botの接続設定
intents = discord.Intents.default()
bot = commands.Bot(command_prefix='/', intents=intents)

# 日本標準時(JST)のタイムゾーンを定義
JST = datetime.timezone(datetime.timedelta(hours=9), 'JST')

# 通知を送る時間を定義（毎日12時0分 JST）
notify_time = datetime.time(hour=12, minute=0, tzinfo=JST)


# Botが起動したときに実行される処理
@bot.event
async def on_ready():
    """
    BotがDiscordに正常に接続し、準備ができたときに呼び出されるイベント。
    """
    print(f'{bot.user} としてログインしました')
    print('------------------------------------')
    # 定期実行タスクを開始する
    send_noon_notification.start()


@tasks.loop(time=notify_time)
async def send_noon_notification():
    """
    毎日、指定された時間(notify_time)に実行されるタスク。
    """
    try:
        # 設定したチャンネルIDからチャンネルオブジェクトを取得
        channel = bot.get_channel(CHANNEL_ID)
        if channel:
            # チャンネルにメッセージを送信
            await channel.send("🕛 正午になりました！お昼の時間です！")
            print(f"{datetime.datetime.now(JST)}: チャンネルID {CHANNEL_ID} に正午の通知を送信しました。")
        else:
            print(f"エラー: チャンネルID {CHANNEL_ID} が見つかりませんでした。")
    except Exception as e:
        print(f"通知の送信中にエラーが発生しました: {e}")


# --- メイン処理 ---
if __name__ == "__main__":
    # Webサーバーを起動
    start_web_server()
    # Discord Botを起動
    bot.run(BOT_TOKEN)
