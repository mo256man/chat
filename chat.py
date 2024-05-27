from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
socketio = SocketIO(app)

# チャットルームに接続したクライアントの一覧を保持する辞書
clients = {}

@app.route('/')
def index():
    return render_template('chat.html')

# チャットに参加した時の処理
@socketio.on('join')
def handle_join(data):
    username = data['username']
    clients[username] = request.sid  # クライアントのIDを保存
    emit('update_chat', {'message': f'{username}がチャットに参加しました'}, broadcast=True)
    emit('update_clients', {'clients': list(clients.keys())}, broadcast=True)  # 参加者リストを更新

# メッセージを送信した時の処理
@socketio.on('send_message')
def handle_message(data):
    sender = data['sender']
    receiver = data['receiver']
    message = data['message']
    
    if receiver == 'all':
        emit('update_chat', {'message': f'{sender}: {message}'}, broadcast=True)
    elif receiver in clients:
        emit('update_chat', {'message': f'{sender}: {message}'}, room=clients[receiver])

# チャットから退出した時の処理
@socketio.on('leave')
def handle_leave(data):
    username = data['username']
    if username in clients:
        del clients[username]  # クライアントのIDを削除
        emit('update_chat', {'message': f'{username}がチャットから退出しました'}, broadcast=True)
        emit('update_clients', {'clients': list(clients.keys())}, broadcast=True)  # 参加者リストを更新

# 参加者リストを要求した時の処理
@socketio.on('get_clients')
def handle_get_clients():
    emit('update_clients', {'clients': list(clients.keys())})  # 現在の参加者リストを返す

# クライアントとの接続が切断された時の処理
@socketio.on('disconnect')
def handle_disconnect():
    # クライアントが参加者リストに存在する場合、そのクライアントを削除して、切断メッセージを送信する
    for username, sid in list(clients.items()):
        if sid == request.sid:
            del clients[username]
            emit('update_chat', {'message': f'{username}がチャットから切断しました'}, broadcast=True)
            emit('update_clients', {'clients': list(clients.keys())}, broadcast=True)  # 参加者リストを更新

if __name__ == '__main__':
    socketio.run(app, debug=True)
