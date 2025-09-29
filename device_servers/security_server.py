from flask import Flask, render_template, jsonify, request
import requests
import threading
import time

app = Flask(__name__, template_folder='../frontend/devices', static_folder='../frontend/devices')

security_state = {
    'status': False
}

@app.route('/')
def security_page():
    return render_template('security.html')

@app.route('/api/state')
def get_state():
    return jsonify(security_state)

@app.route('/api/update', methods=['POST'])
def update_state():
    global security_state
    data = request.get_json()
    security_state.update(data)
    return jsonify({'success': True, 'state': security_state})

def sync_with_main_server():
    while True:
        try:
            response = requests.get('http://localhost:5000/api/devices')
            if response.status_code == 200:
                main_state = response.json().get('security', {})
                if main_state:
                    security_state.update(main_state)
        except:
            pass
        time.sleep(1)

if __name__ == '__main__':
    sync_thread = threading.Thread(target=sync_with_main_server, daemon=True)
    sync_thread.start()
    app.run(debug=True, host='0.0.0.0', port=5003)