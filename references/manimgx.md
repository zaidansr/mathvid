# ManimGX implementation

Use the installed `manimgx` skill when available, with Mathvid's portrait and audio choices taking precedence. The separate `manim-video` skill is useful for scene planning. Neither its generic `manim` CLI nor a ManimGL import selects this renderer.

## Environment

ManimGX currently requires Python 3.13 or 3.14. Windows renders through Direct3D 12. Its package includes typesetting, fonts, and video encoding; a separate LaTeX installation is unnecessary. Install into a project environment when producing a video, preserving any existing environment:

```powershell
py -3.13 -m venv .venv
.venv\Scripts\python.exe -m pip install manimgx
.venv\Scripts\manimgx.exe --version
```

Use the version and CLI actually installed; record that version in the production notes. These commands install the renderer, not this skill. See the [official quickstart](https://manimgx.academa.ai/user-guide/quickstart/) and [repository](https://github.com/academa-labs/manimgx).

## Portrait composition

Import `manimgx as m`. Set `m.config.pixel_width, m.config.pixel_height = 1080, 1920` and `m.config.frame_rate = 30` before constructing the scene. The short side is 8 scene units, so portrait has a frame approximately 8 wide and 14.22 high. Lay out the scene for portrait directly; do not crop a landscape composition. Keep room for captions and Reels controls. See [configuration](https://manimgx.academa.ai/reference/rendering/configuration/).

Copy `assets/portrait_smoke.py` into the job's `work/` folder for a three-second geometry/typesetting check. It is a renderer check, not a completed sample lesson. Commands assume an active environment with ManimGX on PATH:

```powershell
manimgx inspect work/portrait_smoke.py MathvidSmoke
manimgx render work/portrait_smoke.py MathvidSmoke -r 540x960 --fps 30 -o work/smoke.mp4
manimgx inspect work/scene.py MathvidScene
manimgx inspect work/scene.py MathvidScene -t 0.5,1.5,end
manimgx render work/scene.py MathvidScene -r 540x960 --fps 30 -o work/draft.mp4
manimgx render work/scene.py MathvidScene -r 1080x1920 --fps 30 --crf 18 -o work/silent.mp4
```

`inspect` samples play/wait endings or requested times. It can flag clipped objects, text collisions, and tiny labels; 3D layout checking is skipped. A clean report does not prove every frame is clean. Inspect transition midpoints and watch the rendered motion. `render` writes MP4, a storyboard, and subtitles when the scene has subcaptions. See [CLI reference](https://manimgx.academa.ai/reference/rendering/command-line/).

## Voice-led timing and assembly

Generate reviewed narration with `scripts/elevenlabs.py speak`; use the actual audio and character alignment to time scenes. Build a single complete narration track, or concatenate beat audio into a full-length stem with deliberate pauses and adjusted timestamps before mixing. The helper's SRT is an editable timing aid; manually review maths wording and breaks, then burn approved captions using scene text. Keep the sidecar SRT too. Neither the speech helper nor the mixing helper automatically burns external subtitles into the MP4.

Time advances through `self.play(..., run_time=seconds)` and `self.wait(seconds)`; adding objects does not advance it. Read alignment timestamps and place reveals just before their spoken references. Leave an end hold after the last words. Preserve the full narration, and change the scene timing if it runs long. The supplied mix helper rejects voice that outlasts the video.

For mixing, install a trusted FFmpeg distribution that provides both `ffmpeg` and `ffprobe` on PATH; this is Mathvid's post-production dependency, not a ManimGX render dependency. The helper validates the default 1080x1920 H.264 output; adapt that check when the user explicitly chooses another format. It normalizes the speech stem toward -16 LUFS, the selected piano segment toward -36 LUFS, then ducks piano further under speech. These are initial settings, not a guarantee of final loudness. It fades the music endpoints, copies final H.264 video, and encodes stereo AAC. Listen and adjust; review any music loop join. See [FFmpeg's filter reference](https://www.ffmpeg.org/ffmpeg-filters.html).

```powershell
python scripts/preflight.py
python scripts/media.py mix --video work/silent.mp4 --voice work/narration.mp3 --music (Join-Path $env:MATHVID_MUSIC_DIR 'TRACK.mp3') --output outputs/mathvid.mp4
ffmpeg -hide_banner -i outputs/mathvid.mp4 -af loudnorm=I=-16:TP=-1:LRA=7:print_format=json -f null -
ffprobe -v error -show_streams -show_format -of json outputs/mathvid.mp4
```

Set `MATHVID_MUSIC_DIR` to your music folder as described in [visual-and-audio.md](visual-and-audio.md), and replace `TRACK.mp3` with an exact existing supplied filename. Treat ffmpeg's `input_i` and `input_tp` from the loudnorm command as measurements of the finished audio. Inspect output dimensions, frame rate, duration, audio channels, and codecs. Recheck visuals and audio after any final encode.
