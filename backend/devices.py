class Device:
    def __init__(self, name, device_type):
        self.name = name
        self.type = device_type
        self.status = False

class Light(Device):
    def __init__(self, name="light"):
        super().__init__(name, "light")
        self.brightness = 50
        
    def toggle(self):
        self.status = not self.status
        return self.status
    
    def set_brightness(self, value):
        self.brightness = max(0, min(100, value))
        return self.brightness

class Temperature(Device):
    def __init__(self, name="temperature"):
        super().__init__(name, "temperature")
        self.value = 22
    
    def increase(self):
        if self.value < 30:
            self.value += 1
        return self.value
    
    def decrease(self):
        if self.value > 15:
            self.value -= 1
        return self.value
    
    def set_value(self, value):
        self.value = max(15, min(30, value))
        return self.value

class Security(Device):
    def __init__(self, name="security"):
        super().__init__(name, "security")
        
    def toggle(self):
        self.status = not self.status
        return self.status

class Music(Device):
    def __init__(self, name="music"):
        super().__init__(name, "music")
        self.volume = 30
        
    def toggle(self):
        self.status = not self.status
        return self.status
    
    def set_volume(self, value):
        self.volume = max(0, min(100, value))
        return self.volume

class DeviceManager:
    def __init__(self):
        self.devices = {
            'light': Light(),
            'temperature': Temperature(),
            'security': Security(),
            'music': Music()
        }
    
    def get_device(self, name):
        return self.devices.get(name)
    
    def get_all_states(self):
        states = {}
        for name, device in self.devices.items():
            if name == 'light':
                states[name] = {'status': device.status, 'brightness': device.brightness}
            elif name == 'temperature':
                states[name] = {'value': device.value}
            elif name == 'security':
                states[name] = {'status': device.status}
            elif name == 'music':
                states[name] = {'status': device.status, 'volume': device.volume}
        return states
    
    def update_device(self, name, data):
        device = self.get_device(name)
        if not device:
            return False
            
        if name == 'light':
            if 'status' in data:
                device.status = data['status']
            if 'brightness' in data:
                device.set_brightness(data['brightness'])
        elif name == 'temperature':
            if 'value' in data:
                device.set_value(data['value'])
        elif name == 'security':
            if 'status' in data:
                device.status = data['status']
        elif name == 'music':
            if 'status' in data:
                device.status = data['status']
            if 'volume' in data:
                device.set_volume(data['volume'])
        
        return True