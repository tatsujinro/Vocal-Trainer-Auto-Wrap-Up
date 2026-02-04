import os

html_content = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Vocal Range Trainer v27.6.1 (Raw Audio)</title>
    <style>
        :root {
            --bg-color: #121212;
            --surface-color: #1e1e1e;
            --primary-color: #bb86fc;
            --secondary-color: #03dac6;
            --text-color: #e0e0e0;
            --error-color: #cf6679;
        }

        body {
            font-family: 'Segoe UI', Roboto, Helvetica, Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 20px;
            display: flex;
            flex-direction: column;
            align-items: center;
            height: 100vh;
            box-sizing: border-box;
        }

        h1 {
            font-weight: 300;
            margin-bottom: 10px;
            font-size: 1.5rem;
        }

        .version-tag {
            font-size: 0.8rem;
            color: var(--secondary-color);
            border: 1px solid var(--secondary-color);
            padding: 2px 6px;
            border-radius: 4px;
            vertical-align: middle;
            margin-left: 10px;
        }

        .main-display {
            background-color: var(--surface-color);
            padding: 20px;
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.3);
            text-align: center;
            width: 100%;
            max-width: 500px;
            margin-bottom: 20px;
        }

        .note-display {
            font-size: 4rem;
            font-weight: bold;
            color: var(--primary-color);
            min-height: 1.2em;
            text-shadow: 0 0 10px rgba(187, 134, 252, 0.3);
        }

        .freq-display {
            font-size: 1.2rem;
            color: #888;
            font-family: 'Courier New', monospace;
            margin-bottom: 10px;
        }

        .cents-display {
            font-size: 1rem;
            color: var(--secondary-color);
            height: 20px;
        }

        canvas {
            width: 100%;
            height: 150px;
            background-color: #000;
            border-radius: 8px;
            margin-top: 15px;
            border: 1px solid #333;
        }

        .controls {
            display: flex;
            gap: 15px;
            margin-bottom: 20px;
        }

        button {
            background-color: var(--primary-color);
            color: #000;
            border: none;
            padding: 10px 24px;
            border-radius: 25px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.1s, opacity 0.2s;
        }

        button:hover {
            opacity: 0.9;
        }

        button:active {
            transform: scale(0.98);
        }

        button.stop {
            background-color: var(--error-color);
            color: white;
        }

        .status-bar {
            font-size: 0.9rem;
            color: #666;
            margin-top: 10px;
        }
        
        /* 音準偏差視覺化 */
        .tuner-bar-container {
            width: 80%;
            height: 10px;
            background-color: #333;
            border-radius: 5px;
            margin: 10px auto;
            position: relative;
            overflow: hidden;
        }
        
        .tuner-center-line {
            position: absolute;
            left: 50%;
            top: 0;
            bottom: 0;
            width: 2px;
            background-color: #fff;
            transform: translateX(-50%);
            z-index: 2;
        }
        
        .tuner-indicator {
            position: absolute;
            top: 0;
            bottom: 0;
            width: 10px;
            background-color: var(--secondary-color);
            left: 50%; 
            border-radius: 50%;
            transform: translateX(-50%);
            transition: left 0.1s ease-out;
        }
    </style>
