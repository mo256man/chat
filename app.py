from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from flask_socketio import SocketIO, emit
import random

app = Flask(__name__)
socketio = SocketIO(app)

class User():
    def __init__(self):
        self.dict = {}
        self.dict["admin"] = ""
        for i in [1, 2, 3, 4]:
            self.dict[f"player{i}"] = ""
        self.names = ["A", "B", "C"][::-1]
        self.sid = ""

    def add(self):
        if len(self.names) > 0:
            name = self.names.pop()
        else:
            name = "定員オーバー"
        return name

user = User()

@app.route("/")
def index():
    return render_template("menu.html", user_name="")


# 接続してsidを取得する
@socketio.on("connect")
def handle_connect():
    sid = request.sid
    name = user.add()
    print(f'クライアント {sid} が接続しました。')
    emit("connect_user", user.dict)


# 参加者切り替え処理
@socketio.on("join_user")
def handle_join_user(data):
    btn_id = data["id"]
    user_name = data["user_name"]

    # すでに登録されている場所を探す
    is_in_key = False
    for key, value in user.dict.items():        # ユーザー名簿の中に
        if value == user_name:                  # ユーザーが登録されているキーがあったら
            is_in_key = True                    # 登録済みのフラグを立てる
            if key in btn_id:                   # それが今回押されたボタンと同じならば
                user.dict[key] = ""             # そのキーは空にする（登録解除）
            else:                               # 別のボタンが押されたら
                pass                            # 何もしない
    if not is_in_key:                           # ユーザー登録済みでなかったら
        for key, value in user.dict.items():    # ユーザー名簿の中の
            if key in btn_id and value == "":   # 今回押されたボタンにユーザー登録されていなかったら
                user.dict[key] = user           # ユーザー登録する

    print(user.dict)
    emit("update_user", user.dict, broadcast=True)


# 参加者リストを要求した時の処理
@socketio.on("get_user")
def handle_get_user():
    print(user.dict)
    emit("update_user", user.dict, broadcast=True)

# 接続
@socketio.on("join")
def handle_join():
    sid = request.sid
    user.sid = sid
    emit("update_user", user.dict, broadcast=True)


# ゲームスタート
@socketio.on("game_start")
def handle_game_start():
    for key, value in user.dict.items():
        if key != "admin":
            emit('redirect', {'redirect_url': url_for('special_page')}, room=user.sid)

if __name__ == "__main__":
    socketio.run(app, debug=True)
