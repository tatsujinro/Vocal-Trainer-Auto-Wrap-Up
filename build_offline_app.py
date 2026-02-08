import urllib.request
import os
import ssl

# ==========================================
# 產品發布: Right On Pitch v1.2 (Song Test)
# 基底: v1.1 (Bluetooth Warning)
# 
# Phase 1 測試重點:
# 1. [Data] 內建 "Twinkle Twinkle Little Star" JSON 資料。
# 2. [Logic] 新增 generateSongTargets() 讀取樂譜。
# 3. [Visual] 在音符方塊上繪製歌詞 (Lyrics)。
# 4. [Test] START 按鈕強制播放歌曲 (暫時忽略音階設定)。
# ==========================================
VERSION = "RightOnPitch_v1_2_SongTest"
FILENAME = f"{VERSION}.html"

print(f"🚀 正在發布 {VERSION} (歌曲測試版)...")

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
# CSS (無變動，沿用 v1.1)
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
        --boo: #ff9800;
        --miss: #ff5252;
    }
    body { font-family: "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: var(--bg-color); color: var(--text-main); margin: 0; padding: 0; overflow: hidden; user-select: none; -webkit-user-select: none; }
    
    #gameStage { position: relative; width: 100vw; height: 50vh; background: #080818; border-bottom: 2px solid #333; overflow: hidden; transform: translateZ(0); }
    canvas { display: block; width: 100%; height: 100%; }
    
    .hud-layer { position: absolute; top: 0; left: 0; width: 100%; height: 100%; pointer-events: none; }
    
    .hp-container { position: absolute; top: 10px; left: 50%; transform: translateX(-50%); width: 60%; height: 15px; background: #333; border: 2px solid #555; border-radius: 10px; overflow: hidden; }
    .hp-fill { height: 100%; width: 100%; background: linear-gradient(90deg, #ff5252, #ff9800, #ffea00, #00e676); transition: width 0.2s; will-change: width; }
    .hp-text { position: absolute; top: 12px; right: 22%; color: #fff; font-size: 0.8rem; font-weight: bold; text-shadow: 1px 1px 2px black; }

    .combo-container { position: absolute; top: 40%; left: 50%; transform: translate(-50%, -50%); text-align: center; opacity: 0; transition: opacity 0.2s, transform 0.1s; will-change: opacity, transform; }
    .combo-num { font-size: 5rem; font-weight: 900; color: rgba(255,255,255,0.1); -webkit-text-stroke: 2px var(--accent); text-shadow: 0 0 20px var(--accent); font-family: 'Impact', sans-serif; }
    .combo-label { font-size: 1.5rem; color: var(--accent); letter-spacing: 5px; font-weight: bold; }
    .combo-active { opacity: 0.8; transform: translate(-50%, -50%) scale(1.1); }

    .hud-score { position: absolute; top: 10px; right: 15px; font-size: 1.2rem; font-family: monospace; color: var(--accent); }
    .version-tag { position: absolute; bottom: 5px; right: 5px; font-size: 0.7rem; color: #555; }

    #countdownLayer {
        position: absolute; top: 0; left: 0; width: 100%; height: 100%;
        display: none; justify-content: center; align-items: center;
        z-index: 50; pointer-events: none;
    }
    .countdown-num {
        font-size: 10rem; font-weight: 900; color: #fff;
        text-shadow: 0 0 30px var(--accent);
        animation: popIn 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    }
    @keyframes popIn {
        0% { transform: scale(0.5); opacity: 0; }
        50% { transform: scale(1.2); opacity: 1; }
        100% { transform: scale(1.0); opacity: 0; }
    }

    /* WARNING MODAL */
    #warningModal {
        position: fixed; top: 0; left: 0; width: 100%; height: 100%;
        background: rgba(0,0,0,0.85); z-index: 2000;
        display: flex; justify-content: center; align-items: center;
        backdrop-filter: blur(5px);
        transition: opacity 0.3s;
    }
    .warning-box {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        border: 2px solid var(--miss);
        border-radius: 20px;
        padding: 30px;
        max-width: 90%; width: 450px;
        text-align: center;
        box-shadow: 0 0 40px rgba(255, 82, 82, 0.4);
        animation: slideUp 0.4s ease-out;
    }
    @keyframes slideUp { from { transform: translateY(50px); opacity: 0; } to { transform: translateY(0); opacity: 1; } }
    .warning-icon { font-size: 3rem; margin-bottom: 10px; }
    .warning-title { font-size: 1.4rem; color: var(--miss); margin-bottom: 5px; font-weight: 800; letter-spacing: 1px; }
    .warning-subtitle { font-size: 1rem; color: #fff; margin-bottom: 20px; font-weight: bold; }
    .warning-content { text-align: left; color: #ccc; font-size: 0.95rem; line-height: 1.6; background: rgba(0,0,0,0.3); padding: 15px; border-radius: 10px; margin-bottom: 25px; }
    .warning-btn {
        background: var(--accent); color: #000; border: none; padding: 12px 40px; border-radius: 30px;
        font-weight: 800; font-size: 1.1rem; cursor: pointer; transition: transform 0.2s, box-shadow 0.2s;
        text-transform: uppercase; letter-spacing: 1px;
    }
    .warning-btn:hover { transform: scale(1.05); box-shadow: 0 0 20px var(--accent); }

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
    <div style="font-size: 3rem; margin-bottom: 20px;">🌟</div>
    <div>Right On Pitch v1.2</div>
    <div style="font-size: 0.8rem; color: #888; margin-top:10px;">歌曲模式載入中...</div>
</div>

<div id="warningModal">
    <div class="warning-box">
        <div class="warning-icon">⚠️</div>
        <div class="warning-title">AUDIO LATENCY WARNING</div>
        <div class="warning-subtitle">音訊延遲提醒</div>
        
        <div class="warning-content">
            <p style="margin-bottom: 10px;">
                <strong style="color: #fff;">Do not use Bluetooth headphones.</strong><br>
                Bluetooth causes significant delay (~200ms).
            </p>
            <hr style="border:0; border-top:1px solid #444; margin: 10px 0;">
            <p>
                <strong style="color: #fff;">請勿使用藍牙耳機。</strong><br>
                藍牙傳輸會造成約 0.2 秒的延遲。建議使用有線耳機。
            </p>
        </div>
        
        <button class="warning-btn" onclick="closeWarning()">I Understand<br><span style="font-size:0.7rem; font-weight:normal;">我知道了</span></button>
    </div>
</div>

<div id="gameStage">
    <canvas id="gameCanvas"></canvas>
    
    <div id="countdownLayer">
        <div id="countdownText" class="countdown-num">5</div>
    </div>

    <div class="hud-layer">
        <div class="hp-container"><div class="hp-fill" id="hpBar"></div></div>
        <div class="hp-text">HP</div>
        <div class="hud-score" id="hudScore">SCORE: 0</div>
        <div class="combo-container" id="comboContainer"><div class="combo-num" id="comboNum">0</div><div class="combo-label">COMBO</div></div>
        <div class="version-tag">Song Test: Twinkle Star</div>
    </div>
</div>

<div id="controlsArea">
    <h2 style="color:var(--accent); margin:0 0 10px 0;">Song Mode</h2>
    
    <div class="control-group">
        <div style="margin-bottom:10px; color:#aaa; font-size:0.9rem;">
            目前模式：單曲測試 (Twinkle Twinkle Little Star)<br>
            按下 START 直接開始歌曲挑戰。
        </div>
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

<button class="play-btn" id="playBtn" onclick="togglePlay()">START SONG</button>

<div id="resultModal">
    <div style="color:#aaa; font-size:1rem; letter-spacing:2px;">RANK</div>
    <div class="rank-big" id="finalRank">S</div>
    
    <div style="display:flex; gap:10px; margin-bottom:20px; flex-wrap:wrap; justify-content:center;">
        <div style="text-align:center; min-width:60px;">
            <div style="font-size:1.2rem; color:var(--perfect);" id="resPerfect">0</div>
            <div style="font-size:0.6rem; color:#888;">PERFECT</div>
        </div>
        <div style="text-align:center; min-width:60px;">
            <div style="font-size:1.2rem; color:var(--good);" id="resGood">0</div>
            <div style="font-size:0.6rem; color:#888;">GOOD</div>
        </div>
        <div style="text-align:center; min-width:60px;">
            <div style="font-size:1.2rem; color:var(--boo);" id="resBoo">0</div>
            <div style="font-size:0.6rem; color:#888;">BOO</div>
        </div>
        <div style="text-align:center; min-width:60px;">
            <div style="font-size:1.2rem; color:var(--miss);" id="resMiss">0</div>
            <div style="font-size:0.6rem; color:#888;">MISS</div>
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
    
    const FPS = 40;
    const ANALYSIS_INTERVAL = 1.0 / FPS;
    const PIXELS_PER_SEC = 120; 
    const PIXELS_PER_SEMITONE = 20;
    const BLOCK_HEIGHT = 40; 
    
    let isPlaying = false;
    let gameLoopId;
    let lastAnalysisTime = 0;
    
    let gameTargets = [];      
    let particles = [];        
    let popups = [];           
    
    let currentDetectedMidi = null;
    
    let hp = 100;
    let score = 0;
    let combo = 0;
    let maxCombo = 0;
    let stats = { perfect:0, good:0, boo:0, miss:0 };
    let isGameOver = false;
    let isDying = false;

    let cameraY = 60; 
    let targetCameraY = 60;
    let lastValidCameraY = 60;

    let pitchSmoothingBuffer = [];
    let audioBuffer = new Float32Array(2048);
    let frequencyBuffer = new Float32Array(2048);
    
    let nextNoteTime = 0;
    let lastGameTime = 0;
    let timerID;
    let renderStartIndex = 0;
    let audioStartIndex = 0;
    let scheduleAheadTime = 0.5; 
    
    const notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];

    // --- PHASE 1: SONG DATA ---
    const SONG_TWINKLE = {
        title: "Twinkle Twinkle Little Star",
        // Format: [Note, Octave, Duration(Beats), Lyric]
        data: [
            ['C', 3, 1, 'Twin'], ['C', 3, 1, 'kle'], ['G', 3, 1, 'Twin'], ['G', 3, 1, 'kle'],
            ['A', 3, 1, 'Lit'],  ['A', 3, 1, 'tle'], ['G', 3, 2, 'Star'],
            [null,0, 1, ''], // Rest
            ['F', 3, 1, 'How'],  ['F', 3, 1, 'I'],   ['E', 3, 1, 'Won'],  ['E', 3, 1, 'der'],
            ['D', 3, 1, 'What'], ['D', 3, 1, 'You'], ['C', 3, 2, 'Are']
        ]
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
        try {
            player = new WebAudioFontPlayer();
            document.getElementById('loadingMask').style.display = 'none';
        } catch(e) { console.log(e); }
    };
    
    function closeWarning() {
        let modal = document.getElementById('warningModal');
        modal.style.opacity = '0';
        setTimeout(() => { modal.style.display = 'none'; }, 300);
    }

    function resizeCanvas() {
        canvas.width = document.getElementById('gameStage').clientWidth;
        canvas.height = document.getElementById('gameStage').clientHeight;
    }

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
        
        try {
            await initAudio(); 
            playWarmupSequence();
            
            document.getElementById('controlsArea').classList.add('immersive-hidden');
            document.getElementById('playBtn').innerText = "STOP";
            document.getElementById('playBtn').classList.add('stop');
            
            playCountdown();
            
        } catch(e) { alert("啟動失敗: " + e.message); }
    }
    
    function playWarmupSequence() {
        if(!player || !audioCtx) return;
        let now = audioCtx.currentTime;
        let startMidi = 45; let endMidi = 76; let step = 0.1;
        for (let m = startMidi; m <= endMidi; m++) {
            let time = now + ((m - startMidi) * step);
            player.queueWaveTable(audioCtx, pianoSplitterNode, _tone_0000_JCLive_sf2_file, time, m, 0.05, 0.0001);
        }
    }
    
    function playCountdown() {
        let layer = document.getElementById('countdownLayer');
        let text = document.getElementById('countdownText');
        layer.style.display = 'flex';
        let count = 5;
        
        let playBeep = (freq) => {
            let osc = audioCtx.createOscillator();
            let g = audioCtx.createGain();
            osc.frequency.setValueAtTime(freq, audioCtx.currentTime);
            g.gain.setValueAtTime(0.1, audioCtx.currentTime);
            g.gain.exponentialRampToValueAtTime(0.001, audioCtx.currentTime + 0.3);
            osc.connect(g);
            g.connect(monitorGainNode);
            osc.start();
            osc.stop(audioCtx.currentTime + 0.3);
        };

        text.innerText = count;
        text.style.color = "#ff5252";
        text.style.animation = 'none';
        text.offsetHeight; 
        text.style.animation = 'popIn 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
        playBeep(880); 

        let interval = setInterval(() => {
            count--;
            if (count > 0) {
                text.innerText = count;
                text.style.color = (count <= 2) ? "#ffea00" : "#00e5ff";
                text.style.animation = 'none';
                text.offsetHeight;
                text.style.animation = 'popIn 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
                playBeep(880);
            } else {
                clearInterval(interval);
                text.innerText = "GO!";
                text.style.color = "#00e676";
                text.style.animation = 'none';
                text.offsetHeight;
                text.style.animation = 'popIn 0.8s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
                playBeep(1760); 
                
                setTimeout(() => {
                    layer.style.display = 'none';
                    startGameLogic();
                }, 800);
            }
        }, 1000); 
    }

    function startGameLogic() {
        isPlaying = true; isGameOver = false; isDying = false;
        document.getElementById('gameStage').classList.remove('stage-dead');
        hp = 100; score = 0; combo = 0; maxCombo = 0;
        stats = {perfect:0, good:0, boo:0, miss:0};
        gameTargets = []; particles = []; popups = [];
        lastGameTime = 0;
        renderStartIndex = 0; audioStartIndex = 0;
        currentDetectedMidi = null; 
        
        let startMidi = 60; // Center camera on C4 initially
        cameraY = startMidi; targetCameraY = startMidi; lastValidCameraY = startMidi;
        
        updateUI(true);
        startSongPlayback(); // CHANGED: Call Song Logic
        scheduler(); 
        renderLoop();
    }

    function stop() {
        isPlaying = false;
        clearTimeout(timerID);
        cancelAnimationFrame(gameLoopId);
        if(player) player.cancelQueue(audioCtx);
        
        document.getElementById('countdownLayer').style.display = 'none'; 
        document.getElementById('controlsArea').classList.remove('immersive-hidden');
        document.getElementById('playBtn').innerText = "START SONG";
        document.getElementById('playBtn').classList.remove('stop');
        if(!isGameOver && !isDying) showResult();
    }

    // --- PHASE 1: SONG GENERATOR ---
    function startSongPlayback() {
        let bpm = document.getElementById('bpm').value; 
        let beatDur = 60.0/bpm;
        let now = audioCtx.currentTime;
        
        // Lead-in stick clicks (4 beats)
        let playStartTime = now + 0.1;
        for(let i=0; i<4; i++) playStickClick(playStartTime + i*beatDur);
        
        let cursorTime = playStartTime + (4 * beatDur);
        nextNoteTime = cursorTime;
        
        // Generate targets from SONG_TWINKLE
        SONG_TWINKLE.data.forEach(item => {
            let noteName = item[0];
            let oct = item[1];
            let beats = item[2];
            let lyric = item[3];
            let dur = beats * beatDur;
            
            if (noteName === null) {
                // Rest
                cursorTime += dur;
            } else {
                // Note
                let midi = notes.indexOf(noteName) + (oct + 1) * 12;
                gameTargets.push({
                    midi: midi,
                    startTime: cursorTime,
                    duration: dur * 0.95, // slight separation
                    hitFrames: 0, totalFrames: 0, processed: false, played: false, isBridge: false,
                    text: lyric // Add lyric data
                });
                cursorTime += dur;
            }
        });
        
        lastGameTime = cursorTime;
    }

    function scheduler() {
        while(isPlaying && nextNoteTime < audioCtx.currentTime + scheduleAheadTime) {
            nextNoteTime += 0.1;
        }
        for(let i = audioStartIndex; i < gameTargets.length; i++) {
            let t = gameTargets[i];
            if (t.startTime < audioCtx.currentTime - 1.0) audioStartIndex = i;
            if(!t.played && t.startTime < audioCtx.currentTime + scheduleAheadTime) {
                t.played = true;
                player.queueWaveTable(audioCtx, pianoSplitterNode, _tone_0000_JCLive_sf2_file, t.startTime, t.midi, t.duration, 0.8);
            }
        }
        if(isPlaying) timerID = setTimeout(scheduler, 50);
    }

    function renderLoop() {
        if(!isPlaying) return;
        let now = audioCtx.currentTime;
        
        let futureNotes = [];
        let count = 0;
        let sum = 0;
        
        for(let i = renderStartIndex; i < gameTargets.length; i++) {
            let t = gameTargets[i];
            if (t.startTime > now + 3.0) break;
            if (!t.isBridge && t.startTime > now) {
                sum += t.midi;
                count++;
            }
        }
        
        if (count > 0) {
            targetCameraY = sum / count;
            lastValidCameraY = targetCameraY; 
        } else {
            targetCameraY = lastValidCameraY; 
        }
        
        cameraY += (targetCameraY - cameraY) * 0.05;

        ctx.fillStyle = "#050510"; ctx.fillRect(0, 0, canvas.width, canvas.height);
        drawGrid(cameraY);
        let phX = canvas.width * 0.2;
        
        for(let i = renderStartIndex; i < gameTargets.length; i++) {
            let t = gameTargets[i];
            if (t.startTime + t.duration < now - 2.0) { renderStartIndex = i; continue; }
            let x = phX + (t.startTime - now) * PIXELS_PER_SEC;
            if (x > canvas.width) break;

            let w = t.duration * PIXELS_PER_SEC;
            let y = getYfromMidi(t.midi);
            
            if (x + w > 0) {
                ctx.fillStyle = "rgba(0, 229, 255, 0.1)";
                ctx.strokeStyle = "rgba(0, 229, 255, 0.5)";
                ctx.lineWidth = 2;
                roundRect(ctx, x, y - BLOCK_HEIGHT/2, w, BLOCK_HEIGHT, 5);
                ctx.stroke();
                ctx.fill();
                
                // Draw Lyrics
                if (t.text) {
                    ctx.fillStyle = "white";
                    ctx.font = "bold 16px Arial";
                    ctx.textAlign = "center";
                    ctx.textBaseline = "middle";
                    ctx.fillText(t.text, x + w/2, y - 30); // Above the note
                }
                
                if (t.hitFrames > 0) {
                    let total = t.totalFrames || 1;
                    let rawRatio = t.hitFrames / total;
                    let adjustedRatio = Math.min(1.0, rawRatio * 1.15); 
                    let fillW = w * adjustedRatio;
                    
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
        drawLaserPointer(phX);
        
        updateAndDrawParticles();
        updateAndDrawPopups();
        
        if(hp <= 0 && !isGameOver && !isDying) triggerDeath();
        if (!isGameOver && !isDying && lastGameTime > 0 && now > lastGameTime + 2.0) stop();

        gameLoopId = requestAnimationFrame(renderLoop);
    }
    
    function drawLaserPointer(x) {
        if (!currentDetectedMidi) return;
        let y = getYfromMidi(currentDetectedMidi);
        if (isNaN(y)) return;

        ctx.save();
        ctx.shadowBlur = 15;
        ctx.shadowColor = "#00e676"; 
        ctx.strokeStyle = "#fff";     
        ctx.lineWidth = 4;
        ctx.lineCap = "round";

        ctx.beginPath();
        ctx.moveTo(x - 25, y);
        ctx.lineTo(x + 25, y);
        ctx.stroke();
        
        ctx.fillStyle = "#00e676";
        ctx.beginPath();
        ctx.arc(x, y, 4, 0, Math.PI*2);
        ctx.fill();
        ctx.restore();
    }
    
    function updateUI(force = false) {
        if (force || isPlaying) {
            if(ui.hpBar) {
                ui.hpBar.style.width = hp + "%";
                if(hp < 30) ui.hpBar.style.background = "#ff5252"; 
                else ui.hpBar.style.background = "linear-gradient(90deg, #ff5252, #ff9800, #ffea00, #00e676)";
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
        let coverage = Math.min(1.0, (note.hitFrames * 1.15) / total);
        let hit = false;
        
        if (coverage >= 0.85) {
            combo++; score += 100 + (combo * 10); hp = Math.min(100, hp + 5); stats.perfect++;
            spawnPopup(visualX, visualY, "PERFECT", "#00e676"); spawnParticles(visualX, visualY, "#00e676", 10);
            hit = true;
        } else if (coverage >= 0.50) {
            combo++; score += 50 + (combo * 5); hp = Math.min(100, hp + 2); stats.good++;
            spawnPopup(visualX, visualY, "GOOD", "#ffea00");
            hit = true;
        } else if (coverage >= 0.20) { 
            combo = 0; score += 10; hp = Math.max(0, hp - 5); stats.boo++;
            spawnPopup(visualX, visualY, "BOO", "#ff9800"); 
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

    function detectAndProcessPitch(now, playheadX) {
        if (now - lastAnalysisTime < ANALYSIS_INTERVAL) { return; }
        lastAnalysisTime = now;
        
        if (!vocalAnalyser) return;
        
        vocalAnalyser.getFloatTimeDomainData(audioBuffer);
        let rms = 0;
        for(let i=0; i<audioBuffer.length; i++) rms += audioBuffer[i]*audioBuffer[i];
        rms = Math.sqrt(rms/audioBuffer.length);
        
        let detectedMidi = null; 
        
        if (rms > 0.01) {
            let freq = detectPitchYIN(audioBuffer, audioCtx.sampleRate);
            if (freq !== -1) {
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
                        currentTarget.hitFrames++; 
                        score += 1;
                        if (Math.random() < 0.2) spawnParticles(playheadX, getYfromMidi(detectedMidi), "#00e676", 1);
                    }
                }
            } else {
                pitchSmoothingBuffer = [];
            }
        }
        
        currentDetectedMidi = detectedMidi;
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

    function restartGame() {
        document.getElementById('resultModal').style.display = 'none';
        togglePlay();
    }
    
    function goHome() {
        document.getElementById('resultModal').style.display = 'none';
        document.getElementById('controlsArea').classList.remove('immersive-hidden');
        document.getElementById('playBtn').innerText = "START SONG";
        document.getElementById('playBtn').classList.remove('stop');
        hp = 100; score = 0; combo = 0;
        updateUI(true);
    }
    
    function showResult() {
        document.getElementById('resultModal').style.display = 'flex';
        let total = stats.perfect + stats.good + stats.boo + stats.miss;
        if(total === 0) total = 1;
        document.getElementById('resPerfect').innerText = stats.perfect;
        document.getElementById('resGood').innerText = stats.good;
        document.getElementById('resBoo').innerText = stats.boo;
        document.getElementById('resMiss').innerText = stats.miss;
        document.getElementById('resCombo').innerText = maxCombo;
        let weightedScore = (stats.perfect * 1.0 + stats.good * 0.8 + stats.boo * 0.4) / total;
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
        f.write(f'<title>Right On Pitch v1.2</title>\n')
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
