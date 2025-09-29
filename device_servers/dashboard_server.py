from flask import Flask, render_template, request
import requests

app = Flask(__name__, template_folder='../frontend/devices', static_folder='../frontend/devices')

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/api/<path:path>', methods=['GET', 'POST'])
def proxy_api(path):
    """Проксирование API запросов к главному серверу"""
    try:
        url = f'http://localhost:5000/api/{path}'
        if request.method == 'GET':
            response = requests.get(url)
        else:
            response = requests.post(url, json=request.get_json())
        
        return response.json(), response.status_code
    except:
        return {'error': 'Main server unavailable'}, 503

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5005)