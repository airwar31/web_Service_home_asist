import cv2
import numpy as np

def test_person_detection():
    """Тест детекции человека"""
    print("=== Тест детекции человека ===")
    
    # Инициализация HOG детектора
    hog = cv2.HOGDescriptor()
    hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
    
    # Подключение к камере
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Не удалось открыть камеру")
        return
    
    print("✅ Камера открыта")
    print("📹 Нажмите 'q' для выхода")
    print("🚶 Встаньте перед камерой для тестирования")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Уменьшаем размер для быстрой обработки
        frame_small = cv2.resize(frame, (320, 240))
        
        # Детекция людей
        boxes, weights = hog.detectMultiScale(
            frame_small,
            winStride=(8, 8),
            padding=(32, 32),
            scale=1.05
        )
        
        # Масштабируем обратно для отображения
        scale_x = frame.shape[1] / 320
        scale_y = frame.shape[0] / 240
        
        person_detected = False
        
        # Рисуем прямоугольники вокруг людей
        for i, (x, y, w, h) in enumerate(boxes):
            if weights[i] > 0.5:  # Порог уверенности
                person_detected = True
                
                # Масштабируем координаты
                x = int(x * scale_x)
                y = int(y * scale_y)
                w = int(w * scale_x)
                h = int(h * scale_y)
                
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.putText(frame, f'Person {weights[i]:.2f}', 
                           (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        # Показываем статус
        status = "ЧЕЛОВЕК ОБНАРУЖЕН!" if person_detected else "Человек не обнаружен"
        color = (0, 255, 0) if person_detected else (0, 0, 255)
        cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, color, 2)
        
        cv2.imshow('Person Detection Test', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("✅ Тест завершен")

if __name__ == "__main__":
    test_person_detection()