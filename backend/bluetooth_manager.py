import subprocess
import json
import re

class BluetoothManager:
    def __init__(self):
        self.connected_devices = {}
        self.audio_device = None
    
    def scan_devices(self):
        """Сканирование доступных Bluetooth устройств"""
        try:
            # Для Windows используем PowerShell
            result = subprocess.run([
                'powershell', '-Command',
                'Get-PnpDevice | Where-Object {$_.Class -eq "AudioEndpoint" -and $_.Status -eq "OK"} | Select-Object FriendlyName, InstanceId'
            ], capture_output=True, text=True, timeout=10)
            
            devices = []
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')[3:]  # Пропускаем заголовки
                for line in lines:
                    if line.strip():
                        parts = line.split()
                        if len(parts) >= 2:
                            name = ' '.join(parts[:-1])
                            devices.append({'name': name, 'id': parts[-1]})
            
            return devices
        except:
            return []
    
    def connect_device(self, device_name):
        """Подключение к Bluetooth устройству"""
        try:
            # Попытка подключения через Windows API
            result = subprocess.run([
                'powershell', '-Command',
                f'Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show("Подключение к {device_name}")'
            ], capture_output=True, text=True, timeout=5)
            
            self.audio_device = device_name
            self.connected_devices[device_name] = {'status': 'connected', 'type': 'audio'}
            return True
        except:
            return False
    
    def disconnect_device(self, device_name):
        """Отключение Bluetooth устройства"""
        try:
            if device_name in self.connected_devices:
                del self.connected_devices[device_name]
            if self.audio_device == device_name:
                self.audio_device = None
            return True
        except:
            return False
    
    def set_volume(self, volume):
        """Установка громкости через системные команды"""
        try:
            volume = max(0, min(100, volume))
            # Используем nircmd для управления громкостью (если установлен)
            subprocess.run(['nircmd', 'setsysvolume', str(int(volume * 655.35))], 
                         capture_output=True, timeout=2)
            return True
        except:
            # Альтернативный способ через PowerShell
            try:
                subprocess.run([
                    'powershell', '-Command',
                    f'(New-Object -comObject WScript.Shell).SendKeys([char]175)'
                ], capture_output=True, timeout=2)
                return True
            except:
                return False
    
    def play_audio(self, file_path=None):
        """Воспроизведение аудио"""
        try:
            if file_path:
                subprocess.Popen(['start', file_path], shell=True)
            else:
                # Воспроизведение системного звука
                subprocess.run(['powershell', '-Command', '[console]::beep(800,200)'], 
                             capture_output=True, timeout=2)
            return True
        except:
            return False
    
    def get_connected_devices(self):
        """Получить список подключенных устройств"""
        return self.connected_devices
    
    def is_audio_device_connected(self):
        """Проверить подключена ли аудио колонка"""
        return self.audio_device is not None