import cv2
import numpy as np

def debug_camera():
    """Отладка камеры с проверкой качества кадра"""
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Камера не найдена")
        return
    
    print("📹 Отладка камеры (нажмите 'q' для выхода)")
    print("🔍 Проверка качества кадров...")
    
    while True:
        ret, frame = cap.read()
        
        if not ret or frame is None:
            print("❌ Не удалось получить кадр")
            continue
        
        # Анализ кадра
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        mean_brightness = np.mean(gray)
        variance = np.var(gray)
        
        # Проверки качества
        is_too_dark = mean_brightness < 10
        is_monotone = variance < 100
        is_valid = not (is_too_dark or is_monotone)
        
        # Отображение информации
        info_text = [
            f"Яркость: {mean_brightness:.1f}",
            f"Вариация: {variance:.1f}",
            f"Статус: {'✅ ВАЛИДНЫЙ' if is_valid else '❌ НЕВАЛИДНЫЙ'}",
        ]
        
        if is_too_dark:
            info_text.append("⚠️ СЛИШКОМ ТЕМНО")
        if is_monotone:
            info_text.append("⚠️ ОДНОТОННЫЙ")
        
        # Рисуем информацию на кадре
        y_offset = 30
        for text in info_text:
            color = (0, 255, 0) if is_valid else (0, 0, 255)
            cv2.putText(frame, text, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            y_offset += 30
        
        # Показываем кадр
        cv2.imshow('Camera Debug', frame)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    cap.release()
    cv2.destroyAllWindows()
    print("✅ Отладка завершена")

if __name__ == "__main__":
    debug_camera()