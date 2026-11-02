"""Original 90s piano-house riffs.

Tempos, lengths, and collections are fixed before the notes. Each piano file
holds both hands. Notes below C4 are the left hand. Notes from C4 up are the
right-hand hook. The bass reference is a separate file and is not core.
Offsets are 0. Nothing here is a reconstruction of a known sampled riff.
"""

from __future__ import annotations

from tools.midi_io import BAR_TICKS_4_4, PPQ, bpm_to_us, effective_bpm

GENERATOR_VERSION = "1.0.0"
PACK_ID = "90s-piano-house-riffs"
PACK_NAME = "90s Piano House Riffs"
BAR = BAR_TICKS_4_4
HAND_SPLIT = 60


class Part:
    def __init__(self, study, part_id, role, variation, core, channel, slug, mono, poly, lo, hi):
        self.study = study
        self.part_id = part_id
        self.role = role
        self.variation = variation
        self.core = core
        self.channel = channel
        self.file_slug = slug
        self.monophonic = mono
        self.max_poly = poly
        self.lo = lo
        self.hi = hi
        self.container_ticks = study["bars"] * BAR
        self.notes = []

    def add(self, start, duration, pitch, velocity, departure=False):
        end = start + duration
        if start < 0 or duration <= 0 or end > self.container_ticks:
            raise ValueError(f"{self.part_id} boundary {start}+{duration}")
        if not self.lo <= pitch <= self.hi:
            raise ValueError(f"{self.part_id} pitch {pitch}")
        if not 1 <= velocity <= 127:
            raise ValueError(f"{self.part_id} velocity {velocity}")
        active = 1
        for other in self.notes:
            o0 = other["performed_start"]
            o1 = o0 + other["duration"]
            if start < o1 and o0 < end:
                if other["pitch"] == pitch or self.monophonic:
                    raise ValueError(f"{self.part_id} overlap {pitch}@{start}")
                active += 1
        if active > self.max_poly:
            raise ValueError(f"{self.part_id} poly {active}")
        self.notes.append({
            "nominal_start": start, "offset": 0, "performed_start": start,
            "duration": duration, "pitch": pitch, "velocity": velocity,
            "channel": self.channel, "departure": departure,
        })

    def finish(self):
        ordered = sorted(self.notes, key=lambda n: (n["performed_start"], n["pitch"]))
        if self.core and len(ordered) < 8:
            raise ValueError(f"{self.part_id} too few notes")
        if not ordered:
            raise ValueError(f"{self.part_id} empty")
        for index, note in enumerate(ordered, 1):
            note["id"] = f"{self.part_id}.n{index:04d}"
        return {
            "id": self.part_id, "study_id": self.study["id"], "slug": self.study["slug"],
            "role": self.role, "variation": self.variation, "core": self.core,
            "channel": self.channel, "file_slug": self.file_slug,
            "path": f"midi/{self.study['slug']}/{self.file_slug}.mid",
            "monophonic": self.monophonic, "max_poly": self.max_poly,
            "container_ticks": self.container_ticks, "container_bars": self.study["bars"],
            "bpm": self.study["bpm"], "tempo_us": self.study["tempo_us"], "notes": ordered,
        }


def piano(study, variation):
    return Part(study, f"{study['id']}.riff.{variation}", "piano-riff", variation, True, 0, f"riff-{variation}", False, 6, 48, 84)


def bass(study, variation):
    return Part(study, f"{study['id']}.bass.{variation}", "bass-reference", variation, False, 1, f"bass-{variation}", True, 1, 28, 50)


def bar(n, ticks=0):
    return n * BAR + ticks


def accent(bar_index, ending=False):
    # Four-bar contour: soft, lift, push, peak. Endings sit above the peak.
    step = (72, 84, 96, 112)[bar_index % 4]
    return min(122, step + (8 if ending else 0))


def paint(part, rhythm, choose):
    for index in range(part.study["bars"]):
        for offset, duration, layer in rhythm(index):
            pitches = choose(index, layer)
            if not pitches:
                continue
            velocity = accent(index, ending=index >= part.study["bars"] - 2)
            for pitch, departure in pitches:
                part.add(bar(index) + offset, duration, pitch, velocity, departure=departure)


def tone(pitch, departure=False):
    return (pitch, departure)


def roots(part, plan, pocket):
    for start, length, pitch in plan:
        for index in range(start, start + length):
            for offset, duration, velocity in pocket:
                part.add(bar(index) + offset, duration, pitch, velocity)


