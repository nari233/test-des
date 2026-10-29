import eventlet
eventlet.monkey_patch()

from flask import Flask, request
from flask_socketio import SocketIO, emit

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

ACCESS_CODE = "123456123456"   # ← غيّر الرمز هنا لو تبي
users = {}

@app.route('/')
def home():
    return "Chat server is running ✅"

@socketio.on('join')
def handle_join(data):
    code = data.get('code')
    name = data.get('name')
    avatar = data.get('avatar')
    if code != ACCESS_CODE:
        emit('join_error', {'msg': 'الرمز غير صحيح!'})
        return
    users[request.sid] = {'name': name, 'avatar': avatar}
    emit('join_ok', {'msg': 'تم الدخول'})
    emit('system_msg', {'msg': f'{name} دخل الدردشة'}, broadcast=True)

@socketio.on('message')
def handle_message(data):
    if request.sid not in users:
        return
    user = users[request.sid]
    emit('new_message', {
        'name': user['name'],
        'avatar': user['avatar'],
        'text': data.get('text', ''),
        'image': data.get('image', None)
    }, broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    if request.sid in users:
        name = users[request.sid]['name']
        del users[request.sid]
        emit('system_msg', {'msg': f'{name} خرج'}, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)