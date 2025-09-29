from flask import Flask, render_template, jsonify, request
import requests
import threading
import time

app = Flask(__name__, template_folder='../frontend/devices', static_folder='../frontend/devices')

temperature_state = {
    'value': 22
}

@app.route('/')
def temperature_page():
    return render_template('temperature.html')

@app.route('/api/state')
def get_state():
    return jsonify(temperature_state)

@app.route('/api/update', methods=['POST'])
def update_state():
    global temperature_state
    data = request.get_json()
    temperature_state.update(data)
    return jsonify({'success': True, 'state': temperature_state})

def sync_with_main_server():
    while True:
        try:
            response = requests.get('http://localhost:5000/api/devices')
            if response.status_code == 200:
                main_state = response.json().get('temperature', {})
                if main_state:
                    temperature_state.update(main_state)
        except:
            pass
        time.sleep(1)

if __name__ == '__main__':
    sync_thread = threading.Thread(target=sync_with_main_server, daemon=True)
    sync_thread.start()
    app.run(debug=True, host='0.0.0.0', port=5002)