def studies():
    common = {
        "meter": "4/4", "bar_ticks": BAR, "ppq": PPQ, "stochastic_draws": 0, "bars": 16,
        "hand_split": HAND_SPLIT,
    }
    rows = [
        {**common, "id": "s01", "slug": "s01-offbeat-ninth", "title": "Offbeat Ninth", "bpm": 122,
         "tonic": "A", "tonal_reference": "A", "collection_name": "A natural minor",
         "pitch_classes": [9, 11, 0, 2, 4, 5, 7], "departures": [], "seed": 12201,
         "harmonic_rhythm": "Four bars each: Am9, Dm9, Am9, Em7.",
         "changes": ["Am9", "Dm9", "Am9", "Em7"], "change_bars": [4, 4, 4, 4],
         "phrases": [
             {"name": "Hook", "start_bar": 0, "bars": 4},
             {"name": "Lift", "start_bar": 4, "bars": 4},
             {"name": "Break", "start_bar": 8, "bars": 4},
             {"name": "Cadence", "start_bar": 12, "bars": 4},
         ],
         "identity": "Offbeat ninth stabs for eight bars, a two-note break, then a longer Em7 cadence. Variation B moves the stabs onto the downbeat and drops the ninth.",
         "limitations": "Use bass A with riff A and bass B with riff B. The break is silence in the left hand, not a missing file.",
         "voicing": "Right hand is a close ninth. Left hand is a tenth-free shell under C4, and only on the first stab of even bars.",
         "layering": "One piano track. Split it at C4 if you want two sampler layers. The bass reference is a third layer.",
         "accent": "Velocity climbs 72, 84, 96, 112 across each four bars. The cadence adds 8."},
        {**common, "id": "s02", "slug": "s02-sixteen-cell", "title": "Sixteen Cell", "bpm": 126,
         "tonic": "D", "tonal_reference": "D", "collection_name": "D natural minor",
         "pitch_classes": [2, 4, 5, 7, 9, 10, 0],
         "departures": ["Variation B bar 15 uses C#4 (61) for one 16th, then returns to D."],
         "seed": 12602,
         "harmonic_rhythm": "Eight bars of Dm, four of Bb, four of Dm11.",
         "changes": ["Dm", "Bb", "Dm11"], "change_bars": [8, 4, 4],
         "phrases": [
             {"name": "Cell", "start_bar": 0, "bars": 4},
             {"name": "Answer", "start_bar": 4, "bars": 4},
             {"name": "Bb", "start_bar": 8, "bars": 4},
             {"name": "Ending", "start_bar": 12, "bars": 4},
         ],
         "identity": "A three-note 16th cell on the front of the bar, then the same cell on beat 3. The last two bars land on a downbeat. Variation B is a single-note answer and one flagged C#.",
         "limitations": "The C# is one 16th. It is not a new key.",
         "voicing": "Variation A is a three-note shell. Variation B is one note at a time until the last bar.",
         "layering": "No left-hand notes in this study. The lower layer is the bass reference only.",
         "accent": "The same four-bar climb. The downbeat ending is the loudest stab."},
        {**common, "id": "s03", "slug": "s03-downbeat-plate", "title": "Downbeat Plate", "bpm": 120,
         "tonic": "F", "tonal_reference": "F", "collection_name": "F natural minor",
         "pitch_classes": [5, 7, 8, 10, 0, 1, 3], "departures": [], "seed": 12003,
         "harmonic_rhythm": "Four bars each: Fm, Ab, Fm, Fm11.",
         "changes": ["Fm", "Ab", "Fm", "Fm11"], "change_bars": [4, 4, 4, 4],
         "phrases": [
             {"name": "Plate", "start_bar": 0, "bars": 4},
             {"name": "Ab", "start_bar": 4, "bars": 4},
             {"name": "Thin", "start_bar": 8, "bars": 4},
             {"name": "Hold", "start_bar": 12, "bars": 4},
         ],
         "identity": "A quarter-note plate on beat 1 and a short answer on the and of 2. Bars 13 to 16 are one held Fm11. Variation B starts every stab an eighth later and never holds.",
         "limitations": "The hold is the phrase ending. It is one chord, not a stuck note.",
         "voicing": "Three-note shells, then a four-note Fm11 with the left hand on Bb3.",
         "layering": "Left hand enters only on the plate and the held ending.",
         "accent": "The held ending uses the peak velocity for its whole duration."},
        {**common, "id": "s04", "slug": "s04-three-then-two", "title": "Three Then Two", "bpm": 128,
         "tonic": "G", "tonal_reference": "G", "collection_name": "G natural minor",
         "pitch_classes": [7, 9, 10, 0, 2, 3, 5],
         "departures": ["Variation B bar 15 beat 4 is F#4 (66), a step below G. It is one 16th."],
         "seed": 12804,
         "harmonic_rhythm": "Four bars each: Gm, Bb, Gm, D.",
         "changes": ["Gm", "Bb", "Gm", "D"], "change_bars": [4, 4, 4, 4],
         "phrases": [
             {"name": "Three", "start_bar": 0, "bars": 4},
             {"name": "Two", "start_bar": 4, "bars": 4},
             {"name": "Swap", "start_bar": 8, "bars": 4},
             {"name": "Turn", "start_bar": 12, "bars": 4},
         ],
         "identity": "Even bars are three 16ths plus two more after a rest. Odd bars move that group onto beat 2. Variation B delays every attack by one 16th and ends on F#.",
         "limitations": "F# is outside G natural minor and is flagged. The rest of the bar stays in the set.",
         "voicing": "Triads. The left hand doubles the root an octave down only on beat 1 of even bars in variation A.",
         "layering": "Root doubling is the left hand. It is not the bass reference.",
         "accent": "The two-note group is louder than the three-note group because it falls later in the bar's contour."},
        {**common, "id": "s05", "slug": "s05-late-answer", "title": "Late Answer", "bpm": 124,
         "tonic": "C", "tonal_reference": "C", "collection_name": "C natural minor",
         "pitch_classes": [0, 2, 3, 5, 7, 8, 10],
         "departures": ["Variation B bar 15 uses E4 (64) under the final C minor stab. The E is flagged."],
         "seed": 12405,
         "harmonic_rhythm": "Eight bars of Cm, four of Ab, four of Cm.",
         "changes": ["Cm", "Ab", "Cm"], "change_bars": [8, 4, 4],
         "phrases": [
             {"name": "Late", "start_bar": 0, "bars": 4},
             {"name": "Still late", "start_bar": 4, "bars": 4},
             {"name": "Ab", "start_bar": 8, "bars": 4},
             {"name": "Arrive", "start_bar": 12, "bars": 4},
         ],
         "identity": "The first eight bars wait until beat 2. The last eight bars push an eighth early and add the ninth. Variation B anticipates by a 16th from the first bar and brightens the last stab with E.",
         "limitations": "The early notes in variation B stay inside the bar. Nothing starts before tick 0.",
         "voicing": "Cm shell, then Ab, then Cm add 9. Left hand on the second half only.",
         "layering": "The ninth is a right-hand note. The bass does not play it.",
         "accent": "The answer half is marked louder than the late half."},
        {**common, "id": "s06", "slug": "s06-dotted-stab", "title": "Dotted Stab", "bpm": 118,
         "tonic": "E", "tonal_reference": "E", "collection_name": "E natural minor",
         "pitch_classes": [4, 6, 7, 9, 11, 0, 2], "departures": [], "seed": 11806,
         "harmonic_rhythm": "Four bars each: Em, D, Em, B.",
         "changes": ["Em", "D", "Em", "B"], "change_bars": [4, 4, 4, 4],
         "phrases": [
             {"name": "Dot", "start_bar": 0, "bars": 4},
             {"name": "D", "start_bar": 4, "bars": 4},
             {"name": "Return", "start_bar": 8, "bars": 4},
             {"name": "B", "start_bar": 12, "bars": 4},
         ],
         "identity": "A dotted eighth chord and a 16th answer, twice per bar. The last two bars stretch both into quarters. Variation B replaces the dot with even eighths and a single-note tail.",
         "limitations": "No swing offset is written. The dot is the duration, not a feel instruction.",
         "voicing": "Em, D, Em, then B as D F# A. All of those pitch classes are inside E natural minor.",
         "layering": "Left hand plays the dotted chord only. The 16th answer is right hand.",
         "accent": "The 16th answer is the louder of the pair because it lands on the later step of the contour."},
        {**common, "id": "s07", "slug": "s07-one-stab", "title": "One Stab", "bpm": 130,
         "tonic": "F", "tonal_reference": "F", "collection_name": "F Dorian",
         "pitch_classes": [5, 7, 8, 10, 0, 2, 3], "departures": [], "seed": 13007,
         "harmonic_rhythm": "Four bars each: Fm6, Ab, Gm, Bb.",
         "changes": ["Fm6", "Ab", "Gm", "Bb"], "change_bars": [4, 4, 4, 4],
         "phrases": [
             {"name": "Space", "start_bar": 0, "bars": 4},
             {"name": "Ab", "start_bar": 4, "bars": 4},
             {"name": "Gm", "start_bar": 8, "bars": 4},
             {"name": "Double", "start_bar": 12, "bars": 4},
         ],
         "identity": "One stab on beat 4 for twelve bars. The ending adds a downbeat answer so the phrase closes. Variation B moves the stab to the and of 2 and fills the last bar with three chords.",
         "limitations": "The empty beats are the hook. Do not quantize them into a busier riff.",
         "voicing": "Four-note Fm6 (F Ab C D). Later chords drop to three notes. The last variation B chord adds the high F.",
         "layering": "Beat-4 stabs are right hand only. Variation B's last bar adds a left-hand shell.",
         "accent": "Because there is one stab, the four-bar velocity climb is the whole contour."},
        {**common, "id": "s08", "slug": "s08-run-and-hold", "title": "Run and Hold", "bpm": 125,
         "tonic": "Bb", "tonal_reference": "Bb", "collection_name": "Bb natural minor",
         "pitch_classes": [10, 0, 1, 3, 5, 6, 8], "departures": [], "seed": 12508,
         "harmonic_rhythm": "Two bars of a single-note run, then chords on Bbm and Gb, then a two-bar hold.",
         "changes": ["Run", "Bbm", "Gb", "Hold"], "change_bars": [2, 6, 6, 2],
         "phrases": [
             {"name": "Run", "start_bar": 0, "bars": 2},
             {"name": "Bbm", "start_bar": 2, "bars": 6},
             {"name": "Gb", "start_bar": 8, "bars": 6},
             {"name": "Hold", "start_bar": 14, "bars": 2},
         ],
         "identity": "Sixteen 16ths of a Bb minor line, then offbeat chords, then one chord held for two bars. Variation B starts with the chords and puts the run at the end.",
         "limitations": "The run is monophonic inside the piano file. It is still the piano riff, not the bass.",
         "voicing": "The run is Bb C Db Eb F Gb. The chords are Bbm and Gb. The hold is Bb Db Eb Gb.",
         "layering": "The run sits above C4. Left hand enters with the Bbm chords, under C4.",
         "accent": "The run stays at the soft step. The hold is the peak."},
    ]
    for row in rows:
        if not 118 <= row["bpm"] <= 130:
            raise ValueError(row["bpm"])
        if sum(row["change_bars"]) != row["bars"] or len(row["change_bars"]) != len(row["changes"]):
            raise ValueError(row["id"])
        if sum(item["bars"] for item in row["phrases"]) != row["bars"]:
            raise ValueError(row["id"] + " phrases")
        row["tempo_us"] = bpm_to_us(row["bpm"])
        row["effective_bpm"] = effective_bpm(row["tempo_us"])
    return rows


