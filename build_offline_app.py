import urllib.request
import os
import ssl

# ==========================================
# 版本更新: v33.2.2 (Performance Tuned)
# 基底: v33.2
# 
# 核心修復 (針對 Pattern 2 掉音):
# 1. [Camera] 實作 Camera Latch (鏡頭鎖定)，防止過門時的畫面劇烈重繪
# 2. [Perf] 實作 renderStartIndex/audioStartIndex，不再遍歷已結束的音符
# 3. [Audio] 過門和弦長度縮減至 90%，避免佔用複音通道
# 
# 保留功能:
# - v29.8.1 泛音抗干擾引擎
# - v33.1 視覺斷線處理
# - v33.2 完整路徑 & 真實評分
# ==========================================
VERSION = "v33_2_2_Performance"
FILENAME = f"VocalTrainer_Offline_{VERSION}.html"

print(f"🚀 正在開始打包 {VERSION} (效能優化版)...")

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
# CSS
# ---------------------------------------------------------
CSS_PART = """
<style>
    :root { 
        --bg-color: #050510; 
        --ui-bg: rgba(20, 20, 30, 0.95); 
        --text-main: #e0e0e0; 
        --accent: #00e5ff; 
        --accent-2: #ff00ff; 
        --perfect: #00e676; 
        --good: #ffea00; 
        --miss: #ff5252;
    }
    body { font-family: "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: var(--bg-color); color: var(--text-main); margin: 0; padding: 0; overflow: hidden; user-select: none; -webkit-user-select: none; }
    
    #gameStage { position: relative; width: 100vw; height: 50vh; background: #080818; border-bottom: 2px solid #333; overflow: hidden; transform: translateZ(0); }
    canvas { display: block; width: 100%; height: 100%; }
    
    .hud-layer { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; }
    
    .hp-container { position: absolute; top: 10px; left: 50%; transform: translateX(-50%); width: 60%; height: 15px; background: #333; border: 2px solid #555; border-radius: 10px; overflow: hidden; }
    .hp-fill { height: 100%; width: 100%; background: linear-gradient(90deg, #ff5252, #ffea00, #00e676); transition: width 0.2s; will-change: width; }
    .hp-text { position: absolute; top: 12px; right: 22%; color: #fff; font-size: 0.8rem; font-weight: bold; text-shadow: 1px 1px 2px black; }

    .combo-container { position: absolute; top: 40%; left: 50%; transform: translate(-50%, -50%); text-align: center; opacity: 0; transition: opacity 0.2s, transform 0.1s; will-change: opacity, transform; }
    .combo-num { font-size: 5rem; font-weight: 900; color: rgba(255,255,255,0.1); -webkit-text-stroke: 2px var(--accent); text-shadow: 0 0 20px var(--accent); font-family: 'Impact', sans-serif; }
    .combo-label { font-size: 1.5rem; color: var(--accent); letter-spacing: 5px; font-weight: bold; }
    .combo-active { opacity: 0.8; transform: translate(-50%, -50%) scale(1.1); }

    .hud-score { position: absolute; top: 10px; right: 15px; font-size: 1.2rem; font-family: monospace; color: var(--accent); }
    .version-tag { position: absolute; bottom: 5px; right: 5px; font-size: 0.7rem; color: #555; }

    #controlsArea { height: 50vh; overflow-y: auto; padding: 15px; box-sizing: border-box; background: var(--bg-color); transition: opacity 0.5s; padding-bottom: 80px; }
    #controlsArea.immersive-hidden { opacity: 0.1; pointer-events: none; }
    
    .control-group { background: var(--ui-bg); border-radius: 12px; padding: 12px; margin-bottom: 12px; border: 1px solid #333; }
    
    .play-btn { position: fixed; bottom: 20px; left: 50%; transform: translateX(-50%); background: linear-gradient(45deg, var(--accent), var(--accent-2)); color: #fff; border: none; padding: 15px 50px; border-radius: 50px; font-size: 1.5rem; font-weight: 800; width: 80%; max-width: 300px; box-shadow: 0 0 25px rgba(0, 229, 255, 0.6); z-index: 100; transition: 0.2s; text-transform: uppercase; letter-spacing: 2px; }
    .play-btn:active { transform: translateX(-50%) scale(0.95); }
    .play-btn.stop { background: #ff5252; box-shadow: 0 0 15px rgba(255, 82, 82, 0.6); }

    .tabs { display: flex; gap: 5px; margin-bottom: 10px; flex-wrap: wrap; }
    .tab-btn { flex: 1 1 30%; padding: 8px; background: #222; border: 1px solid #444; color: #888; border-radius: 5px; cursor: pointer; font-size: 0.8rem; }
    .tab-btn.active { background: #333; color: var(--accent); border-color: var(--accent); }
    input[type=range] { width: 100%; accent-color: var(--accent); }
    select { background: #222; color: #fff; border: 1px solid #444; padding: 5px; width: 100%; }
    .add-btn { width: 100%; padding: 10px; background: #333; color: white; border: 1px solid #555; border-radius: 8px; cursor: pointer; }
    
    #resultModal { position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.95); z-index: 200; display: none; flex-direction: column; justify-content: center; align-items: center; }
    .rank-big { font-size: 6rem; font-weight: 900; margin-bottom: 10px; text-shadow: 0 0 30px white; }
    .rank-S { color: var(--accent-2); text-shadow: 0 0 30px var(--accent-2); }
    .rank-A { color: var(--perfect); }
    .rank-B { color: var(--good); }
    .rank-C { color: orange; }
    .rank-F { color: var(--miss); }
    
    .loading-mask { position: fixed; top:0; left:0; width:100%; height:100%; background: #000; z-index: 999; display: flex; justify-content: center; align-items: center; color: var(--accent); flex-direction: column; }
    .stage-dead { filter: grayscale(100%) brightness(0.5) blur(2px); }
    
    .result-actions { display: flex; gap: 20px; margin-top: 20px; }
    .result-btn { padding: 15px 30px; border-radius: 30px; font-size: 1.2rem; font-weight: bold; border: none; cursor: pointer; text-transform: uppercase; color: white; min-width: 150px; }
    .btn-restart { background: var(--accent); box-shadow: 0 0 15px rgba(0,229,255,0.4); }
    .btn-home { background: #444; box-shadow: 0 0 15px rgba(255,255,255,0.1); }
</style>
"""

