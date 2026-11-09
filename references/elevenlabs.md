# ElevenLabs and piano audio

Use this reference for first-time setup, speech generation, timing, and mixing. Checked against official documentation on 2026-11-08; recheck when an endpoint or account feature changes.

## First-time Windows setup

1. Sign in to [ElevenLabs API Keys](https://elevenlabs.io/app/developers/api-keys). In the app this is **Developers → API Keys**. Create a key named `Mathvid`, keep it restricted, and choose a credit limit suitable for your usage. Grant Text to Speech access. Grant Voices read access for the voice-list helper; Models read is needed only if querying available models. Do not enable unrelated write permissions. The key is shown in full only at creation. See [official key setup](https://elevenlabs.io/docs/help-center/technical/how-do-i-authorize-myself-using-an-api-key) and [key scoping](https://elevenlabs.io/docs/api-reference/authentication).
2. Browse the [Voice Library](https://elevenlabs.io/app/voice-library), listen to existing previews, and choose a clear English narrator. Save it to My Voices for convenience. Open the voice's three-dot menu and choose **Copy voice ID**. A voice ID can be shared in chat; the API key should be entered only into the local setup prompt. See [finding a voice ID](https://elevenlabs.io/docs/help-center/technical/how-do-i-find-the-voice-id-of-my-voices-via-the-website-and-api).
3. From this skill's directory, run `python scripts/elevenlabs.py configure --voice-id YOUR_VOICE_ID` in a local terminal. Paste the key into the hidden prompt **once**, then press Enter: no characters or asterisks appear while entering it. The helper rejects control characters or repeated copies instead of saving a malformed key. The Windows helper encrypts it with DPAPI for the current Windows user and saves it under `%LOCALAPPDATA%/Mathvid/elevenlabs.json`. Environment variables `ELEVENLABS_API_KEY` and `ELEVENLABS_VOICE_ID` override saved values. Do not put the key into source, commands, logs, or chat.
4. Run `python scripts/elevenlabs.py voices` to check authentication and list available voice IDs. This read operation does not synthesize speech. A successful voice listing verifies access to Voices, not permission or quota for synthesis.

Do not hardcode a public tutorial voice ID: availability varies by account. Setup is incomplete until a voice is selected and a deliberate short speech generation has succeeded. Do not generate paid test speech merely to validate the skill package.

## Speech and timing

Run `python scripts/elevenlabs.py speak --text-file work/narration.txt --output work/narration.mp3` after the script and mathematical reasoning are ready. This consumes the user's ElevenLabs quota. It writes MP3, character alignment JSON, and SRT captions. Review the actual pronunciation and captions before using them.

The helper uses `POST /v1/text-to-speech/{voice_id}/with-timestamps`, an `xi-api-key` header, and the documented `mp3_44100_128` output. The response contains `audio_base64`, `alignment`, and `normalized_alignment`. Alignment has `characters`, `character_start_times_seconds`, and `character_end_times_seconds`. Use these timing arrays only with their matching text; normalization can change numbers and punctuation. The documented default model is `eleven_multilingual_v2`; it does not support `language_code`. This is a compatible baseline, not a claim to be the newest model. See [speech with timing](https://elevenlabs.io/docs/api-reference/text-to-speech/convert-with-timestamps) and [models](https://elevenlabs.io/docs/overview/models).

Build the animation timeline from measured speech duration and aligned phrases. Leave brief pauses for a new equation and the final result. Avoid speeding up speech to force a dense proof into 60 seconds. Rewrite for clarity and regenerate only the affected material when practical. A successful HTTP response does not prove the words, mathematical pronunciation, or timing are correct.

## Piano and final review

Choose a calm section from the user-provided piano library. Use an explicit file path and inspect the selected excerpt. Prefer one track per reel; fade its start and ending. Start with the music roughly 18–24 dB below the narration's perceived level during speech, then adjust by listening. This is a mixing starting point, not a platform specification.

Run `python scripts/media.py mix --video work/silent.mp4 --voice work/narration.mp3 --music "FULL_MUSIC_PATH" --output outputs/mathvid-reel.mp4`. The helper uses FFmpeg and FFprobe from PATH. Match video and narration timing before mixing. Inspect any looping seam. Use narration-controlled ducking so piano recedes under speech.

Measure the final encoded mix for clipping and loudness, and listen through it at low volume on ordinary speakers. A practical target is approximately -16 LUFS integrated with true peaks below -1 dBTP, adjusted for intelligibility. These are project targets, not an Instagram guarantee. Normalizing the separate narration does not establish the final mix's loudness or true peak; music, ducking, summing, and encoding change the result. Check every spoken equation against the approved solution and on-screen symbols. Record any unreviewed listening or playback checks honestly.