def _pair(study):
    return piano(study, "a"), piano(study, "b"), bass(study, "a"), bass(study, "b")


def _s01(study):
    a, b, ba, bb = _pair(study)

    def choose_a(index, layer):
        if index < 4:
            rh, lh = [tone(72), tone(76), tone(79), tone(83)], [tone(52), tone(55)]
        elif index < 8:
            rh, lh = [tone(65), tone(69), tone(72), tone(76)], [tone(53), tone(57)]
        elif index < 12:
            rh, lh = [tone(76), tone(79)], []
        else:
            rh, lh = [tone(64), tone(67), tone(71)], [tone(52), tone(59)]
        if layer == "both":
            return rh + lh
        return rh

    def rhythm_a(index):
        if 8 <= index <= 11:
            return [(1440, 240, "rh"), (3360, 240, "rh")]
        if index >= 14:
            return [(480, 960, "both"), (2400, PPQ + 480, "rh")]
        if index % 2 == 0:
            return [(480, 240, "both"), (1440, 240, "rh"), (2400, 240, "rh"), (3360, 240, "rh")]
        return [(480, 240, "rh"), (1440, 240, "rh"), (2400, 240, "rh"), (3360, 240, "rh")]

    def choose_b(index, layer):
        if index < 8:
            rh, lh = [tone(72), tone(76), tone(79)], [tone(48), tone(55)]
        elif index < 12:
            rh, lh = [tone(69), tone(72)], []
        else:
            rh, lh = [tone(67), tone(71), tone(74)], [tone(55), tone(59)]
        if layer == "both":
            return rh + lh
        return rh

    def rhythm_b(index):
        if index >= 14:
            return [(0, PPQ * 2, "both"), (2880, 480, "rh")]
        if 8 <= index <= 11:
            return [(0, 480, "rh")]
        return [(0, 240, "both"), (960, 240, "rh"), (1920, 480, "rh")]

    paint(a, rhythm_a, choose_a)
    paint(b, rhythm_b, choose_b)
    roots(ba, [(0, 4, 33), (4, 4, 38), (8, 4, 33), (12, 4, 40)], [(0, PPQ, 104), (PPQ * 2, PPQ, 88)])
    roots(bb, [(0, 4, 45), (4, 4, 41), (8, 4, 45), (12, 4, 40)], [(480, 480, 100), (1440, 480, 84)])
    return [a, b, ba, bb]


