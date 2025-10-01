document.addEventListener('DOMContentLoaded', function() {
    const commandInput = document.getElementById('command-input');
    const sendButton = document.getElementById('send-command');
    const responseP = document.getElementById('response');
    const deviceStatusP = document.getElementById('device-status');

    loadStatus();

    sendButton.addEventListener('click', function() {
        const text = commandInput.value.trim();
        if (text) {
            sendCommand(text);
        }
    });

    function sendCommand(text) {
        fetch('/api/text_command', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: text })
        })
        .then(response => response.json())
        .then(data => {
            responseP.textContent = data.response || 'Команда выполнена';
            loadStatus();
        })
        .catch(error => {
            responseP.textContent = 'Ошибка: ' + error.message;
        });
    }

    function loadStatus() {
        fetch('/api/devices')
        .then(response => response.json())
        .then(data => {
            if (data.devices && data.devices.length > 0) {

                const rooms = {};
                data.devices.forEach(dev => {
                    const room = dev.room || 'без комнаты';
                    if (!rooms[room]) rooms[room] = {};
                    rooms[room][dev.type] = dev;
                });

                let thermometers = window.lastThermometers || {};

                deviceStatusP.innerHTML = Object.keys(rooms).map(room => {
                    let light = rooms[room].light ? (rooms[room].light.is_on ? 'включен' : 'выключен') : '-';

                    let temp = '-';
                    let hum = '-';
                    if (thermometers[room]) {
                        temp = thermometers[room].temperature + '°C';
                        hum = thermometers[room].humidity + '💧';
                    }
                    return `<b>${room}</b><br>Свет: ${light}<br>Температура: ${temp}<br>Влажность: ${hum}<br>`;
                }).join('<hr>');
            } else {
                deviceStatusP.textContent = 'Нет устройств';
            }
        })
        .catch(error => {
            deviceStatusP.textContent = 'Ошибка загрузки статуса';
        });
    }

    if (typeof EventSource !== 'undefined') {
        const sse = new EventSource('/api/devices/stream');
        sse.onmessage = (e) => {
            try {
                const state = JSON.parse(e.data);
                window.lastThermometers = state.thermometers || {};
                loadStatus();
            } catch (err) {}
        };
    }

    let mediaRecorder, chunks = [], blob = null, isRecording = false;
    const voiceRecordBtn = document.getElementById('voice-record');
    const voiceOut = document.getElementById('voice-out');

    async function startVoiceRecording() {
        if (isRecording) return;
        if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
            voiceOut.textContent = 'Ваш браузер не поддерживает запись аудио. Обновите браузер или используйте другой.';
            return;
        }
        if (location.protocol !== 'https:' && location.hostname !== 'localhost' && location.hostname !== '127.0.0.1') {
            voiceOut.textContent = 'Запись микрофона доступна только по HTTPS. Откройте сайт по защищенному адресу.';
            return;
        }
        let stream;
        try {
            stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        } catch (err) {
            const msg = (err && err.name) ? err.name : 'Неизвестная ошибка доступа к микрофону';
            voiceOut.textContent = 'Не удалось получить доступ к микрофону: ' + msg + '. Проверьте разрешения браузера и откройте сайт по HTTPS.';
            return;
        }
        mediaRecorder = new MediaRecorder(stream);
        chunks = [];
        mediaRecorder.ondataavailable = e => chunks.push(e.data);
        mediaRecorder.onstop = async () => {
            blob = new Blob(chunks, { type: (chunks[0] && chunks[0].type) || blob?.type || 'audio/webm' });

            const mime = blob.type || '';
            let ext = 'webm';
            if (mime.includes('ogg')) ext = 'ogg';
            else if (mime.includes('wav')) ext = 'wav';
            else if (mime.includes('mp4')) ext = 'm4a';
            else if (mime.includes('aac')) ext = 'aac';
            else if (mime.includes('mp3')) ext = 'mp3';

            const fileBlob = new File([blob], `recording.${ext}`, { type: mime || `audio/${ext}` });
            const form = new FormData();
            form.append('audio', fileBlob);
            const res = await fetch('/api/speech_to_action', {
                method: 'POST',
                body: form
            });
            let json;
            try { json = await res.json(); } catch(e) { json = { error: 'Не удалось распарсить ответ сервера' }; }
            voiceOut.textContent = JSON.stringify(json, null, 2);
            voiceRecordBtn.textContent = 'Записать голосовую команду';
            isRecording = false;
        };
        mediaRecorder.start();
        voiceRecordBtn.textContent = 'Идет запись... Нажмите снова, чтобы отправить';
        isRecording = true;
    }
    function stopVoiceRecording() {
        if (isRecording && mediaRecorder) {
            mediaRecorder.stop();
        }
    }
    if (voiceRecordBtn && voiceOut) {

        voiceRecordBtn.addEventListener('click', () => {
            if (!isRecording) startVoiceRecording(); else stopVoiceRecording();
        });

        voiceRecordBtn.addEventListener('touchend', (e) => {
            e.preventDefault();
            if (!isRecording) startVoiceRecording(); else stopVoiceRecording();
        }, { passive: false });
    }
});
