import re

class VoiceProcessor:
    def __init__(self, device_manager):
        self.device_manager = device_manager
        self.commands = {
            'light_on': [r'включи свет', r'включить свет', r'зажги свет'],
            'light_off': [r'выключи свет', r'выключить свет', r'погаси свет'],
            'light_brightness': [r'яркость света (\d+)', r'установи яркость (\d+)', r'яркость (\d+)'],
            'temp_up': [r'увеличь температуру', r'теплее', r'прибавь температуру'],
            'temp_down': [r'уменьши температуру', r'холоднее', r'убавь температуру'],
            'temp_up_by': [r'увеличь температуру на (\d+)', r'прибавь (\d+) градус'],
            'temp_down_by': [r'уменьши температуру на (\d+)', r'убавь (\d+) градус'],
            'temp_set': [r'установи температуру (\d+)', r'температура (\d+)'],
            'security_on': [r'включи охрану', r'активируй безопасность', r'включи сигнализацию'],
            'security_off': [r'выключи охрану', r'отключи безопасность', r'выключи сигнализацию'],
            'music_on': [r'включи музыку', r'играй музыку', r'запусти музыку'],
            'music_off': [r'выключи музыку', r'останови музыку', r'пауза'],
            'music_volume': [r'громкость (\d+)', r'установи громкость (\d+)', r'звук (\d+)'],
            'music_volume_up': [r'громче', r'увеличь громкость', r'прибавь звук'],
            'music_volume_down': [r'тише', r'уменьши громкость', r'убавь звук'],
            'scenario_morning': [r'сценарий утро', r'режим утро', r'доброе утро'],
            'scenario_evening': [r'сценарий вечер', r'режим вечер', r'добрый вечер'],
            'scenario_sleep': [r'сценарий сон', r'режим сна', r'спокойной ночи'],
            'scenario_work': [r'сценарий работа', r'режим работы', r'рабочий режим'],
            'all_off': [r'выключи все', r'выключи всё', r'отключи все'],
            'all_on': [r'включи все', r'включи всё', r'активируй все']
        }
    
    def process_command(self, command_text):
        command_text = command_text.lower().strip()
        
        for command_type, patterns in self.commands.items():
            for pattern in patterns:
                match = re.search(pattern, command_text)
                if match:
                    value = match.group(1) if match.groups() else None
                    return self._execute_command(command_type, value)
        
        return "Команда не распознана"
    
    def _execute_command(self, command_type, value=None):
        try:
            if command_type == 'light_on':
                self.device_manager.update_device('light', {'status': True})
                return "Свет включен"
            
            elif command_type == 'light_off':
                self.device_manager.update_device('light', {'status': False})
                return "Свет выключен"
            
            elif command_type == 'light_brightness' and value:
                brightness = max(0, min(100, int(value)))
                self.device_manager.update_device('light', {'brightness': brightness, 'status': True})
                return f"Яркость света установлена на {brightness}%"
            
            elif command_type == 'temp_up':
                device = self.device_manager.get_device('temperature')
                new_temp = device.increase()
                return f"Температура увеличена до {new_temp}°C"
            
            elif command_type == 'temp_down':
                device = self.device_manager.get_device('temperature')
                new_temp = device.decrease()
                return f"Температура уменьшена до {new_temp}°C"
            
            elif command_type == 'temp_up_by' and value:
                device = self.device_manager.get_device('temperature')
                increase = int(value)
                new_temp = min(30, device.value + increase)
                device.set_value(new_temp)
                return f"Температура увеличена на {increase}° до {new_temp}°C"
            
            elif command_type == 'temp_down_by' and value:
                device = self.device_manager.get_device('temperature')
                decrease = int(value)
                new_temp = max(15, device.value - decrease)
                device.set_value(new_temp)
                return f"Температура уменьшена на {decrease}° до {new_temp}°C"
            
            elif command_type == 'temp_set' and value:
                temp = max(15, min(30, int(value)))
                self.device_manager.update_device('temperature', {'value': temp})
                return f"Температура установлена на {temp}°C"
            
            elif command_type == 'security_on':
                self.device_manager.update_device('security', {'status': True})
                return "Система безопасности активирована"
            
            elif command_type == 'security_off':
                self.device_manager.update_device('security', {'status': False})
                return "Система безопасности отключена"
            
            elif command_type == 'music_on':
                self.device_manager.update_device('music', {'status': True})
                return "Музыка включена"
            
            elif command_type == 'music_off':
                self.device_manager.update_device('music', {'status': False})
                return "Музыка выключена"
            
            elif command_type == 'music_volume' and value:
                volume = max(0, min(100, int(value)))
                self.device_manager.update_device('music', {'volume': volume})
                return f"Громкость установлена на {volume}%"
            
            elif command_type == 'music_volume_up':
                device = self.device_manager.get_device('music')
                new_volume = min(100, device.volume + 10)
                device.set_volume(new_volume)
                return f"Громкость увеличена до {new_volume}%"
            
            elif command_type == 'music_volume_down':
                device = self.device_manager.get_device('music')
                new_volume = max(0, device.volume - 10)
                device.set_volume(new_volume)
                return f"Громкость уменьшена до {new_volume}%"
            
            elif command_type == 'scenario_morning':
                self._activate_scenario('утро')
                return "Активирован утренний сценарий"
            
            elif command_type == 'scenario_evening':
                self._activate_scenario('вечер')
                return "Активирован вечерний сценарий"
            
            elif command_type == 'scenario_sleep':
                self._activate_scenario('сон')
                return "Активирован ночной сценарий"
            
            elif command_type == 'scenario_work':
                self._activate_scenario('работа')
                return "Активирован рабочий сценарий"
            
            elif command_type == 'all_off':
                self.device_manager.update_device('light', {'status': False})
                self.device_manager.update_device('music', {'status': False})
                return "Все устройства выключены"
            
            elif command_type == 'all_on':
                self.device_manager.update_device('light', {'status': True})
                self.device_manager.update_device('music', {'status': True})
                return "Все устройства включены"
            
        except Exception as e:
            return f"Ошибка выполнения команды: {str(e)}"
        
        return "Неизвестная команда"
    
    def _activate_scenario(self, scenario):
        """Активация сценария"""
        scenarios = {
            'утро': {'light': {'status': True, 'brightness': 80}, 'temperature': {'value': 22}, 'music': {'status': True, 'volume': 40}},
            'вечер': {'light': {'status': True, 'brightness': 30}, 'temperature': {'value': 20}, 'security': {'status': True}},
            'сон': {'light': {'status': False}, 'temperature': {'value': 18}, 'music': {'status': False}, 'security': {'status': True}},
            'работа': {'light': {'status': True, 'brightness': 100}, 'temperature': {'value': 23}, 'music': {'status': False}}
        }
        
        if scenario in scenarios:
            for device, config in scenarios[scenario].items():
                self.device_manager.update_device(device, config)