def _s02(study):
    a, b, ba, bb = _pair(study)

    def choose_a(index, layer):
        if index < 8:
            return [tone(74), tone(77), tone(81)]
        if index < 12:
            return [tone(70), tone(74), tone(77)]
        return [tone(72), tone(77), tone(81)]

    def rhythm_a(index):
        if index >= 14:
            return [(0, PPQ * 2, "rh"), (2880, 480, "rh")]
        if index % 4 < 2:
            return [(240, 240, "rh"), (480, 240, "rh"), (960, 480, "rh")]
        return [(2160, 240, "rh"), (2400, 240, "rh"), (2880, 480, "rh")]

    def choose_b(index, layer):
        line = [74, 77, 81, 77, 72, 74, 70, 72]
        if index == 15:
            return [tone(61, True), tone(62)]
        return [tone(line[index % 8])]

    def rhythm_b(index):
        if index == 15:
            return [(0, 240, "rh"), (240, PPQ, "rh")]
        if index >= 12:
            return [(0, 480, "rh"), (1440, 480, "rh"), (2880, 480, "rh")]
        return [(480, 240, "rh"), (1440, 240, "rh"), (2400, 480, "rh")]

    paint(a, rhythm_a, choose_a)
    paint(b, rhythm_b, choose_b)
    roots(ba, [(0, 8, 38), (8, 4, 34), (12, 4, 38)], [(0, PPQ, 102), (PPQ * 2, 480, 86)])
    roots(bb, [(0, 8, 26 + 12, ), (8, 4, 46), (12, 4, 38)], [(480, PPQ, 98)])
    return [a, b, ba, bb]


