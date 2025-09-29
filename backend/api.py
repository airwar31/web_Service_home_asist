from flask import Blueprint, jsonify, request
from .devices import DeviceManager
from .voice_processor import VoiceProcessor
from .bluetooth_manager import BluetoothManager
from .ai_processor import AIProcessor
from .sensors import SensorManager
from .notifications import NotificationManager
from .camera_manager import CameraManager

# Создаем Blueprint для API
api_bp = Blueprint('api', __name__, url_prefix='/api')

# Инициализируем все системы
device_manager = DeviceManager()
voice_processor = VoiceProcessor(device_manager)
bluetooth_manager = BluetoothManager()
notification_manager = NotificationManager()
ai_processor = AIProcessor(device_manager)
sensor_manager = SensorManager(device_manager)
camera_manager = CameraManager(notification_manager)
camera_manager.start_monitoring()

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
        
        # Сначала пробуем AI обработку
        ai_response = ai_processor.process_natural_command(command)
        if ai_response != 'Команда обработана':
            response = ai_response
        else:
            response = voice_processor.process_command(command)
        
        devices_state = device_manager.get_all_states()
        
        return jsonify({
            'success': True,
            'response': response,
            'devices': devices_state
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/bluetooth/scan', methods=['GET'])
def scan_bluetooth():
    """Сканирование Bluetooth устройств"""
    devices = bluetooth_manager.scan_devices()
    return jsonify({'devices': devices})

@api_bp.route('/bluetooth/connect', methods=['POST'])
def connect_bluetooth():
    """Подключение к Bluetooth устройству"""
    try:
        data = request.get_json()
        device_name = data.get('device_name')
        
        if bluetooth_manager.connect_device(device_name):
            # Обновляем музыкальное устройство
            music_device = device_manager.get_device('music')
            music_device.connect_bluetooth(device_name)
            
            return jsonify({
                'success': True,
                'message': f'Подключено к {device_name}',
                'connected_device': device_name
            })
        else:
            return jsonify({'success': False, 'error': 'Ошибка подключения'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/bluetooth/disconnect', methods=['POST'])
def disconnect_bluetooth():
    """Отключение Bluetooth устройства"""
    try:
        data = request.get_json()
        device_name = data.get('device_name')
        
        if bluetooth_manager.disconnect_device(device_name):
            music_device = device_manager.get_device('music')
            music_device.disconnect_bluetooth()
            
            return jsonify({
                'success': True,
                'message': f'Отключено от {device_name}'
            })
        else:
            return jsonify({'success': False, 'error': 'Ошибка отключения'}), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/sensors', methods=['GET'])
def get_sensors():
    """Получить показания датчиков"""
    return jsonify(sensor_manager.get_all_sensors())

@api_bp.route('/sensors/auto-mode', methods=['POST'])
def toggle_auto_mode():
    """Переключить авторежим"""
    auto_mode = sensor_manager.toggle_auto_mode()
    return jsonify({'auto_mode': auto_mode})

@api_bp.route('/notifications', methods=['GET'])
def get_notifications():
    """Получить уведомления"""
    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    return jsonify(notification_manager.get_notifications(unread_only))

@api_bp.route('/notifications/<int:notification_id>/read', methods=['POST'])
def mark_notification_read(notification_id):
    """Отметить уведомление как прочитанное"""
    success = notification_manager.mark_read(notification_id)
    return jsonify({'success': success})

@api_bp.route('/scenarios/<scenario_name>', methods=['POST'])
def activate_scenario(scenario_name):
    """Активировать сценарий"""
    response = ai_processor._handle_scenario(f'сценарий {scenario_name}')
    return jsonify({'success': True, 'response': response})

@api_bp.route('/cameras', methods=['GET'])
def get_cameras():
    """Получить список камер"""
    return jsonify(camera_manager.get_camera_status())

@api_bp.route('/cameras/add', methods=['POST'])
def add_camera():
    """Добавить IP камеру"""
    try:
        data = request.get_json()
        name = data.get('name')
        url = data.get('url')
        motion_detection = data.get('motion_detection', True)
        
        if camera_manager.add_camera(name, url, motion_detection):
            return jsonify({'success': True, 'message': f'Камера {name} добавлена'})
        else:
            return jsonify({'success': False, 'error': 'Не удалось подключиться к камере'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/cameras/<name>/remove', methods=['POST'])
def remove_camera(name):
    """Удалить камеру"""
    if camera_manager.remove_camera(name):
        return jsonify({'success': True, 'message': f'Камера {name} удалена'})
    else:
        return jsonify({'success': False, 'error': 'Камера не найдена'}), 404

@api_bp.route('/cameras/<name>/stream')
def camera_stream(name):
    """Получить кадр с камеры"""
    frame = camera_manager.get_camera_frame(name)
    if frame:
        return frame, 200, {'Content-Type': 'image/jpeg'}
    else:
        return jsonify({'error': 'Камера недоступна'}), 404

@api_bp.route('/cameras/test', methods=['POST'])
def test_camera():
    """Тестирование URL камеры"""
    try:
        data = request.get_json()
        url = data.get('url')
        
        if camera_manager.test_camera_url(url):
            return jsonify({'success': True, 'message': 'Камера доступна'})
        else:
            return jsonify({'success': False, 'error': 'Камера недоступна'}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@api_bp.route('/status', methods=['GET'])
def api_status():
    """Проверить статус API"""
    return jsonify({
        'status': 'online',
        'devices_count': len(device_manager.devices),
        'available_devices': list(device_manager.devices.keys()),
        'bluetooth_connected': bluetooth_manager.is_audio_device_connected(),
        'bluetooth_devices': bluetooth_manager.get_connected_devices(),
        'auto_mode': sensor_manager.auto_mode,
        'unread_notifications': len(notification_manager.get_notifications(True)),
        'sensors_active': True,
        'cameras_count': len(camera_manager.cameras),
        'cameras_status': camera_manager.get_camera_status()
    })