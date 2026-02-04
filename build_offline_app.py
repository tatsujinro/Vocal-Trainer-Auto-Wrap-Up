import urllib.request
import os
import ssl

print("🚀 正在開始打包 v27.2 (邏輯修復版)...")

# 1. 忽略 SSL 驗證
ssl_context = ssl._create_unverified_context()

# 2. 定義資源
PLAYER_URL = "https://surikov.github.io/webaudiofont/npm/dist/WebAudioFontPlayer.js"
PIANO_URL = "https://surikov.github.io/webaudiofontdata/sound/0000_JCLive_sf2_file.js"

# 3. 下載資源
try:
    print("📥 [1/4] 下載播放引擎...")
    with urllib.request.urlopen(PLAYER_URL, context=ssl_context) as response:
        player_code = response.read().decode('utf-8')
    
    print("📥 [2/4] 下載鋼琴音色庫...")
    with urllib.request.urlopen(PIANO_URL, context=ssl_context) as response:
        piano_code = response.read().decode('utf-8')
        
    if len(piano_code) < 50000:
        print("⚠️ 警告：音色庫檔案過小，可能下載不完整。")
    else:
        print("✅ 資源下載完成！")
        
except Exception as e:
    print(f"❌ 下載失敗: {e}")
    exit(1)

# ---------------------------------------------------------
# 4. 定義各個區塊
# ---------------------------------------------------------

# Part A: CSS
css_part = """
<style>
    :root { --bg-color: #000000; --ui-bg: #1e1e1e; --text-main: #e0e0e0; --accent: #00e5ff; --meter-green: #00e676; --meter-yellow: #ffea00; --meter-red: #ff5252; }
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: var(--bg-color); color: var(--text-main); margin: 0; padding: 0; overflow: hidden; }
    #gameStage { position: relative; width: 100vw; height: 45vh; background: #111; border-bottom: 2px solid #333; overflow: hidden; }
    canvas { display: block; width: 100%; height: 100%; }
    .hud-score { position: absolute; top: 15px; right: 15px; font-size: 1.5rem; font-weight: bold; color: white; text-shadow: 0 0 10px var(--accent); font-family: monospace; }
    .hud-feedback { position: absolute; top: 15px; left: 50%; transform: translateX(-50%); font-size: 1.2rem; font-weight: bold; text-shadow: 0 2px 4px rgba(0,0,0,0.8); }
    #controlsArea { height: 55vh; overflow-y: auto; padding: 15px; box-sizing: border-box; background: var(--bg-color); transition: opacity 0.5s; padding-bottom: 80px; }
    #controlsArea.immersive-hidden { opacity: 0.1; pointer-events: none; }
    h1 { color: var(--accent); margin: 0 0 10px 0; font-size: 1.2rem; }
    .control-group { background: var(--ui-bg); border-radius: 12px; padding: 12px; margin-bottom: 12px; border: 1px solid #333; }
    .mixer-container { display: flex; gap: 10px; margin-top: 5px; }
    .mixer-channel { flex: 1; background: #111; padding: 10px; border-radius: 8px; border: 1px solid #333; text-align: center; }
    .mixer-label { font-size: 0.8rem; color: #888; margin-bottom: 5px; }
    .meter-box { width: 100%; height: 8px; background: #333; border-radius: 4px; margin-bottom: 8px; overflow: hidden; }
    .meter-fill { height: 100%; width: 0%; background: linear-gradient(to right, var(--meter-green) 60%, var(--meter-yellow) 80%, var(--meter-red) 100%); transition: width 0.05s linear; }
    .fader-wrapper input { width: 100%; }
    .tabs { display: flex; gap: 5px; margin-bottom: 10px; flex-wrap: wrap; }
    .tab-btn { background: transparent; color: #888; padding: 8px 5px; border: 1px solid #444; border-radius: 6px; cursor: pointer; flex: 1 1 30%; font-size: 0.8rem; transition: 0.2s; }
    .tab-btn.active { background: #333; color: var(--accent); border-color: var(--accent); box-shadow: 0 0 10px rgba(0, 229, 255, 0.2); }
    .range-selectors { display: flex; gap: 5px; margin-bottom: 10px; }
    .range-col { flex: 1; }
    .range-col label { font-size: 0.7rem; color: #666; display: block; text-align: center; }
    select { background: #222; color: white; border: 1px solid #444; width: 100%; border-radius: 4px; padding: 5px; font-size: 0.9rem; text-align: center; }
    .add-btn { background: #333; color: white; border: 1px solid #555; padding: 10px; width: 100%; border-radius: 8px; cursor: pointer; font-weight: bold; margin-bottom: 10px; }
    .routine-list { list-style: none; padding: 0; margin: 0; background: #0a0a0a; border-radius: 8px; min-height: 40px; margin-bottom: 10px; }
    .routine-item { padding: 8px; border-bottom: 1px solid #222; display: flex; justify-content: space-between; align-items: center; font-size: 0.85rem; }
    .routine-item.active { background: #1a2a1a; border-left: 3px solid var(--accent); }
    .delete-btn { color: #666; cursor: pointer; padding: 0 10px; }
    .play-btn { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: var(--accent); color: #000; border: none; padding: 15px 40px; border-radius: 50px; font-size: 1.2rem; font-weight: 800; width: 80%; max-width: 300px; box-shadow: 0 0 20px rgba(0, 229, 255, 0.4); z-index: 100; transition: 0.2s; }
    .play-btn.stop { background: #ff5252; color: white; box-shadow: none; }
    #resultModal { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.95); z-index: 200; display: none; flex-direction: column; justify-content: center; align-items: center; text-align: center; }
    .score-circle { width: 120px; height: 120px; border-radius: 50%; border: 5px solid var(--accent); display: flex; justify-content: center; align-items: center; font-size: 2.5rem; font-weight: bold; color: white; margin-bottom: 20px; box-shadow: 0 0 30px var(--accent); }
    .stat-row { display: flex; gap: 15px; margin-bottom: 20px; }
    .stat-item { text-align: center; }
    .stat-val { font-size: 1.2rem; font-weight: bold; }
    .stat-label { font-size: 0.8rem; color: #888; }
    .audio-player { width: 90%; margin-bottom: 20px; }
    .modal-btn { padding: 10px 30px; border-radius: 20px; border: 1px solid #fff; background: transparent; color: white; font-size: 1rem; cursor: pointer; }
    .loading-mask { position: fixed; top:0; left:0; width:100%; height:100%; background: #000; z-index: 999; display: flex; justify-content: center; align-items: center; color: white; flex-direction: column; }
    .warning-msg { color: #ff5252; font-size: 0.8rem; margin-top: 5px; display: none; }
</style>
"""