def _s03(study):
    a, b, ba, bb = _pair(study)

    def choose_a(index, layer):
        if index >= 12:
            rh, lh = [tone(65), tone(68), tone(70), tone(75)], [tone(58)]
        elif index < 4 or 8 <= index < 12:
            rh, lh = [tone(65), tone(68), tone(72)], [tone(53), tone(56)]
        else:
            rh, lh = [tone(68), tone(72), tone(75)], [tone(56), tone(60)]
        if index >= 12 and index > 12:
            return []
        if layer == "both":
            return rh + lh
        if layer == "thin":
            return rh[:2]
        return rh

    def rhythm_a(index):
        if index == 12:
            return [(0, 4 * BAR, "both")]
        if index > 12:
            return []
        if 8 <= index <= 11:
            return [(0, 480, "thin")]
        return [(0, PPQ, "both"), (1440, 240, "rh")]

    def choose_b(index, layer):
        if index < 4 or 8 <= index < 12:
            return [tone(60), tone(65), tone(68)]
        if index < 8:
            return [tone(63), tone(68), tone(72)]
        return [tone(65), tone(68), tone(72), tone(75)]

    def rhythm_b(index):
        if index >= 14:
            return [(480, PPQ, "rh"), (2400, 480, "rh")]
        return [(480, 480, "rh"), (1920, 240, "rh")]

    paint(a, rhythm_a, choose_a)
    paint(b, rhythm_b, choose_b)
    roots(ba, [(0, 4, 41), (4, 4, 44), (8, 4, 41), (12, 4, 41)], [(0, PPQ * 2, 100)])
    roots(bb, [(0, 4, 29), (4, 4, 32), (8, 4, 29), (12, 4, 41)], [(480, PPQ, 96), (PPQ * 2 + 480, 480, 80)])
    return [a, b, ba, bb]


