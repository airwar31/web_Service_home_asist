import re

class VoiceProcessor:
    def __init__(self, device_manager):
        self.device_manager = device_manager
        self.commands = {
            'light_on': [r'включи свет', r'включить свет', r'зажги свет'],
            'light_off': [r'выключи свет', r'выключить свет', r'погаси свет'],
            'temp_up': [r'увеличь температуру', r'теплее', r'прибавь температуру'],
            'temp_down': [r'уменьши температуру', r'холоднее', r'убавь температуру'],
            'security_on': [r'включи охрану', r'активируй безопасность', r'включи сигнализацию'],
            'security_off': [r'выключи охрану', r'отключи безопасность', r'выключи сигнализацию'],
            'music_on': [r'включи музыку', r'играй музыку', r'запусти музыку'],
            'music_off': [r'выключи музыку', r'останови музыку', r'пауза']
        }
    
    def process_command(self, command_text):
        command_text = command_text.lower().strip()
        
        for command_type, patterns in self.commands.items():
            for pattern in patterns:
                if re.search(pattern, command_text):
                    return self._execute_command(command_type)
        
        return "Команда не распознана"
    
    def _execute_command(self, command_type):
        try:
            if command_type == 'light_on':
                self.device_manager.update_device('light', {'status': True})
                return "Свет включен"
            
            elif command_type == 'light_off':
                self.device_manager.update_device('light', {'status': False})
                return "Свет выключен"
            
            elif command_type == 'temp_up':
                device = self.device_manager.get_device('temperature')
                new_temp = device.increase()
                return f"Температура увеличена до {new_temp}°C"
            
            elif command_type == 'temp_down':
                device = self.device_manager.get_device('temperature')
                new_temp = device.decrease()
                return f"Температура уменьшена до {new_temp}°C"
            
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
            
        except Exception as e:
            return f"Ошибка выполнения команды: {str(e)}"
        
        return "Неизвестная команда"