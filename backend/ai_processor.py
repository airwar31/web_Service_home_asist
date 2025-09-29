import re
import json
from datetime import datetime, timedelta
import threading
import time

class AIProcessor:
    def __init__(self, device_manager):
        self.device_manager = device_manager
        self.context = {}
        self.schedules = {}
        self.learning_data = []
        self.scenarios = {
            'утро': {'light': {'status': True, 'brightness': 80}, 'temperature': {'value': 22}, 'music': {'status': True, 'volume': 40}},
            'вечер': {'light': {'status': True, 'brightness': 30}, 'temperature': {'value': 20}, 'security': {'status': True}},
            'сон': {'light': {'status': False}, 'temperature': {'value': 18}, 'music': {'status': False}, 'security': {'status': True}},
            'работа': {'light': {'status': True, 'brightness': 100}, 'temperature': {'value': 23}, 'music': {'status': False}}
        }
        
    def process_natural_command(self, text):
        text = text.lower().strip()
        
        # Сценарии
        if any(word in text for word in ['сценарий', 'режим']):
            return self._handle_scenario(text)
        
        # Расписание
        if any(word in text for word in ['через', 'в', 'завтра', 'сегодня']):
            return self._handle_schedule(text)
        
        # Контекстные команды
        if any(word in text for word in ['все', 'всё', 'дом']):
            return self._handle_global_command(text)
        
        # Умные предложения
        return self._smart_suggestions(text)
    
    def _handle_scenario(self, text):
        for scenario, settings in self.scenarios.items():
            if scenario in text:
                for device, config in settings.items():
                    self.device_manager.update_device(device, config)
                return f"Активирован сценарий '{scenario}'"
        return "Сценарий не найден"
    
    def _handle_schedule(self, text):
        # Простое планирование
        if 'через' in text:
            match = re.search(r'через (\d+) (минут|час)', text)
            if match:
                delay = int(match.group(1))
                unit = match.group(2)
                minutes = delay if unit == 'минут' else delay * 60
                
                # Планируем выполнение
                timer = threading.Timer(minutes * 60, self._execute_delayed_command, [text])
                timer.start()
                return f"Команда запланирована через {delay} {unit}"
        
        return "Не удалось запланировать команду"
    
    def _handle_global_command(self, text):
        if 'выключи все' in text or 'выключи всё' in text:
            self.device_manager.update_device('light', {'status': False})
            self.device_manager.update_device('music', {'status': False})
            return "Все устройства выключены"
        
        if 'включи все' in text or 'включи всё' in text:
            self.device_manager.update_device('light', {'status': True})
            self.device_manager.update_device('music', {'status': True})
            return "Все устройства включены"
        
        return "Команда не распознана"
    
    def _smart_suggestions(self, text):
        current_hour = datetime.now().hour
        
        if current_hour < 8 and 'свет' in text:
            return "Рекомендую мягкое освещение утром. Установить яркость 50%?"
        
        if current_hour > 22 and any(word in text for word in ['музыка', 'звук']):
            return "Поздний час. Рекомендую тихую громкость 20%"
        
        return "Команда обработана"
    
    def _execute_delayed_command(self, command):
        # Выполнение отложенной команды
        pass