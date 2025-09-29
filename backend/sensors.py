import random
import time
import threading
from datetime import datetime

class SensorManager:
    def __init__(self, device_manager):
        self.device_manager = device_manager
        self.sensors = {
            'motion': {'status': False, 'last_detected': None},
            'light_level': {'value': 50, 'auto_adjust': True},
            'noise_level': {'value': 30},
            'air_quality': {'value': 85},
            'humidity': {'value': 45}
        }
        self.auto_mode = True
        self.start_monitoring()
    
    def start_monitoring(self):
        """Запуск мониторинга датчиков"""
        threading.Thread(target=self._sensor_loop, daemon=True).start()
    
    def _sensor_loop(self):
        """Основной цикл мониторинга"""
        while True:
            self._update_sensors()
            if self.auto_mode:
                self._auto_adjust()
            time.sleep(5)
    
    def _update_sensors(self):
        """Обновление показаний датчиков"""
        # Симуляция датчиков
        self.sensors['light_level']['value'] = max(0, min(100, 
            self.sensors['light_level']['value'] + random.randint(-5, 5)))
        
        self.sensors['noise_level']['value'] = max(0, min(100,
            self.sensors['noise_level']['value'] + random.randint(-3, 3)))
        
        self.sensors['air_quality']['value'] = max(0, min(100,
            self.sensors['air_quality']['value'] + random.randint(-2, 2)))
        
        self.sensors['humidity']['value'] = max(0, min(100,
            self.sensors['humidity']['value'] + random.randint(-1, 1)))
        
        # Датчик движения
        if random.random() < 0.1:  # 10% шанс обнаружения движения
            self.sensors['motion']['status'] = True
            self.sensors['motion']['last_detected'] = datetime.now()
        else:
            self.sensors['motion']['status'] = False
    
    def _auto_adjust(self):
        """Автоматическая настройка устройств"""
        # Автоматическая регулировка освещения
        if self.sensors['light_level']['auto_adjust']:
            light_level = self.sensors['light_level']['value']
            if light_level < 30:
                brightness = min(100, 100 - light_level)
                self.device_manager.update_device('light', {
                    'status': True, 
                    'brightness': brightness
                })
            elif light_level > 80:
                self.device_manager.update_device('light', {'status': False})
        
        # Автоматическая активация охраны при отсутствии движения
        if not self.sensors['motion']['status']:
            last_motion = self.sensors['motion']['last_detected']
            if last_motion and (datetime.now() - last_motion).seconds > 300:  # 5 минут
                self.device_manager.update_device('security', {'status': True})
    
    def get_all_sensors(self):
        """Получить все показания датчиков"""
        return self.sensors
    
    def toggle_auto_mode(self):
        """Переключить автоматический режим"""
        self.auto_mode = not self.auto_mode
        return self.auto_mode