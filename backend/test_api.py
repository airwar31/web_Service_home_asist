#!/usr/bin/env python3
"""
Простые тесты для проверки работы API
"""

import requests
import json

BASE_URL = 'http://localhost:5000/api'

def test_api_status():
    """Тест статуса API"""
    try:
        response = requests.get(f'{BASE_URL}/status')
        print(f"API Status: {response.status_code}")
        print(f"Response: {response.json()}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error testing API status: {e}")
        return False

def test_get_devices():
    """Тест получения устройств"""
    try:
        response = requests.get(f'{BASE_URL}/devices')
        print(f"Get Devices: {response.status_code}")
        print(f"Devices: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error getting devices: {e}")
        return False

def test_update_light():
    """Тест обновления освещения"""
    try:
        data = {'status': True, 'brightness': 75}
        response = requests.post(f'{BASE_URL}/devices/light', json=data)
        print(f"Update Light: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error updating light: {e}")
        return False

def test_voice_command():
    """Тест голосовой команды"""
    try:
        data = {'command': 'включи свет'}
        response = requests.post(f'{BASE_URL}/voice-command', json=data)
        print(f"Voice Command: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
        return response.status_code == 200
    except Exception as e:
        print(f"Error with voice command: {e}")
        return False

if __name__ == '__main__':
    print("🧪 Тестирование Smart Home API...")
    print("=" * 50)
    
    tests = [
        ("API Status", test_api_status),
        ("Get Devices", test_get_devices),
        ("Update Light", test_update_light),
        ("Voice Command", test_voice_command)
    ]
    
    passed = 0
    for test_name, test_func in tests:
        print(f"\n🔍 {test_name}:")
        if test_func():
            print("✅ PASSED")
            passed += 1
        else:
            print("❌ FAILED")
    
    print(f"\n📊 Результат: {passed}/{len(tests)} тестов прошли успешно")