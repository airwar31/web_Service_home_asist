from flask import Flask, render_template
from backend.api import api_bp

app = Flask(__name__, template_folder='frontend', static_folder='frontend')

# Регистрируем Blueprint для API
app.register_blueprint(api_bp)

@app.route('/')
def index():
    return render_template('index.html')

@app.errorhandler(404)
def not_found(error):
    return {'error': 'Endpoint not found'}, 404

@app.errorhandler(500)
def internal_error(error):
    return {'error': 'Internal server error'}, 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8080)