from flask import Flask, render_template, jsonify, request
import requests
import threading
import time

app = Flask(__name__, template_folder='../frontend/devices', static_folder='../frontend/devices')

light_state = {
    'status': False,
    'brightness': 50,
    'color': '#ffffff'
}

@app.route('/')
def light_page():
    return render_template('light.html')

@app.route('/api/state')
def get_state():
    return jsonify(light_state)

@app.route('/api/update', methods=['POST'])
def update_state():
    global light_state
    data = request.get_json()
    light_state.update(data)
    return jsonify({'success': True, 'state': light_state})

def sync_with_main_server():
    while True:
        try:
            response = requests.get('http://localhost:5000/api/devices')
            if response.status_code == 200:
                main_state = response.json().get('light', {})
                if main_state:
                    light_state.update(main_state)
        except:
            pass
        time.sleep(1)

if __name__ == '__main__':
    sync_thread = threading.Thread(target=sync_with_main_server, daemon=True)
    sync_thread.start()
    app.run(debug=True, host='0.0.0.0', port=5001)