# Part B: HTML Body
HTML_PART = """
<div id="loadingMask" class="loading-mask">
    <div style="font-size: 3rem; margin-bottom: 20px;">⚡</div>
    <div>v33.2.2 Performance</div>
    <div style="font-size: 0.8rem; color: #888; margin-top:10px;">系統初始化中...</div>
</div>

<div id="gameStage">
    <canvas id="gameCanvas"></canvas>
    
    <div class="hud-layer">
        <div class="hp-container"><div class="hp-fill" id="hpBar"></div></div>
        <div class="hp-text">HP</div>
        <div class="hud-score" id="hudScore">SCORE: 0</div>
        <div class="combo-container" id="comboContainer"><div class="combo-num" id="comboNum">0</div><div class="combo-label">COMBO</div></div>
        <div class="version-tag">v33.2.2 Perf</div>
    </div>
</div>

<div id="controlsArea">
    <h2 style="color:var(--accent); margin:0 0 10px 0;">Vocal Arcade</h2>
    
    <div class="control-group">
        <div class="tabs">
            <button id="btn-triad" class="tab-btn active" onclick="switchConfigMode('triad')">大三和弦</button>
            <button id="btn-scale5" class="tab-btn" onclick="switchConfigMode('scale5')">五度音階</button>
            <button id="btn-octave" class="tab-btn" onclick="switchConfigMode('octave')">八度音程</button>
            <button id="btn-p5" class="tab-btn" onclick="switchConfigMode('p5')">五度</button>
            <button id="btn-p4" class="tab-btn" onclick="switchConfigMode('p4')">四度</button>
        </div>
        
        <div style="display:flex; gap:5px; margin-top:10px; align-items:center;">
            <select id="startNote"></select>
            <span>⮕</span>
            <select id="peakNote"></select>
            <span>⮕</span>
            <select id="endNote"></select>
        </div>
        
        <button class="add-btn" style="margin-top:10px;" onclick="addToRoutine()">⬇️ 加入挑戰清單</button>
    </div>

    <div class="control-group">
        <div style="display:flex; justify-content:space-between; margin-bottom:5px;">
            <span>📋 挑戰清單</span>
            <span style="color:var(--miss); cursor:pointer;" onclick="clearRoutine()">清空</span>
        </div>
        <ul id="routineList" style="list-style:none; padding:0; margin:0; background:#111; min-height:40px; border-radius:5px;">
            <li style="padding:10px; color:#666; text-align:center;">(尚未加入)</li>
        </ul>
        <div style="margin-top:10px; font-size:0.9rem;">速度 (BPM): <span id="bpmVal">100</span></div>
        <input type="range" id="bpm" min="60" max="180" value="100" oninput="document.getElementById('bpmVal').innerText = this.value">
    </div>
    
    <div class="control-group">
        <div style="font-size:0.9rem;">監聽音量</div>
        <input type="range" id="volMonitor" min="0" max="100" value="80">
        <div style="font-size:0.9rem; margin-top:5px;">藍牙延遲: <span id="latencyVal">0</span>ms</div>
        <input type="range" id="latencySlider" min="0" max="500" value="0" step="10">
    </div>
</div>

<button class="play-btn" id="playBtn" onclick="togglePlay()">START</button>

<div id="resultModal">
    <div style="color:#aaa; font-size:1rem; letter-spacing:2px;">RANK</div>
    <div class="rank-big" id="finalRank">S</div>
    
    <div style="display:flex; gap:20px; margin-bottom:20px;">
        <div style="text-align:center;">
            <div style="font-size:1.5rem; color:var(--perfect);" id="resPerfect">0</div>
            <div style="font-size:0.7rem; color:#888;">PERFECT</div>
        </div>
        <div style="text-align:center;">
            <div style="font-size:1.5rem; color:var(--good);" id="resGood">0</div>
            <div style="font-size:0.7rem; color:#888;">GOOD</div>
        </div>
        <div style="text-align:center;">
            <div style="font-size:1.5rem; color:var(--miss);" id="resMiss">0</div>
            <div style="font-size:0.7rem; color:#888;">MISS</div>
        </div>
    </div>
    
    <div style="color:white; font-size:1.2rem; margin-bottom:20px;">Max Combo: <span id="resCombo" style="color:var(--accent);">0</span></div>
    
    <div class="result-actions">
        <button class="result-btn btn-home" onclick="goHome()">🏠 HOME</button>
        <button class="result-btn btn-restart" onclick="restartGame()">🔄 RESTART</button>
    </div>
</div>
"""

