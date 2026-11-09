# Mathvid

A Codex skill for turning a maths question and its solution into an approximately 60-second English Instagram Reel, using [ManimGX](https://github.com/academa-labs/manimgx), ElevenLabs narration, and quiet piano music.

The mathematical level follows the question. Default output is 1080 × 1920 portrait at 30 fps, with burned-in captions and an SRT file. Visuals use black backgrounds, white mathematical typography, blue grids, and selective yellow highlights.

Each reel also includes a short, ready-to-post description outlining the problem, the verified answer, and a useful key idea when one can be drawn from the solution. It is delivered as `reel-description.txt` and in the handoff message.

## Use

Invoke `$mathvid` and provide:

```text
Question title: ...
Question: ...
Solution: ...
```

Mathvid coordinates four roles:

| Role | Responsibility |
| --- | --- |
| Coding | Write ManimGX scenes and fit animations to measured speech timing. |
| Scriptwriting | Check the supplied reasoning and use Humanizer when installed to write natural English narration. |
| Voiceover | Generate ElevenLabs speech, align captions, and mix piano below the narration. |
| Reviewer | Independently check the maths, spoken claims, motion, layout, captions, audio balance, and sync. |

The skill uses the available worker slots in stages. It flags or corrects faulty reasoning before synthesis and prioritizes a sound explanation over forcing a dense proof into exactly one minute.

## Install in Codex

Clone this repository into a new `mathvid` directory under your Codex skills folder. For the default Windows location:

```powershell
git clone https://github.com/zaidansr/mathvid.git "$env:USERPROFILE/.codex/skills/mathvid"
```

If you use a custom `CODEX_HOME`, install under its `skills/mathvid` directory instead. Preserve any existing Mathvid installation. The entry point is [SKILL.md](SKILL.md); [agents/openai.yaml](agents/openai.yaml) provides the display metadata.

## Configure tools and media

- **ManimGX:** Python 3.13 or 3.14 and a compatible graphics environment. Follow [renderer setup](references/manimgx.md). This is ManimGX, not Manim Community Edition or ManimGL.
- **FFmpeg and FFprobe:** required on PATH for the bundled audio mixing and media checks.
- **ElevenLabs:** select a voice and configure your own API key using [the setup guide](references/elevenlabs.md). Speech synthesis uses your provider quota.
- **Piano:** set `MATHVID_MUSIC_DIR` to your music folder. Audio files are not bundled.
- **Humanizer:** the narration workflow discovers an installed `humanizer` skill; see [scriptwriting](references/scriptwriting.md) for its role and fallback guidance.

From this repository's directory:

```powershell
python scripts/preflight.py
python scripts/elevenlabs.py configure
python scripts/elevenlabs.py voices
```

The Windows setup prompt hides the key: paste once and press Enter. It stores the key encrypted for your Windows user outside the repository. The `voices` command is a read-only authentication check; it does not generate speech. Other systems can supply `ELEVENLABS_API_KEY` and `ELEVENLABS_VOICE_ID` through their local environment.

## Contents and validation

[references/](references/) contains the production workflow and review criteria. [assets/portrait_smoke.py](assets/portrait_smoke.py) is a short renderer check, not a completed lesson. The three PNGs are user-supplied visual references; they are not generated lesson frames. Piano files, credentials, and finished videos are not included.

The helper scripts have passed local offline behavior checks, and a read-only ElevenLabs voice request has been verified. A complete narrated video has not yet been rendered and reviewed end to end. Follow [the review procedure](references/review.md) for each produced reel.