</head>
<body>

    <h1>Vocal Trainer <span class="version-tag">v27.6.1 Raw</span></h1>

    <div class="main-display">
        <div class="note-display" id="note">--</div>
        <div class="freq-display"><span id="frequency">0.0</span> Hz</div>
        
        <div class="tuner-bar-container">
            <div class="tuner-center-line"></div>
            <div class="tuner-indicator" id="tuner-dot"></div>
        </div>
        <div class="cents-display" id="cents"></div>

        <canvas id="visualizer"></canvas>
    </div>

    <div class="controls">
        <button id="startBtn" onclick="startAudio()">開啟麥克風 (Raw)</button>
        <button id="stopBtn" class="stop" onclick="stopAudio()" disabled>停止</button>
    </div>

    <div class="status-bar" id="status">準備就緒，請點擊開啟麥克風。</div>

    <script>
        let audioContext;
        let analyser;
        let microphoneStream;
        let source;
        let isRunning = false;
        
        // 繪圖變數
        let canvas, canvasCtx;
        let dataArray;
        let bufferLength;

        const noteStrings = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"];

        window.onload = () => {
            canvas = document.getElementById("visualizer");
            canvasCtx = canvas.getContext("2d");
            canvas.width = canvas.offsetWidth;
            canvas.height = canvas.offsetHeight;
            
            window.addEventListener('resize', () => {
                canvas.width = canvas.offsetWidth;
                canvas.height = canvas.offsetHeight;
            });
        };

        async function startAudio() {
            if (isRunning) return;

            // --- v27.6.1 修正：強制請求原始訊號 ---
            // 這些設定對於繞過 MacOS/iOS 的語音處理至關重要
            const audioConstraints = {
                audio: {
                    echoCancellation: false,  // 關閉回音消除
                    noiseSuppression: false,  // 關閉降噪 (這是高頻殺手)
                    autoGainControl: false,   // 關閉自動增益
                    channelCount: 1           // 單聲道
                }
            };

            try {
                updateStatus("正在請求 Raw Audio 麥克風權限...");
                microphoneStream = await navigator.mediaDevices.getUserMedia(audioConstraints);
                
                // 嘗試使用 48kHz 採樣率
                audioContext = new (window.AudioContext || window.webkitAudioContext)({
                    sampleRate: 48000
                });

                source = audioContext.createMediaStreamSource(microphoneStream);
                analyser = audioContext.createAnalyser();
                analyser.fftSize = 2048;
                bufferLength = analyser.frequencyBinCount;
                dataArray = new Uint8Array(bufferLength);

                // --- v27.6.1 修正：Bypass 濾波器 ---
                // 這裡不再創建 lowPassFilter，直接將 source 連接到 analyser
                // 原本是: source -> filter -> analyser
                // 現在是: source -> analyser (直通)
                source.connect(analyser); 

                isRunning = true;
                document.getElementById("startBtn").disabled = true;
                document.getElementById("stopBtn").disabled = false;
                updateStatus("監聽中 - 原始音訊模式 (無濾波)");

                detectPitch();
                drawVisualizer();

            } catch (err) {
                console.error("麥克風啟動失敗:", err);
                updateStatus("錯誤: 無法存取麥克風，請檢查權限。");
            }
        }

        function stopAudio() {
            if (!isRunning) return;
            
            if (source) source.disconnect();
            if (analyser) analyser.disconnect();
            if (microphoneStream) {
                microphoneStream.getTracks().forEach(track => track.stop());
            }
            if (audioContext && audioContext.state !== 'closed') {
                audioContext.close();
            }

            isRunning = false;
            document.getElementById("startBtn").disabled = false;
            document.getElementById("stopBtn").disabled = true;
            
            document.getElementById("note").innerText = "--";
            document.getElementById("frequency").innerText = "0.0";
            document.getElementById("cents").innerText = "";
            moveTunerIndicator(0);
            
            canvasCtx.fillStyle = '#000';
            canvasCtx.fillRect(0, 0, canvas.width, canvas.height);
            
            updateStatus("已停止");
        }

        function detectPitch() {
            if (!isRunning) return;

            const buffer = new Float32Array(analyser.fftSize);
            analyser.getFloatTimeDomainData(buffer);
            
            const fundamentalFreq = autoCorrelate(buffer, audioContext.sampleRate);
            updateDisplay(fundamentalFreq);
            requestAnimationFrame(detectPitch);
        }

        function autoCorrelate(buf, sampleRate) {
            let SIZE = buf.length;
            let rms = 0;

            for (let i = 0; i < SIZE; i++) {
                let val = buf[i];
                rms += val * val;
            }
            rms = Math.sqrt(rms / SIZE);

            if (rms < 0.01) return -1; 

            let r1 = 0, r2 = SIZE - 1, thres = 0.2;
            for (let i = 0; i < SIZE / 2; i++) {
                if (Math.abs(buf[i]) < thres) { r1 = i; break; }
            }
            for (let i = 1; i < SIZE / 2; i++) {
                if (Math.abs(buf[SIZE - i]) < thres) { r2 = SIZE - i; break; }
            }

            buf = buf.slice(r1, r2);
            SIZE = buf.length;

            let c = new Array(SIZE).fill(0);
            for (let i = 0; i < SIZE; i++) {
                for (let j = 0; j < SIZE - i; j++) {
                    c[i] = c[i] + buf[j] * buf[j + i];
                }
            }

            let d = 0; while (c[d] > c[d + 1]) d++;
            let maxval = -1, maxpos = -1;
            for (let i = d; i < SIZE; i++) {
                if (c[i] > maxval) {
                    maxval = c[i];
                    maxpos = i;
                }
            }
            let T0 = maxpos;

            let x1 = c[T0 - 1], x2 = c[T0], x3 = c[T0 + 1];
            let a = (x1 + x3 - 2 * x2) / 2;
            let b = (x3 - x1) / 2;
            if (a) T0 = T0 - b / (2 * a);

            return sampleRate / T0;
        }

        function updateDisplay(frequency) {
            const noteDiv = document.getElementById("note");
            const freqDiv = document.getElementById("frequency");
            const centsDiv = document.getElementById("cents");

            if (frequency === -1 || frequency < 50 || frequency > 3000) { 
                return;
            }

            freqDiv.innerText = frequency.toFixed(1);

            const noteInfo = getNote(frequency);
            noteDiv.innerText = noteInfo.note;
            
            const centsOff = noteInfo.cents;
            const centsText = centsOff > 0 ? `+${centsOff}` : centsOff;
            centsDiv.innerText = `${centsText} cents`;
            
            moveTunerIndicator(centsOff);

            if (Math.abs(centsOff) < 10) {
                noteDiv.style.color = "#03dac6";
            } else {
                noteDiv.style.color = "#bb86fc";
            }
        }

        function getNote(frequency) {
            const noteNum = 12 * (Math.log(frequency / 440) / Math.log(2));
            const midiNum = Math.round(noteNum) + 69;
            const note = noteStrings[midiNum % 12];
            const octave = Math.floor(midiNum / 12) - 1;
            
            const desiredFreq = 440 * Math.pow(2, (midiNum - 69) / 12);
            const cents = Math.floor(1200 * Math.log(frequency / desiredFreq) / Math.log(2));

            return {
                note: note + octave,
                cents: cents
            };
        }
        
        function moveTunerIndicator(cents) {
            let visualCents = Math.max(-50, Math.min(50, cents));
            let percent = ((visualCents + 50) / 100) * 100;
            
            const dot = document.getElementById('tuner-dot');
            dot.style.left = `${percent}%`;
            
            if (Math.abs(visualCents) < 5) {
                dot.style.backgroundColor = '#03dac6';
            } else {
                dot.style.backgroundColor = '#cf6679';
            }
        }

        function updateStatus(msg) {
            document.getElementById("status").innerText = msg;
        }

        function drawVisualizer() {
            if (!isRunning) return;
            requestAnimationFrame(drawVisualizer);

            analyser.getByteTimeDomainData(dataArray);

            canvasCtx.fillStyle = '#1e1e1e';
            canvasCtx.fillRect(0, 0, canvas.width, canvas.height);

            canvasCtx.lineWidth = 2;
            canvasCtx.strokeStyle = '#bb86fc';
            canvasCtx.beginPath();

            const sliceWidth = canvas.width * 1.0 / bufferLength;
            let x = 0;

            for (let i = 0; i < bufferLength; i++) {
                const v = dataArray[i] / 128.0;
                const y = v * canvas.height / 2;

                if (i === 0) {
                    canvasCtx.moveTo(x, y);
                } else {
                    canvasCtx.lineTo(x, y);
                }

                x += sliceWidth;
            }

            canvasCtx.lineTo(canvas.width, canvas.height / 2);
            canvasCtx.stroke();
        }
    </script>
</body>
</html>
"""

# 將內容寫入 HTML 檔案
filename = "vocal_trainer_v27.6.1.html"
with open(filename, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"成功生成檔案: {filename}")
print("請在瀏覽器中打開此檔案，並記得檢查 MacOS/iOS 控制中心的麥克風模式設為「標準」。")