# Part B: HTML
html_part = """
<div id="loadingMask" class="loading-mask">
    <div style="font-size: 3rem; margin-bottom: 20px;">🎧</div>
    <div>v27.2 邏輯修復版</div>
    <div style="font-size: 0.8rem; color: #888; margin-top:10px;">系統初始化...</div>
    <div id="errorDisplay" style="color:red; margin-top:20px; font-size:0.8rem;"></div>
</div>

<div id="gameStage">
    <canvas id="gameCanvas"></canvas>
    <div class="hud-score" id="hudScore">0000</div>
    <div class="hud-feedback" id="hudFeedback"></div>
</div>

<div id="controlsArea">
    <h1>Vocal Trainer <span style="font-size:0.8rem; color:#666;">v27.2</span></h1>
    
    <div class="control-group">
        <div style="font-size:0.9rem; font-weight:bold; margin-bottom:5px;">🎛️ 錄音室混音台</div>
        <div class="mixer-container">
            <div class="mixer-channel">
                <div class="mixer-label">🎹 伴奏</div>
                <div class="meter-box"><div class="meter-fill" id="meterPiano"></div></div>
                <div class="fader-wrapper"><input type="range" id="faderPianoRec" min="0" max="100" value="40"></div>
                <div style="font-size:0.7rem; color:#666; margin-top:3px;">40%</div>
            </div>
            <div class="mixer-channel">
                <div class="mixer-label">🎤 人聲</div>
                <div class="meter-box"><div class="meter-fill" id="meterVocal"></div></div>
                <div class="fader-wrapper"><input type="range" id="faderVocalRec" min="0" max="300" value="100"></div>
                <div style="font-size:0.7rem; color:#666; margin-top:3px;">100%</div>
            </div>
        </div>
        
        <div style="margin-top:15px; border-top:1px solid #333; padding-top:10px;">
            <div style="font-size:0.8rem; color:var(--accent); margin-bottom:5px;">🎧 藍牙延遲補償 (Bluetooth Sync)</div>
            <input type="range" id="latencySlider" min="0" max="500" value="0" step="10" style="width:100%">
            <div style="font-size:0.7rem; color:#888; text-align:right;">延遲: <span id="latencyVal" style="color:white; font-weight:bold;">0</span> ms</div>
            <div style="font-size:0.7rem; color:#666;">若回放時人聲比鋼琴慢，請增加此數值。</div>
        </div>
        <div id="micWarning" class="warning-msg">⚠️ 麥克風未啟用，人聲軌將無作用。</div>
    </div>

    <div class="control-group">
        <div style="font-size:0.9rem; margin-bottom:5px;">🎧 監聽音量 (僅自己聽得到): <span id="volMonitorVal">80%</span></div>
        <input type="range" id="volMonitor" min="0" max="100" value="80" style="width:100%">
    </div>

    <div class="control-group">
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
        <button class="add-btn" onclick="addToRoutine()">⬇️ 加入課程清單</button>
    </div>

    <div class="control-group">
        <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
            <span>📋 課程清單</span>
            <span style="color:var(--score-red); cursor:pointer; font-size:0.8rem;" onclick="clearRoutine()">清空</span>
        </div>
        <ul id="routineList" class="routine-list"><li style="padding:10px; color:#666; text-align:center;">(尚未加入練習)</li></ul>
        <div style="font-size:0.9rem;">BPM: <span id="bpmVal">100</span></div>
        <input type="range" id="bpm" min="60" max="180" value="100" style="width:100%">
    </div>
</div>

<button class="play-btn" id="playBtn" onclick="togglePlay()">▶ 開始特訓</button>

<div id="resultModal">
    <h2 style="color:white; margin-bottom:10px;">練習完成!</h2>
    <div class="score-circle" id="finalScore">0</div>
    <div class="stat-row">
        <div class="stat-item"><div class="stat-val" style="color:var(--meter-green)" id="statPerfect">0%</div><div class="stat-label">Perfect</div></div>
        <div class="stat-item"><div class="stat-val" style="color:var(--meter-yellow)" id="statGood">0%</div><div class="stat-label">Good</div></div>
        <div class="stat-item"><div class="stat-val" style="color:var(--meter-red)" id="statMiss">0%</div><div class="stat-label">Miss</div></div>
    </div>
    <div id="audioPlayerWrapper">
        <audio id="resultAudio" class="audio-player" controls></audio>
        <div style="display:flex; gap:10px; justify-content:center;">
            <a id="downloadLink" class="modal-btn" style="border-color:var(--accent); color:var(--accent);">下載錄音</a>
        </div>
    </div>
    <div id="noRecMsg" style="display:none; color:#888; margin-bottom:20px;">(本次練習未啟用錄音功能)</div>
    <button class="modal-btn" onclick="closeResult()" style="margin-top:10px;">關閉</button>
</div>
"""

