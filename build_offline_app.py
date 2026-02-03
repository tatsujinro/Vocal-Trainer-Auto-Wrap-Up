import urllib.request
import os
import ssl

print("🚀 正在開始打包您的離線版聲樂教練 (v17 螢幕恆亮版)...")

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
    <title>Daily Vocal Workout</title>
    <style>
        :root {{ --bg-color: #121212; --card-bg: #1e1e1e; --text-main: #e0e0e0; --accent: #ff5252; --accent-light: #ff867f; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: var(--bg-color); color: var(--text-main); margin: 0; padding: 20px; text-align: center; user-select: none; }}
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
        
        input[type="range"] {{ 
            width: 100%; height: 6px; background: #444; border-radius: 5px; outline: none; -webkit-appearance: none; 
        }}
        input[type="range"]::-webkit-slider-thumb {{ 
            -webkit-appearance: none; width: 24px; height: 24px; background: white; border: 2px solid var(--accent); border-radius: 50%; cursor: pointer; margin-top: -9px; 
        }}
        input[type="range"]::-webkit-slider-runnable-track {{
            width: 100%; height: 6px; background: #444; border-radius: 5px;
        }}

        .tabs {{ display: flex; gap: 8px; margin-bottom: 20px; background: #111; padding: 5px; border-radius: 12px; }}
        .tab-btn {{ background: transparent; color: #666; padding: 12px; border: none; flex: 1; border-radius: 8px; cursor: pointer; transition: 0.2s; font-weight: 600; }}
        .tab-btn.active {{ background: var(--card-bg); color: var(--accent); box-shadow: 0 2px 8px rgba(0,0,0,0.3); }}
        
        .play-btn {{ 
            background: var(--accent); color: white; border: none; padding: 18px 40px; border-radius: 50px; 
            font-size: 1.2rem; font-weight: 800; margin-top: 10px; width: 100%; letter-spacing: 1px;
            box-shadow: 0 0 20px rgba(255, 82, 82, 0.4); transition: transform 0.1s;
        }}
        .play-btn:active {{ transform: scale(0.96); }}
        .play-btn.stop {{ background: #536dfe; color: white; box-shadow: none; }}
        .play-btn.warming {{ background: #333; color: #888; pointer-events: none; }}

        .status-display {{ margin-top: 10px; height: 100px; display: flex; flex-direction: column; justify-content: center; background: #000; border-radius: 12px; border: 1px solid #333; }}
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
        <div>v17 系統初始化中...</div>
        <div id="errorDisplay" style="color:red; margin-top:20px; font-size:0.8rem; padding:20px;"></div>
    </div>

    <h1>聲樂教練 Pro</h1>
    <p>螢幕恆亮版</p>

    <div class="tabs">
        <button id="btn-liptrill" class="tab-btn active" onclick="switchMode('liptrill')">👄 唇顫音</button>
        <button id="btn-expansion" class="tab-btn" onclick="switchMode('expansion')">📢 擴張</button>
        <button id="btn-jumps" class="tab-btn" onclick="switchMode('jumps')">📈 大跳</button>
    </div>

    <div class="control-panel">
        <div class="range-selectors">
            <div class="range-col">
                <label>1. 起始 (低)</label>
                <select id="startNote"></select>
            </div>
            <div class="range-col">
                <label>2. 頂點 (高)</label>
                <select id="peakNote"></select>
            </div>
            <div class="range-col">
                <label>3. 結束 (低)</label>
                <select id="endNote"></select>
            </div>
        </div>

        <div class="slider-group">
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
        <div class="wake-status" id="wakeStatus">💡 省電模式待機中</div>
    </div>

    <button class="play-btn" id="playBtn" onclick="togglePlay()">▶ 開始練習</button>

    <script>
    {player_code}
    {piano_code}
    </script>

    <script>
    let audioCtx, player;
    let melodyGainNode, chordGainNode;
    let isPlaying = false;
    
    let nextNoteTime = 0.0;
    let timerID;
    let lookahead = 25.0; 
    let scheduleAheadTime = 0.1; 
    
    let currentRoots = [];
    let rootIndex = 0;
    let patternStepIndex = 0;
    let currentMode = 'liptrill';
    let globalPeakIndex = 0;
    
    let countInBeats = 4; 
    
    // v17: 喚醒鎖變數
    let wakeLock = null;

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
        switchMode('liptrill');
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
            document.getElementById(id).addEventListener('change', generateRoots);
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

    function switchMode(mode) {{
        currentMode = mode;
        document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        document.getElementById('btn-' + mode).classList.add('active');
        
        let s = document.getElementById('startNote');
        let p = document.getElementById('peakNote');
        let e = document.getElementById('endNote');

        if(mode==='liptrill'){{ s.value='A3'; p.value='C#4'; e.value='A2'; }}
        else if(mode==='expansion'){{ s.value='A3'; p.value='G4'; e.value='A2'; }}
        else {{ s.value='C3'; p.value='G4'; e.value='C3'; }}
        
        generateRoots();
        if(isPlaying) {{
            rootIndex = 0;
            patternStepIndex = 0;
        }}
    }}

    function generateRoots() {{
        let s = document.getElementById('startNote').value;
        let p = document.getElementById('peakNote').value;
        let e = document.getElementById('endNote').value;
        
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

    // --- v17: 螢幕喚醒鎖定邏輯 ---
    async function requestWakeLock() {{
        try {{
            if ('wakeLock' in navigator) {{
                wakeLock = await navigator.wakeLock.request('screen');
                document.getElementById('wakeStatus').innerText = "☀️ 螢幕恆亮已開啟";
                wakeLock.addEventListener('release', () => {{
                    document.getElementById('wakeStatus').innerText = "💡 螢幕恆亮已釋放";
                }});
            }} else {{
                document.getElementById('wakeStatus').innerText = "⚠️ 此瀏覽器不支援恆亮";
            }}
        }} catch (err) {{
            console.error(err);
            document.getElementById('wakeStatus').innerText = "⚠️ 恆亮啟用失敗 (低電量模式?)";
        }}
    }}

    function releaseWakeLock() {{
        if (wakeLock !== null) {{
            wakeLock.release();
            wakeLock = null;
        }}
    }}

    async function togglePlay() {{
        if (isPlaying) {{ stop(); return; }}

        // 1. 請求螢幕恆亮
        requestWakeLock();

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
        rootIndex = 0;
        patternStepIndex = 0;
        generateRoots();

        let btn = document.getElementById('playBtn');
        btn.innerHTML = "🥁 1, 2, 3, 4 ...";
        btn.classList.add('warming');
        
        let bpm = parseFloat(document.getElementById('bpm').value);
        let beatDur = 60.0 / bpm;
        let now = audioCtx.currentTime;
        
        let preset = _tone_0000_JCLive_sf2_file;
        let firstRootName = currentRoots[0];
        let firstRootMidi = getMidiPitch(firstRootName);
        let chordDur = beatDur * 4;

        for(let i=0; i<countInBeats; i++) {{
            let t = now + (i * beatDur);
            playStickClick(t);
            if(i === 0) {{
                [0, 4, 7].forEach(semi => {{
                    player.queueWaveTable(audioCtx, chordGainNode, preset, t, firstRootMidi + semi, chordDur, 0.5);
                }});
            }}
        }}

        let startDelay = countInBeats * beatDur;
        nextNoteTime = now + startDelay;
        
        setTimeout(() => {{
            if(isPlaying) {{
                btn.innerHTML = "⏹ 停止";
                btn.classList.remove('warming');
                btn.classList.add('stop');
            }}
        }}, startDelay * 1000);
        
        scheduler();
    }}

    function stop() {{
        isPlaying = false;
        
        // 2. 釋放螢幕恆亮
        releaseWakeLock();
        
        clearTimeout(timerID);
        if(player && audioCtx) player.cancelQueue(audioCtx);
        
        let btn = document.getElementById('playBtn');
        btn.innerHTML = "▶ 開始練習";
        btn.classList.remove('stop');
        btn.classList.remove('warming');
        
        document.getElementById('noteDisplay').innerText = "Ready";
        document.getElementById('actionDisplay').innerText = "暫停中";
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

        let intervals, totalBeats;
        if(currentMode==='liptrill') {{ intervals=[0,4,7,4,0]; totalBeats=6; }}
        else if(currentMode==='expansion') {{ intervals=[0,2,4,5,7,5,4,2,0]; totalBeats=10; }}
        else {{ intervals=[0,12,0]; totalBeats=4; }}

        patternStepIndex++;
        if (patternStepIndex >= totalBeats) {{
            patternStepIndex = 0;
            rootIndex++;
            if (rootIndex >= currentRoots.length) rootIndex = 0;
        }}
    }}

    function scheduleNote(idx, step, time) {{
        let rootName = currentRoots[idx];

        if (step === 0) {{
            document.getElementById('noteDisplay').innerText = rootName;
            let dir = "";
            if(idx === globalPeakIndex) dir = "🏆 頂點";
            else if(idx < globalPeakIndex) dir = "⬆ 上升";
            else dir = "⬇ 下降";
            document.getElementById('actionDisplay').innerText = dir;
        }}
        
        let bpm = parseFloat(document.getElementById('bpm').value);
        let beatDur = 60.0 / bpm;
        let rootMidi = getMidiPitch(rootName);
        let preset = _tone_0000_JCLive_sf2_file;

        let intervals, totalBeats;
        if(currentMode==='liptrill') {{ intervals=[0,4,7,4,0]; totalBeats=6; }}
        else if(currentMode==='expansion') {{ intervals=[0,2,4,5,7,5,4,2,0]; totalBeats=10; }}
        else {{ intervals=[0,12,0]; totalBeats=4; }}

        if (step === totalBeats - 1) {{
             document.getElementById('actionDisplay').innerText = "😤 吸氣";
             return;
        }}

        if (step < intervals.length) {{
            let noteMidi = rootMidi + intervals[step];
            player.queueWaveTable(audioCtx, melodyGainNode, preset, time, noteMidi, beatDur*0.9, 1.0);
        }}

        if (step === 0) {{
            let chordDur = beatDur * (totalBeats - 1);
            [0, 4, 7].forEach(semi => {{
                player.queueWaveTable(audioCtx, chordGainNode, preset, time, rootMidi + semi, chordDur, 0.5);
            }});
        }}
    }}
    </script>
</body>
</html>
"""

# 5. 寫入檔案
output_filename = "VocalTrainer_Offline_v17.html"
with open(output_filename, "w", encoding="utf-8") as f:
    f.write(html_template)

print(f"✅ 成功！已建立檔案: {output_filename}")
print(f"👉 v17 特性：加入螢幕喚醒鎖 (Wake Lock)，播放期間螢幕將保持恆亮，防止手機休眠斷線！")