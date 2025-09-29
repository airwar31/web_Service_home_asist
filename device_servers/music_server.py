from flask import Flask, render_template, jsonify, request
import requests
import threading
import time

app = Flask(__name__, template_folder='../frontend/devices', static_folder='../frontend/devices')

music_state = {
    'status': False,
    'volume': 30
}

@app.route('/')
def music_page():
    return render_template('music.html')

@app.route('/api/state')
def get_state():
    return jsonify(music_state)

@app.route('/api/update', methods=['POST'])
def update_state():
    global music_state
    data = request.get_json()
    music_state.update(data)
    return jsonify({'success': True, 'state': music_state})

def sync_with_main_server():
    while True:
        try:
            response = requests.get('http://localhost:5000/api/devices')
            if response.status_code == 200:
                main_state = response.json().get('music', {})
                if main_state:
                    music_state.update(main_state)
        except:
            pass
        time.sleep(1)

if __name__ == '__main__':
    sync_thread = threading.Thread(target=sync_with_main_server, daemon=True)
    sync_thread.start()
    app.run(debug=True, host='0.0.0.0', port=5004)