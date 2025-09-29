import cv2
import sys

def test_camera(camera_id):
    """Простой тест камеры"""
    try:
        print(f"Тестирование камеры: {camera_id}")
        
        # Преобразуем в число если это цифра
        if str(camera_id).isdigit():
            camera_id = int(camera_id)
        
        cap = cv2.VideoCapture(camera_id)
        
        if not cap.isOpened():
            print("❌ Не удалось открыть камеру")
            return False
        
        print("✅ Камера открыта")
        
        # Пробуем прочитать кадр
        ret, frame = cap.read()
        
        if ret and frame is not None:
            print(f"✅ Кадр получен: {frame.shape}")
            
            # Показываем кадр на 3 секунды
            cv2.imshow('Camera Test', frame)
            cv2.waitKey(3000)
            cv2.destroyAllWindows()
            
            cap.release()
            return True
        else:
            print("❌ Не удалось получить кадр")
            cap.release()
            return False
            
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        return False

if __name__ == "__main__":
    # Тестируем USB камеры
    print("=== Тест USB камер ===")
    for i in range(3):
        print(f"\nТест камеры {i}:")
        if test_camera(i):
            print(f"✅ Камера {i} работает!")
            break
    else:
        print("❌ USB камеры не найдены")
    
    # Можно добавить свой URL для теста
    if len(sys.argv) > 1:
        custom_url = sys.argv[1]
        print(f"\n=== Тест пользовательского URL ===")
        print(f"URL: {custom_url}")
        test_camera(custom_url)