# Part C: JavaScript
js_part = """
<script>
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    let audioCtx, player;
    let pianoSplitterNode, monitorGainNode, recPianoGainNode, recVocalGainNode, mixerNode, micSource, pianoDelayNode; 
    let pianoAnalyser, vocalAnalyser;
    let isPlaying = false;
    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    let gameLoopId;
    let gameTargets = []; 
    let userPitchHistory = [];
    let score = 0;
    let stats = { perfect:0, good:0, miss:0, totalFrames:0 };
    
    const PIXELS_PER_SEC = 100;
    const PIXELS_PER_SEMITONE = 15;
    const VISUAL_OFFSET_SEC = 0.15; 
    const BLOCK_HEIGHT = 30;
    let viewCenterMidi = 60; 

    let nextNoteTime = 0.0, timerID, lookahead = 25.0, scheduleAheadTime = 0.1;
    let currentRoots = [], rootIndex = 0, patternStepIndex = 0;
    let editingMode = 'triad';
    let routineQueue = [];
    let currentRoutineIndex = 0;
    let countInBeats = 4;
    let wakeLock = null;

    let mediaRecorder = null, audioChunks = [], audioBuffer = new Float32Array(2048);
    let canRecord = true;

    const notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
    
    let rangeProfiles = {
        'triad':  { s:'A3', p:'C#4', e:'A2', name:'大三和弦' },
        'scale5': { s:'A3', p:'G4',  e:'A2', name:'五度音階' },
        'octave': { s:'C3', p:'G4',  e:'C3', name:'八度音程' },
        'p5':     { s:'C3', p:'G4',  e:'C3', name:'五度音程' },
        'p4':     { s:'C3', p:'G4',  e:'C3', name:'四度音程' }
    };

    window.onload = function() {
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);
        loadLocalStorage();
        if (typeof MediaRecorder === 'undefined') { canRecord = false; document.getElementById('micWarning').style.display = 'block'; }
        setTimeout(() => {
            try {
                if (typeof WebAudioFontPlayer === 'undefined') throw new Error("引擎載入失敗");
                initSelects(); initUIListeners();
                player = new WebAudioFontPlayer();
                document.getElementById('loadingMask').style.display = 'none';
            } catch (e) { document.getElementById('errorDisplay').innerText = e.message; }
        }, 500);
    };

    function resizeCanvas() {
        canvas.width = document.getElementById('gameStage').clientWidth;
        canvas.height = document.getElementById('gameStage').clientHeight;
    }

    function saveLocalStorage() {
        const data = { 
            profiles: rangeProfiles, routine: routineQueue, bpm: document.getElementById('bpm').value,
            volMonitor: document.getElementById('volMonitor').value,
            recPiano: document.getElementById('faderPianoRec').value,
            recVocal: document.getElementById('faderVocalRec').value,
            latency: document.getElementById('latencySlider').value
        };
        localStorage.setItem('v27_2_data', JSON.stringify(data));
    }

    function loadLocalStorage() {
        const raw = localStorage.getItem('v27_2_data');
        if (raw) {
            try {
                const data = JSON.parse(raw);
                if(data.profiles) rangeProfiles = data.profiles;
                if(data.routine) routineQueue = data.routine;
                if(data.bpm) document.getElementById('bpm').value = data.bpm;
                if(data.volMonitor) document.getElementById('volMonitor').value = data.volMonitor;
                if(data.recPiano) document.getElementById('faderPianoRec').value = data.recPiano;
                if(data.recVocal) document.getElementById('faderVocalRec').value = data.recVocal;
                if(data.latency) {
                    document.getElementById('latencySlider').value = data.latency;
                    document.getElementById('latencyVal').innerText = data.latency;
                }
                renderRoutine();
                document.getElementById('bpmVal').innerText = document.getElementById('bpm').value;
                document.getElementById('volMonitorVal').innerText = document.getElementById('volMonitor').value + "%";
            } catch(e) {}
        }
    }

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
        document.getElementById('volMonitor').addEventListener('input', function(e) { document.getElementById('volMonitorVal').innerText = e.target.value + "%"; updateGains(); saveLocalStorage(); });
        document.getElementById('faderPianoRec').addEventListener('input', function(e) { e.target.parentNode.nextElementSibling.innerText = e.target.value + "%"; updateGains(); saveLocalStorage(); });
        document.getElementById('faderVocalRec').addEventListener('input', function(e) { e.target.parentNode.nextElementSibling.innerText = e.target.value + "%"; updateGains(); saveLocalStorage(); });
        document.getElementById('latencySlider').addEventListener('input', function(e) { document.getElementById('latencyVal').innerText = e.target.value; updateGains(); saveLocalStorage(); });
        document.getElementById('bpm').addEventListener('input', function(e) { document.getElementById('bpmVal').innerText = e.target.value; saveLocalStorage(); });
        ['startNote', 'peakNote', 'endNote'].forEach(id => { document.getElementById(id).addEventListener('change', function() { saveCurrentProfile(); }); });
    }

    function updateGains() {
        if (!audioCtx) return;
        let now = audioCtx.currentTime;
        let volMon = document.getElementById('volMonitor').value / 100.0;
        if(monitorGainNode) monitorGainNode.gain.setTargetAtTime(volMon, now, 0.05);
        let volPianoRec = document.getElementById('faderPianoRec').value / 100.0;
        if(recPianoGainNode) recPianoGainNode.gain.setTargetAtTime(volPianoRec, now, 0.05);
        let volVocalRec = document.getElementById('faderVocalRec').value / 100.0;
        if(recVocalGainNode) recVocalGainNode.gain.setTargetAtTime(volVocalRec, now, 0.05);
        let latencyMs = parseFloat(document.getElementById('latencySlider').value);
        if(pianoDelayNode) pianoDelayNode.delayTime.setTargetAtTime(latencyMs / 1000.0, now, 0.05);
    }

    function switchConfigMode(mode) { saveCurrentProfile(); editingMode = mode; document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active')); document.getElementById('btn-' + mode).classList.add('active'); applyProfile(mode); }
    function saveCurrentProfile() { rangeProfiles[editingMode].s = document.getElementById('startNote').value; rangeProfiles[editingMode].p = document.getElementById('peakNote').value; rangeProfiles[editingMode].e = document.getElementById('endNote').value; saveLocalStorage(); }
    function applyProfile(mode) { let p = rangeProfiles[mode]; if(p) { document.getElementById('startNote').value = p.s; document.getElementById('peakNote').value = p.p; document.getElementById('endNote').value = p.e; } }
    function addToRoutine() { saveCurrentProfile(); let p = rangeProfiles[editingMode]; routineQueue.push({ mode: editingMode, s: p.s, p: p.p, e: p.e, name: p.name }); renderRoutine(); saveLocalStorage(); }
    function renderRoutine() {
        let list = document.getElementById('routineList'); list.innerHTML = "";
        if(routineQueue.length === 0) { list.innerHTML = '<li style="padding:10px; color:#666; text-align:center;">(尚未加入練習)</li>'; return; }
        routineQueue.forEach((item, idx) => {
            let li = document.createElement('li'); li.className = 'routine-item';
            if(isPlaying && currentRoutineIndex === idx) li.classList.add('active');
            li.innerHTML = `<div><b>${idx+1}. ${item.name}</b> <span style="color:#888;">${item.s}⮕${item.p}</span></div><span class="delete-btn" onclick="removeItem(${idx})">✕</span>`;
            list.appendChild(li);
        });
    }
    function removeItem(idx) { routineQueue.splice(idx, 1); renderRoutine(); saveLocalStorage(); }
    function clearRoutine() { routineQueue = []; renderRoutine(); saveLocalStorage(); }

    async function initAudio() {
        if (!audioCtx) {
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            mixerNode = audioCtx.createMediaStreamDestination();
            pianoAnalyser = audioCtx.createAnalyser(); pianoAnalyser.fftSize = 256;
            vocalAnalyser = audioCtx.createAnalyser(); vocalAnalyser.fftSize = 256;
            pianoSplitterNode = audioCtx.createGain();
            
            monitorGainNode = audioCtx.createGain();
            pianoSplitterNode.connect(monitorGainNode);
            monitorGainNode.connect(audioCtx.destination);
            
            pianoDelayNode = audioCtx.createDelay(1.0);
            recPianoGainNode = audioCtx.createGain();
            pianoSplitterNode.connect(pianoDelayNode);
            pianoDelayNode.connect(recPianoGainNode);
            recPianoGainNode.connect(mixerNode);
            recPianoGainNode.connect(pianoAnalyser); 
            
            if (canRecord) {
                try {
                    let stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                    micSource = audioCtx.createMediaStreamSource(stream);
                    recVocalGainNode = audioCtx.createGain();
                    micSource.connect(recVocalGainNode);
                    recVocalGainNode.connect(mixerNode);
                    recVocalGainNode.connect(vocalAnalyser); 
                } catch (e) {
                    canRecord = false; document.getElementById('micWarning').style.display = 'block';
                }
            }
        }
        if (audioCtx.state === 'suspended') await audioCtx.resume();
        updateGains();
    }

    async function togglePlay() {
        if (isPlaying) { stop(); return; }
        if (routineQueue.length === 0) { alert("請加入課程！"); return; }
        await initAudio(); requestWakeLock();
        if (canRecord && mixerNode && mixerNode.stream) {
            audioChunks = [];
            try {
                let options = {};
                if (MediaRecorder.isTypeSupported('audio/mp4')) options = { mimeType: 'audio/mp4' };
                else if (MediaRecorder.isTypeSupported('audio/webm')) options = { mimeType: 'audio/webm' };
                mediaRecorder = new MediaRecorder(mixerNode.stream, options);
                mediaRecorder.ondataavailable = e => { if (e.data.size > 0) audioChunks.push(e.data); };
                mediaRecorder.onstop = showResultModal; 
                mediaRecorder.start();
            } catch(e) { canRecord = false; }
        }
        score = 0; stats = { perfect:0, good:0, miss:0, totalFrames:0 };
        gameTargets = []; userPitchHistory = [];
        currentRoutineIndex = 0; isPlaying = true;
        document.getElementById('controlsArea').classList.add('immersive-hidden');
        document.getElementById('playBtn').innerText = "⏹ 停止";
        document.getElementById('playBtn').classList.add('stop');
        startRoutineItem(); scheduler(); renderLoop(); 
    }

    function stop() {
        isPlaying = false; releaseWakeLock();
        if (mediaRecorder && mediaRecorder.state !== 'inactive') mediaRecorder.stop();
        else if (!canRecord) showResultModal();
        clearTimeout(timerID); if (player) player.cancelQueue(audioCtx); cancelAnimationFrame(gameLoopId);
        document.getElementById('controlsArea').classList.remove('immersive-hidden');
        document.getElementById('playBtn').innerText = "▶ 開始特訓";
        document.getElementById('playBtn').classList.remove('stop');
        renderRoutine();
    }

    function renderLoop() {
        if (!isPlaying) return;
        ctx.fillStyle = "#111"; ctx.fillRect(0, 0, canvas.width, canvas.height); drawGrid();
        let now = audioCtx.currentTime; let playheadX = canvas.width * 0.2;
        gameTargets.forEach(t => {
            let x = playheadX + (t.startTime - now) * PIXELS_PER_SEC;
            let width = t.duration * PIXELS_PER_SEC;
            let y = getYfromMidi(t.midi);
            if (x + width > 0 && x < canvas.width) {
                ctx.strokeStyle = "rgba(0, 229, 255, 0.8)"; ctx.fillStyle = "rgba(0, 229, 255, 0.1)";
                ctx.lineWidth = 2; ctx.fillRect(x, y - BLOCK_HEIGHT/2, width, BLOCK_HEIGHT); ctx.strokeRect(x, y - BLOCK_HEIGHT/2, width, BLOCK_HEIGHT);
            }
        });
        detectAndDrawPitch(now, playheadX);
        document.getElementById('hudScore').innerText = score.toString().padStart(4, '0');
        updateMeters();
        gameLoopId = requestAnimationFrame(renderLoop);
    }

    function updateMeters() {
        if(pianoAnalyser) {
            let arr = new Uint8Array(pianoAnalyser.frequencyBinCount); pianoAnalyser.getByteFrequencyData(arr);
            let avg = arr.reduce((a,b)=>a+b,0) / arr.length;
            document.getElementById('meterPiano').style.width = Math.min(100, avg * 1.5) + "%";
        }
        if(vocalAnalyser) {
            let arr = new Uint8Array(vocalAnalyser.frequencyBinCount); vocalAnalyser.getByteFrequencyData(arr);
            let avg = arr.reduce((a,b)=>a+b,0) / arr.length;
            document.getElementById('meterVocal').style.width = Math.min(100, avg * 2.0) + "%";
        }
    }

    function drawGrid() {
        ctx.strokeStyle = "#333"; ctx.lineWidth = 1;
        for (let m = viewCenterMidi - 6; m <= viewCenterMidi + 6; m++) { let y = getYfromMidi(m); ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke(); }
        ctx.strokeStyle = "#fff"; ctx.beginPath(); ctx.moveTo(canvas.width * 0.2, 0); ctx.lineTo(canvas.width * 0.2, canvas.height); ctx.stroke();
    }

    // v27.2: 音準平滑修正
    function detectAndDrawPitch(now, playheadX) {
        if (!vocalAnalyser) return;
        vocalAnalyser.getFloatTimeDomainData(audioBuffer);
        let freq = autoCorrelate(audioBuffer, audioCtx.sampleRate);
        let color = "rgba(255, 255, 255, 0.1)"; 
        let detectedMidi = null;

        if (freq !== -1) {
            let rawMidi = 12 * (Math.log(freq / 440) / Math.log(2)) + 69;
            
            // v27.2: 倍頻與平滑修正
            if (userPitchHistory.length > 0 && userPitchHistory[userPitchHistory.length - 1].midi) {
                let prev = userPitchHistory[userPitchHistory.length - 1].midi;
                
                // 倍頻檢查: 如果跳太遠 (超過7個半音)，降低平滑權重(或暫時忽略)
                if (Math.abs(rawMidi - prev) > 7) {
                     // 這裡選擇比較保守的更新: 稍微跟隨，但不大改
                     detectedMidi = prev * 0.9 + rawMidi * 0.1;
                } else {
                     // 正常情況: 平滑係數 0.5 (平衡)
                     detectedMidi = prev * 0.5 + rawMidi * 0.5;
                }
            } else { detectedMidi = rawMidi; }

            let currentTarget = gameTargets.find(t => now >= t.startTime && now <= t.startTime + t.duration);
            if (currentTarget) {
                let diff = Math.abs(detectedMidi - currentTarget.midi);
                if (diff < 0.15) { color = "#00e676"; score += 3; stats.perfect++; document.getElementById('hudFeedback').innerText = "Perfect!"; document.getElementById('hudFeedback').style.color = color; } 
                else if (diff < 0.5) { color = "#ffea00"; score += 1; stats.good++; document.getElementById('hudFeedback').innerText = "Good"; document.getElementById('hudFeedback').style.color = color; } 
                else { color = "#ff5252"; stats.miss++; let txt = (detectedMidi > currentTarget.midi) ? "High ⬆" : "Low ⬇"; document.getElementById('hudFeedback').innerText = txt; document.getElementById('hudFeedback').style.color = color; }
            } else { color = "#aaa"; document.getElementById('hudFeedback').innerText = ""; }
            stats.totalFrames++;
        }

        userPitchHistory.push({ time: now + VISUAL_OFFSET_SEC, midi: detectedMidi, color: color });
        while(userPitchHistory.length > 0 && userPitchHistory[0].time < now - 1.0) { userPitchHistory.shift(); }

        if (userPitchHistory.length > 1) {
            ctx.lineWidth = 20; ctx.lineCap = "round"; ctx.lineJoin = "round"; 
            for (let i = 1; i < userPitchHistory.length; i++) {
                let p1 = userPitchHistory[i-1]; let p2 = userPitchHistory[i];
                if (p1.midi && p2.midi && Math.abs(p1.midi - p2.midi) < 2) { 
                    let x1 = playheadX + (p1.time - now) * PIXELS_PER_SEC; let x2 = playheadX + (p2.time - now) * PIXELS_PER_SEC;
                    let y1 = getYfromMidi(p1.midi); let y2 = getYfromMidi(p2.midi);
                    ctx.strokeStyle = p2.color; ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke();
                }
            }
        }
    }

    function getYfromMidi(midi) { return (canvas.height / 2) - (midi - viewCenterMidi) * PIXELS_PER_SEMITONE; }
    
    function generateRootsFromConfig(config) {
        let allOpts = []; for(let oct=2; oct<=5; oct++) notes.forEach(n => allOpts.push(`${n}${oct}`));
        let sIdx = allOpts.indexOf(config.s), pIdx = allOpts.indexOf(config.p), eIdx = allOpts.indexOf(config.e);
        currentRoots = [];
        if (sIdx <= pIdx) for(let i=sIdx; i<=pIdx; i++) currentRoots.push(allOpts[i]); else currentRoots.push(config.s);
        globalPeakIndex = currentRoots.length - 1;
        if (eIdx < pIdx && eIdx >= 0) for(let i=pIdx-1; i>=eIdx; i--) currentRoots.push(allOpts[i]);
        viewCenterMidi = (getMidiPitch(config.s) + getMidiPitch(config.p)) / 2;
    }

    function previewPatternVisuals(root, startTime, beatDur) {
        let mode = routineQueue[currentRoutineIndex].mode;
        let intervals = (mode==='triad')?[0,4,7,4,0] : (mode==='scale5')?[0,2,4,5,7,5,4,2,0] : (mode==='octave')?[0,12,0] : (mode==='p5')?[0,7,0] : [0,5,0];
        for(let i=0; i<intervals.length; i++) {
            gameTargets.push({ midi: root + intervals[i], startTime: startTime + (i * beatDur), duration: beatDur * 0.95 });
        }
    }

    function startRoutineItem() {
        rootIndex = 0; patternStepIndex = 0;
        let config = routineQueue[currentRoutineIndex]; generateRootsFromConfig(config); renderRoutine();
        let bpm = document.getElementById('bpm').value; let beatDur = 60.0 / bpm;
        let now = audioCtx.currentTime; if (nextNoteTime < now) nextNoteTime = now + 0.5;
        for(let i=0; i<countInBeats; i++) {
            let t = nextNoteTime + (i * beatDur); playStickClick(t);
            if(i === 0) {
                let root = getMidiPitch(currentRoots[0]); playChord(root, t, beatDur * 4);
                gameTargets.push({ midi: root, startTime: t, duration: beatDur * 4 });
            }
        }
        nextNoteTime += (countInBeats * beatDur);
        
        // v27.2: 修正 Pattern 接力 (一次預判 3 個)
        let root1 = getMidiPitch(currentRoots[0]); 
        previewPatternVisuals(root1, nextNoteTime, beatDur);

        if (currentRoots.length > 1) {
            let root2 = getMidiPitch(currentRoots[1]);
            let len = (routineQueue[currentRoutineIndex].mode==='scale5') ? 9 : (routineQueue[currentRoutineIndex].mode==='triad') ? 5 : 3; 
            previewPatternVisuals(root2, nextNoteTime + (len+2)*beatDur, beatDur);
            
            // 這裡補上第三個 (P3)，防止接棒掉落
            if (currentRoots.length > 2) {
                 let root3 = getMidiPitch(currentRoots[2]);
                 previewPatternVisuals(root3, nextNoteTime + (len+2)*beatDur*2, beatDur);
            }
        }
    }

    function scheduler() {
        while (isPlaying && nextNoteTime < audioCtx.currentTime + scheduleAheadTime) { scheduleNote(rootIndex, patternStepIndex, nextNoteTime); nextStep(); }
        if (isPlaying) timerID = window.setTimeout(scheduler, lookahead);
    }

    function nextStep() {
        let bpm = document.getElementById('bpm').value; let beatDur = 60.0 / bpm;
        nextNoteTime += beatDur;
        let mode = routineQueue[currentRoutineIndex].mode;
        let len = (mode==='triad')?4 : (mode==='scale5')?8 : 2; // intervals.length - 1
        patternStepIndex++;
        if (patternStepIndex > len + 2) {
            patternStepIndex = 0; rootIndex++;
            if (rootIndex >= currentRoots.length) {
                currentRoutineIndex++;
                if (currentRoutineIndex < routineQueue.length) { nextNoteTime += 2.0; startRoutineItem(); } else { stop(); }
            } else {
                let futureIndex = rootIndex + 2; 
                if(futureIndex < currentRoots.length) {
                    let nextRoot = getMidiPitch(currentRoots[futureIndex]);
                    let pLen = (mode==='scale5') ? 9 : (mode==='triad') ? 5 : 3; 
                    previewPatternVisuals(nextRoot, nextNoteTime + (pLen+2)*beatDur*2, beatDur);
                }
            }
        }
    }

    function scheduleNote(idx, step, time) {
        if(idx >= currentRoots.length) return;
        let root = getMidiPitch(currentRoots[idx]); let bpm = document.getElementById('bpm').value; let beatDur = 60.0 / bpm;
        let mode = routineQueue[currentRoutineIndex].mode;
        let intervals = (mode==='triad')?[0,4,7,4,0] : (mode==='scale5')?[0,2,4,5,7,5,4,2,0] : (mode==='octave')?[0,12,0] : (mode==='p5')?[0,7,0] : [0,5,0];
        if (step < intervals.length) {
            let note = root + intervals[step]; let preset = _tone_0000_JCLive_sf2_file;
            player.queueWaveTable(audioCtx, pianoSplitterNode, preset, time, note, beatDur*0.9, 1.0);
            if(step===0) playChord(root, time, beatDur*intervals.length);
        } else {
            if(step === intervals.length) playChord(root, time, beatDur);
            else if(step === intervals.length + 1) {
                let nextRoot = (idx+1 < currentRoots.length) ? getMidiPitch(currentRoots[idx+1]) : root;
                playChord(nextRoot, time, beatDur);
            }
        }
    }

    function showResultModal() {
        let modal = document.getElementById('resultModal'); modal.style.display = 'flex';
        document.getElementById('finalScore').innerText = score;
        let total = stats.totalFrames || 1;
        document.getElementById('statPerfect').innerText = Math.round((stats.perfect/total)*100) + "%";
        document.getElementById('statGood').innerText = Math.round((stats.good/total)*100) + "%";
        document.getElementById('statMiss').innerText = Math.round((stats.miss/total)*100) + "%";
        if (canRecord && audioChunks.length > 0) {
            let blob = new Blob(audioChunks, { type: mediaRecorder.mimeType });
            let url = URL.createObjectURL(blob);
            document.getElementById('resultAudio').src = url;
            document.getElementById('downloadLink').href = url;
            document.getElementById('downloadLink').download = `vocal_score_${score}.mp4`;
            document.getElementById('audioPlayerWrapper').style.display = 'block'; document.getElementById('noRecMsg').style.display = 'none';
        } else {
            document.getElementById('audioPlayerWrapper').style.display = 'none'; document.getElementById('noRecMsg').style.display = 'block';
        }
    }
    function closeResult() { document.getElementById('resultModal').style.display = 'none'; }
    function getMidiPitch(n) { let note = n.slice(0, -1), oct = parseInt(n.slice(-1)); return notes.indexOf(note) + (oct + 1) * 12; }
    function playStickClick(t) { let osc = audioCtx.createOscillator(); let g = audioCtx.createGain(); osc.frequency.setValueAtTime(1200, t); osc.frequency.exponentialRampToValueAtTime(800, t+0.05); g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(0.5, t+0.001); g.gain.exponentialRampToValueAtTime(0.001, t+0.08); osc.connect(g); g.connect(audioCtx.destination); osc.start(t); osc.stop(t+0.1); }
    function playChord(root, t, dur) { let preset = _tone_0000_JCLive_sf2_file; [0,4,7].forEach(s => player.queueWaveTable(audioCtx, pianoSplitterNode, preset, t, root+s, dur, 0.5)); }
    async function requestWakeLock() { try { if('wakeLock' in navigator) wakeLock = await navigator.wakeLock.request('screen'); } catch(e){} }
    function releaseWakeLock() { if(wakeLock){ wakeLock.release(); wakeLock=null; } }
    function autoCorrelate(buf, sampleRate) {
        let SIZE = buf.length, rms = 0;
        for (let i=0; i<SIZE; i++) rms += buf[i]*buf[i];
        if (Math.sqrt(rms/SIZE) < 0.01) return -1;
        let r1=0, r2=SIZE-1, thres=0.2;
        for (let i=0; i<SIZE/2; i++) if (Math.abs(buf[i])<thres) { r1=i; break; }
        for (let i=1; i<SIZE/2; i++) if (Math.abs(buf[SIZE-i])<thres) { r2=SIZE-i; break; }
        buf = buf.slice(r1, r2); SIZE = buf.length;
        let c = new Array(SIZE).fill(0);
        for (let i=0; i<SIZE; i++) for (let j=0; j<SIZE-i; j++) c[i] += buf[j]*buf[j+i];
        let d=0; while(c[d]>c[d+1]) d++;
        let maxval=-1, maxpos=-1;
        for(let i=d; i<SIZE; i++) if(c[i]>maxval){ maxval=c[i]; maxpos=i; }
        return sampleRate/maxpos;
    }
</script>
"""

# ---------------------------------------------------------
# 5. 組合並寫入檔案
# ---------------------------------------------------------

print("🔨 [3/4] 正在組裝 HTML 檔案...")

final_content = """<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>!!!Right On Pitch!!! Your Daily Vocal Workout v27.2</title>
""" + css_part + """
</head>
<body>
""" + html_part + """
    <script>
""" + player_code + """
""" + piano_code + """
    </script>
""" + js_part + """
</body>
</html>
"""

output_filename = "VocalTrainer_Offline_v27_2.html"

try:
    print(f"💾 [4/4] 正在寫入 {output_filename} ...")
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(final_content)
    print(f"✅ 成功！檔案已建立: {output_filename}")
    
except Exception as e:
    print(f"❌ 寫入檔案失敗: {e}")
    exit(1)
