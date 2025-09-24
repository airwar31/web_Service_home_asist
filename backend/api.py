from flask import Blueprint, jsonify, request
from .devices import DeviceManager
from .voice_processor import VoiceProcessor

# Создаем Blueprint для API
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Инициализируем менеджер устройств и процессор голоса
device_manager = DeviceManager()
voice_processor = VoiceProcessor(device_manager)

@api_bp.route('/devices', methods=['GET'])
def get_devices():
    """Получить состояние всех устройств"""
    return jsonify(device_manager.get_all_states())

@api_bp.route('/devices/<device_name>', methods=['POST'])
def update_device(device_name):
    """Обновить состояние устройства"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        success = device_manager.update_device(device_name, data)
        if success:
            device_state = device_manager.get_all_states().get(device_name)
            return jsonify({
                'success': True, 
                'device': device_name, 
                'state': device_state
            })
        else:
            return jsonify({'success': False, 'error': 'Device not found'}), 404
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/voice-command', methods=['POST'])
def voice_command():
    """Обработать голосовую команду"""
    try:
        data = request.get_json()
        command = data.get('command', '').strip()
        
        if not command:
            return jsonify({'success': False, 'error': 'No command provided'}), 400
        
        response = voice_processor.process_command(command)
        devices_state = device_manager.get_all_states()
        
        return jsonify({
            'success': True,
            'response': response,
            'devices': devices_state
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/status', methods=['GET'])
def api_status():
    """Проверить статус API"""
    return jsonify({
        'status': 'online',
        'devices_count': len(device_manager.devices),
        'available_devices': list(device_manager.devices.keys())
    })