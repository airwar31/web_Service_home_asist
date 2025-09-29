import subprocess
import time
import os

def start_server(script_name, port):
    """Запуск сервера в отдельном процессе"""
    print(f"Запуск {script_name} на порту {port}...")
    return subprocess.Popen(['python', script_name], cwd=os.getcwd())

def main():
    servers = []
    
    try:
        # Запуск главного сервера
        servers.append(start_server('app.py', 5000))
        time.sleep(2)
        
        # Запуск серверов устройств
        device_servers = [
            ('device_servers/light_server.py', 5001),
            ('device_servers/temperature_server.py', 5002),
            ('device_servers/security_server.py', 5003),
            ('device_servers/music_server.py', 5004),
            ('device_servers/dashboard_server.py', 5005)
        ]
        
        for script, port in device_servers:
            servers.append(start_server(script, port))
            time.sleep(1)
        
        print("\nВсе серверы запущены!")
        print("Главный сервер: http://localhost:5000")
        print("Лампочка: http://localhost:5001")
        print("Температура: http://localhost:5002")
        print("Безопасность: http://localhost:5003")
        print("Музыка: http://localhost:5004")
        print("Панель управления: http://localhost:5005")
        print("\nНажмите Ctrl+C для остановки всех серверов")
        
        # Ожидание завершения
        for server in servers:
            server.wait()
            
    except KeyboardInterrupt:
        print("\nОстановка серверов...")
        for server in servers:
            server.terminate()
        print("Все серверы остановлены")

if __name__ == '__main__':
    main()