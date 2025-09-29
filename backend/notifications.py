import json
import time
from datetime import datetime
from collections import deque

class NotificationManager:
    def __init__(self):
        self.notifications = deque(maxlen=50)
        self.subscribers = []
        self.alert_rules = {
            'security_breach': {'priority': 'high', 'sound': True},
            'temperature_critical': {'priority': 'high', 'sound': True},
            'device_offline': {'priority': 'medium', 'sound': False},
            'sensor_alert': {'priority': 'low', 'sound': False}
        }
    
    def add_notification(self, type, message, priority='low', data=None):
        """Добавить уведомление"""
        notification = {
            'id': int(time.time() * 1000),
            'type': type,
            'message': message,
            'priority': priority,
            'timestamp': datetime.now().isoformat(),
            'read': False,
            'data': data or {}
        }
        
        self.notifications.appendleft(notification)
        self._notify_subscribers(notification)
        return notification
    
    def get_notifications(self, unread_only=False):
        """Получить уведомления"""
        if unread_only:
            return [n for n in self.notifications if not n['read']]
        return list(self.notifications)
    
    def mark_read(self, notification_id):
        """Отметить как прочитанное"""
        for notification in self.notifications:
            if notification['id'] == notification_id:
                notification['read'] = True
                return True
        return False
    
    def clear_all(self):
        """Очистить все уведомления"""
        self.notifications.clear()
    
    def _notify_subscribers(self, notification):
        """Уведомить подписчиков"""
        for callback in self.subscribers:
            try:
                callback(notification)
            except:
                pass
    
    def subscribe(self, callback):
        """Подписаться на уведомления"""
        self.subscribers.append(callback)
    
    def create_security_alert(self, message):
        """Создать уведомление безопасности"""
        return self.add_notification('security_breach', message, 'high')
    
    def create_device_alert(self, device, status):
        """Создать уведомление об устройстве"""
        message = f"Устройство {device}: {status}"
        return self.add_notification('device_status', message, 'medium', {'device': device})
    
    def create_sensor_alert(self, sensor, value, threshold):
        """Создать уведомление датчика"""
        message = f"Датчик {sensor}: {value} (порог: {threshold})"
        return self.add_notification('sensor_alert', message, 'low', {
            'sensor': sensor, 'value': value, 'threshold': threshold
        })