def _s04(study):
    a, b, ba, bb = _pair(study)

    def choose_a(index, layer):
        if index < 4 or 8 <= index < 12:
            rh, lh = [tone(67), tone(70), tone(74)], [tone(55)]
        elif index < 8:
            rh, lh = [tone(70), tone(74), tone(77)], [tone(58)]
        else:
            rh, lh = [tone(62), tone(65), tone(69)], [tone(50)]
        if layer == "both":
            return rh + lh
        return rh

    def rhythm_a(index):
        if index % 2 == 0:
            return [(0, 240, "both"), (240, 240, "rh"), (480, 240, "rh"), (1440, 240, "rh"), (1680, 240, "rh")]
        return [(960, 240, "rh"), (1200, 240, "rh"), (1440, 240, "rh"), (2400, 240, "rh"), (2640, 240, "rh")]

    def choose_b(index, layer):
        if index == 15 and layer == "dep":
            return [tone(66, True)]
        if index == 15:
            return [tone(67), tone(70)]
        if index < 8:
            return [tone(70), tone(74), tone(79)]
        return [tone(67), tone(72), tone(75)]

    def rhythm_b(index):
        if index == 15:
            return [(240, 240, "rh"), (480, 240, "rh"), (3360, 240, "dep")]
        if index % 2 == 0:
            return [(240, 240, "rh"), (480, 240, "rh"), (720, 240, "rh"), (1680, 240, "rh"), (1920, 240, "rh")]
        return [(1200, 240, "rh"), (1440, 240, "rh"), (1680, 240, "rh"), (2640, 240, "rh"), (2880, 240, "rh")]

    paint(a, rhythm_a, choose_a)
    paint(b, rhythm_b, choose_b)
    roots(ba, [(0, 4, 43), (4, 4, 46), (8, 4, 43), (12, 4, 38)], [(0, 480, 104), (1440, 480, 90)])
    roots(bb, [(0, 4, 31), (4, 4, 34), (8, 4, 31), (12, 4, 38)], [(PPQ, PPQ, 98)])
    return [a, b, ba, bb]


def _s05(study):
    a, b, ba, bb = _pair(study)

    def choose_a(index, layer):
        if index < 8:
            rh, lh = [tone(63), tone(67), tone(70)], []
        elif index < 12:
            rh, lh = [tone(68), tone(72), tone(75)], [tone(56)]
        else:
            rh, lh = [tone(60), tone(65), tone(67), tone(72)], [tone(48), tone(55)]
        if layer == "both":
            return rh + lh
        return rh

    def rhythm_a(index):
        if index < 8:
            return [(960, 480, "rh"), (2400, 240, "rh")]
        if index >= 14:
            return [(720, PPQ, "both"), (2400, 960, "rh")]
        return [(720, 240, "both"), (1680, 480, "rh"), (3120, 240, "rh")]

    def choose_b(index, layer):
        if index == 15:
            return [tone(60), tone(63), tone(67), tone(64, True)]
        if index < 8:
            return [tone(67), tone(70), tone(72)]
        if index < 12:
            return [tone(68), tone(72), tone(75)]
        return [tone(63), tone(67), tone(72)]

    def rhythm_b(index):
        if index == 15:
            return [(0, PPQ * 2, "rh")]
        return [(720, 240, "rh"), (1680, 240, "rh"), (2640, 480, "rh")]

    paint(a, rhythm_a, choose_a)
    paint(b, rhythm_b, choose_b)
    roots(ba, [(0, 8, 36), (8, 4, 44), (12, 4, 36)], [(0, PPQ, 100), (PPQ * 2, PPQ, 86)])
    roots(bb, [(0, 8, 48), (8, 4, 44), (12, 4, 36)], [(240, 480, 96), (1680, 480, 82)])
    return [a, b, ba, bb]


def _s06(study):
    a, b, ba, bb = _pair(study)

    def choose_a(index, layer):
        if index < 4 or 8 <= index < 12:
            rh, lh = [tone(64), tone(67), tone(71)], [tone(52), tone(55)]
        elif index < 8:
            rh, lh = [tone(62), tone(66), tone(69)], [tone(50), tone(54)]
        else:
            rh, lh = [tone(59), tone(66), tone(71)], [tone(50), tone(54)]
        if layer == "both":
            return rh + lh
        return rh

    def rhythm_a(index):
        if index >= 14:
            return [(0, PPQ + 480, "both"), (1920, PPQ + 480, "rh")]
        return [(0, 720, "both"), (720, 240, "rh"), (1920, 720, "both"), (2640, 240, "rh")]

    def choose_b(index, layer):
        line = [76, 74, 71, 67, 66, 64, 62, 64]
        if index >= 14:
            return [tone(64), tone(71), tone(76)]
        return [tone(line[index % 8])]

    def rhythm_b(index):
        if index >= 14:
            return [(0, PPQ * 2, "rh"), (2880, PPQ, "rh")]
        return [(0, 480, "rh"), (480, 480, "rh"), (1920, 480, "rh"), (2400, 480, "rh")]

    paint(a, rhythm_a, choose_a)
    paint(b, rhythm_b, choose_b)
    roots(ba, [(0, 4, 40), (4, 4, 38), (8, 4, 40), (12, 4, 35)], [(0, 720, 104), (1920, 720, 90)])
    roots(bb, [(0, 4, 40), (4, 4, 38), (8, 4, 40), (12, 4, 47)], [(480, PPQ, 96)])
    return [a, b, ba, bb]


