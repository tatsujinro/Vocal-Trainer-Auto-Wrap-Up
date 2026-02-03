import urllib.request
import os
import ssl

print("🚀 正在開始打包您的離線版聲樂教練 (v21 課程編排版)...")

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
        
except Exception as e:
    print(f"❌ 下載失敗: {e}")
    exit()

# 4. HTML 模板
html_template = f"""<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>吉他手聲樂教練 v21</title>
    <style>
        :root {{ --bg-color: #121212; --card-bg: #1e1e1e; --text-main: #e0e0e0; --accent: #ff4081; --accent-dark: #c60055; --accent-light: #ff80ab; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: var(--bg-color); color: var(--text-main); margin: 0; padding: 20px; text-align: center; user-select: none; padding-bottom: 100px; }}
        h1 {{ color: var(--accent); margin-bottom: 5px; font-size: 1.5rem; }}
        p {{ color: #888; margin-top: 0; font-size: 0.9rem; }}
        
        .control-panel {{ background: var(--card-bg); border-radius: 16px; padding: 20px; margin-bottom: 20px; border: 1px solid #333; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }}
        
        .range-selectors {{ display: flex; gap: 8px; margin-bottom: 20px; }}
        .range-col {{ flex: 1; display: flex; flex-direction: column; gap: 5px; }}
        .range-col label {{ font-size: 0.8rem; color: var(--accent-light); text-align: center; margin: 0; }}
        select {{ background: #333; color: white; border: 1px solid #444; padding: 8px; width: 100%; border-radius: 6px; font-size: 1rem; text-align: center; }}
        
        .slider-group {{ margin-bottom: 15px; text-align: left; }}
        .slider-label-row {{ display: flex; justify-content: space-between; margin-bottom: 8px; color: #bbb; font-size: 0.9rem; }}
        .val-display {{ color: var(--accent); font-weight: bold; font-family: monospace; }}
        
        input[type="range"] {{ width: 100%; height: 6px; background: #444; border-radius: 5px; outline: none; -webkit-appearance: none; }}
        input[type="range"]::-webkit-slider-thumb {{ -webkit-appearance: none; width: 24px; height: 24px; background: white; border: 2px solid var(--accent); border-radius: 50%; cursor: pointer; margin-top: -9px; }}
        input[type="range"]::-webkit-slider-runnable-track {{ width: 100%; height: 6px; background: #444; border-radius: 5px; }}

        .tabs {{ display: flex; gap: 8px; margin-bottom: 15px; background: #111; padding: 10px; border-radius: 12px; flex-wrap: wrap; justify-content: center; }}
        .tab-btn {{ 
            background: transparent; color: #666; padding: 8px 12px; border: 1px solid #333; 
            border-radius: 8px; cursor: pointer; transition: 0.2s; font-weight: 600; font-size: 0.85rem;
            min-width: 80px; flex: 1 1 30%; 
        }}
        .tab-btn.active {{ background: var(--card-bg); color: var(--accent); border-color: var(--accent); box-shadow: 0 2px 8px rgba(0,0,0,0.3); }}
        
        /* v21: 新增加入清單按鈕 */
        .add-btn {{
            background: #333; color: white; border: 1px solid #555; padding: 12px; width: 100%; 
            border-radius: 8px; margin-bottom: 20px; cursor: pointer; display: flex; align-items: center; justify-content: center; gap: 10px; font-weight: bold;
        }}
        .add-btn:active {{ background: #444; }}

        /* v21: 播放清單樣式 */
        .routine-container {{ text-align: left; margin-bottom: 20px; }}
        .routine-header {{ font-size: 0.9rem; color: #888; margin-bottom: 10px; display: flex; justify-content: space-between; }}
        .routine-list {{ list-style: none; padding: 0; margin: 0; min-height: 50px; background: #111; border-radius: 12px; padding: 10px; }}
        .routine-item {{ 
            background: #222; margin-bottom: 8px; padding: 10px; border-radius: 8px; 
            display: flex; justify-content: space-between; align-items: center; border-left: 4px solid #444;
        }}
        .routine-item.active {{ border-left-color: var(--accent); background: #2a1a2a; }}
        .routine-info {{ font-size: 0.9rem; }}
        .routine-range {{ font-size: 0.75rem; color: #888; font-family: monospace; margin-top: 3px; }}
        .delete-btn {{ background: none; border: none; color: #666; font-size: 1.2rem; cursor: pointer; padding: 0 10px; }}
        .delete-btn:hover {{ color: #ff5252; }}

        .play-btn {{ 
            background: var(--accent); color: white; border: none; padding: 18px 40px; border-radius: 50px; 
            font-size: 1.2rem; font-weight: 800; width: 100%; letter-spacing: 1px;
            box-shadow: 0 0 20px rgba(255, 64, 129, 0.4); transition: transform 0.1s;
            position: fixed; bottom: 30px; left: 50%; transform: translateX(-50%); width: 90%; max-width: 400px; z-index: 100;
        }}
        .play-btn:active {{ transform: translateX(-50%) scale(0.96); }}
        .play-btn.stop {{ background: #b0bec5; color: #000; box-shadow: none; }}
        .play-btn.warming {{ background: #333; color: #888; pointer-events: none; }}

        .status-display {{ margin-top: 10px; height: 100px; display: flex; flex-direction: column; justify-content: center; background: #000; border-radius: 12px; border: 1px solid #333; margin-bottom: 80px; }}
        .current-note {{ font-size: 3rem; color: white; font-weight: 800; line-height: 1; }}
        .action-text {{ font-size: 1.2rem; color: var(--accent); margin-top: 5px; font-weight: bold; }}
        .wake-status {{ font-size: 0.8rem; color: #555; margin-top: 5px; }}
        
        .loading-mask {{
            position: fixed; top:0; left:0; width:100%; height:100%; background: #121212; z-index: 999;
            display: flex; justify-content: center; align-items: center; color: white; flex-direction: column;
        }}
    </style>
</head>
<body>

    <div id="loadingMask" class="loading-mask">
        <div style="font-size: 2rem; margin-bottom: 10px;">🎹</div>
        <div>v21 系統初始化中...</div>
        <div id="errorDisplay" style="color:red; margin-top:20px; font-size:0.8rem; padding:20px;"></div>
    </div>

    <h1>聲樂教練 Pro</h1>
    <p>課程編排版</p>

    <div class="control-panel">
        <div class="tabs">
            <button id="btn-triad" class="tab-btn active" onclick="switchConfigMode('triad')">大三和弦</button>
            <button id="btn-scale5" class="tab-btn" onclick="switchConfigMode('scale5')">五度音階</button>
            <button id="btn-octave" class="tab-btn" onclick="switchConfigMode('octave')">八度音程</button>
            <button id="btn-p5" class="tab-btn" onclick="switchConfigMode('p5')">五度音程</button>
            <button id="btn-p4" class="tab-btn" onclick="switchConfigMode('p4')">四度音程</button>
        </div>

        <div class="range-selectors">
            <div class="range-col">
                <label>1. 起始</label>
                <select id="startNote"></select>
            </div>
            <div class="range-col">
                <label>2. 頂點</label>
                <select id="peakNote"></select>
            </div>
            <div class="range-col">
                <label>3. 結束</label>
                <select id="endNote"></select>
            </div>
        </div>

        <button class="add-btn" onclick="addToRoutine()">
            <span>⬇️ 加入練習清單</span>
        </button>

        <hr style="border: 0; border-top: 1px solid #333; margin: 15px 0;">
        
        <div class="routine-container">
            <div class="routine-header">
                <span>📋 你的課程清單</span>
                <span style="color:var(--accent); cursor:pointer;" onclick="clearRoutine()">清空</span>
            </div>
            <ul id="routineList" class="routine-list">
                <li style="color:#444; text-align:center; padding:10px;">(目前是空的，請上方加入練習)</li>
            </ul>
        </div>
        
        <div class="slider-group" style="margin-top:20px;">
            <div class="slider-label-row">
                <span>速度 (BPM)</span>
                <span id="bpmVal" class="val-display">100</span>
            </div>
            <input type="range" id="bpm" min="60" max="180" step="1" value="100">
        </div>

        <div class="slider-group">
            <div class="slider-label-row">
                <span>預備拍音量</span>
                <span id="volStickVal" class="val-display">60%</span>
            </div>
            <input type="range" id="volStick" min="0" max="100" step="1" value="60">
        </div>

        <div class="slider-group">
            <div class="slider-label-row">
                <span>導引音量</span>
                <span id="volMelodyVal" class="val-display">70%</span>
            </div>
            <input type="range" id="volMelody" min="0" max="100" step="1" value="70">
        </div>

        <div class="slider-group">
            <div class="slider-label-row">
                <span>伴奏音量</span>
                <span id="volChordVal" class="val-display">40%</span>
            </div>
            <input type="range" id="volChord" min="0" max="100" step="1" value="40">
        </div>
    </div>

    <div class="status-display">
        <div class="current-note" id="noteDisplay">Ready</div>
        <div class="action-text" id="actionDisplay">準備開始</div>
        <div class="wake-status" id="wakeStatus"></div>
    </div>

    <button class="play-btn" id="playBtn" onclick="togglePlay()">▶ 開始執行課程</button>

    <script>
    {player_code}
    {piano_code}
    </script>

    <script>
    const SILENT_MP3 = "data:audio/mp3;base64,SUQzBAAAAAAAI1RTU0UAAAAPAAADTGF2ZjU4Ljc2LjEwMAAAAAAAAAAAAAAA//OEAAAAAAAAAAAAAAAAAAAAAAAASW5mbwAAAA8AAAAEAAABIADAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMD//////////////////////////////////////////////////////////////////wAAAP9MYXZj৫৮Ljc2LjEwMAAAAAAAAAAAAP/zBKAAAAAAABHgAAAAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAA//OEAAAAAAAAAAAAAAAAAAAAAAAASW5mbwAAAA8AAAAEAAABIADAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMD//////////////////////////////////////////////////////////////////wAAAP9MYXZj৫৮Ljc2LjEwMAAAAAAAAAAAAP/zBKAAAAAAABHgAAAAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAA";

    let audioCtx, player;
    let melodyGainNode, chordGainNode;
    let isPlaying = false;
    let silentAudioPlayer = new Audio(SILENT_MP3);
    silentAudioPlayer.loop = true;

    let nextNoteTime = 0.0;
    let timerID;
    let lookahead = 25.0; 
    let scheduleAheadTime = 0.1; 
    
    // 播放狀態
    let currentRoots = [];
    let rootIndex = 0;
    let patternStepIndex = 0;
    
    // v21: 課程與設定狀態
    let editingMode = 'triad'; // 目前在編輯哪種模式
    let routineQueue = [];     // 待播放清單 {{mode, s, p, e, name}}
    let currentRoutineIndex = 0; // 目前播到清單第幾首
    
    let globalPeakIndex = 0;
    let countInBeats = 4; 
    let wakeLock = null;

    let rangeProfiles = {{
        'triad':  {{ s:'A3', p:'C#4', e:'A2', name:'大三和弦' }},
        'scale5': {{ s:'A3', p:'G4',  e:'A2', name:'五度音階' }},
        'octave': {{ s:'C3', p:'G4',  e:'C3', name:'八度音程' }},
        'p5':     {{ s:'C3', p:'G4',  e:'C3', name:'五度音程' }},
        'p4':     {{ s:'C3', p:'G4',  e:'C3', name:'四度音程' }}
    }};

    const notes = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B'];
    
    window.onload = function() {{
        setTimeout(() => {{
            try {{
                if (typeof WebAudioFontPlayer === 'undefined') throw new Error("引擎載入失敗");
                initSelects();
                initUIListeners();
                player = new WebAudioFontPlayer();
                document.getElementById('loadingMask').style.display = 'none';
            }} catch (e) {{
                document.getElementById('errorDisplay').innerText = e.message;
            }}
        }}, 500);
    }};

    function initSelects() {{
        const startSel = document.getElementById('startNote');
        const peakSel = document.getElementById('peakNote');
        const endSel = document.getElementById('endNote');
        
        for(let oct=2; oct<=5; oct++) {{
            notes.forEach(n => {{
                let val = `${{n}}${{oct}}`;
                startSel.add(new Option(val, val));
                peakSel.add(new Option(val, val));
                endSel.add(new Option(val, val));
            }});
        }}
        // 初始化
        applyProfile('triad');
    }}

    function initUIListeners() {{
        document.getElementById('bpm').addEventListener('input', function(e) {{
            document.getElementById('bpmVal').innerText = e.target.value;
        }});
        document.getElementById('volMelody').addEventListener('input', updateGains);
        document.getElementById('volChord').addEventListener('input', updateGains);
        document.getElementById('volStick').addEventListener('input', function(e){{
             document.getElementById('volStickVal').innerText = e.target.value + "%";
        }});
        
        ['startNote', 'peakNote', 'endNote'].forEach(id => {{
            document.getElementById(id).addEventListener('change', function() {{
                saveCurrentProfile();
            }});
        }});
    }}

    function updateGains() {{
        let melVol = document.getElementById('volMelody').value;
        let choVol = document.getElementById('volChord').value;
        document.getElementById('volMelodyVal').innerText = melVol + "%";
        document.getElementById('volChordVal').innerText = choVol + "%";
        
        if(melodyGainNode) melodyGainNode.gain.setTargetAtTime(melVol / 100.0, audioCtx.currentTime, 0.05);
        if(chordGainNode) chordGainNode.gain.setTargetAtTime(choVol / 100.0, audioCtx.currentTime, 0.05);
    }}

    // --- v21: 課程清單邏輯 ---

    function switchConfigMode(mode) {{
        saveCurrentProfile();
        editingMode = mode;
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.getElementById('btn-' + mode).classList.add('active');
        applyProfile(mode);
    }}

    function saveCurrentProfile() {{
        let s = document.getElementById('startNote').value;
        let p = document.getElementById('peakNote').value;
        let e = document.getElementById('endNote').value;
        // 僅更新數值，不改變名稱
        rangeProfiles[editingMode].s = s;
        rangeProfiles[editingMode].p = p;
        rangeProfiles[editingMode].e = e;
    }}

    function applyProfile(mode) {{
        let profile = rangeProfiles[mode];
        if(profile) {{
            document.getElementById('startNote').value = profile.s;
            document.getElementById('peakNote').value = profile.p;
            document.getElementById('endNote').value = profile.e;
        }}
    }}

    function addToRoutine() {{
        saveCurrentProfile();
        let p = rangeProfiles[editingMode];
        // 複製一份當下的設定加入清單
        routineQueue.push({{
            mode: editingMode,
            s: p.s,
            p: p.p,
            e: p.e,
            name: p.name
        }});
        renderRoutine();
    }}

    function renderRoutine() {{
        let list = document.getElementById('routineList');
        list.innerHTML = "";
        if(routineQueue.length === 0) {{
            list.innerHTML = '<li style="color:#444; text-align:center; padding:10px;">(目前是空的，請上方加入練習)</li>';
            return;
        }}
        
        routineQueue.forEach((item, idx) => {{
            let li = document.createElement('li');
            li.className = 'routine-item';
            if(isPlaying && currentRoutineIndex === idx) li.classList.add('active');
            
            li.innerHTML = `
                <div class="routine-info">
                    <div style="font-weight:bold">${{idx+1}}. ${{item.name}}</div>
                    <div class="routine-range">${{item.s}} ⮕ ${{item.p}} ⮕ ${{item.e}}</div>
                </div>
                <button class="delete-btn" onclick="removeItem(${{idx}})">×</button>
            `;
            list.appendChild(li);
        }});
    }}

    function removeItem(idx) {{
        routineQueue.splice(idx, 1);
        renderRoutine();
    }}

    function clearRoutine() {{
        routineQueue = [];
        renderRoutine();
    }}

    // --- 核心播放邏輯修改 ---

    // 根據傳入的設定物件生成路徑
    function generateRootsFromConfig(config) {{
        let s = config.s;
        let p = config.p;
        let e = config.e;
        
        let allOpts = Array.from(document.getElementById('startNote').options).map(o=>o.value);
        let sIdx = allOpts.indexOf(s);
        let pIdx = allOpts.indexOf(p);
        let eIdx = allOpts.indexOf(e);
        
        currentRoots = [];
        globalPeakIndex = 0; 
        
        if (sIdx <= pIdx) {{
            for(let i=sIdx; i<=pIdx; i++) currentRoots.push(allOpts[i]);
        }} else {{
            currentRoots.push(s);
        }}
        
        globalPeakIndex = currentRoots.length - 1;

        if (eIdx < pIdx) {{
            for(let i=pIdx-1; i>=eIdx; i--) currentRoots.push(allOpts[i]);
        }}
    }}

    function getMidiPitch(n) {{
        let note = n.slice(0, -1), oct = parseInt(n.slice(-1));
        return notes.indexOf(note) + (oct + 1) * 12;
    }}

    function playStickClick(time) {{
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
    }}

    function playChord(midiRoot, time, duration) {{
        let preset = _tone_0000_JCLive_sf2_file;
        [0, 4, 7].forEach(semi => {{
            player.queueWaveTable(audioCtx, chordGainNode, preset, time, midiRoot + semi, duration, 0.5);
        }});
    }}

    async function requestWakeLock() {{
        try {{
            if ('wakeLock' in navigator) {{
                wakeLock = await navigator.wakeLock.request('screen');
                document.getElementById('wakeStatus').innerText = "💡 螢幕恆亮 | 🔊 媒體模式";
            }}
        }} catch (err) {{
            console.error(err);
        }}
    }}

    function releaseWakeLock() {{
        if (wakeLock !== null) {{
            wakeLock.release();
            wakeLock = null;
            document.getElementById('wakeStatus').innerText = "";
        }}
    }}

    async function togglePlay() {{
        if (isPlaying) {{ stop(); return; }}

        if (routineQueue.length === 0) {{
            alert("請先將練習加入下方清單！");
            return;
        }}

        requestWakeLock();
        try {{ await silentAudioPlayer.play(); }} catch(e) {{}}

        if (!audioCtx) {{
            audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            melodyGainNode = audioCtx.createGain();
            chordGainNode = audioCtx.createGain();
            melodyGainNode.connect(audioCtx.destination);
            chordGainNode.connect(audioCtx.destination);
        }}
        if (audioCtx.state === 'suspended') await audioCtx.resume();

        updateGains();

        isPlaying = true;
        currentRoutineIndex = 0; // 從第一首開始
        startRoutineItem();
        
        let btn = document.getElementById('playBtn');
        btn.innerHTML = "⏹ 停止課程";
        btn.classList.add('stop');
        
        scheduler();
    }}

    // v21: 啟動單項練習邏輯 (含預備拍)
    function startRoutineItem() {{
        rootIndex = 0;
        patternStepIndex = 0;
        
        let config = routineQueue[currentRoutineIndex];
        generateRootsFromConfig(config); // 載入該項目的路徑
        renderRoutine(); // 更新 UI 顯示 active 狀態

        let bpm = parseFloat(document.getElementById('bpm').value);
        let beatDur = 60.0 / bpm;
        let now = audioCtx.currentTime;
        
        // 如果是剛開始播放(或者切換項目)，給予一點點緩衝時間
        // 若不是第一首，nextNoteTime 應該已經在未來了，這裡重新校正
        if (nextNoteTime < now) nextNoteTime = now + 0.5;

        let startDelay = countInBeats * beatDur;
        
        // 預備拍事件
        let preset = _tone_0000_JCLive_sf2_file;
        let firstRootName = currentRoots[0];
        let firstRootMidi = getMidiPitch(firstRootName);
        let chordDur = beatDur * 4;

        for(let i=0; i<countInBeats; i++) {{
            let t = nextNoteTime + (i * beatDur);
            playStickClick(t);
            if(i === 0) {{
                // 播放該項目的起始和弦定調
                playChord(firstRootMidi, t, chordDur);
            }}
        }}

        // 正式開始時間往後推
        nextNoteTime += startDelay;
    }}

    function stop() {{
        isPlaying = false;
        releaseWakeLock();
        silentAudioPlayer.pause();
        silentAudioPlayer.currentTime = 0;
        clearTimeout(timerID);
        if(player && audioCtx) player.cancelQueue(audioCtx);
        
        let btn = document.getElementById('playBtn');
        btn.innerHTML = "▶ 開始執行課程";
        btn.classList.remove('stop');
        
        document.getElementById('noteDisplay').innerText = "Ready";
        document.getElementById('actionDisplay').innerText = "暫停中";
        renderRoutine(); // 清除 active
    }}

    function scheduler() {{
        while (isPlaying && nextNoteTime < audioCtx.currentTime + scheduleAheadTime) {{
            scheduleNote(rootIndex, patternStepIndex, nextNoteTime);
            nextStep();
        }}
        if (isPlaying) timerID = window.setTimeout(scheduler, lookahead);
    }}

    function nextStep() {{
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
        
        // 一個 pattern 結束
        if (patternStepIndex >= totalBeats) {{
            patternStepIndex = 0;
            rootIndex++;
            
            // v21: 檢查該項目是否已跑完所有根音
            if (rootIndex >= currentRoots.length) {{
                // 該項目結束，進入下一個
                currentRoutineIndex++;
                if (currentRoutineIndex < routineQueue.length) {{
                    // 還有下一首，休息 2 秒 (80 BPM 約 1.5秒，給 2 秒 buffer)
                    nextNoteTime += 2.0; 
                    startRoutineItem();
                }} else {{
                    // 清單全部結束
                    stop();
                    document.getElementById('actionDisplay').innerText = "🎉 課程完成！";
                }}
            }}
        }}
    }}

    function scheduleNote(idx, step, time) {{
        // 若超過範圍(切換間隙)，不處理
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

        if (step === 0) {{
            document.getElementById('noteDisplay').innerText = rootName;
            let dir = "";
            if(idx === globalPeakIndex) dir = "🏆 頂點";
            else if(idx < globalPeakIndex) dir = "⬆ 上升";
            else dir = "⬇ 下降";
            document.getElementById('actionDisplay').innerText = dir;
        }}

        if (step < intervals.length) {{
            let noteMidi = rootMidi + intervals[step];
            player.queueWaveTable(audioCtx, melodyGainNode, preset, time, noteMidi, beatDur*0.9, 1.0);
            
            if (step === 0) {{
                let chordDur = beatDur * intervals.length;
                playChord(rootMidi, time, chordDur);
            }}
        }} 
        else if (step === intervals.length) {{
            document.getElementById('actionDisplay').innerText = "😤 吸氣 (1/2)";
            playChord(rootMidi, time, beatDur);
        }}
        else if (step === intervals.length + 1) {{
             // 檢查是否還有下一個根音
             let nextIdx = idx + 1;
             
             // 如果這是該練習的最後一個根音
             if (nextIdx >= currentRoots.length) {{
                 document.getElementById('actionDisplay').innerText = "🏁 練習結束，準備休息";
                 // 不彈轉調和弦，因為要結束了(或接下一個練習)
             }} else {{
                 document.getElementById('actionDisplay').innerText = "👉 準備轉調";
                 let nextRootName = currentRoots[nextIdx];
                 let nextRootMidi = getMidiPitch(nextRootName);
                 playChord(nextRootMidi, time, beatDur);
             }}
        }}
    }}
    </script>
</body>
</html>
"""

# 5. 寫入檔案
output_filename = "VocalTrainer_Offline_v21.html"
with open(output_filename, "w", encoding="utf-8") as f:
    f.write(html_template)

print(f"✅ 成功！已建立檔案: {output_filename}")
print(f"👉 v21 重大更新：全新的「課程編排」模式！請新增練習到清單後再開始播放。")