# Part C: JavaScript
JS_PART = """
<script>
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    let audioCtx, player;
    let pianoSplitterNode, monitorGainNode, mixerNode, micSource, pianoDelayNode; 
    let pianoAnalyser, vocalAnalyser, pitchFilterNode; 
    
    // Constants
    const FPS = 40;
    const ANALYSIS_INTERVAL = 1.0 / FPS;
    const PIXELS_PER_SEC = 120; 
    const PIXELS_PER_SEMITONE = 20;
    const VISUAL_OFFSET_SEC = 0.15; 
    const BLOCK_HEIGHT = 40; 
    
    let isPlaying = false;
    let gameLoopId;
    let lastAnalysisTime = 0;
    
    let gameTargets = [];      
    let userPitchHistory = []; 
    let particles = [];        
    let popups = [];           
    
    let hp = 100;
    let score = 0;
    let combo = 0;
    let maxCombo = 0;
    let stats = { perfect:0, good:0, miss:0 };
    let isGameOver = false;
    let isDying = false;

    // Camera State
    let cameraY = 60; 
    let targetCameraY = 60;
    let lastValidCameraY = 60; // FIX: Camera Latch

    let pitchSmoothingBuffer = [];
    let audioBuffer = new Float32Array(2048);
    let frequencyBuffer = new Float32Array(2048);
    
    let routineQueue = [];
    let currentRoutineIndex = 0;
    let nextNoteTime = 0;
    let lastGameTime = 0;
    let timerID;
    
    // Performance Indices (Optimization)
    let renderStartIndex = 0;
    let audioStartIndex = 0;
    
    let scheduleAheadTime = 0.5; 
    
    let editingMode = 'triad';
    let countInBeats = 4;

    const notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
    let rangeProfiles = {
        'triad':  { s:'C3', p:'C4', e:'C3' },
        'scale5': { s:'C3', p:'G3', e:'C3' },
        'octave': { s:'C3', p:'C4', e:'C3' },
        'p5':     { s:'C3', p:'C4', e:'C3' },
        'p4':     { s:'C3', p:'C4', e:'C3' }
    };

    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');
    let ui = {};

    window.onload = function() {
        ui = {
            hpBar: document.getElementById('hpBar'),
            score: document.getElementById('hudScore'),
            comboContainer: document.getElementById('comboContainer'),
            comboNum: document.getElementById('comboNum')
        };
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);
        initSelects();
        try {
            player = new WebAudioFontPlayer();
            document.getElementById('loadingMask').style.display = 'none';
        } catch(e) { console.log(e); }
    };

    function resizeCanvas() {
        canvas.width = document.getElementById('gameStage').clientWidth;
        canvas.height = document.getElementById('gameStage').clientHeight;
    }

    function initSelects() {
        const s = document.getElementById('startNote');
        const p = document.getElementById('peakNote');
        const e = document.getElementById('endNote');
        for(let oct=2; oct<=5; oct++) {
            notes.forEach(n => {
                let val = `${n}${oct}`;
                s.add(new Option(val, val));
                p.add(new Option(val, val));
                e.add(new Option(val, val));
            });
        }
        applyProfile('triad');
    }
    
    function switchConfigMode(mode) {
        editingMode = mode;
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.getElementById('btn-'+mode).classList.add('active');
        applyProfile(mode);
    }
    
    function applyProfile(mode) {
        let d = rangeProfiles[mode];
        if(d) {
            document.getElementById('startNote').value = d.s;
            document.getElementById('peakNote').value = d.p;
            document.getElementById('endNote').value = d.e;
        }
    }
    
    function addToRoutine() {
        let s = document.getElementById('startNote').value;
        let p = document.getElementById('peakNote').value;
        let e = document.getElementById('endNote').value;
        routineQueue.push({ mode: editingMode, s:s, p:p, e:e });
        renderRoutine();
    }
    
    function renderRoutine() {
        let ul = document.getElementById('routineList');
        ul.innerHTML = "";
        routineQueue.forEach((item, i) => {
            ul.innerHTML += `<li style="padding:8px; border-bottom:1px solid #222; display:flex; justify-content:space-between;"><span>${i+1}. ${item.mode} (${item.s} ⮕ ${item.p} ⮕ ${item.e})</span><span onclick="routineQueue.splice(${i},1);renderRoutine();" style="color:#666;cursor:pointer;">✕</span></li>`;
        });
    }
    
    function clearRoutine() { routineQueue = []; renderRoutine(); }

    async function initAudio() {
        if(!audioCtx) {
            audioCtx = new (window.AudioContext||window.webkitAudioContext)({sampleRate:48000});
            mixerNode = audioCtx.createMediaStreamDestination();
            pianoAnalyser = audioCtx.createAnalyser();
            vocalAnalyser = audioCtx.createAnalyser(); vocalAnalyser.fftSize = 2048;
            pianoSplitterNode = audioCtx.createGain();
            monitorGainNode = audioCtx.createGain();
            pianoSplitterNode.connect(monitorGainNode);
            monitorGainNode.connect(audioCtx.destination);
            pianoDelayNode = audioCtx.createDelay(1.0);
            pianoSplitterNode.connect(pianoDelayNode);
            try {
                let stream = await navigator.mediaDevices.getUserMedia({audio:{echoCancellation:false, autoGainControl:false, noiseSuppression:false}});
                micSource = audioCtx.createMediaStreamSource(stream);
                pitchFilterNode = audioCtx.createBiquadFilter();
                pitchFilterNode.type = "lowpass";
                pitchFilterNode.frequency.value = 1500;
                micSource.connect(pitchFilterNode);
                pitchFilterNode.connect(vocalAnalyser);
                let micDirect = audioCtx.createGain();
                micSource.connect(micDirect);
                micDirect.connect(monitorGainNode);
            } catch(e) { console.log("Mic error"); }
        }
        if(audioCtx.state === 'suspended') await audioCtx.resume();
        monitorGainNode.gain.value = document.getElementById('volMonitor').value/100;
        pianoDelayNode.delayTime.value = document.getElementById('latencySlider').value/1000;
    }

    async function togglePlay() {
        if(isPlaying) { stop(); return; }
        if(routineQueue.length===0) { alert("請加入挑戰！"); return; }
        
        try {
            await initAudio(); 
            
            isPlaying = true; isGameOver = false; isDying = false;
            document.getElementById('gameStage').classList.remove('stage-dead');
            hp = 100; score = 0; combo = 0; maxCombo = 0;
            stats = {perfect:0, good:0, miss:0};
            gameTargets = []; userPitchHistory = []; pitchSmoothingBuffer = []; particles = []; popups = [];
            currentRoutineIndex = 0;
            lastGameTime = 0;
            renderStartIndex = 0; audioStartIndex = 0;
            
            let startMidi = getMidiPitch(routineQueue[0].s);
            cameraY = startMidi; targetCameraY = startMidi; lastValidCameraY = startMidi;
            
            document.getElementById('controlsArea').classList.add('immersive-hidden');
            document.getElementById('playBtn').innerText = "STOP";
            document.getElementById('playBtn').classList.add('stop');
            updateUI(true);
            
            setTimeout(() => {
                startRoutineItem(); 
                scheduler(); 
                renderLoop();
            }, 50);
            
        } catch(e) { alert("啟動失敗: " + e.message); }
    }

    function stop() {
        isPlaying = false;
        clearTimeout(timerID);
        cancelAnimationFrame(gameLoopId);
        if(player) player.cancelQueue(audioCtx);
        document.getElementById('controlsArea').classList.remove('immersive-hidden');
        document.getElementById('playBtn').innerText = "START";
        document.getElementById('playBtn').classList.remove('stop');
        if(!isGameOver && !isDying) showResult();
    }

    function scheduler() {
        while(isPlaying && nextNoteTime < audioCtx.currentTime + scheduleAheadTime) {
            nextNoteTime += 0.1;
        }
        // OPTIMIZATION: Use audioStartIndex
        for(let i = audioStartIndex; i < gameTargets.length; i++) {
            let t = gameTargets[i];
            
            // Advance index if note is long gone (keep buffer for low latency systems)
            if (t.startTime < audioCtx.currentTime - 1.0) {
                audioStartIndex = i;
            }
            
            if(!t.played && t.startTime < audioCtx.currentTime + scheduleAheadTime) {
                t.played = true;
                let vol = t.isBridge ? 0.7 : 0.5;
                player.queueWaveTable(audioCtx, pianoSplitterNode, _tone_0000_JCLive_sf2_file, t.startTime, t.midi, t.duration, vol);
            }
        }
        if(isPlaying) timerID = setTimeout(scheduler, 50);
    }

    function renderLoop() {
        if(!isPlaying) return;
        let now = audioCtx.currentTime;
        
        // --- 1. OPTIMIZED CAMERA LOGIC (With Latch) ---
        let futureNotes = [];
        let count = 0;
        let sum = 0;
        
        // Scan for future notes (optimized loop)
        for(let i = renderStartIndex; i < gameTargets.length; i++) {
            let t = gameTargets[i];
            // Stop scanning if too far in future
            if (t.startTime > now + 3.0) break;
            
            if (!t.isBridge && t.startTime > now) {
                sum += t.midi;
                count++;
            }
        }
        
        if (count > 0) {
            targetCameraY = sum / count;
            lastValidCameraY = targetCameraY; // Update Latch
        } else {
            targetCameraY = lastValidCameraY; // HOLD POSITION (Anti-Panic)
        }
        
        cameraY += (targetCameraY - cameraY) * 0.05;

        // --- 2. RENDER ---
        ctx.fillStyle = "#050510"; ctx.fillRect(0, 0, canvas.width, canvas.height);
        drawGrid(cameraY);
        let phX = canvas.width * 0.2;
        
        // OPTIMIZATION: Render loop with Start Index
        for(let i = renderStartIndex; i < gameTargets.length; i++) {
            let t = gameTargets[i];
            
            // Garbage Collection for Renderer
            if (t.startTime + t.duration < now - 2.0) {
                renderStartIndex = i; // Advance start pointer
                continue; 
            }
            
            // Stop drawing if off-screen to the right
            let x = phX + (t.startTime - now) * PIXELS_PER_SEC;
            if (x > canvas.width) break;

            if(t.isBridge) continue;

            let w = t.duration * PIXELS_PER_SEC;
            let y = getYfromMidi(t.midi);
            
            if (x + w > 0) {
                ctx.fillStyle = "rgba(0, 229, 255, 0.1)";
                ctx.strokeStyle = "rgba(0, 229, 255, 0.5)";
                ctx.lineWidth = 2;
                roundRect(ctx, x, y - BLOCK_HEIGHT/2, w, BLOCK_HEIGHT, 5);
                ctx.stroke();
                ctx.fill();
                
                if (t.hitFrames > 0) {
                    let fillW = w * (t.hitFrames / t.totalFrames);
                    ctx.fillStyle = "rgba(0, 229, 255, 0.8)";
                    ctx.shadowBlur = 10; ctx.shadowColor = "#00e5ff";
                    ctx.fillRect(x, y - BLOCK_HEIGHT/2 + 2, Math.min(w, fillW), BLOCK_HEIGHT - 4);
                    ctx.shadowBlur = 0;
                }
            }
            if (!t.processed && now > t.startTime + t.duration) {
                t.processed = true;
                evaluateNote(t, x + w, y);
            }
        }

        if(!isDying) detectAndProcessPitch(now, phX);
        updateAndDrawParticles();
        updateAndDrawPopups();
        
        if(hp <= 0 && !isGameOver && !isDying) {
            triggerDeath();
        }
        
        if (!isGameOver && !isDying && lastGameTime > 0 && now > lastGameTime + 2.0) {
            stop();
        }

        gameLoopId = requestAnimationFrame(renderLoop);
    }
    
    function updateUI(force = false) {
        if (force || isPlaying) {
            if(ui.hpBar) {
                ui.hpBar.style.width = hp + "%";
                if(hp < 30) ui.hpBar.style.background = "#ff5252"; 
                else ui.hpBar.style.background = "linear-gradient(90deg, #ff5252, #ffea00, #00e676)";
            }
            if(ui.score) ui.score.innerText = "SCORE: " + score;
            if(ui.comboContainer) {
                if(combo > 1) { 
                    ui.comboNum.innerText = combo; 
                    ui.comboContainer.classList.add('combo-active'); 
                } else { 
                    ui.comboContainer.classList.remove('combo-active'); 
                }
            }
        }
    }
    
    function triggerDeath() {
        isDying = true;
        document.getElementById('gameStage').classList.add('stage-dead');
        updateUI(true);
        setTimeout(() => {
            isGameOver = true;
            stop();
            showResult();
        }, 800);
    }
    
    function evaluateNote(note, visualX, visualY) {
        if(isDying || note.isBridge) return; 
        
        let total = note.totalFrames > 0 ? note.totalFrames : 1;
        let coverage = note.hitFrames / total;
        let hit = false;
        
        if (coverage >= 0.85) {
            combo++; score += 100 + (combo * 10); hp = Math.min(100, hp + 5); stats.perfect++;
            spawnPopup(visualX, visualY, "PERFECT", "#00e676"); spawnParticles(visualX, visualY, "#00e676", 10);
            hit = true;
        } else if (coverage >= 0.50) {
            combo++; score += 50 + (combo * 5); hp = Math.min(100, hp + 2); stats.good++;
            spawnPopup(visualX, visualY, "GOOD", "#ffea00");
            hit = true;
        } else {
            combo = 0; hp = Math.max(0, hp - 10); 
            stats.miss++;
            spawnPopup(visualX, visualY, "MISS", "#ff5252");
        }
        if (combo > maxCombo) maxCombo = combo;
        if (hit || combo === 0) updateUI();
    }

    function detectPitchYIN(buffer, sampleRate) {
        const threshold = 0.15; 
        const bufferSize = buffer.length; 
        const yinBufferLength = bufferSize / 2; 
        let yinBuffer = new Float32Array(yinBufferLength);
        const minTau = Math.floor(sampleRate / 1000); 
        const maxTau = Math.floor(sampleRate / 60); 
        if (maxTau > yinBufferLength) return -1;
        for (let tau = 0; tau < maxTau; tau++) { 
            let sum = 0; 
            for (let i = 0; i < yinBufferLength; i++) { 
                let delta = buffer[i] - buffer[i + tau]; 
                sum += delta * delta; 
            } 
            yinBuffer[tau] = sum; 
        }
        yinBuffer[0] = 1; let runningSum = 0; yinBuffer[0] = 1;
        for (let tau = 1; tau < maxTau; tau++) { runningSum += yinBuffer[tau]; yinBuffer[tau] *= tau / runningSum; }
        let tauEstimate = -1; 
        for (let tau = minTau; tau < maxTau; tau++) { if (yinBuffer[tau] < threshold) { while (tau + 1 < maxTau && yinBuffer[tau + 1] < yinBuffer[tau]) { tau++; } tauEstimate = tau; break; } }
        if (tauEstimate === -1) { let minVal = 100; for (let tau = minTau; tau < maxTau; tau++) { if (yinBuffer[tau] < minVal) { minVal = yinBuffer[tau]; tauEstimate = tau; } } }
        if (tauEstimate === -1) return -1;
        let betterTau = tauEstimate; 
        if (tauEstimate > 0 && tauEstimate < maxTau - 1) { let s0 = yinBuffer[tauEstimate - 1]; let s1 = yinBuffer[tauEstimate]; let s2 = yinBuffer[tauEstimate + 1]; let adjustment = (s2 - s0) / (2 * (2 * s1 - s2 - s0)); betterTau += adjustment; }
        return sampleRate / betterTau;
    }

    // --- VISUAL FIX: v33.1 Logic (Line Break) ---
    function detectAndProcessPitch(now, playheadX) {
        if (now - lastAnalysisTime < ANALYSIS_INTERVAL) { drawTrail(now, playheadX); return; }
        lastAnalysisTime = now;
        
        if (!vocalAnalyser) return;
        
        vocalAnalyser.getFloatTimeDomainData(audioBuffer);
        let rms = 0;
        for(let i=0; i<audioBuffer.length; i++) rms += audioBuffer[i]*audioBuffer[i];
        rms = Math.sqrt(rms/audioBuffer.length);
        
        let detectedMidi = null; 
        let color = "rgba(255,255,255,0.2)"; 
        let isHit = false;

        if (rms > 0.01) {
            let freq = detectPitchYIN(audioBuffer, audioCtx.sampleRate);
            if (freq !== -1) {
                // v29.8.1 Logic (Restored)
                let currentTarget = gameTargets.find(t => !t.isBridge && now >= t.startTime && now <= t.startTime + t.duration);
                if (currentTarget) {
                    let targetFreq = midiToFreq(currentTarget.midi);
                    let ratio = freq / targetFreq;
                    let nearestInt = Math.round(ratio);
                    let diffFromInt = Math.abs(ratio - nearestInt);
                    
                    if (nearestInt > 1 && nearestInt <= 4 && diffFromInt < 0.1) {
                         vocalAnalyser.getFloatFrequencyData(frequencyBuffer);
                         let peakCheck = checkPeakProminence(targetFreq, audioCtx.sampleRate, frequencyBuffer);
                         if (peakCheck.isPeak && peakCheck.energy > 0) freq = targetFreq;
                    }
                    else {
                        let rawMidi = freqToMidi(freq);
                        let midiDiff = rawMidi - currentTarget.midi;
                         if (Math.abs(midiDiff - 12) < 2.0 || Math.abs(midiDiff - 24) < 2.0 || Math.abs(midiDiff - 19) < 2.0) {
                             vocalAnalyser.getFloatFrequencyData(frequencyBuffer);
                             let peakCheck = checkPeakProminence(targetFreq, audioCtx.sampleRate, frequencyBuffer);
                             if (peakCheck.isPeak) freq = targetFreq;
                         }
                    }
                }
                
                let processedMidi = freqToMidi(freq);
                pitchSmoothingBuffer.push(processedMidi);
                if(pitchSmoothingBuffer.length > 3) pitchSmoothingBuffer.shift();
                detectedMidi = pitchSmoothingBuffer.reduce((a,b)=>a+b,0) / pitchSmoothingBuffer.length;
                
                if (currentTarget) {
                    currentTarget.totalFrames++;
                    if (Math.abs(detectedMidi - currentTarget.midi) <= 0.5) {
                        isHit = true; 
                        currentTarget.hitFrames++; 
                        color = "#00e676"; 
                        score += 1;
                        if (Math.random() < 0.2) spawnParticles(playheadX, getYfromMidi(detectedMidi), "#00e676", 1);
                    } else {
                        color = "#ff5252";
                    }
                }
            } else {
                pitchSmoothingBuffer = [];
            }
        }
        
        userPitchHistory.push({ time: now + VISUAL_OFFSET_SEC, midi: detectedMidi, color: color, isHit: isHit });
        while(userPitchHistory.length > 0 && userPitchHistory[0].time < now - 2.0) userPitchHistory.shift();
        drawTrail(now, playheadX);
    }
    
    function getLinearEnergy(targetFreq, sampleRate, buffer) { let nyquist = sampleRate / 2; let index = Math.round((targetFreq / nyquist) * buffer.length); if (index < 0 || index >= buffer.length) return 0; let db = buffer[index]; return Math.pow(10, db / 20); }

    function checkPeakProminence(targetFreq, sampleRate, buffer) {
        let nyquist = sampleRate / 2; let centerIdx = Math.round((targetFreq / nyquist) * buffer.length);
        if (centerIdx < 2 || centerIdx >= buffer.length - 2) return { energy: 0, isPeak: false };
        let maxIdx = centerIdx; let maxDb = buffer[centerIdx];
        if (buffer[centerIdx-1] > maxDb) { maxDb = buffer[centerIdx-1]; maxIdx = centerIdx-1; }
        if (buffer[centerIdx+1] > maxDb) { maxDb = buffer[centerIdx+1]; maxIdx = centerIdx+1; }
        let centerLinear = Math.pow(10, maxDb / 20);
        let neighborAvg = (Math.pow(10, buffer[maxIdx-2]/20) + Math.pow(10, buffer[maxIdx+2]/20)) / 2;
        return { energy: centerLinear, isPeak: centerLinear > (neighborAvg * 1.2) };
    }

    function drawGrid(camY) {
        if(isNaN(camY)) camY = 60;
        let centerMidi = Math.round(camY);
        ctx.textAlign = "right"; ctx.textBaseline = "middle"; ctx.font = "12px monospace";
        for (let m = centerMidi - 12; m <= centerMidi + 12; m++) {
            let y = getYfromMidi(m);
            let isC = (m % 12) === 0;
            ctx.strokeStyle = isC ? "#444" : "#222";
            ctx.lineWidth = 1;
            ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
            if (isC) { ctx.fillStyle = "#666"; ctx.fillText(getNoteName(m), canvas.width - 10, y); }
        }
        ctx.strokeStyle = "rgba(255,255,255,0.3)"; ctx.beginPath(); ctx.moveTo(canvas.width * 0.2, 0); ctx.lineTo(canvas.width * 0.2, canvas.height); ctx.stroke();
    }

    function drawTrail(now, phX) {
        if(userPitchHistory.length < 2) return;
        ctx.lineWidth = 4; ctx.lineCap = "round"; ctx.lineJoin = "round";
        for(let i=1; i<userPitchHistory.length; i++) {
            let p1 = userPitchHistory[i-1]; let p2 = userPitchHistory[i];
            if (p1.midi && p2.midi) {
                // v33.1 Visual Fix: Break line on large jumps
                if (Math.abs(p1.midi - p2.midi) > 3.0) continue;
                
                let x1 = phX + (p1.time - now) * PIXELS_PER_SEC; let x2 = phX + (p2.time - now) * PIXELS_PER_SEC;
                let y1 = getYfromMidi(p1.midi); let y2 = getYfromMidi(p2.midi);
                if(!isNaN(y1) && !isNaN(y2)) {
                    ctx.strokeStyle = p2.color;
                    if (p2.isHit) { ctx.shadowBlur = 10; ctx.shadowColor = p2.color; ctx.lineWidth = 6; } else { ctx.shadowBlur = 0; ctx.lineWidth = 4; }
                    ctx.beginPath(); ctx.moveTo(x1, y1); ctx.lineTo(x2, y2); ctx.stroke(); ctx.shadowBlur = 0;
                }
            }
        }
    }

    function spawnParticles(x, y, color, count) { for(let i=0; i<count; i++) particles.push({ x: x, y: y, vx: (Math.random()-0.5)*4, vy: (Math.random()-0.5)*4, life: 1.0, color: color }); }
    function updateAndDrawParticles() {
        for(let i=particles.length-1; i>=0; i--) {
            let p = particles[i]; p.x += p.vx; p.y += p.vy; p.life -= 0.05;
            if(p.life <= 0) { particles.splice(i, 1); continue; }
            ctx.globalAlpha = p.life; ctx.fillStyle = p.color; ctx.beginPath(); ctx.arc(p.x, p.y, 3, 0, Math.PI*2); ctx.fill(); ctx.globalAlpha = 1.0;
        }
    }
    
    function spawnPopup(x, y, text, color) { popups.push({x:x, y:y, text:text, color:color, life:1.0, floatY:0}); }
    function updateAndDrawPopups() {
        ctx.font = "bold 20px Arial"; ctx.textAlign = "center";
        for(let i=popups.length-1; i>=0; i--) {
            let p = popups[i]; p.life -= 0.02; p.floatY -= 1;
            if(p.life <= 0) { popups.splice(i, 1); continue; }
            ctx.globalAlpha = p.life; ctx.fillStyle = p.color; ctx.shadowBlur = 5; ctx.shadowColor = "black"; ctx.fillText(p.text, p.x, p.y + p.floatY); ctx.shadowBlur = 0; ctx.globalAlpha = 1.0;
        }
    }

    function midiToFreq(m) { return 440 * Math.pow(2, (m-69)/12); }
    function freqToMidi(f) { return 12 * (Math.log(f/440)/Math.log(2)) + 69; }
    function getYfromMidi(m) { return (canvas.height/2) - (m - cameraY) * PIXELS_PER_SEMITONE; }
    function roundRect(ctx, x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
    function getNoteName(m) { let n=notes[m%12]; let o=Math.floor(m/12)-1; return n+o; }
    function playStickClick(t) { let osc = audioCtx.createOscillator(); let g = audioCtx.createGain(); osc.frequency.setValueAtTime(1200, t); osc.frequency.exponentialRampToValueAtTime(800, t+0.05); g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(0.5, t+0.001); g.gain.exponentialRampToValueAtTime(0.001, t+0.08); osc.connect(g); g.connect(audioCtx.destination); osc.start(t); osc.stop(t+0.1); }
    function playChord(root, t, dur) { [0,4,7].forEach(s => player.queueWaveTable(audioCtx, pianoSplitterNode, _tone_0000_JCLive_sf2_file, t, root+s, dur, 0.3)); }
    function getMidiPitch(n) { let note = n.slice(0, -1), oct = parseInt(n.slice(-1)); return notes.indexOf(note) + (oct + 1) * 12; }

    function startRoutineItem() {
        let config = routineQueue[currentRoutineIndex];
        let bpm = document.getElementById('bpm').value; 
        let beatDur = 60.0/bpm;
        
        let now = audioCtx.currentTime;
        let playStartTime = now + 1.0; 
        nextNoteTime = playStartTime;
        
        let rootMidi = getMidiPitch(config.s);
        playChord(rootMidi, playStartTime, beatDur * 4);
        for(let i=0; i<4; i++) playStickClick(playStartTime + i*beatDur);
        
        let singingStartTime = playStartTime + (4 * beatDur);
        generateTargets(config, singingStartTime, beatDur);
        
        nextNoteTime = singingStartTime; 
    }
    
    // FEATURE: Full Path Generation (Start -> Peak -> End)
    function generateTargets(config, startTime, beatDur) {
        let allOpts = []; for(let oct=2; oct<=5; oct++) notes.forEach(n => allOpts.push(`${n}${oct}`));
        let sIdx = allOpts.indexOf(config.s);
        let pIdx = allOpts.indexOf(config.p);
        let eIdx = allOpts.indexOf(config.e);
        
        let currentRoots = [];
        
        // Ascent: Start -> Peak
        if (sIdx <= pIdx) {
            for(let i=sIdx; i<=pIdx; i++) currentRoots.push(allOpts[i]);
        }
        
        // Descent: (Peak-1) -> End
        // Check to avoid duplicates if Peak == Start
        if (eIdx !== -1 && pIdx > eIdx) {
            for(let i=pIdx-1; i>=eIdx; i--) currentRoots.push(allOpts[i]);
        }
        
        let currentTime = startTime; 
        
        currentRoots.forEach((r, idx) => {
            let rootMidi = getMidiPitch(r);
            let intervals = [0, 4, 7, 4, 0];
            if(config.mode === 'scale5') intervals = [0, 2, 4, 5, 7, 5, 4, 2, 0];
            else if(config.mode === 'octave') intervals = [0, 12, 0];
            else if(config.mode === 'p5') intervals = [0, 7, 0];
            else if(config.mode === 'p4') intervals = [0, 5, 0];
            
            intervals.forEach((iv, i) => {
                gameTargets.push({ 
                    midi: rootMidi + iv, 
                    startTime: currentTime + (i * beatDur), 
                    duration: beatDur * 0.9, 
                    hitFrames: 0, totalFrames: 0, processed: false, played: false, isBridge: false
                });
            });
            
            let patternDuration = intervals.length * beatDur;
            let restDuration = 2 * beatDur;
            
            // Bridge Logic
            if (idx < currentRoots.length - 1) {
                // FIX: Bridge duration slightly shorter to prevent voice stealing
                let bridgeDur = beatDur * 0.9;
                
                // Beat 1: Current
                gameTargets.push({ midi: rootMidi, startTime: currentTime + patternDuration, duration: bridgeDur, hitFrames: 0, totalFrames: 0, processed: true, played: false, isBridge: true });
                // Beat 2: Next
                let nextRootMidi = getMidiPitch(currentRoots[idx+1]);
                gameTargets.push({ midi: nextRootMidi, startTime: currentTime + patternDuration + beatDur, duration: bridgeDur, hitFrames: 0, totalFrames: 0, processed: true, played: false, isBridge: true });
            }

            currentTime += (patternDuration + restDuration);
        });
        nextNoteTime = currentTime;
        lastGameTime = currentTime; 
    }
    
    function restartGame() {
        document.getElementById('resultModal').style.display = 'none';
        togglePlay();
    }
    
    function goHome() {
        document.getElementById('resultModal').style.display = 'none';
        document.getElementById('controlsArea').classList.remove('immersive-hidden');
        document.getElementById('playBtn').innerText = "START";
        document.getElementById('playBtn').classList.remove('stop');
        hp = 100; score = 0; combo = 0;
        updateUI(true);
    }
    
    // SCORING FIX: Weighted Total (Good = 0.5)
    function showResult() {
        document.getElementById('resultModal').style.display = 'flex';
        let total = stats.perfect + stats.good + stats.miss;
        if(total === 0) total = 1;
        
        document.getElementById('resPerfect').innerText = stats.perfect;
        document.getElementById('resGood').innerText = stats.good;
        document.getElementById('resMiss').innerText = stats.miss;
        document.getElementById('resCombo').innerText = maxCombo;
        
        // New Formula: (Perfect*1 + Good*0.5) / Total
        let weightedScore = (stats.perfect * 1.0 + stats.good * 0.5) / total;
        
        let rank = "F";
        if(weightedScore >= 0.95) rank = "S";
        else if(weightedScore >= 0.8) rank = "A";
        else if(weightedScore >= 0.6) rank = "B";
        else if(weightedScore >= 0.4) rank = "C";
        
        let rEl = document.getElementById('finalRank');
        rEl.innerText = rank;
        rEl.className = "rank-big rank-" + rank;
    }

</script>
"""

# ---------------------------------------------------------
# 5. 寫入檔案
# ---------------------------------------------------------
try:
    print(f"💾 [3/4] 正在寫入 {FILENAME} ...")
    with open(FILENAME, "w", encoding="utf-8") as f:
        f.write('<!DOCTYPE html>\n<html lang="zh-TW">\n<head>\n')
        f.write('<meta charset="UTF-8">\n<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">\n')
        f.write(f'<title>Vocal Arcade {VERSION}</title>\n')
        f.write(CSS_PART)
        f.write('\n</head>\n<body>\n')
        f.write(HTML_PART)
        f.write('\n<script>\n')
        f.write(player_code)
        f.write('\n')
        f.write(piano_code)
        f.write('\n</script>\n')
        f.write(JS_PART)
        f.write('\n</body>\n</html>')
    print(f"✅ 成功！檔案已建立: {FILENAME}")
except Exception as e:
    print(f"❌ 寫入檔案失敗: {e}")
    exit(1)