def _s07(study):
    a, b, ba, bb = _pair(study)

    def choose_a(index, layer):
        if index < 4:
            return [tone(65), tone(68), tone(72), tone(74)]
        if index < 8:
            return [tone(68), tone(72), tone(75)]
        if index < 12:
            return [tone(67), tone(70), tone(74)]
        return [tone(70), tone(74), tone(77)]

    def rhythm_a(index):
        if index >= 12:
            return [(0, 480, "rh"), (2880, PPQ, "rh")]
        return [(2880, 720, "rh")]

    def choose_b(index, layer):
        if index >= 14:
            return [tone(65), tone(68), tone(72), tone(77)] + ([tone(53), tone(56)] if layer == "both" else [])
        if index < 4:
            return [tone(65), tone(72), tone(77)]
        if index < 8:
            return [tone(68), tone(72), tone(80)]
        if index < 12:
            return [tone(67), tone(74), tone(79)]
        return [tone(70), tone(74), tone(82)]

    def rhythm_b(index):
        if index >= 14:
            return [(480, 480, "both"), (1440, 480, "rh"), (2880, 720, "rh")]
        return [(1440, 480, "rh")]

    paint(a, rhythm_a, choose_a)
    paint(b, rhythm_b, choose_b)
    roots(ba, [(0, 4, 41), (4, 4, 44), (8, 4, 43), (12, 4, 46)], [(2880, 720, 108)])
    roots(bb, [(0, 4, 29), (4, 4, 32), (8, 4, 31), (12, 4, 34)], [(1440, PPQ, 100)])
    return [a, b, ba, bb]


def _s08(study):
    a, b, ba, bb = _pair(study)
    run = [70, 72, 73, 75, 77, 78]

    def choose_a(index, layer):
        if index < 2:
            return [tone(run[(index * 16 + layer) % 6])] if isinstance(layer, int) else []
        if index >= 14:
            return [tone(70), tone(73), tone(75), tone(78)]
        if index < 8:
            rh, lh = [tone(70), tone(73), tone(77)], [tone(58), tone(51)]
        else:
            rh, lh = [tone(68), tone(73), tone(75)], [tone(56), tone(49)]
        if layer == "both":
            return rh + lh
        return rh

    def rhythm_a(index):
        if index < 2:
            return [(step * 240, 240, step) for step in range(16)]
        if index == 14:
            return [(0, 2 * BAR, "both")]
        if index > 14:
            return []
        return [(480, 240, "both"), (1920, 240, "rh")]

    def choose_b(index, layer):
        if index >= 14:
            return [tone(run[(index * 8 + (layer if isinstance(layer, int) else 0)) % 6])]
        if index < 8:
            return [tone(70), tone(73), tone(77)]
        return [tone(66), tone(70), tone(73)]

    def rhythm_b(index):
        if index >= 14:
            return [(step * 240, 240, step % 6) for step in range(8)]
        if index % 2 == 0:
            return [(0, 480, "rh"), (1440, 240, "rh"), (2880, 240, "rh")]
        return [(960, 480, "rh"), (2400, 480, "rh")]

    paint(a, rhythm_a, choose_a)
    paint(b, rhythm_b, choose_b)
    roots(ba, [(0, 2, 34), (2, 6, 34), (8, 6, 30), (14, 2, 34)], [(0, PPQ, 100), (PPQ * 2, 480, 84)])
    roots(bb, [(0, 8, 46), (8, 6, 42), (14, 2, 34)], [(480, 480, 96), (1920, 480, 82)])
    return [a, b, ba, bb]


BUILDERS = {f"s0{i}": fn for i, fn in enumerate([_s01, _s02, _s03, _s04, _s05, _s06, _s07, _s08], 1)}


def _sig(notes):
    return tuple((note["performed_start"], note["pitch"], note["duration"]) for note in notes)


