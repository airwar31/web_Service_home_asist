import cv2
import numpy as np
import threading
import time
from datetime import datetime
import requests
import os

class CameraManager:
    def __init__(self, notification_manager):
        self.notification_manager = notification_manager
        self.cameras = {}
        self.motion_detectors = {}
        self.is_monitoring = False
        self.person_cascade = self._load_person_detector()
        
    def add_camera(self, name, url, motion_detection=True):
        """Добавить IP камеру"""
        try:
            # Преобразуем строку в число для USB камер
            camera_url = int(url) if url.isdigit() else url
            
            cap = cv2.VideoCapture(camera_url)
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            if cap.isOpened():
                # Проверяем, что можно прочитать кадр
                ret, frame = cap.read()
                if ret and frame is not None:
                    self.cameras[name] = {
                        'url': url,
                        'capture': cap,
                        'status': 'connected',
                        'motion_detection': motion_detection,
                        'last_motion': None
                    }
                    
                    if motion_detection:
                        self.motion_detectors[name] = {
                            'background': None,
                            'motion_threshold': 3000,
                            'sensitivity': 30,
                            'person_detection': True,
                            'last_frame_time': time.time(),
                            'last_detection': 0,
                            'detection_cooldown': 10  # 10 секунд между уведомлениями
                        }
                    
                    return True
                else:
                    cap.release()
                    return False
            else:
                cap.release()
                return False
        except Exception as e:
            print(f"Add camera error: {e}")
            return False
    
    def _load_person_detector(self):
        """Загрузка детектора человека"""
        try:
            # Пробуем загрузить HOG детектор
            hog = cv2.HOGDescriptor()
            hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
            return hog
        except:
            return None
    
    def _detect_person(self, frame):
        """Детекция человека на кадре"""
        if self.person_cascade is None:
            return False
        
        try:
            boxes, weights = self.person_cascade.detectMultiScale(
                frame, 
                winStride=(8, 8),
                padding=(32, 32),
                scale=1.05
            )
            
            # Строгая фильтрация
            if len(boxes) == 0 or len(weights) == 0:
                return False
            
            # Проверяем размер и уверенность
            valid_detections = 0
            for i, (x, y, w, h) in enumerate(boxes):
                if weights[i] > 0.7 and w > 30 and h > 60:  # Минимальные размеры человека
                    valid_detections += 1
            
            return valid_detections > 0
        except:
            return False
    
    def _check_motion(self, name, frame):
        """Проверка движения"""
        try:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            gray = cv2.GaussianBlur(gray, (21, 21), 0)
            
            detector = self.motion_detectors[name]
            
            # Инициализация фона
            if detector['background'] is None:
                detector['background'] = gray
                return False
            
            # Вычисление разности
            frame_delta = cv2.absdiff(detector['background'], gray)
            thresh = cv2.threshold(frame_delta, detector['sensitivity'], 255, cv2.THRESH_BINARY)[1]
            thresh = cv2.dilate(thresh, None, iterations=2)
            
            # Поиск контуров
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            motion_detected = False
            for contour in contours:
                if cv2.contourArea(contour) > detector['motion_threshold']:
                    motion_detected = True
                    break
            
            # Обновляем фон медленнее
            detector['background'] = cv2.addWeighted(detector['background'], 0.98, gray, 0.02, 0)
            
            return motion_detected
        except:
            return False
    
    def _is_valid_frame(self, frame):
        """Проверка качества кадра"""
        if frame is None or frame.size == 0:
            return False
        
        # Проверяем яркость (избегаем черные кадры)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mean_brightness = np.mean(gray)
        
        # Если кадр слишком темный (камера закрыта)
        if mean_brightness < 10:
            return False
        
        # Проверяем вариацию (избегаем однотонные кадры)
        variance = np.var(gray)
        if variance < 100:
            return False
        
        return True
    
    def _check_detection_cooldown(self, name):
        """Проверка кулдауна между уведомлениями"""
        detector = self.motion_detectors[name]
        current_time = time.time()
        
        if current_time - detector['last_detection'] < detector['detection_cooldown']:
            return False
        
        return True
    
    def remove_camera(self, name):
        """Удалить камеру"""
        if name in self.cameras:
            self.cameras[name]['capture'].release()
            del self.cameras[name]
            if name in self.motion_detectors:
                del self.motion_detectors[name]
            return True
        return False
    
    def start_monitoring(self):
        """Запуск мониторинга движения"""
        if not self.is_monitoring:
            self.is_monitoring = True
            threading.Thread(target=self._monitoring_loop, daemon=True).start()
    
    def stop_monitoring(self):
        """Остановка мониторинга"""
        self.is_monitoring = False
    
    def _monitoring_loop(self):
        """Основной цикл мониторинга"""
        while self.is_monitoring:
            for name, camera in self.cameras.items():
                if camera['motion_detection'] and camera['status'] == 'connected':
                    self._detect_motion(name, camera)
            time.sleep(0.1)
    
    def _detect_motion(self, name, camera):
        """Детекция движения и человека"""
        try:
            ret, frame = camera['capture'].read()
            if not ret or frame is None:
                detector = self.motion_detectors[name]
                if time.time() - detector['last_frame_time'] > 30:
                    camera['status'] = 'disconnected'
                return
            
            # Проверяем качество кадра
            if not self._is_valid_frame(frame):
                return
            
            self.motion_detectors[name]['last_frame_time'] = time.time()
            camera['status'] = 'connected'
            
            frame_resized = cv2.resize(frame, (320, 240))
            
            # Проверяем антиспам
            if not self._check_detection_cooldown(name):
                return
            
            person_detected = self._detect_person(frame_resized)
            
            if person_detected:
                motion_detected = self._check_motion(name, frame_resized)
                
                if motion_detected:
                    camera['last_motion'] = datetime.now()
                    self.motion_detectors[name]['last_detection'] = time.time()
                    self.notification_manager.add_notification(
                        'person_detected',
                        f'Обнаружен человек: {name}',
                        'high',
                        {'camera': name, 'timestamp': camera['last_motion'].isoformat()}
                    )
            
        except Exception as e:
            print(f"Motion detection error for {name}: {e}")
            camera['status'] = 'error'
    
    def get_camera_status(self):
        """Получить статус всех камер"""
        status = {}
        for name, camera in self.cameras.items():
            status[name] = {
                'url': camera['url'],
                'status': camera['status'],
                'motion_detection': camera['motion_detection'],
                'last_motion': camera['last_motion'].isoformat() if camera['last_motion'] else None
            }
        return status
    
    def get_camera_frame(self, name):
        """Получить кадр с камеры"""
        if name in self.cameras:
            camera = self.cameras[name]
            try:
                ret, frame = camera['capture'].read()
                if ret and frame is not None:
                    camera['status'] = 'connected'
                    # Кодируем в JPEG
                    _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
                    return buffer.tobytes()
                else:
                    camera['status'] = 'disconnected'
            except:
                camera['status'] = 'error'
        return None
    
    def test_camera_url(self, url):
        """Тестирование URL камеры"""
        try:
            # Преобразуем строку в число для USB камер
            if url.isdigit():
                url = int(url)
            
            cap = cv2.VideoCapture(url)
            
            # Устанавливаем таймаут
            cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            
            # Проверяем открытие
            if not cap.isOpened():
                cap.release()
                return False
            
            # Пробуем прочитать кадр
            ret, frame = cap.read()
            cap.release()
            
            return ret and frame is not None
        except Exception as e:
            print(f"Camera test error: {e}")
            return False