import urllib.request
import os
import ssl

# ==========================================
# 版本更新: v30.2 (Stable Arcade)
# 修正項目:
# 1. 補回 P4 (四度) 與 P5 (五度) 練習模式
# 2. 修復 generateTargets 寫死三和弦的邏輯錯誤
# 3. 修復動態鏡頭因「除以零」導致畫面 NaN (音符消失) 的 Bug
# 4. 包含 v30.1 的所有修正 (預備拍、BPM、死掉動畫)
# ==========================================
VERSION = "v30_2_Stable"
FILENAME = f"VocalTrainer_Offline_{VERSION}.html"

print(f"🚀 正在開始打包 {VERSION} (穩定街機版)...")

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
# 4. 定義內容區塊
# ---------------------------------------------------------

# Part A: CSS
CSS_PART = """
<style>
    :root { 
        --bg-color: #050510; 
        --ui-bg: rgba(20, 20, 30, 0.95); 
        --text-main: #e0e0e0; 
        --accent: #00e5ff; /* Cyan */
        --accent-2: #ff00ff; /* Magenta */
        --perfect: #00e676; 
        --good: #ffea00; 
        --miss: #ff5252;
    }
    body { font-family: "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: var(--bg-color); color: var(--text-main); margin: 0; padding: 0; overflow: hidden; user-select: none; -webkit-user-select: none; }
    
    #gameStage { position: relative; width: 100vw; height: 50vh; background: #080818; border-bottom: 2px solid #333; overflow: hidden; transition: filter 0.5s; }
    canvas { display: block; width: 100%; height: 100%; }
    
    .hud-layer { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; }
    
    /* HP Bar */
    .hp-container { position: absolute; top: 10px; left: 50%; transform: translateX(-50%); width: 60%; height: 15px; background: #333; border: 2px solid #555; border-radius: 10px; overflow: hidden; box-shadow: 0 0 10px rgba(0,0,0,0.5); }
    .hp-fill { height: 100%; width: 100%; background: linear-gradient(90deg, #ff5252, #ffea00, #00e676); transition: width 0.2s linear; }
    .hp-text { position: absolute; top: 12px; right: 22%; color: #fff; font-size: 0.8rem; font-weight: bold; text-shadow: 1px 1px 2px black; }

    .combo-container { position: absolute; top: 40%; left: 50%; transform: translate(-50%, -50%); text-align: center; opacity: 0; transition: opacity 0.2s, transform 0.1s; }
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
</style>
"""

# Part B: HTML Body
HTML_PART = """
<div id="loadingMask" class="loading-mask">
    <div style="font-size: 3rem; margin-bottom: 20px;">🛡️</div>
    <div>v30.2 Stable</div>
    <div style="font-size: 0.8rem; color: #888; margin-top:10px;">修復鏡頭與練習模式...</div>
</div>

<div id="gameStage">
    <canvas id="gameCanvas"></canvas>
    
    <div class="hud-layer">
        <div class="hp-container">
            <div class="hp-fill" id="hpBar"></div>
        </div>
        <div class="hp-text">HP</div>
        <div class="hud-score" id="hudScore">SCORE: 0</div>
        <div class="combo-container" id="comboContainer">
            <div class="combo-num" id="comboNum">0</div>
            <div class="combo-label">COMBO</div>
        </div>
        <div class="version-tag">v30.2 Stable</div>
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
        <div style="display:flex; gap:5px; margin-top:10px;">
            <select id="startNote"></select>
            <span style="align-self:center;">⮕</span>
            <select id="peakNote"></select>
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
    
    <button class="play-btn" style="position:relative; bottom:auto; left:auto; transform:none; width:auto; padding:10px 40px; font-size:1rem;" onclick="closeResult()">CONTINUE</button>
</div>
"""

