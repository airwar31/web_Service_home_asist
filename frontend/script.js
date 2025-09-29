class SmartHomeController {
    constructor() {
        this.devices = {
            light: { status: false, brightness: 50 },
            temperature: { value: 22 },
            security: { status: false },
            music: { status: false, volume: 30, bluetooth_connected: false, bluetooth_device: null }
        };
        
        this.recognition = null;
        this.isListening = false;
        this.initSpeechRecognition();
        this.initEventListeners();
        this.loadDevicesState();
    }

    async loadDevicesState() {
        try {
            const response = await fetch('/api/devices');
            if (response.ok) {
                this.devices = await response.json();
                this.updateAllUI();
            }
        } catch (error) {
            console.error('Ошибка загрузки состояния устройств:', error);
        }
    }

    async updateDevice(device, data) {
        try {
            const response = await fetch(`/api/devices/${device}`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            });
            const result = await response.json();
            if (result.success) {
                this.devices[device] = result.state;
                this.updateDeviceUI(device);
            }
        } catch (error) {
            console.error('Ошибка обновления устройства:', error);
        }
    }

    initSpeechRecognition() {
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.recognition.lang = 'ru-RU';
            this.recognition.continuous = false;
            this.recognition.interimResults = false;

            this.recognition.onstart = () => {
                this.isListening = true;
                this.updateVoiceButton();
                document.getElementById('voiceStatus').textContent = 'Слушаю...';
                this.startVoiceAnimation();
                this.startVoiceReactiveAnimation();
            };

            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript.toLowerCase();
                this.processVoiceCommand(transcript);
            };

            this.recognition.onend = () => {
                this.isListening = false;
                this.updateVoiceButton();
                document.getElementById('voiceStatus').textContent = 'Голосовой помощник готов';
                this.stopVoiceAnimation();
            };

            this.recognition.onerror = () => {
                this.isListening = false;
                this.updateVoiceButton();
                document.getElementById('voiceStatus').textContent = 'Голосовой помощник готов';
                this.stopVoiceAnimation();
            };
        }
    }

    initEventListeners() {
        // Навигация
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const sectionId = e.currentTarget.dataset.section;
                this.showSection(sectionId);
                this.setActiveNav(e.currentTarget);
            });
        });

        // Голосовое управление
        document.getElementById('voiceBtn').addEventListener('click', () => {
            this.toggleVoiceRecognition();
        });

        // Устройства
        document.querySelectorAll('.toggle-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const device = e.target.closest('.device-card').dataset.device;
                this.handleDeviceToggle(device, e.target);
            });
        });

        document.querySelectorAll('.temp-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.target.dataset.action;
                this.adjustTemperature(action);
            });
        });

        document.querySelectorAll('.brightness, .volume').forEach(slider => {
            slider.addEventListener('input', (e) => {
                const device = e.target.closest('.device-card').dataset.device;
                const value = parseInt(e.target.value);
                this.updateSlider(device, value);
                this.updateValueDisplay(e.target, value);
            });
        });

        // Настройки
        document.getElementById('themeToggle').addEventListener('change', (e) => {
            this.toggleTheme(e.target.checked);
        });

        document.getElementById('languageSelect').addEventListener('change', (e) => {
            this.changeLanguage(e.target.value);
        });
        
        // Bluetooth управление
        document.getElementById('bluetoothBtn').addEventListener('click', () => {
            this.handleBluetoothToggle();
        });
    }

    toggleVoiceRecognition() {
        if (!this.recognition) return;

        if (this.isListening) {
            this.recognition.stop();
        } else {
            this.recognition.start();
        }
    }

    updateVoiceButton() {
        const btn = document.getElementById('voiceBtn');
        btn.classList.toggle('listening', this.isListening);
    }

    startVoiceAnimation() {
        const btn = document.getElementById('voiceBtn');
        btn.style.animation = 'voicePulse 1.5s infinite';
    }

    startVoiceReactiveAnimation() {
        const btn = document.getElementById('voiceBtn');
        // Симуляция реакции на голос
        this.voiceReactiveInterval = setInterval(() => {
            const intensity = Math.random() * 0.5 + 0.5;
            btn.style.boxShadow = `0 0 ${30 + intensity * 30}px rgba(76, 205, 196, ${0.3 + intensity * 0.5})`;
        }, 100);
    }

    stopVoiceAnimation() {
        const btn = document.getElementById('voiceBtn');
        btn.style.animation = '';
        if (this.voiceReactiveInterval) {
            clearInterval(this.voiceReactiveInterval);
        }
        btn.style.boxShadow = '';
    }

    async processVoiceCommand(command) {
        try {
            const response = await fetch('/api/voice-command', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command })
            });
            const result = await response.json();
            if (result.success) {
                this.devices = result.devices;
                this.updateAllUI();
                this.speak(result.response);
            }
        } catch (error) {
            console.error('Ошибка обработки голосовой команды:', error);
            this.speak('Ошибка обработки команды');
        }
    }

    speak(text) {
        if ('speechSynthesis' in window) {
            const utterance = new SpeechSynthesisUtterance(text);
            utterance.lang = 'ru-RU';
            utterance.rate = 0.8;
            speechSynthesis.speak(utterance);
        }
    }

    async handleDeviceToggle(device, button) {
        const newStatus = !this.devices[device].status;
        await this.updateDevice(device, { status: newStatus });
    }

    async adjustTemperature(action) {
        let newValue = this.devices.temperature.value;
        if (action === 'increase' && newValue < 30) {
            newValue++;
        } else if (action === 'decrease' && newValue > 15) {
            newValue--;
        }
        await this.updateDevice('temperature', { value: newValue });
    }

    async updateSlider(device, value) {
        if (device === 'light') {
            await this.updateDevice('light', { brightness: value });
        } else if (device === 'music') {
            await this.updateDevice('music', { volume: value });
        }
    }

    updateValueDisplay(slider, value) {
        const display = slider.parentElement.querySelector('.value-display');
        if (display) {
            display.textContent = `${value}%`;
        }
    }

    updateAllUI() {
        this.updateDeviceUI('light');
        this.updateDeviceUI('temperature');
        this.updateDeviceUI('security');
        this.updateDeviceUI('music');
    }

    showSection(sectionId) {
        document.querySelectorAll('.section').forEach(section => {
            section.classList.add('hidden');
        });
        document.getElementById(sectionId).classList.remove('hidden');
    }

    setActiveNav(activeBtn) {
        document.querySelectorAll('.nav-btn').forEach(btn => {
            btn.classList.remove('active');
        });
        activeBtn.classList.add('active');
        
        // Динамическая анимация индикатора
        const buttons = Array.from(document.querySelectorAll('.nav-btn'));
        const activeIndex = buttons.indexOf(activeBtn);
        const indicator = document.querySelector('.nav-indicator');
        const nav = document.querySelector('.bottom-nav');
        const navPadding = parseInt(getComputedStyle(nav).paddingLeft);
        const gap = parseInt(getComputedStyle(nav).gap) || 5;
        
        // Рассчитываем позицию и размеры
        const buttonWidth = activeBtn.offsetWidth;
        const buttonHeight = activeBtn.offsetHeight;
        let offset = navPadding;
        
        for (let i = 0; i < activeIndex; i++) {
            offset += buttons[i].offsetWidth + gap;
        }
        
        // Применяем стили
        indicator.style.width = `${buttonWidth}px`;
        indicator.style.height = `${buttonHeight}px`;
        indicator.style.left = `${offset}px`;
        indicator.style.top = `${navPadding}px`;
        indicator.style.transform = 'none';
    }

    toggleTheme(isLight) {
        document.body.classList.toggle('light', isLight);
        localStorage.setItem('theme', isLight ? 'light' : 'dark');
    }

    changeLanguage(lang) {
        // Базовая смена языка
        if (this.recognition) {
            this.recognition.lang = lang === 'ru' ? 'ru-RU' : 'en-US';
        }
        localStorage.setItem('language', lang);
    }

    loadSettings() {
        const savedTheme = localStorage.getItem('theme');
        const savedLang = localStorage.getItem('language');
        
        if (savedTheme === 'light') {
            document.body.classList.add('light');
            document.getElementById('themeToggle').checked = true;
        }
        
        if (savedLang) {
            document.getElementById('languageSelect').value = savedLang;
            if (this.recognition) {
                this.recognition.lang = savedLang === 'ru' ? 'ru-RU' : 'en-US';
            }
        }
    }

    updateDeviceUI(device) {
        const card = document.querySelector(`[data-device="${device}"]`);
        if (!card) return;

        switch (device) {
            case 'light':
                const lightBtn = card.querySelector('.toggle-btn');
                const brightnessSlider = card.querySelector('.brightness');
                const brightnessDisplay = card.querySelector('.value-display');
                
                lightBtn.classList.toggle('active', this.devices.light.status);
                lightBtn.textContent = this.devices.light.status ? 'Включен' : 'Выключен';
                brightnessSlider.value = this.devices.light.brightness;
                brightnessDisplay.textContent = `${this.devices.light.brightness}%`;
                break;

            case 'temperature':
                const tempDisplay = card.querySelector('.temp-display');
                tempDisplay.textContent = `${this.devices.temperature.value}°C`;
                break;

            case 'security':
                const securityBtn = card.querySelector('.toggle-btn');
                const securityStatus = card.querySelector('.status');
                
                securityBtn.classList.toggle('active', this.devices.security.status);
                securityBtn.textContent = this.devices.security.status ? 'Включена' : 'Отключена';
                securityStatus.textContent = this.devices.security.status ? 'Система активна' : 'Система отключена';
                break;

            case 'music':
                const musicBtn = card.querySelector('.toggle-btn');
                const volumeSlider = card.querySelector('.volume');
                const volumeDisplay = card.querySelector('.value-display');
                const bluetoothStatus = card.querySelector('#bluetoothStatus');
                
                musicBtn.classList.toggle('active', this.devices.music.status);
                musicBtn.textContent = this.devices.music.status ? 'Играет' : 'Остановлена';
                volumeSlider.value = this.devices.music.volume;
                volumeDisplay.textContent = `${this.devices.music.volume}%`;
                
                // Обновляем Bluetooth статус
                if (this.devices.music.bluetooth_connected && this.devices.music.bluetooth_device) {
                    bluetoothStatus.textContent = `Подключен: ${this.devices.music.bluetooth_device}`;
                    bluetoothStatus.style.color = '#4CAF50';
                } else {
                    bluetoothStatus.textContent = 'Не подключен';
                    bluetoothStatus.style.color = '#888';
                }
                break;
        }
    }
    
    async handleBluetoothToggle() {
        try {
            if (this.devices.music.bluetooth_connected) {
                // Отключаем
                const response = await fetch('/api/bluetooth/disconnect', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ device_name: this.devices.music.bluetooth_device })
                });
                const result = await response.json();
                if (result.success) {
                    this.devices.music.bluetooth_connected = false;
                    this.devices.music.bluetooth_device = null;
                    this.updateDeviceUI('music');
                    this.speak('Отключено от Bluetooth устройства');
                }
            } else {
                // Сканируем и подключаем
                const scanResponse = await fetch('/api/bluetooth/scan');
                const scanResult = await scanResponse.json();
                
                if (scanResult.devices && scanResult.devices.length > 0) {
                    // Подключаемся к первому найденному устройству
                    const device = scanResult.devices[0];
                    const connectResponse = await fetch('/api/bluetooth/connect', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ device_name: device.name })
                    });
                    const connectResult = await connectResponse.json();
                    
                    if (connectResult.success) {
                        this.devices.music.bluetooth_connected = true;
                        this.devices.music.bluetooth_device = device.name;
                        this.updateDeviceUI('music');
                        this.speak(`Подключено к ${device.name}`);
                    }
                } else {
                    this.speak('Не найдено Bluetooth устройств');
                }
            }
        } catch (error) {
            console.error('Ошибка Bluetooth:', error);
            this.speak('Ошибка подключения Bluetooth');
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const controller = new SmartHomeController();
    controller.loadSettings();
});