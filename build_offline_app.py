import urllib.request
import os
import ssl

print("🚀 正在開始打包您的離線版聲樂教練 (v25 權限與音質修復版)...")

# 1. 忽略 SSL 驗證
ssl_context = ssl._create_unverified_context()

# 2. 定義資源
PLAYER_URL = "https://surikov.github.io/webaudiofont/npm/dist/WebAudioFontPlayer.js"
PIANO_URL = "https://surikov.github.io/webaudiofontdata/sound/0000_JCLive_sf2_file.js"

# 3. 下載資源
try:
    print("📥 下載播放引擎...")
    with urllib.request.urlopen(PLAYER_URL, context=ssl_context) as response:
        player_code = response.read().decode('utf-8')
    
    print("📥 下載鋼琴音色庫...")
    with urllib.request.urlopen(PIANO_URL, context=ssl_context) as response:
        piano_code = response.read().decode('utf-8')
        
    if len(piano_code) < 50000:
        print("⚠️ 警告：音色庫檔案過小，可能下載不完整。")
    else:
        print("✅ 音色庫下載完成！")
        
except Exception as e:
    print(f"❌ 下載失敗: {e}")
    exit()

# 4. HTML 模板
html_template = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>Daily Vocal Workout</title>
    <style>
        :root { --bg-color: #121212; --card-bg: #1e1e1e; --text-main: #e0e0e0; --accent: #40c4ff; --accent-dark: #0094cc; --pitch-target: #2979ff; --pitch-user: #ffea00; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: var(--bg-color); color: var(--text-main); margin: 0; padding: 20px; text-align: center; user-select: none; padding-bottom: 120px; }
        h1 { color: var(--accent); margin-bottom: 5px; font-size: 1.5rem; }
        p { color: #888; margin-top: 0; font-size: 0.9rem; }
        
        .control-panel { background: var(--card-bg); border-radius: 16px; padding: 20px; margin-bottom: 20px; border: 1px solid #333; }
        
        .pitch-monitor {
            background: #000; border: 2px solid #333; border-radius: 12px; height: 120px; 
            margin-bottom: 15px; position: relative; overflow: hidden; display: flex; align-items: center; justify-content: center;
        }
        .pitch-monitor.active { border-color: var(--accent); }
        
        .note-marker {
            position: absolute; width: 60px; height: 60px; border-radius: 50%; 
            display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 1.2rem;
            transition: left 0.1s ease-out; top: 30px;
        }
        .target-marker { background: var(--pitch-target); color: white; border: 3px solid white; z-index: 10; opacity: 0.3; }
        .target-marker.active { opacity: 1; box-shadow: 0 0 15px var(--pitch-target); }
        .user-marker { background: var(--pitch-user); color: black; border: 3px solid white; z-index: 20; opacity: 0; transform: scale(0.8); }
        .user-marker.singing { opacity: 1; transform: scale(1); }
        
        .judge-text { position: absolute; top: 5px; width: 100%; text-align: center; font-size: 0.9rem; font-weight: bold; color: #555; }
        .judge-text.match { color: var(--accent); text-shadow: 0 0 10px var(--accent); font-size: 1.2rem; }

        .audio-player-container { margin-top: 15px; display: none; }
        audio { width: 100%; height: 40px; margin-top: 5px; }
        
        .range-selectors { display: flex; gap: 8px; margin-bottom: 20px; }
        .range-col { flex: 1; display: flex; flex-direction: column; gap: 5px; }
        .range-col label { font-size: 0.8rem; color: #888; text-align: center; margin: 0; }
        select { background: #333; color: white; border: 1px solid #444; padding: 8px; width: 100%; border-radius: 6px; font-size: 1rem; text-align: center; }
        
        .tabs { display: flex; gap: 8px; margin-bottom: 15px; background: #111; padding: 10px; border-radius: 12px; flex-wrap: wrap; justify-content: center; }
        .tab-btn { 
            background: transparent; color: #666; padding: 8px 12px; border: 1px solid #333; 
            border-radius: 8px; cursor: pointer; transition: 0.2s; font-weight: 600; font-size: 0.85rem;
            min-width: 80px; flex: 1 1 30%; 
        }
        .tab-btn.active { background: var(--card-bg); color: var(--accent); border-color: var(--accent); box-shadow: 0 2px 8px rgba(0,0,0,0.3); }
        
        .add-btn {
            background: #333; color: white; border: 1px solid #555; padding: 12px; width: 100%; 
            border-radius: 8px; margin-bottom: 20px; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 10px; font-weight: bold;
        }
        
        .routine-container { text-align: left; margin-bottom: 20px; }
        .routine-header { font-size: 0.9rem; color: #888; margin-bottom: 10px; display: flex; justify-content: space-between; }
        .routine-list { list-style: none; padding: 0; margin: 0; min-height: 50px; background: #111; border-radius: 12px; padding: 10px; }
        .routine-item { 
            background: #222; margin-bottom: 8px; padding: 10px; border-radius: 8px; 
            display: flex; justify-content: space-between; align-items: center; border-left: 4px solid #444;
        }
        .routine-item.active { border-left-color: var(--accent); background: #1a2a1a; }
        .routine-info { font-size: 0.9rem; }
        .routine-range { font-size: 0.75rem; color: #888; font-family: monospace; margin-top: 3px; }
        .delete-btn { background: none; border: none; color: #666; font-size: 1.2rem; cursor: pointer; padding: 0 10px; }
        
        .play-btn { 
            background: var(--accent); color: #000; border: none; padding: 18px 40px; border-radius: 50px; 
            font-size: 1.2rem; font-weight: 800; width: 100%; letter-spacing: 1px;
            box-shadow: 0 0 20px rgba(64, 196, 255, 0.4); transition: transform 0.1s;
            position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%); width: 90%; max-width: 400px; z-index: 100;
        }
        .play-btn:active { transform: translateX(-50%) scale(0.96); }
        .play-btn.stop { background: #ff5252; color: white; box-shadow: none; }
        
        .slider-group { margin-bottom: 10px; text-align: left; }
        .slider-label-row { display: flex; justify-content: space-between; margin-bottom: 5px; color: #bbb; font-size: 0.9rem; }
        .val-display { color: var(--accent); font-weight: bold; font-family: monospace; }
        input[type="range"] { width: 100%; height: 6px; background: #444; border-radius: 5px; outline: none; -webkit-appearance: none; }
        input[type="range"]::-webkit-slider-thumb { -webkit-appearance: none; width: 20px; height: 20px; background: white; border: 2px solid var(--accent); border-radius: 50%; cursor: pointer; margin-top: -7px; }
        
        .loading-mask { position: fixed; top:0; left:0; width:100%; height:100%; background: #121212; z-index: 999; display: flex; justify-content: center; align-items: center; color: white; flex-direction: column; }
    </style>
</head>
<body>

    <div id="loadingMask" class="loading-mask">
        <div style="font-size: 2rem; margin-bottom: 10px;">⚡</div>
        <div>v25 權限修復版...</div>
        <div style="font-size: 0.8rem; color: #888; margin-top:5px;">請務必佩戴耳機</div>
        <div id="errorDisplay" style="color:red; margin-top:20px; font-size:0.8rem; padding:20px;"></div>
    </div>

    <h1>聲樂教練 Pro</h1>
    <p>Hi-Fi 音質 & 秒開權限</p>

    <div class="pitch-monitor" id="pitchMonitor">
        <div class="judge-text" id="judgeText">等待開始...</div>
        <div class="note-marker target-marker" id="targetMarker">C4</div>
        <div class="note-marker user-marker" id="userMarker">?</div>
        <div style="position: absolute; bottom: 5px; width: 100%; display: flex; justify-content: space-around; font-size: 0.7rem; color: #333;">
            <span>Low</span><span>Pitch</span><span>High</span>
        </div>
    </div>

    <div id="audioContainer" class="audio-player-container">
        <div style="font-size: 0.9rem; color: var(--accent);">🎵 練習回放：</div>
        <audio id="playbackAudio" controls></audio>
        <a id="downloadLink" style="display:block; margin-top:5px; color:#888; font-size:0.8rem;" href="#">下載錄音</a>
    </div>

    <div class="control-panel">
        <div class="tabs">
            <button id="btn-triad" class="tab-btn active" onclick="switchConfigMode('triad')">大三和弦</button>
            <button id="btn-scale5" class="tab-btn" onclick="switchConfigMode('scale5')">五度音階</button>
            <button id="btn-octave" class="tab-btn" onclick="switchConfigMode('octave')">八度音程</button>
            <button id="btn-p5" class="tab-btn" onclick="switchConfigMode('p5')">五度音程</button>
            <button id="btn-p4" class="tab-btn" onclick="switchConfigMode('p4')">四度音程</button>
        </div>

        <div class="range-selectors">
            <div class="range-col"><label>起始</label><select id="startNote"></select></div>
            <div class="range-col"><label>頂點</label><select id="peakNote"></select></div>
            <div class="range-col"><label>結束</label><select id="endNote"></select></div>
        </div>

        <button class="add-btn" onclick="addToRoutine()"><span>⬇️ 加入練習清單</span></button>

        <div class="routine-container">
            <div class="routine-header">
                <span>📋 課程清單</span>
                <span style="color:var(--accent); cursor:pointer;" onclick="clearRoutine()">清空</span>
            </div>
            <ul id="routineList" class="routine-list">
                <li style="color:#444; text-align:center; padding:10px;">(目前是空的)</li>
            </ul>
        </div>
        
        <div class="slider-group">
            <div class="slider-label-row"><span>速度 (BPM)</span><span id="bpmVal" class="val-display">100</span></div>
            <input type="range" id="bpm" min="60" max="180" step="1" value="100">
        </div>
        <div class="slider-group">
            <div class="slider-label-row"><span>預備拍音量</span><span id="volStickVal" class="val-display">60%</span></div>
            <input type="range" id="volStick" min="0" max="100" step="1" value="60">
        </div>
        <div class="slider-group">
            <div class="slider-label-row"><span>總音量</span><span id="volMasterVal" class="val-display">80%</span></div>
            <input type="range" id="volMaster" min="0" max="100" step="1" value="80">
        </div>
    </div>

    <div class="status-display" style="display:none;">
        <div class="current-note" id="noteDisplay">Ready</div>
        <div class="action-text" id="actionDisplay">準備開始</div>
        <div class="wake-status" id="wakeStatus"></div>
    </div>

    <button class="play-btn" id="playBtn" onclick="togglePlay()">▶ 開始執行課程</button>

    <script>
    /*__INJECT_RESOURCES__*/
    </script>

    <script>
    let audioCtx, player;
    let masterGainNode;
    let isPlaying = false;
    
    // v25: 移除 Silent MP3，避免音訊 Session 衝突
    // let silentAudioPlayer = new Audio(SILENT_MP3); <-- Removed

    let nextNoteTime = 0.0;
    let timerID;
    let lookahead = 25.0; 
    let scheduleAheadTime = 0.1; 
    let currentRoots = [];
    let rootIndex = 0;
    let patternStepIndex = 0;
    
    let editingMode = 'triad';
    let routineQueue = [];
    let currentRoutineIndex = 0;
    
    let globalPeakIndex = 0;
    let countInBeats = 4; 
    let wakeLock = null;
    let rangeProfiles = {
        'triad':  { s:'A3', p:'C#4', e:'A2', name:'大三和弦' },
        'scale5': { s:'A3', p:'G4',  e:'A2', name:'五度音階' },
        'octave': { s:'C3', p:'G4',  e:'C3', name:'八度音程' },
        'p5':     { s:'C3', p:'G4',  e:'C3', name:'五度音程' },
        'p4':     { s:'C3', p:'G4',  e:'C3', name:'四度音程' }
    };

    let mediaRecorder;
    let audioChunks = [];
    let analyser;
    let microphoneStream;
    let pitchCheckInterval;
    let currentTargetMidi = -1; 
    let audioBuffer = new Float32Array(2048);

    const notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
    
    window.onload = function() {
        setTimeout(() => {
            try {
                if (typeof WebAudioFontPlayer === 'undefined') throw new Error("引擎載入失敗");
                initSelects();
                initUIListeners();
                player = new WebAudioFontPlayer();
                document.getElementById('loadingMask').style.display = 'none';
            } catch (e) {
                document.getElementById('errorDisplay').innerText = e.message;
            }
        }, 500);
    };

    function initSelects() {
        const startSel = document.getElementById('startNote');
        const peakSel = document.getElementById('peakNote');
        const endSel = document.getElementById('endNote');
        for(let oct=2; oct<=5; oct++) {
            notes.forEach(n => {
                let val = `${n}${oct}`;
                startSel.add(new Option(val, val));
                peakSel.add(new Option(val, val));
                endSel.add(new Option(val, val));
            });
        }
        applyProfile('triad');
    }

    function initUIListeners() {
        document.getElementById('bpm').addEventListener('input', function(e) { document.getElementById('bpmVal').innerText = e.target.value; });
        document.getElementById('volMaster').addEventListener('input', updateGains);
        document.getElementById('volStick').addEventListener('input', function(e){
             document.getElementById('volStickVal').innerText = e.target.value + "%";
        });
        ['startNote', 'peakNote', 'endNote'].forEach(id => {
            document.getElementById(id).addEventListener('change', function() { saveCurrentProfile(); });
        });
    }

    function updateGains() {
        let vol = document.getElementById('volMaster').value;
        document.getElementById('volMasterVal').innerText = vol + "%";
        if(masterGainNode) masterGainNode.gain.setTargetAtTime(vol / 100.0, audioCtx.currentTime, 0.05);
    }

    function switchConfigMode(mode) {
        saveCurrentProfile();
        editingMode = mode;
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.getElementById('btn-' + mode).classList.add('active');
        applyProfile(mode);
    }
    
    function saveCurrentProfile() {
        let s = document.getElementById('startNote').value;
        let p = document.getElementById('peakNote').value;
        let e = document.getElementById('endNote').value;
        rangeProfiles[editingMode].s = s;
        rangeProfiles[editingMode].p = p;
        rangeProfiles[editingMode].e = e;
    }
    function applyProfile(mode) {
        let p = rangeProfiles[mode];
        if(p) {
            document.getElementById('startNote').value = p.s;
            document.getElementById('peakNote').value = p.p;
            document.getElementById('endNote').value = p.e;
        }
    }
    function addToRoutine() {
        saveCurrentProfile();
        let p = rangeProfiles[editingMode];
        routineQueue.push({ mode: editingMode, s: p.s, p: p.p, e: p.e, name: p.name });
        renderRoutine();
    }
    function renderRoutine() {
        let list = document.getElementById('routineList');
        list.innerHTML = "";
        if(routineQueue.length === 0) {
            list.innerHTML = '<li style="color:#444; text-align:center; padding:10px;">(目前是空的)</li>'; return;
        }
        routineQueue.forEach((item, idx) => {
            let li = document.createElement('li');
            li.className = 'routine-item';
            if(isPlaying && currentRoutineIndex === idx) li.classList.add('active');
            li.innerHTML = `<div class="routine-info"><div style="font-weight:bold">${idx+1}. ${item.name}</div><div class="routine-range">${item.s} ⮕ ${item.p} ⮕ ${item.e}</div></div><button class="delete-btn" onclick="removeItem(${idx})">×</button>`;
            list.appendChild(li);
        });
    }
    function removeItem(idx) { routineQueue.splice(idx, 1); renderRoutine(); }
    function clearRoutine() { routineQueue = []; renderRoutine(); }

    function generateRootsFromConfig(config) {
        let allOpts = Array.from(document.getElementById('startNote').options).map(o=>o.value);
        let sIdx = allOpts.indexOf(config.s);
        let pIdx = allOpts.indexOf(config.p);
        let eIdx = allOpts.indexOf(config.e);
        currentRoots = [];
        if (sIdx <= pIdx) { for(let i=sIdx; i<=pIdx; i++) currentRoots.push(allOpts[i]); } 
        else { currentRoots.push(config.s); }
        globalPeakIndex = currentRoots.length - 1;
        if (eIdx < pIdx) { for(let i=pIdx-1; i>=eIdx; i--) currentRoots.push(allOpts[i]); }
    }

    function getMidiPitch(n) {
        let note = n.slice(0, -1), oct = parseInt(n.slice(-1));
        return notes.indexOf(note) + (oct + 1) * 12;
    }
    
    function midiToNote(midi) {
        let noteIndex = midi % 12;
        let octave = Math.floor(midi / 12) - 1;
        return notes[noteIndex] + octave;
    }

    function autoCorrelate(buf, sampleRate) {
        let SIZE = buf.length;
        let rms = 0;
        for (let i = 0; i < SIZE; i++) rms += buf[i] * buf[i];
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
            for (let j = 0; j < SIZE - i; j++) c[i] = c[i] + buf[j] * buf[j + i];
        }
        let d = 0; while (c[d] > c[d + 1]) d++;
        let maxval = -1, maxpos = -1;
        for (let i = d; i < SIZE; i++) {
            if (c[i] > maxval) { maxval = c[i]; maxpos = i; }
        }
        let T0 = maxpos;
        return sampleRate / T0;
    }

    function updatePitchMonitor() {
        if (!analyser) return;
        analyser.getFloatTimeDomainData(audioBuffer);
        let frequency = autoCorrelate(audioBuffer, audioCtx.sampleRate);
        
        let userMarker = document.getElementById('userMarker');
        let judgeText = document.getElementById('judgeText');
        
        if (frequency === -1) {
            userMarker.classList.remove('singing');
            judgeText.innerText = "🎤 請唱歌...";
            judgeText.className = "judge-text";
        } else {
            let midi = 12 * (Math.log(frequency / 440) / Math.log(2)) + 69;
            let noteName = midiToNote(Math.round(midi));
            
            userMarker.innerText = noteName;
            userMarker.classList.add('singing');
            
            if (currentTargetMidi > 0) {
                let diff = midi - currentTargetMidi;
                let visualDiff = Math.max(-3, Math.min(3, diff));
                let leftPercent = 50 + (visualDiff * 13);
                userMarker.style.left = `calc(${leftPercent}% - 30px)`;

                if (Math.abs(diff) < 0.5) {
                    userMarker.style.backgroundColor = "#00e676"; 
                    judgeText.innerText = "✨ Perfect! ✨";
                    judgeText.className = "judge-text match";
                } else {
                    userMarker.style.backgroundColor = "#ffea00"; 
                    let hint = diff > 0 ? "太高 ⬆" : "太低 ⬇";
                    judgeText.innerText = hint;
                    judgeText.className = "judge-text";
                }
            } else {
                userMarker.style.left = `calc(50% - 30px)`;
                judgeText.innerText = "🎤 " + noteName;
            }
        }
    }

    async function startRecording() {
        try {
            const constraints = {
                audio: {
                    echoCancellation: false,
                    noiseSuppression: false,
                    autoGainControl: false
                }
            };
            
            // v25: 這裡會觸發權限詢問
            microphoneStream = await navigator.mediaDevices.getUserMedia(constraints);
            
            // v25: 智慧格式選擇
            let options = {};
            if (MediaRecorder.isTypeSupported('audio/mp4')) { options = { mimeType: 'audio/mp4' }; }
            else if (MediaRecorder.isTypeSupported('audio/webm')) { options = { mimeType: 'audio/webm' }; }

            mediaRecorder = new MediaRecorder(microphoneStream, options);
            audioChunks = [];
            
            let micSource = audioCtx.createMediaStreamSource(microphoneStream);
            analyser = audioCtx.createAnalyser();
            analyser.fftSize = 2048;
            micSource.connect(analyser);
            
            mediaRecorder.ondataavailable = event => {
                if (event.data.size > 0) audioChunks.push(event.data);
            };
            
            mediaRecorder.onstop = () => {
                let mimeType = mediaRecorder.mimeType || 'audio/webm'; // fallback
                let audioBlob = new Blob(audioChunks, { type: mimeType });
                let audioUrl = URL.createObjectURL(audioBlob);
                let audio = document.getElementById('playbackAudio');
                audio.src = audioUrl;
                document.getElementById('downloadLink').href = audioUrl;
                document.getElementById('downloadLink').download = "vocal_practice" + (mimeType.includes("mp4") ? ".mp4" : ".webm");
                document.getElementById('audioContainer').style.display = "block";
                
                if(pitchCheckInterval) clearInterval(pitchCheckInterval);
            };
            
            mediaRecorder.start();
            document.getElementById('pitchMonitor').classList.add('active');
            pitchCheckInterval = setInterval(updatePitchMonitor, 100); // 降低檢測頻率以減輕CPU
            
        } catch(err) {
            console.error("Mic Error:", err);
            alert("麥克風權限失敗: " + err.message);
            throw err; // 中斷後續執行
        }
    }

    function stopRecording() {
        if (mediaRecorder && mediaRecorder.state !== 'inactive') {
            mediaRecorder.stop();
            microphoneStream.getTracks().forEach(track => track.stop());
        }
        document.getElementById('pitchMonitor').classList.remove('active');
    }

    async function requestWakeLock() {
        try { if ('wakeLock' in navigator) wakeLock = await navigator.wakeLock.request('screen'); } catch (err) {}
    }
    function releaseWakeLock() { if (wakeLock) { wakeLock.release(); wakeLock = null; } }

    function playStickClick(time) {
        let vol = document.getElementById('volStick').value / 100.0;
        if(vol <= 0.01) return;
        let osc = audioCtx.createOscillator();
        let gain = audioCtx.createGain();
        osc.frequency.setValueAtTime(1200, time);
        osc.frequency.exponentialRampToValueAtTime(800, time + 0.05);
        gain.gain.setValueAtTime(0, time);
        gain.gain.linearRampToValueAtTime(vol, time + 0.001); 
        gain.gain.exponentialRampToValueAtTime(0.001, time + 0.08);
        osc.connect(gain);
        gain.connect(audioCtx.destination);
        osc.start(time);
        osc.stop(time + 0.1);
    }

    function playChord(midiRoot, time, duration) {
        let preset = _tone_0000_JCLive_sf2_file;
        [0, 4, 7].forEach(semi => {
            player.queueWaveTable(audioCtx, masterGainNode, preset, time, midiRoot + semi, duration, 0.5);
        });
    }

    async function togglePlay() {
        if (isPlaying) { stop(); return; }
        if (routineQueue.length === 0) { alert("請先將練習加入下方清單！"); return; }

        document.getElementById('audioContainer').style.display = "none";
        
        // v25: 優先請求麥克風 (這會觸發 UI 互動，解決延遲問題)
        try {
            await startRecording(); 
        } catch (e) {
            return; // 沒權限就不開始
        }
        
        // 麥克風成功後，再請求螢幕喚醒和音訊環境
        requestWakeLock();
        
        if (!audioCtx) {
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            masterGainNode = audioCtx.createGain();
            masterGainNode.connect(audioCtx.destination);
        }
        if (audioCtx.state === 'suspended') await audioCtx.resume();
        
        updateGains();

        isPlaying = true;
        currentRoutineIndex = 0;
        startRoutineItem();
        
        let btn = document.getElementById('playBtn');
        btn.innerHTML = "⏹ 停止 & 完成錄音";
        btn.classList.add('stop');
        
        scheduler();
    }

    function startRoutineItem() {
        rootIndex = 0;
        patternStepIndex = 0;
        let config = routineQueue[currentRoutineIndex];
        generateRootsFromConfig(config);
        renderRoutine(); 
        
        let bpm = parseFloat(document.getElementById('bpm').value);
        let beatDur = 60.0 / bpm;
        let now = audioCtx.currentTime;
        if (nextNoteTime < now) nextNoteTime = now + 0.5;

        for(let i=0; i<countInBeats; i++) {
            let t = nextNoteTime + (i * beatDur);
            playStickClick(t);
            if(i === 0) {
                let firstRootMidi = getMidiPitch(currentRoots[0]);
                playChord(firstRootMidi, t, beatDur * 4);
                currentTargetMidi = firstRootMidi;
                updateTargetMarker(midiToNote(firstRootMidi));
            }
        }
        nextNoteTime += (countInBeats * beatDur);
    }

    function updateTargetMarker(noteName) {
        let t = document.getElementById('targetMarker');
        t.innerText = noteName;
        t.classList.add('active');
        t.style.left = `calc(50% - 30px)`;
    }

    function stop() {
        isPlaying = false;
        releaseWakeLock();
        stopRecording();
        
        // v25: 移除 silentAudioPlayer.pause();
        clearTimeout(timerID);
        if(player && audioCtx) player.cancelQueue(audioCtx);
        
        let btn = document.getElementById('playBtn');
        btn.innerHTML = "▶ 開始執行課程";
        btn.classList.remove('stop');
        
        document.getElementById('noteDisplay').innerText = "Ready";
        document.getElementById('actionDisplay').innerText = "練習結束";
        document.getElementById('targetMarker').classList.remove('active');
        document.getElementById('userMarker').classList.remove('singing');
        renderRoutine();
    }

    function scheduler() {
        while (isPlaying && nextNoteTime < audioCtx.currentTime + scheduleAheadTime) {
            scheduleNote(rootIndex, patternStepIndex, nextNoteTime);
            nextStep();
        }
        if (isPlaying) timerID = window.setTimeout(scheduler, lookahead);
    }

    function nextStep() {
        let bpm = parseFloat(document.getElementById('bpm').value);
        let secondsPerBeat = 60.0 / bpm;
        nextNoteTime += secondsPerBeat;
        let mode = routineQueue[currentRoutineIndex].mode;
        let intervals;
        if(mode === 'triad') intervals = [0, 4, 7, 4, 0];
        else if(mode === 'scale5') intervals = [0, 2, 4, 5, 7, 5, 4, 2, 0];
        else if(mode === 'octave') intervals = [0, 12, 0];
        else if(mode === 'p5') intervals = [0, 7, 0];
        else if(mode === 'p4') intervals = [0, 5, 0];
        let totalBeats = intervals.length + 2; 

        patternStepIndex++;
        if (patternStepIndex >= totalBeats) {
            patternStepIndex = 0;
            rootIndex++;
            if (rootIndex >= currentRoots.length) {
                currentRoutineIndex++;
                if (currentRoutineIndex < routineQueue.length) {
                    nextNoteTime += 2.0; 
                    startRoutineItem();
                } else {
                    stop();
                    document.getElementById('actionDisplay').innerText = "🎉 課程完成！";
                }
            }
        }
    }

    function scheduleNote(idx, step, time) {
        if(idx >= currentRoots.length) return;
        let rootName = currentRoots[idx];
        let bpm = parseFloat(document.getElementById('bpm').value);
        let beatDur = 60.0 / bpm;
        let rootMidi = getMidiPitch(rootName);
        let preset = _tone_0000_JCLive_sf2_file;
        let mode = routineQueue[currentRoutineIndex].mode;
        let intervals;
        if(mode === 'triad') intervals = [0, 4, 7, 4, 0];
        else if(mode === 'scale5') intervals = [0, 2, 4, 5, 7, 5, 4, 2, 0];
        else if(mode === 'octave') intervals = [0, 12, 0];
        else if(mode === 'p5') intervals = [0, 7, 0];
        else if(mode === 'p4') intervals = [0, 5, 0];

        if (step === 0) {
            document.getElementById('noteDisplay').innerText = rootName;
        }

        if (step < intervals.length) {
            let noteMidi = rootMidi + intervals[step];
            player.queueWaveTable(audioCtx, masterGainNode, preset, time, noteMidi, beatDur*0.9, 1.0);
            
            let delayMs = (time - audioCtx.currentTime) * 1000;
            setTimeout(() => {
                if(isPlaying) {
                    currentTargetMidi = noteMidi;
                    updateTargetMarker(midiToNote(noteMidi));
                }
            }, delayMs);

            if (step === 0) {
                let chordDur = beatDur * intervals.length;
                playChord(rootMidi, time, chordDur);
            }
        } 
        else {
            let delayMs = (time - audioCtx.currentTime) * 1000;
            setTimeout(() => {
                if(isPlaying) {
                    currentTargetMidi = -1; 
                    document.getElementById('targetMarker').classList.remove('active');
                    document.getElementById('judgeText').innerText = (step===intervals.length) ? "😤 吸氣..." : "👉 轉調...";
                }
            }, delayMs);
            
            if (step === intervals.length) playChord(rootMidi, time, beatDur);
            else if (step === intervals.length + 1) {
                 let nextIdx = idx + 1;
                 if (nextIdx < currentRoots.length) {
                     let nextRootName = currentRoots[nextIdx];
                     let nextRootMidi = getMidiPitch(nextRootName);
                     playChord(nextRootMidi, time, beatDur);
                 }
            }
        }
    }
    </script>
</body>
</html>
"""

# 5. 合成最終檔案 (注入資源)
final_html = html_template.replace("/*__INJECT_RESOURCES__*/", f"{player_code}\n{piano_code}")

# 6. 寫入檔案
output_filename = "VocalTrainer_Offline_v25.html"
with open(output_filename, "w", encoding="utf-8") as f:
    f.write(final_html)

print(f"✅ 成功！已建立檔案: {output_filename}")
print(f"👉 v25 修復：現在按下播放後，會優先請求麥克風（通知會秒跳），並移除隱形MP3以確保錄音音質清晰。")