def assert_collections(catalog_studies, parts):
    allowed = {study["id"]: set(study["pitch_classes"]) for study in catalog_studies}
    for part in parts:
        pool = allowed[part["study_id"]]
        for note in part["notes"]:
            inside = (note["pitch"] % 12) in pool
            if note["departure"] and inside:
                raise ValueError(f"{part['id']} departure {note['pitch']} is inside the collection")
            if not note["departure"] and not inside:
                raise ValueError(f"{part['id']} note {note['pitch']} left the collection")


def assert_identities(parts):
    riffs = [part for part in parts if part["role"] == "piano-riff"]
    by = {}
    for part in riffs:
        by.setdefault(part["study_id"], {})[part["variation"]] = part
    rhythms = {}
    report = []
    for study_id, vars_ in by.items():
        if _sig(vars_["a"]["notes"]) == _sig(vars_["b"]["notes"]):
            raise ValueError(f"{study_id} variations match")
        rhythm = tuple(note["performed_start"] for note in vars_["a"]["notes"])
        if rhythm in rhythms:
            raise ValueError(f"{study_id} rhythm repeats {rhythms[rhythm]}")
        rhythms[rhythm] = study_id
        report.append({"study_id": study_id, "a": len(vars_["a"]["notes"]), "b": len(vars_["b"]["notes"])})
    return {"studies": report, "method": "riff variations differ; variation A attack times are not shared"}


def compose():
    catalog_studies = studies()
    parts = []
    for study in catalog_studies:
        for part in BUILDERS[study["id"]](study):
            parts.append(part.finish())
    assert_collections(catalog_studies, parts)
    identity = assert_identities(parts)
    core = [part for part in parts if part["core"]]
    refs = [part for part in parts if not part["core"]]
    if len(core) != 16 or len(refs) != 16:
        raise ValueError((len(core), len(refs)))
    arrangement = {
        "id": "arrangement-preview-s01a",
        "path": "midi/arrangement.mid",
        "format": 1,
        "container_ticks": 16 * BAR,
        "bpm": 122,
        "tempo_us": bpm_to_us(122),
        "meter": "4/4",
        "description": "Study 01 variation A riff with bass reference A. The bass is not inside the piano file.",
        "tracks": [
            {"name": "Conductor", "source_part": None, "channel": None},
            {"name": "Piano Riff", "source_part": "s01.riff.a", "channel": 0},
            {"name": "Bass Reference", "source_part": "s01.bass.a", "channel": 1},
        ],
    }
    catalog = {
        "pack_id": PACK_ID, "pack_name": PACK_NAME,
        "catalog_version": GENERATOR_VERSION, "generator_version": GENERATOR_VERSION,
        "ppq": PPQ, "meter": {"numerator": 4, "denominator": 4, "bar_ticks": BAR},
        "pitched_range": [28, 84], "c4": 60, "hand_split": HAND_SPLIT,
        "note_policy": "note-only MIDI. Swing, chorus, and sampler layers are not encoded.",
        "microtiming": "offset is 0; performed_start = nominal_start",
        "stochastic_draws": 0,
        "seed_meaning": "Seeds identify studies. Nothing is random.",
        "core_part_count": len(core), "reference_part_count": len(refs),
        "range_statement": "Piano riffs use MIDI 48 to 84, at most six notes at once. Notes below 60 are the left hand. Notes from 60 up are the right hand. Bass references are monophonic, MIDI 28 to 50, and are not part of the core count.",
        "studies": [{key: study[key] for key in (
            "id", "slug", "title", "bpm", "tempo_us", "effective_bpm", "bars", "meter", "bar_ticks",
            "tonic", "tonal_reference", "collection_name", "pitch_classes", "departures", "seed",
            "harmonic_rhythm", "changes", "change_bars", "phrases", "identity", "limitations",
            "voicing", "layering", "accent", "hand_split", "stochastic_draws",
        )} for study in catalog_studies],
        "parts": [{
            "id": part["id"], "study_id": part["study_id"], "role": part["role"], "variation": part["variation"],
            "core": part["core"], "channel": part["channel"], "path": part["path"], "notes": len(part["notes"]),
            "container_bars": part["container_bars"], "bpm": part["bpm"], "monophonic": part["monophonic"],
        } for part in parts],
        "arrangement": arrangement,
        "preview_part_ids": ["s01.riff.a", "s01.bass.a"],
        "stack_warning": "Use either the combined arrangement or the separate parts. Do not stack the part files on top of the combined file.",
    }
    score = {
        "pack_id": PACK_ID, "generator_version": GENERATOR_VERSION, "ppq": PPQ,
        "parts": parts, "arrangement": arrangement, "identity_check": identity,
    }
    return {"catalog": catalog, "score": score}
