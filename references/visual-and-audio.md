# Reference treatment and music library

Inspect these images as visual references, not as source mathematics for unrelated questions:

- [Coordinate grid](../assets/reference-grid.png): black canvas, thin muted-blue minor lines, stronger blue major lines, white axes and mathematical axis labels.
- [Equations](../assets/reference-equations.png): white serif maths, ample black space, yellow outline for a grouped expression, one enlarged result.
- [Diagram](../assets/reference-diagram.png): subtle grey construction lines, white symbols, yellow focus, blue secondary annotations. Break dense landscape arrangements into successive portrait beats.

Use genuine mathematical typesetting for equations and clean, readable text for narration captions. A useful starting palette is black `#000000`, off-white `#F5F5F5`, blue `#4AA3C6`, yellow `#F3E65A`, and muted grey `#888888`; these are approximations, not extracted brand colours. Keep semantic colours stable across beats.

At 1080 × 1920, start with roughly 90 px left padding, 150 px right padding, 180 px top padding and 300 px bottom padding for essential content. These are conservative design margins; inspect the actual composition at phone size. Use short captions, usually one or two lines. Avoid covering equations with captions or displaying redundant paragraphs. Split long equations across meaningful steps instead of shrinking them until illegible.

## User-supplied piano tracks

Set `MATHVID_MUSIC_DIR` to the folder containing your piano tracks. For example, in PowerShell, use `$env:MATHVID_MUSIC_DIR = 'C:\path\to\piano'` with your actual folder. Use literal paths because filenames may include square brackets and Unicode characters. Select a passage that is calm and has few sharp transients. These filenames are optional examples from a user-supplied collection; no audio files are included:

- `[background music] reflections - beautiful slow jazz piano for cinema 🎥 relaxing no copyright.mp3`
- `[Background Music] Shifting - Japanese Jazz Piano 🎹 Chill No Copyright Music.mp3`
- `[background music] stillness - soft piano for reflection & inspiration 🌙 relaxing no copyright (1).mp3`
- `[background music] stillness - soft piano for reflection & inspiration 🌙 relaxing no copyright.mp3`
- `Oak Studios Live Session #1 - Chill & Cinematic Piano Improvisation [no copyright background music].mp3`

The two stillness examples may duplicate each other; check before treating them as different choices. Keep music as external source files, not bundled copies. If the configured folder or requested track is unavailable, ask for a replacement folder or file. A filename saying “no copyright” is not independently verified licensing information; do not claim licensing was checked.

Use the mix starting levels and ducking procedure in [elevenlabs.md](elevenlabs.md). Use short fades and avoid audible looping seams. Those settings are a starting point, not an audibility guarantee. Verify speech during quiet syllables and the loudest piano passage on ordinary speakers and at low volume.