# Part C: JavaScript
JS_PART = """
<script>
    const AudioContext = window.AudioContext || window.webkitAudioContext;
    let audioCtx, player;
    let pianoSplitterNode, monitorGainNode, mixerNode, micSource, pianoDelayNode; 
    let pianoAnalyser, vocalAnalyser;
    let pitchFilterNode; 
    
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

    let cameraY = 60; 
    let targetCameraY = 60;

    let pitchSmoothingBuffer = [];
    let audioBuffer = new Float32Array(2048);
    let frequencyBuffer = new Float32Array(2048);
    
    let routineQueue = [];
    let currentRoutineIndex = 0;
    let nextNoteTime = 0;
    let timerID;
    let scheduleAheadTime = 0.1;
    let editingMode = 'triad';
    let countInBeats = 4;

    const notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
    
    // Updated Profiles with P4 and P5
    let rangeProfiles = {
        'triad':  { s:'C3', p:'C4', e:'C3' },
        'scale5': { s:'C3', p:'G3', e:'C3' },
        'octave': { s:'C3', p:'C4', e:'C3' },
        'p5':     { s:'C3', p:'C4', e:'C3' },
        'p4':     { s:'C3', p:'C4', e:'C3' }
    };

    const canvas = document.getElementById('gameCanvas');
    const ctx = canvas.getContext('2d');

    window.onload = function() {
        resizeCanvas();
        window.addEventListener('resize', resizeCanvas);
        initSelects();
        try {
            player = new WebAudioFontPlayer();
            document.getElementById('loadingMask').style.display = 'none';
        } catch(e) {}
    };

    function resizeCanvas() {
        canvas.width = document.getElementById('gameStage').clientWidth;
        canvas.height = document.getElementById('gameStage').clientHeight;
    }

    function initSelects() {
        const s = document.getElementById('startNote');
        const p = document.getElementById('peakNote');
        for(let oct=2; oct<=5; oct++) {
            notes.forEach(n => {
                let val = `${n}${oct}`;
                s.add(new Option(val, val));
                p.add(new Option(val, val));
            });
        }
        applyProfile('triad');
    }
    
    function switchConfigMode(mode) { editingMode = mode; document.querySelectorAll('.tab-btn').forEach(b=>b.classList.remove('active')); document.getElementById('btn-'+mode).classList.add('active'); applyProfile(mode); }
    function applyProfile(mode) { let d=rangeProfiles[mode]; if(d){ document.getElementById('startNote').value=d.s; document.getElementById('peakNote').value=d.p; } }
    function addToRoutine() { 
        let s = document.getElementById('startNote').value;
        let p = document.getElementById('peakNote').value;
        routineQueue.push({ mode: editingMode, s:s, p:p });
        renderRoutine();
    }
    function renderRoutine() {
        let ul = document.getElementById('routineList'); ul.innerHTML = "";
        routineQueue.forEach((item, i) => {
            ul.innerHTML += `<li style="padding:8px; border-bottom:1px solid #222; display:flex; justify-content:space-between;"><span>${i+1}. ${item.mode} (${item.s}-${item.p})</span><span onclick="routineQueue.splice(${i},1);renderRoutine();" style="color:#666;cursor:pointer;">✕</span></li>`;
        });
    }
    function clearRoutine() { routineQueue=[]; renderRoutine(); }

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
                pitchFilterNode.type = "lowpass"; pitchFilterNode.frequency.value = 1500;
                micSource.connect(pitchFilterNode);
                pitchFilterNode.connect(vocalAnalyser);
                let micDirect = audioCtx.createGain();
                micSource.connect(micDirect);
                micDirect.connect(monitorGainNode);
            } catch(e) { console.log("Mic error"); }
        }
        if(audioCtx.state === 'suspended') await audioCtx.resume();
        
        let vol = document.getElementById('volMonitor').value/100;
        monitorGainNode.gain.value = vol;
        let lat = document.getElementById('latencySlider').value/1000;
        pianoDelayNode.delayTime.value = lat;
    }

    async function togglePlay() {
        if(isPlaying) { stop(); return; }
        if(routineQueue.length===0) { alert("請加入挑戰！"); return; }
        
        await initAudio();
        isPlaying = true; isGameOver = false; isDying = false;
        document.getElementById('gameStage').classList.remove('stage-dead');
        
        hp = 100; score = 0; combo = 0; maxCombo = 0;
        stats = {perfect:0, good:0, miss:0};
        gameTargets = []; userPitchHistory = []; pitchSmoothingBuffer = []; particles = []; popups = [];
        
        currentRoutineIndex = 0;
        document.getElementById('controlsArea').classList.add('immersive-hidden');
        document.getElementById('playBtn').innerText = "STOP";
        document.getElementById('playBtn').classList.add('stop');
        
        startRoutineItem();
        scheduler();
        renderLoop();
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

    function renderLoop() {
        if(!isPlaying) return;
        
        let now = audioCtx.currentTime;
        let futureNotes = gameTargets.filter(t => t.startTime > now && t.startTime < now + 3.0);
        
        // BUG FIX: Prevent Divide by Zero (NaN Camera)
        if (futureNotes.length > 0) {
            let sum = futureNotes.reduce((a,b) => a + b.midi, 0);
            targetCameraY = sum / futureNotes.length;
        } else {
            // If no notes, keep camera where it is (or move to center if completely empty)
            // targetCameraY = cameraY; 
        }
        
        // Safety check for NaN
        if (isNaN(targetCameraY)) targetCameraY = 60;
        
        cameraY += (targetCameraY - cameraY) * 0.05;

        ctx.fillStyle = "#050510"; ctx.fillRect(0, 0, canvas.width, canvas.height);
        drawGrid(cameraY);
        
        let playheadX = canvas.width * 0.2;
        
        gameTargets.forEach(t => {
            let x = playheadX + (t.startTime - now) * PIXELS_PER_SEC;
            let w = t.duration * PIXELS_PER_SEC;
            let y = getYfromMidi(t.midi);
            
            if (x + w > 0 && x < canvas.width) {
                ctx.fillStyle = "rgba(0, 229, 255, 0.1)";
                ctx.strokeStyle = "rgba(0, 229, 255, 0.5)";
                ctx.lineWidth = 2;
                roundRect(ctx, x, y - BLOCK_HEIGHT/2, w, BLOCK_HEIGHT, 5);
                ctx.stroke();
                ctx.fill();
                
                if (t.hitFrames > 0) {
                    let fillRatio = t.hitFrames / t.totalFrames;
                    let fillW = w * fillRatio;
                    ctx.fillStyle = "rgba(0, 229, 255, 0.8)";
                    ctx.shadowBlur = 15; ctx.shadowColor = "#00e5ff";
                    ctx.fillRect(x, y - BLOCK_HEIGHT/2 + 2, Math.min(w, fillW), BLOCK_HEIGHT - 4);
                    ctx.shadowBlur = 0;
                }
            }
            
            if (!t.processed && now > t.startTime + t.duration) {
                t.processed = true;
                evaluateNote(t, x + w, y);
            }
        });

        if(!isDying) detectAndProcessPitch(now, playheadX);

        updateAndDrawParticles();
        updateAndDrawPopups();
        updateHUD();
        
        if(hp <= 0 && !isGameOver && !isDying) {
            triggerDeath();
        }

        gameLoopId = requestAnimationFrame(renderLoop);
    }
    
    function triggerDeath() {
        isDying = true;
        document.getElementById('gameStage').classList.add('stage-dead');
        setTimeout(() => {
            isGameOver = true;
            stop();
            showResult();
        }, 800);
    }
    
    function evaluateNote(note, visualX, visualY) {
        if(isDying) return; 
        let total = note.totalFrames > 0 ? note.totalFrames : 1;
        let coverage = note.hitFrames / total;
        
        if (coverage >= 0.85) {
            combo++; score += 100 + (combo * 10); hp = Math.min(100, hp + 5); stats.perfect++;
            spawnPopup(visualX, visualY, "PERFECT", "#00e676"); spawnParticles(visualX, visualY, "#00e676", 10);
        } else if (coverage >= 0.50) {
            combo++; score += 50 + (combo * 5); hp = Math.min(100, hp + 2); stats.good++;
            spawnPopup(visualX, visualY, "GOOD", "#ffea00");
        } else {
            combo = 0; hp = Math.max(0, hp - 10); 
            stats.miss++;
            spawnPopup(visualX, visualY, "MISS", "#ff5252");
        }
        if (combo > maxCombo) maxCombo = combo;
    }

    function detectAndProcessPitch(now, playheadX) {
        if (now - lastAnalysisTime < ANALYSIS_INTERVAL) { drawTrail(now, playheadX); return; }
        lastAnalysisTime = now;
        if (!vocalAnalyser) return;
        
        vocalAnalyser.getFloatTimeDomainData(audioBuffer);
        let rms = 0; for(let i=0; i<audioBuffer.length; i++) rms += audioBuffer[i]*audioBuffer[i];
        rms = Math.sqrt(rms/audioBuffer.length);
        
        let detectedMidi = null; let color = "rgba(255,255,255,0.2)"; let isHit = false;

        if (rms > 0.01) {
            let freq = detectPitchYIN(audioBuffer, audioCtx.sampleRate);
            if (freq !== -1) {
                let rawMidi = freqToMidi(freq);
                let currentTarget = gameTargets.find(t => now >= t.startTime && now <= t.startTime + t.duration);
                if (currentTarget) {
                    let diff = rawMidi - currentTarget.midi;
                    if (Math.abs(diff - 12) < 2.0 || Math.abs(diff - 24) < 2.0) {
                        vocalAnalyser.getFloatFrequencyData(frequencyBuffer);
                        let targetFreq = midiToFreq(currentTarget.midi);
                        let peakCheck = checkPeakProminence(targetFreq, audioCtx.sampleRate, frequencyBuffer);
                        let energyHigh = getLinearEnergy(freq, audioCtx.sampleRate, frequencyBuffer);
                        let ratio = (energyHigh > 0) ? (peakCheck.energy / energyHigh) : 0;
                        if (ratio > 0.35 && peakCheck.isPeak) freq = targetFreq;
                    }
                }
                
                let processedMidi = freqToMidi(freq);
                pitchSmoothingBuffer.push(processedMidi);
                if(pitchSmoothingBuffer.length > 3) pitchSmoothingBuffer.shift();
                detectedMidi = pitchSmoothingBuffer.reduce((a,b)=>a+b,0) / pitchSmoothingBuffer.length;
                
                if (currentTarget) {
                    currentTarget.totalFrames++;
                    if (Math.abs(detectedMidi - currentTarget.midi) <= 0.5) {
                        isHit = true; currentTarget.hitFrames++; color = "#00e676"; score += 1;
                        if (Math.random() < 0.2) spawnParticles(playheadX, getYfromMidi(detectedMidi), "#00e676", 1);
                    } else color = "#ff5252";
                }
            } else pitchSmoothingBuffer = [];
        } else {
            let currentTarget = gameTargets.find(t => now >= t.startTime && now <= t.startTime + t.duration);
            if (currentTarget) currentTarget.totalFrames++;
        }

        userPitchHistory.push({ time: now + VISUAL_OFFSET_SEC, midi: detectedMidi, color: color, isHit: isHit });
        while(userPitchHistory.length > 0 && userPitchHistory[0].time < now - 2.0) userPitchHistory.shift();
        drawTrail(now, playheadX);
    }

    function drawGrid(camY) {
        if(isNaN(camY)) camY = 60; // Extra safety
        let centerMidi = Math.round(camY);
        ctx.textAlign = "right"; ctx.textBaseline = "middle"; ctx.font = "12px monospace";
        for (let m = centerMidi - 12; m <= centerMidi + 12; m++) {
            let y = getYfromMidi(m);
            let isC = (m % 12) === 0;
            ctx.strokeStyle = isC ? "#444" : "#222"; ctx.lineWidth = 1;
            ctx.beginPath(); ctx.moveTo(0, y); ctx.lineTo(canvas.width, y); ctx.stroke();
            if (isC) { ctx.fillStyle = "#666"; ctx.fillText(getNoteName(m), canvas.width - 10, y); }
        }
        ctx.strokeStyle = "rgba(255,255,255,0.3)";
        ctx.beginPath(); ctx.moveTo(canvas.width * 0.2, 0); ctx.lineTo(canvas.width * 0.2, canvas.height); ctx.stroke();
    }

    function drawTrail(now, phX) {
        if(userPitchHistory.length < 2) return;
        ctx.lineWidth = 4; ctx.lineCap = "round"; ctx.lineJoin = "round";
        for(let i=1; i<userPitchHistory.length; i++) {
            let p1 = userPitchHistory[i-1]; let p2 = userPitchHistory[i];
            if (p1.midi && p2.midi && Math.abs(p1.midi - p2.midi) < 5) {
                let x1 = phX + (p1.time - now) * PIXELS_PER_SEC;
                let x2 = phX + (p2.time - now) * PIXELS_PER_SEC;
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
    function updateHUD() {
        let hpBar = document.getElementById('hpBar'); hpBar.style.width = hp + "%";
        if(hp < 30) hpBar.style.background = "#ff5252"; else hpBar.style.background = "linear-gradient(90deg, #ff5252, #ffea00, #00e676)";
        document.getElementById('hudScore').innerText = "SCORE: " + score;
        let comboEl = document.getElementById('comboContainer');
        if(combo > 1) { document.getElementById('comboNum').innerText = combo; comboEl.classList.add('combo-active'); } else comboEl.classList.remove('combo-active');
    }

    function midiToFreq(m) { return 440 * Math.pow(2, (m-69)/12); }
    function freqToMidi(f) { return 12 * (Math.log(f/440)/Math.log(2)) + 69; }
    function getYfromMidi(m) { return (canvas.height/2) - (m - cameraY) * PIXELS_PER_SEMITONE; }
    function roundRect(ctx, x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
    function getNoteName(m) { let n=notes[m%12]; let o=Math.floor(m/12)-1; return n+o; }

    function detectPitchYIN(buffer, sampleRate) {
        const threshold = 0.15; const bufferSize = buffer.length; const yinBufferLength = bufferSize / 2; let yinBuffer = new Float32Array(yinBufferLength);
        const minTau = Math.floor(sampleRate / 1000); const maxTau = Math.floor(sampleRate / 60); if (maxTau > yinBufferLength) return -1;
        for (let tau = 0; tau < maxTau; tau++) { let sum = 0; for (let i = 0; i < yinBufferLength; i++) { let delta = buffer[i] - buffer[i + tau]; sum += delta * delta; } yinBuffer[tau] = sum; }
        yinBuffer[0] = 1; let runningSum = 0; yinBuffer[0] = 1;
        for (let tau = 1; tau < maxTau; tau++) { runningSum += yinBuffer[tau]; yinBuffer[tau] *= tau / runningSum; }
        let tauEstimate = -1;
        for (let tau = minTau; tau < maxTau; tau++) { if (yinBuffer[tau] < threshold) { while (tau + 1 < maxTau && yinBuffer[tau + 1] < yinBuffer[tau]) tau++; tauEstimate = tau; break; } }
        if (tauEstimate === -1) { let minVal = 100; for (let tau = minTau; tau < maxTau; tau++) { if (yinBuffer[tau] < minVal) { minVal = yinBuffer[tau]; tauEstimate = tau; } } }
        if (tauEstimate === -1) return -1;
        let betterTau = tauEstimate;
        if (tauEstimate > 0 && tauEstimate < maxTau - 1) { let s0 = yinBuffer[tauEstimate - 1]; let s1 = yinBuffer[tauEstimate]; let s2 = yinBuffer[tauEstimate + 1]; let adjustment = (s2 - s0) / (2 * (2 * s1 - s2 - s0)); betterTau += adjustment; }
        return sampleRate / betterTau;
    }
    function getLinearEnergy(targetFreq, sampleRate, buffer) { let nyquist = sampleRate / 2; let index = Math.round((targetFreq / nyquist) * buffer.length); if (index < 0 || index >= buffer.length) return 0; let db = buffer[index]; return Math.pow(10, db / 20); }
    function checkPeakProminence(targetFreq, sampleRate, buffer) { let nyquist = sampleRate / 2; let centerIdx = Math.round((targetFreq / nyquist) * buffer.length); if (centerIdx < 2 || centerIdx >= buffer.length - 2) return { energy: 0, isPeak: false }; let maxIdx = centerIdx; let maxDb = buffer[centerIdx]; if (buffer[centerIdx-1] > maxDb) { maxDb = buffer[centerIdx-1]; maxIdx = centerIdx-1; } if (buffer[centerIdx+1] > maxDb) { maxDb = buffer[centerIdx+1]; maxIdx = centerIdx+1; } let centerLinear = Math.pow(10, maxDb / 20); let leftDb = buffer[maxIdx - 2]; let rightDb = buffer[maxIdx + 2]; let leftLinear = Math.pow(10, leftDb / 20); let rightLinear = Math.pow(10, rightDb / 20); let neighborAvg = (leftLinear + rightLinear) / 2; let isProminent = centerLinear > (neighborAvg * 1.5); return { energy: centerLinear, isPeak: isProminent }; }

    function startRoutineItem() {
        let config = routineQueue[currentRoutineIndex];
        generateTargets(config);
        
        let now = audioCtx.currentTime;
        if (nextNoteTime < now) nextNoteTime = now + 0.5;
        let bpm = document.getElementById('bpm').value; 
        let beatDur = 60.0/bpm;
        
        // Count-in Audio
        let rootMidi = getMidiPitch(config.s);
        playChord(rootMidi, nextNoteTime, beatDur * 4);
        for(let i=0; i<4; i++) playStickClick(nextNoteTime + i*beatDur);
        
        nextNoteTime += (4 * beatDur);
    }
    
    function generateTargets(config) {
        let allOpts = []; for(let oct=2; oct<=5; oct++) notes.forEach(n => allOpts.push(`${n}${oct}`));
        let sIdx = allOpts.indexOf(config.s), pIdx = allOpts.indexOf(config.p);
        let currentRoots = [];
        if (sIdx <= pIdx) for(let i=sIdx; i<=pIdx; i++) currentRoots.push(allOpts[i]);
        
        let bpm = document.getElementById('bpm').value; 
        let beatDur = 60.0/bpm;
        let currentTime = nextNoteTime;
        
        currentRoots.forEach(r => {
            let rootMidi = getMidiPitch(r);
            // BUG FIX: Dynamic Intervals based on Mode
            let intervals = [0, 4, 7, 4, 0]; // Default Triad
            if(config.mode === 'scale5') intervals = [0, 2, 4, 5, 7, 5, 4, 2, 0];
            else if(config.mode === 'octave') intervals = [0, 12, 0];
            else if(config.mode === 'p5') intervals = [0, 7, 0];
            else if(config.mode === 'p4') intervals = [0, 5, 0];
            
            intervals.forEach((iv, i) => {
                let noteDur = beatDur * 0.9;
                gameTargets.push({
                    midi: rootMidi + iv,
                    startTime: currentTime + (i * beatDur),
                    duration: noteDur,
                    hitFrames: 0,
                    totalFrames: 0,
                    processed: false,
                    played: false
                });
            });
            currentTime += (intervals.length + 2) * beatDur;
        });
    }
    
    function scheduler() {
        while(isPlaying && nextNoteTime < audioCtx.currentTime + scheduleAheadTime) {
            nextNoteTime += 0.1;
        }
        // Audio Scheduler
        gameTargets.forEach(t => {
            if(!t.played && t.startTime < audioCtx.currentTime + scheduleAheadTime) {
                t.played = true;
                player.queueWaveTable(audioCtx, pianoSplitterNode, _tone_0000_JCLive_sf2_file, t.startTime, t.midi, t.duration, 0.5);
            }
        });
        if(isPlaying) timerID = setTimeout(scheduler, 50);
    }
    
    function playStickClick(t) { 
        let osc = audioCtx.createOscillator(); let g = audioCtx.createGain(); 
        osc.frequency.setValueAtTime(1200, t); osc.frequency.exponentialRampToValueAtTime(800, t+0.05); 
        g.gain.setValueAtTime(0, t); g.gain.linearRampToValueAtTime(0.5, t+0.001); g.gain.exponentialRampToValueAtTime(0.001, t+0.08); 
        osc.connect(g); g.connect(audioCtx.destination); osc.start(t); osc.stop(t+0.1); 
    }
    function playChord(root, t, dur) { 
        [0,4,7].forEach(s => player.queueWaveTable(audioCtx, pianoSplitterNode, _tone_0000_JCLive_sf2_file, t, root+s, dur, 0.3)); 
    }
    function getMidiPitch(n) { let note = n.slice(0, -1), oct = parseInt(n.slice(-1)); return notes.indexOf(note) + (oct + 1) * 12; }
    
    function showResult() {
        document.getElementById('resultModal').style.display = 'flex';
        let total = stats.perfect + stats.good + stats.miss;
        if(total===0) total=1;
        document.getElementById('resPerfect').innerText = stats.perfect;
        document.getElementById('resGood').innerText = stats.good;
        document.getElementById('resMiss').innerText = stats.miss;
        document.getElementById('resCombo').innerText = maxCombo;
        let pRate = stats.perfect / total;
        let rank = "F";
        if(pRate > 0.95 && stats.miss===0) rank = "S"; else if(pRate > 0.8) rank = "A"; else if(pRate > 0.6) rank = "B"; else if(pRate > 0.4) rank = "C";
        let rEl = document.getElementById('finalRank'); rEl.innerText = rank; rEl.className = "rank-big rank-" + rank;
    }
    function closeResult() { document.getElementById('resultModal').style.display = 'none'; }

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
    print("📂 目前目錄檔案列表:", os.listdir("."))
except Exception as e:
    print(f"❌ 寫入檔案失敗: {e}")
    exit(1)
