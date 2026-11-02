# 90s Piano House Riffs

Original note-only MIDI studies of syncopated piano hooks. Eight studies, two variations of the piano riff. Each riff is 16 bars: a hook, an answer, a break or lift, and a phrase ending. Bass references are cataloged separately and are not part of the core count. They are not merged into the piano files.

This repository is the pack. The GitHub repository is https://github.com/mizcausevic-dev/90s-piano-house-riffs and it is public. The catalog page is https://mizcausevic-dev.github.io/90s-piano-house-riffs/ .

## What you can open

- `index.html` is the file catalog. The roll is drawn from the MIDI bytes, split at C4.
- `media.html` is the stills page. The film sits under the pictures.
- `midi/arrangement.mid` is a Format 1 preview arrangement of study 01, variation A: piano riff and bass reference.
- Individual Format 0 parts live under `midi/`.
- `midi/validation-Cursor.json` is the report from reopening those exact bytes.
- `preview/preview.mp3` is the primary music preview. It is 31.475 seconds in the encoded file. preview, not a master.
- `film/preview.mp4` and `film/preview.vtt` are the film. On-picture and caption text is `preview, not master`.
- `art/hero.jpg` is a 1280x720 illustration. `art/square.jpg` is 1080x1080. Neither is a photograph.

Use either the combined arrangement or the separate parts. Do not stack the part files on top of the combined file.

## Studies

- s01 Offbeat Ninth: 122 BPM, 16 bars, A natural minor, tonic reference A.
- s02 Sixteen Cell: 126 BPM, 16 bars, D natural minor, tonic reference D.
- s03 Downbeat Plate: 120 BPM, 16 bars, F natural minor, tonic reference F.
- s04 Three Then Two: 128 BPM, 16 bars, G natural minor, tonic reference G.
- s05 Late Answer: 124 BPM, 16 bars, C natural minor, tonic reference C.
- s06 Dotted Stab: 118 BPM, 16 bars, E natural minor, tonic reference E.
- s07 One Stab: 130 BPM, 16 bars, F Dorian, tonic reference F.
- s08 Run and Hold: 125 BPM, 16 bars, Bb natural minor, tonic reference Bb.

Core files: 16. Reference files: 16.

Piano riffs use MIDI 48 to 84, at most six notes at once. Notes below 60 are the left hand. Notes from 60 up are the right hand. Bass references are monophonic, MIDI 28 to 50, and are not part of the core count. C4 is 60. PPQ is 960. Meter is 4/4. Offsets are 0. Seeds identify studies and are not random draws. Generator 1.0.0. Harmonic rhythm, hand split, layering, and accent contour are written on each study.

## Preview path

The preview renders the canonical notes for `s01.riff.a` and `s01.bass.a` with `simple-synth-1.0.0`. Tempo authority is the encoded microsecond value in the MIDI, 491803 us per quarter note. Sample positions use `floor(seconds * 44100 + 0.5)` from tick 0. Intervals are not summed. Sample-exact repeating loops at an arbitrary BPM are not promised.

The synth mapping is a sine plus a quiet triangle for the piano and a sine for the bass. No program changes are encoded. A conventional GM player will normally use its default piano program for pitched channels unless configured otherwise; compatible GM channel 10 percussion is treated separately. Player behavior may vary. The mapping is not encoded in the MIDI.

Encoded MP3 settings: libmp3lame, 192 kbps. Film audio is AAC at 160 kbps re-encoded from that MP3, so the decoded film audio is not byte-identical to the MP3. Film duration probe: 31.458 seconds. MP3 container probe 31.475 seconds. MP4 probe 31.458 seconds. The film ends on a video frame, so it is slightly shorter than the MP3 container. The music is the same preview, not a different excerpt. The picture is a still illustration with rasterized disclosure text. DejaVu Sans Bold from the build machine supplies the glyphs. The font file is not in this pack.

No human listening audition was performed for this build. A sample peak is recorded in the preview manifest. It is not LUFS and it is not a true peak.

## Build

From the repository root, with Python 3.11+ and ffmpeg (libmp3lame, aac, libx264):

```bash
python3 tools/build_pack.py
python3 -m http.server 41773
```

The page is static. It is served with Python's HTTP server so the MIDI and media keep working relative paths. There is no application server and no package install. Standard library only.

`build/` holds the intermediate WAV, the procedural PPM, and the film plate. Those files are gitignored. The delivered audio is the MP3.

## Checks the validator actually runs

File existence, parse, PPQ, tempo, 4/4, end-of-track boundary, note pairing, ranges, monophonic bass, piano polyphony cap of six, note-off before note-on at a shared tick, absence of program changes and other channel messages, departure flags against the declared pitch-class set, agreement with the canonical score, and agreement between `arrangement.mid` and the two source files. A negative overlap fixture is written outside the pack and must be rejected.

## Drafts and publication

Social captions, the X post, and the Medium article are drafts. They are not access controls. If this repository is public, the drafts are public. Do not treat them as posted to Instagram, X, or Medium.

Prepared repository description: Original note-only MIDI studies of 90s piano house riffs, with matched validation and a simple-synth preview.

Prepared topics: midi, house, piano, music-production, composition, general-midi, study-pack.

No release tag was created. `index.html` keeps its name because players and links depend on it. This page is the file catalog the pack requires.

## Limitations

Variation compatibility is per study and is written on the page. Variation A and variation B of a study are alternatives. Pair bass A with riff A, and bass B with riff B. The arrangement is only study 01. Stacking it with the part files doubles those notes. These riffs are original. They are not reconstructions of known sampled hooks.
