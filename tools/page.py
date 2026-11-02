"""Catalog page. The roll is measured from the MIDI files."""

from __future__ import annotations

import json
from pathlib import Path

from tools.statements import AUDITION, ON_PICTURE, PREVIEW_LINE, PROGRAM, PUBLICATION, WARNING

SPELL = {
    "s01": ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
    "s02": ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "G#", "A", "Bb", "B"],
    "s03": ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"],
    "s04": ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "G#", "A", "Bb", "B"],
    "s05": ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"],
    "s06": ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"],
    "s07": ["C", "C#", "D", "Eb", "E", "F", "F#", "G", "Ab", "A", "Bb", "B"],
    "s08": ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"],
}


def write_page(path: Path, catalog: dict, report: dict, preview: dict, film: dict) -> None:
    path.write_text(render_page(catalog, report, preview, film), encoding="utf-8")
    path.with_name("media.html").write_text(_media_html(), encoding="utf-8")


def render_page(catalog: dict, report: dict, preview: dict, film: dict) -> str:
    rows = []
    for part in catalog["parts"]:
        kind = "core" if part["core"] else "bass reference"
        rows.append(
            "<tr>"
            f"<td><a href=\"{part['path']}\">{part['id']}</a></td>"
            f"<td>{part['role']}</td>"
            f"<td>{part['variation']}</td>"
            f"<td>{kind}</td>"
            f"<td>{part['bpm']}</td>"
            f"<td>{part['notes']}</td>"
            "</tr>"
        )
    payload = {
        "hand_split": catalog["hand_split"],
        "studies": [
            {
                "id": study["id"],
                "title": study["title"],
                "bpm": study["bpm"],
                "bars": study["bars"],
                "collection": study["collection_name"],
                "tonic": study["tonal_reference"],
                "identity": study["identity"],
                "limitations": study["limitations"],
                "voicing": study["voicing"],
                "layering": study["layering"],
                "accent": study["accent"],
                "departures": study["departures"],
                "harmonic_rhythm": study["harmonic_rhythm"],
                "changes": study["changes"],
                "change_bars": study["change_bars"],
                "phrases": study["phrases"],
                "tempo_us": study["tempo_us"],
                "spell": SPELL[study["id"]],
            }
            for study in catalog["studies"]
        ],
        "parts": [
            {
                "id": part["id"],
                "study_id": part["study_id"],
                "role": part["role"],
                "variation": part["variation"],
                "path": part["path"],
            }
            for part in catalog["parts"]
        ],
    }
    data = json.dumps(payload, ensure_ascii=False).replace("<", "\\u003c")
    seconds = f"{preview['seconds_encoded']:.2f}"
    film_seconds = f"{film['duration_seconds']:.2f}"
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>90s Piano House Riffs</title>
  <style>
    :root {{
      --bg: #1a1218;
      --paper: #f4efe6;
      --ink: #241c28;
      --magenta: #d23070;
      --teal: #1f6f6a;
      --muted: #cbbec6;
      --line: rgba(244, 239, 230, .16);
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0; background: var(--bg); color: var(--paper);
      font-family: Georgia, "Iowan Old Style", Palatino, serif;
      line-height: 1.45; padding-bottom: 88px;
    }}
    a {{ color: #f0a0c0; }}
    button, .meta, .note, .transport {{ font-family: ui-monospace, Menlo, Consolas, monospace; }}
    .top {{
      position: sticky; top: 0; z-index: 6;
      display: flex; justify-content: space-between; gap: 12px; align-items: center;
      padding: 12px 20px; background: rgba(26, 18, 24, .94); border-bottom: 1px solid var(--line);
    }}
    .brand {{ letter-spacing: .14em; text-transform: uppercase; font-size: .72rem; }}
    .top nav {{ display: flex; gap: 14px; font-size: .78rem; }}
    main {{ width: min(1180px, calc(100% - 2rem)); margin: 0 auto; }}
    .stage {{
      display: grid; grid-template-columns: minmax(0, .8fr) minmax(0, 1.2fr);
      gap: 28px; align-items: start; padding: 26px 0 8px;
    }}
    .stage > div {{ min-width: 0; }}
    h1 {{ font-weight: 500; font-size: clamp(2.4rem, 5vw, 4.4rem); line-height: .92; margin: 8px 0 10px; }}
    .kicker {{ letter-spacing: .16em; text-transform: uppercase; color: var(--magenta); font-size: .74rem; margin: 0; }}
    .meta, .note {{ color: var(--muted); font-size: .82rem; }}
    .hero img {{ display: block; width: 100%; height: auto; border-radius: 12px; }}
    .rail, .phrases, .switch {{ display: flex; gap: 8px; flex-wrap: wrap; margin: 8px 0; }}
    .rail {{ overflow-x: auto; flex-wrap: nowrap; max-width: 100%; padding-bottom: 4px; }}
    button {{
      border: 1px solid var(--line); background: transparent; color: var(--paper);
      border-radius: 999px; padding: 7px 11px; cursor: pointer;
    }}
    button[aria-pressed="true"] {{ background: var(--magenta); color: white; border-color: var(--magenta); }}
    .scroller {{ overflow-x: auto; max-width: 100%; background: var(--paper); color: var(--ink); border-radius: 16px; padding: 8px 0 12px; }}
    .ruler, .hand, .basslane {{ position: relative; }}
    .ruler {{ height: 28px; }}
    .change {{
      position: absolute; top: 4px; height: 20px; border-left: 2px solid var(--magenta);
      padding-left: 5px; font-size: 11px; white-space: nowrap; overflow: hidden;
    }}
    .hand {{ height: 132px; border-top: 1px solid rgba(36, 28, 40, .12); }}
    .hand-label {{
      position: sticky; left: 8px; top: 4px; z-index: 2;
      font-size: 10px; letter-spacing: .12em; text-transform: uppercase; color: #6d6170;
    }}
    .block {{
      position: absolute; border-radius: 3px; min-width: 3px;
    }}
    .block.rh {{ background: var(--ink); }}
    .block.rh.hot {{ background: var(--magenta); }}
    .block.lh {{ background: var(--teal); }}
    .phrase-band {{
      position: absolute; top: 0; bottom: 0; background: rgba(210, 48, 112, .08); pointer-events: none;
    }}
    .basslane {{ height: 46px; background: #241c28; color: var(--paper); display: none; }}
    .basslane.on {{ display: block; }}
    .bnote {{
      position: absolute; top: 14px; height: 18px; border-radius: 999px;
      background: #f4efe6; color: #241c28; font-size: 10px; padding: 1px 4px;
    }}
    .spark {{ display: flex; align-items: flex-end; gap: 2px; height: 46px; margin-top: 8px; }}
    .spark i {{ display: block; width: 4px; background: var(--magenta); border-radius: 2px 2px 0 0; }}
    .legend {{ display: flex; gap: 14px; flex-wrap: wrap; font-size: .78rem; color: var(--muted); }}
    .swatch {{ display: inline-block; width: 10px; height: 10px; border-radius: 2px; margin-right: 4px; }}
    .table-scroll {{ overflow-x: auto; max-width: 100%; }}
    table {{ width: 100%; border-collapse: collapse; font-size: .8rem; }}
    th, td {{ text-align: left; padding: 7px 6px; border-bottom: 1px solid var(--line); }}
    .flow {{ display: flex; flex-wrap: wrap; gap: 8px; }}
    .flow span {{ border: 1px solid var(--line); border-radius: 999px; padding: 4px 8px; font-size: .78rem; }}
    audio, video {{ display: block; width: 100%; height: auto; margin: 10px 0 16px; background: #000; }}
    .transport {{
      position: fixed; left: 0; right: 0; bottom: 0; z-index: 7;
      display: flex; gap: 10px; flex-wrap: wrap; align-items: center;
      padding: 10px 16px; background: #120c12; border-top: 1px solid var(--line);
    }}
    @media (max-width: 860px) {{
      .stage {{ grid-template-columns: 1fr; }}
      .top nav {{ display: none; }}
    }}
  </style>
</head>
<body>
  <header class="top">
    <a class="brand" href="index.html">90s Piano House Riffs</a>
    <nav>
      <a href="#roll">Roll</a>
      <a href="#files">Files</a>
      <a href="#reading">Recorded reading</a>
      <a href="media.html">Stills</a>
      <a href="midi/arrangement.mid">Arrangement</a>
    </nav>
  </header>
  <main>
    <section class="stage">
      <div>
        <p class="kicker">Eight 16-bar hooks · accent, voicing, ending</p>
        <h1 id="title">Offbeat Ninth</h1>
        <p id="identity"></p>
        <p class="meta" id="facts"></p>
        <p id="rhythm"></p>
        <p id="voicing"></p>
        <p id="layering"></p>
        <p id="accent-copy"></p>
        <p class="note" id="limits"></p>
        <p class="note" id="departures"></p>
      </div>
      <div id="roll">
        <figure class="hero">
          <img src="art/hero.jpg" width="1280" height="720" alt="Illustration of a piano roll with taller bars for louder accents. Not a photograph of a studio or of performers.">
        </figure>
        <div class="rail" id="rail"></div>
        <div class="switch">
          <button type="button" id="var-a" aria-pressed="true">Variation A</button>
          <button type="button" id="var-b" aria-pressed="false">Variation B</button>
        </div>
        <div class="phrases" id="phrases"></div>
        <div class="scroller" id="scroller">
          <div class="ruler" id="ruler"></div>
          <div class="hand" id="right"><div class="hand-label">Right hand, C4 and up</div></div>
          <div class="hand" id="left"><div class="hand-label">Left hand, below C4</div></div>
          <div class="basslane on" id="basslane"><div class="hand-label">Bass reference, not in the piano file</div></div>
        </div>
        <div class="spark" id="spark" aria-hidden="true"></div>
        <p class="legend">
          <span><i class="swatch" style="background:#241c28"></i>right hand</span>
          <span><i class="swatch" style="background:#d23070"></i>velocity 105 and up</span>
          <span><i class="swatch" style="background:#1f6f6a"></i>left hand</span>
          <span>Bar height follows velocity.</span>
        </p>
        <p class="note" id="status">Reading the MIDI.</p>
      </div>
    </section>
    <p>{catalog['range_statement']}</p>
    <div class="flow">
      <span>Score</span><span>MIDI</span><span>Reopened validation</span><span>MP3</span><span>Film</span><span>Stills</span><span>Drafts</span>
    </div>
    <p class="note"><a href="articles/medium-draft-Cursor.md">Article draft</a> · <a href="articles/medium-paste-Cursor.txt">plain text</a></p>
    <p>{WARNING}</p>
    <h2 id="files">Files</h2>
    <p class="meta">Validation {report['result']}. Core {catalog['core_part_count']}. Bass references {catalog['reference_part_count']}. <a href="midi/validation-Cursor.json">validation report</a> · <a href="catalog/catalog-Cursor.json">catalog</a></p>
    <div class="table-scroll">
      <table>
        <thead><tr><th>Part</th><th>Role</th><th>Var</th><th>Count</th><th>BPM</th><th>Notes</th></tr></thead>
        <tbody>{''.join(rows)}</tbody>
      </table>
    </div>
    <section id="reading">
      <p class="kicker">Recorded reading · study 01 variation A, all 16 bars</p>
      <p>This MP3 is {seconds} seconds. {PREVIEW_LINE}. The film is {film_seconds} seconds and shows {ON_PICTURE}.</p>
      <audio controls preload="metadata" src="preview/preview.mp3"></audio>
      <p><a href="preview/preview.mp3">preview/preview.mp3</a></p>
      <video controls preload="metadata" poster="film/poster.jpg" width="1280" height="720">
        <source src="film/preview.mp4" type="video/mp4">
        <track kind="captions" src="film/preview.vtt" srclang="en" label="English" default>
      </video>
    </section>
    <p>{PROGRAM}</p>
    <p>{AUDITION}</p>
    <p>{PUBLICATION}</p>
  </main>
  <div class="transport">
    <button type="button" id="play">Play riff</button>
    <button type="button" id="bass-toggle" aria-pressed="true">Bass reference</button>
    <span id="transport-label">Space plays. J and K change study.</span>
  </div>
  <script id="pack" type="application/json">{data}</script>
  <script>
    const pack = JSON.parse(document.getElementById("pack").textContent);
    const rail = document.getElementById("rail");
    const phrases = document.getElementById("phrases");
    const scroller = document.getElementById("scroller");
    const ruler = document.getElementById("ruler");
    const right = document.getElementById("right");
    const left = document.getElementById("left");
    const basslane = document.getElementById("basslane");
    const spark = document.getElementById("spark");
    const status = document.getElementById("status");
    let studyId = "s01";
    let variation = "a";
    let pianoNotes = [];
    let bassNotes = [];
    let showBass = true;
    let audio = null;
    let playing = false;
    let followId = 0;
    let rollWidth = 1200;

    function study() {{
      return pack.studies.find((item) => item.id === studyId);
    }}
    function pitchName(pitch) {{
      return study().spell[pitch % 12] + (Math.floor(pitch / 12) - 1);
    }}
    function readVlq(view, offset) {{
      let value = 0;
      let byte = 0;
      do {{
        byte = view.getUint8(offset);
        offset += 1;
        value = (value << 7) | (byte & 0x7f);
      }} while (byte & 0x80);
      return [value, offset];
    }}
    function parseMidi(buffer) {{
      const view = new DataView(buffer);
      if (String.fromCharCode(view.getUint8(0), view.getUint8(1), view.getUint8(2), view.getUint8(3)) !== "MThd" || view.getUint16(12) !== 960) {{
        throw new Error("unexpected MIDI header");
      }}
      const tracks = view.getUint16(10);
      let offset = 14;
      const notes = [];
      for (let track = 0; track < tracks; track += 1) {{
        if (String.fromCharCode(view.getUint8(offset), view.getUint8(offset + 1), view.getUint8(offset + 2), view.getUint8(offset + 3)) !== "MTrk") {{
          throw new Error("missing track");
        }}
        const length = view.getUint32(offset + 4);
        offset += 8;
        const end = offset + length;
        let tick = 0;
        let running = 0;
        const open = new Map();
        while (offset < end) {{
          let delta;
          [delta, offset] = readVlq(view, offset);
          tick += delta;
          let byte = view.getUint8(offset);
          if (byte >= 0x80) {{
            running = byte;
            offset += 1;
          }}
          if (running === 0xff) {{
            offset += 1;
            let metaLen;
            [metaLen, offset] = readVlq(view, offset);
            offset += metaLen;
            continue;
          }}
          const kind = running & 0xf0;
          const data1 = byte < 0x80 ? byte : view.getUint8(offset);
          if (byte >= 0x80) offset += 1;
          let data2 = 0;
          if (kind !== 0xc0 && kind !== 0xd0) {{
            data2 = view.getUint8(offset);
            offset += 1;
          }}
          const key = (running & 0x0f) + ":" + data1;
          if (kind === 0x90 && data2 > 0) open.set(key, {{ tick: tick, velocity: data2 }});
          else if (kind === 0x80 || (kind === 0x90 && data2 === 0)) {{
            const started = open.get(key);
            if (started) {{
              notes.push({{ pitch: data1, start: started.tick, duration: tick - started.tick, velocity: started.velocity }});
              open.delete(key);
            }}
          }}
        }}
      }}
      notes.sort((a, b) => a.start - b.start || a.pitch - b.pitch);
      return notes;
    }}
    function partPath(role) {{
      const found = pack.parts.find((part) => part.study_id === studyId && part.role === role && part.variation === variation);
      if (!found) throw new Error("missing " + role);
      return found.path;
    }}
    function renderCopy() {{
      const item = study();
      document.getElementById("title").textContent = item.title;
      document.getElementById("identity").textContent = item.identity;
      document.getElementById("facts").textContent = item.id + " · " + item.bpm + " BPM · " + item.bars + " bars · " + item.collection + " · tonic " + item.tonic;
      document.getElementById("rhythm").textContent = item.harmonic_rhythm;
      document.getElementById("voicing").textContent = item.voicing;
      document.getElementById("layering").textContent = item.layering;
      document.getElementById("accent-copy").textContent = item.accent;
      document.getElementById("limits").textContent = item.limitations;
      document.getElementById("departures").textContent = item.departures.length ? item.departures.join(" ") : "No pitch in this study is flagged as a departure.";
      document.getElementById("transport-label").textContent = item.title + " " + variation.toUpperCase() + " · Space plays · J and K change study";
      for (const button of rail.querySelectorAll("button")) button.setAttribute("aria-pressed", button.dataset.id === studyId ? "true" : "false");
      document.getElementById("var-a").setAttribute("aria-pressed", variation === "a" ? "true" : "false");
      document.getElementById("var-b").setAttribute("aria-pressed", variation === "b" ? "true" : "false");
      phrases.innerHTML = "";
      item.phrases.forEach((phrase) => {{
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = phrase.name;
        button.addEventListener("click", () => {{
          const x = (phrase.start_bar / item.bars) * rollWidth;
          scroller.scrollTo({{ left: Math.max(0, x - 12), behavior: "smooth" }});
        }});
        phrases.appendChild(button);
      }});
    }}
    function laneNotes(host, notes, klass) {{
      host.querySelectorAll(".block, .phrase-band, .empty").forEach((node) => node.remove());
      const item = study();
      const container = item.bars * 4 * 960;
      if (!notes.length) {{
        const empty = document.createElement("p");
        empty.className = "empty hand-label";
        empty.textContent = klass === "lh" ? "Left hand rests in this variation." : "No notes.";
        host.appendChild(empty);
        return;
      }}
      const low = Math.min(...notes.map((note) => note.pitch));
      const high = Math.max(...notes.map((note) => note.pitch));
      const span = Math.max(1, high - low);
      item.phrases.forEach((phrase, index) => {{
        if (index % 2) return;
        const band = document.createElement("div");
        band.className = "phrase-band";
        band.style.left = (phrase.start_bar / item.bars) * rollWidth + "px";
        band.style.width = (phrase.bars / item.bars) * rollWidth + "px";
        host.appendChild(band);
      }});
      notes.forEach((note) => {{
        const block = document.createElement("div");
        block.className = "block " + klass + (note.velocity >= 105 ? " hot" : "");
        block.title = pitchName(note.pitch) + " · velocity " + note.velocity;
        block.dataset.start = String(note.start);
        block.dataset.end = String(note.start + note.duration);
        const y = 18 + (1 - (note.pitch - low) / span) * 90;
        block.style.left = (note.start / container) * rollWidth + "px";
        block.style.width = Math.max(3, (note.duration / container) * rollWidth - 1) + "px";
        block.style.top = y + "px";
        block.style.height = (8 + (note.velocity / 127) * 16) + "px";
        host.appendChild(block);
      }});
    }}
    function draw() {{
      const item = study();
      const container = item.bars * 4 * 960;
      rollWidth = Math.max(960, item.bars * 210);
      [ruler, right, left, basslane].forEach((node) => {{ node.style.width = rollWidth + "px"; }});
      ruler.innerHTML = "";
      let bar = 0;
      item.changes.forEach((name, index) => {{
        const span = item.change_bars[index];
        const mark = document.createElement("div");
        mark.className = "change";
        mark.textContent = name;
        mark.style.left = (bar / item.bars) * rollWidth + "px";
        mark.style.width = (span / item.bars) * rollWidth + "px";
        ruler.appendChild(mark);
        bar += span;
      }});
      const split = pack.hand_split;
      laneNotes(right, pianoNotes.filter((note) => note.pitch >= split), "rh");
      laneNotes(left, pianoNotes.filter((note) => note.pitch < split), "lh");
      basslane.classList.toggle("on", showBass);
      basslane.querySelectorAll(".bnote").forEach((node) => node.remove());
      if (showBass) {{
        bassNotes.forEach((note) => {{
          const mark = document.createElement("div");
          mark.className = "bnote";
          mark.textContent = pitchName(note.pitch);
          mark.style.left = (note.start / container) * rollWidth + "px";
          basslane.appendChild(mark);
        }});
      }}
      spark.innerHTML = "";
      pianoNotes.filter((note) => note.pitch >= split).forEach((note) => {{
        const bar = document.createElement("i");
        bar.style.height = Math.max(4, (note.velocity / 127) * 46) + "px";
        spark.appendChild(bar);
      }});
      status.textContent = pianoNotes.length + " piano notes. " + pianoNotes.filter((note) => note.pitch < split).length + " are left hand.";
    }}
    async function loadStudy() {{
      stopPlayback();
      renderCopy();
      status.textContent = "Reading the MIDI.";
      try {{
        const pianoRes = await fetch(partPath("piano-riff"));
        const bassRes = await fetch(partPath("bass-reference"));
        if (!pianoRes.ok || !bassRes.ok) throw new Error("MIDI request failed");
        pianoNotes = parseMidi(await pianoRes.arrayBuffer());
        bassNotes = parseMidi(await bassRes.arrayBuffer());
        draw();
      }} catch (error) {{
        pianoNotes = [];
        bassNotes = [];
        status.textContent = "The MIDI did not load. " + error.message;
      }}
    }}
    function freq(pitch) {{
      return 440 * Math.pow(2, (pitch - 69) / 12);
    }}
    function schedule(ctx, note, origin, amount, type) {{
      const item = study();
      const seconds = (tick) => tick / 960 * item.tempo_us / 1000000;
      const when = origin + seconds(note.start);
      const duration = Math.max(0.04, seconds(note.duration));
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = type;
      osc.frequency.value = freq(note.pitch);
      const level = amount * (note.velocity / 110);
      const attack = Math.min(0.012, duration * 0.25);
      gain.gain.setValueAtTime(0.0001, when);
      gain.gain.exponentialRampToValueAtTime(Math.max(0.0002, level), when + attack);
      gain.gain.exponentialRampToValueAtTime(0.0001, when + duration);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(when);
      osc.stop(when + duration + 0.02);
    }}
    function stopPlayback() {{
      playing = false;
      cancelAnimationFrame(followId);
      if (audio) audio.close();
      audio = null;
      document.getElementById("play").textContent = "Play riff";
    }}
    function playRiff() {{
      if (!pianoNotes.length) return;
      stopPlayback();
      const ctx = new AudioContext();
      audio = ctx;
      playing = true;
      document.getElementById("play").textContent = "Stop";
      const origin = ctx.currentTime + 0.05;
      pianoNotes.forEach((note) => {{
        schedule(ctx, note, origin, note.pitch >= pack.hand_split ? 0.05 : 0.03, "triangle");
        if (note.pitch >= pack.hand_split) schedule(ctx, note, origin, 0.02, "sine");
      }});
      if (showBass) bassNotes.forEach((note) => schedule(ctx, note, origin, 0.09, "sine"));
      const item = study();
      const container = item.bars * 4 * 60 / item.bpm;
      const follow = () => {{
        if (!playing || !audio) return;
        if (audio.currentTime - origin < container) followId = requestAnimationFrame(follow);
        else stopPlayback();
      }};
      follow();
    }}
    function stepStudy(direction) {{
      const index = pack.studies.findIndex((item) => item.id === studyId);
      studyId = pack.studies[(index + direction + pack.studies.length) % pack.studies.length].id;
      loadStudy();
    }}
    pack.studies.forEach((item) => {{
      const button = document.createElement("button");
      button.type = "button";
      button.dataset.id = item.id;
      button.textContent = item.id.slice(1) + " " + item.title;
      button.addEventListener("click", () => {{ studyId = item.id; loadStudy(); }});
      rail.appendChild(button);
    }});
    document.getElementById("var-a").addEventListener("click", () => {{ variation = "a"; loadStudy(); }});
    document.getElementById("var-b").addEventListener("click", () => {{ variation = "b"; loadStudy(); }});
    document.getElementById("play").addEventListener("click", () => {{ if (playing) stopPlayback(); else playRiff(); }});
    document.getElementById("bass-toggle").addEventListener("click", () => {{
      showBass = !showBass;
      document.getElementById("bass-toggle").setAttribute("aria-pressed", showBass ? "true" : "false");
      if (pianoNotes.length) draw();
    }});
    window.addEventListener("keydown", (event) => {{
      const tag = document.activeElement && document.activeElement.tagName;
      if (tag === "INPUT" || tag === "TEXTAREA") return;
      if (event.code === "Space") {{ event.preventDefault(); if (playing) stopPlayback(); else playRiff(); }}
      else if (event.key === "j" || event.key === "J") stepStudy(-1);
      else if (event.key === "k" || event.key === "K") stepStudy(1);
    }});
    loadStudy();
  </script>
</body>
</html>
"""


def _media_html() -> str:
    return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>90s Piano House Riffs, stills</title>
  <style>
    :root { --bg:#1a1218; --paper:#f4efe6; --muted:#cbbec6; --line:rgba(244,239,230,.16); --magenta:#d23070; }
    * { box-sizing: border-box; }
    body { margin: 0; background: var(--bg); color: var(--paper); font-family: Georgia, "Iowan Old Style", serif; line-height: 1.45; }
    a { color: var(--magenta); }
    header, main { width: min(1120px, calc(100% - 2rem)); margin: 0 auto; }
    header { padding: 28px 0 8px; }
    h1 { font-weight: 500; font-size: clamp(2.2rem, 5vw, 4rem); line-height: .95; margin: 8px 0; }
    .kicker { font-family: ui-monospace, Menlo, Consolas, monospace; letter-spacing: .14em; text-transform: uppercase; color: var(--magenta); font-size: .75rem; }
    .hero, .shot, .play { margin: 0 0 28px; }
    img, video, audio { display: block; width: 100%; height: auto; background: #000; }
    figcaption { color: var(--muted); font-family: ui-monospace, Menlo, Consolas, monospace; font-size: .82rem; padding: 8px 0 0; }
    .gallery { display: grid; grid-template-columns: 1.1fr .7fr; gap: 18px; align-items: start; margin-bottom: 28px; }
    .play { border-top: 1px solid var(--line); padding-top: 22px; }
    @media (max-width: 800px) { .gallery { grid-template-columns: 1fr; } }
  </style>
</head>
<body>
  <header>
    <p class="kicker"><a href="index.html">90s Piano House Riffs</a></p>
    <h1>Stills, then the recording.</h1>
    <p>Each frame keeps its own shape. The film and the MP3 sit under the pictures.</p>
  </header>
  <main>
    <figure class="hero">
      <img src="art/hero.jpg" width="1280" height="720" alt="Illustration of a piano roll with taller bars for louder accents. Not a photograph of a studio or of performers.">
      <figcaption>art/hero.jpg · 1280 by 720</figcaption>
    </figure>
    <div class="gallery">
      <figure class="shot">
        <img src="art/square.jpg" width="1080" height="1080" alt="Square illustration of the accented piano roll.">
        <figcaption>art/square.jpg · 1080 by 1080</figcaption>
      </figure>
      <figure class="shot">
        <img src="social/instagram-Cursor/portrait.jpg" width="1080" height="1350" alt="Vertical crop of the piano-roll illustration.">
        <figcaption>portrait · 1080 by 1350</figcaption>
      </figure>
    </div>
    <div class="gallery">
      <figure class="shot">
        <img src="social/x-Cursor/card.jpg" width="1600" height="900" alt="Wide card of the piano-roll illustration.">
        <figcaption>x card · 1600 by 900</figcaption>
      </figure>
      <figure class="shot">
        <img src="film/poster.jpg" width="1280" height="720" alt="Film poster with the words preview, not master.">
        <figcaption>film/poster.jpg · disclosure on the picture</figcaption>
      </figure>
    </div>
    <section class="play">
      <p class="kicker">Recorded reading · study 01, all 16 bars</p>
      <audio controls preload="metadata" src="preview/preview.mp3"></audio>
      <p><a href="preview/preview.mp3">preview/preview.mp3</a></p>
      <video controls preload="metadata" poster="film/poster.jpg" width="1280" height="720">
        <source src="film/preview.mp4" type="video/mp4">
        <track kind="captions" src="film/preview.vtt" srclang="en" label="English" default>
      </video>
    </section>
  </main>
</body>
</html>
"""
