"""Mathvid's explicit ElevenLabs setup, voice listing, and timed speech helper.

Uses only Python's standard library. No network request occurs during configure.
"""
from __future__ import annotations

import argparse
import base64
import ctypes
from ctypes import wintypes
import getpass
import json
import math
import os
from pathlib import Path
import re
import sys
import textwrap
import warnings
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, quote
from urllib.request import Request, urlopen


def config_path() -> Path:
    base = os.environ.get("LOCALAPPDATA")
    if not base:
        raise ValueError("Windows LOCALAPPDATA is unavailable; use environment credentials.")
    return Path(base) / "Mathvid" / "elevenlabs.json"


def dpapi(data: bytes, decrypt: bool = False) -> bytes:
    if os.name != "nt":
        raise ValueError("Encrypted configuration requires Windows; use environment credentials.")

    class Blob(ctypes.Structure):
        _fields_ = [("size", wintypes.DWORD), ("data", ctypes.POINTER(ctypes.c_ubyte))]

    buf = ctypes.create_string_buffer(data)
    source = Blob(len(data), ctypes.cast(buf, ctypes.POINTER(ctypes.c_ubyte)))
    target = Blob()
    crypto = ctypes.WinDLL("crypt32", use_last_error=True)
    kernel = ctypes.WinDLL("kernel32", use_last_error=True)
    fn = crypto.CryptUnprotectData if decrypt else crypto.CryptProtectData
    fn.argtypes = [ctypes.POINTER(Blob), ctypes.c_void_p, ctypes.c_void_p,
                   ctypes.c_void_p, ctypes.c_void_p, wintypes.DWORD, ctypes.POINTER(Blob)]
    fn.restype = wintypes.BOOL
    kernel.LocalFree.argtypes = [ctypes.c_void_p]
    kernel.LocalFree.restype = ctypes.c_void_p
    if not fn(ctypes.byref(source), None, None, None, None, 1, ctypes.byref(target)):
        raise ValueError("Windows could not protect/unprotect the credential for this user.")
    try:
        return ctypes.string_at(target.data, target.size)
    finally:
        kernel.LocalFree(target.data)


def settings() -> dict:
    if not os.environ.get("LOCALAPPDATA"):
        return {}
    path = config_path()
    if not path.exists():
        return {}
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("Invalid Mathvid credential configuration.")
    return value


def validate_key(key: str) -> str:
    if not isinstance(key, str) or not key:
        raise ValueError("No ElevenLabs key entered or configured.")
    if not key.isascii() or any(c.isspace() or ord(c) < 32 or ord(c) == 127 for c in key):
        raise ValueError("The API key contains invalid characters. Run configure again and paste the key once; hidden input does not display pasted characters.")
    parts = key.split("sk_")
    if len(parts) > 2 and parts[0] == "" and parts[1] and all(part == parts[1] for part in parts[1:]):
        raise ValueError("The API key appears to have been pasted more than once. Run configure again and paste it once; hidden input does not display pasted characters.")
    return key


def credential(cfg: dict) -> str:
    key = os.environ.get("ELEVENLABS_API_KEY", "")
    if key:
        return validate_key(key)
    if cfg.get("key_dpapi_base64"):
        return validate_key(dpapi(base64.b64decode(cfg["key_dpapi_base64"], validate=True), True).decode())
    raise ValueError("No ElevenLabs key configured. Run configure in a local terminal first.")


def api(path: str, key: str, body: dict | None = None) -> dict:
    validate_key(key)
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = Request("https://api.elevenlabs.io" + path, data=data,
                  headers={"xi-api-key": key, "Content-Type": "application/json"})
    try:
        with urlopen(req, timeout=120) as response:
            result = json.load(response)
    except HTTPError as exc:
        # Use fixed explanations, never raw provider bodies or headers.
        explanations = {
            "invalid_api_key": "The API key was not accepted; re-enter the full secret key.",
            "missing_api_key": "The API key was not received.",
            "unauthorized": "Authentication failed; check the full secret key.",
            "needs_authorization": "Authentication is required.",
            "insufficient_permissions": "The key lacks permission for this endpoint.",
            "quota_exceeded": "The account has insufficient credits.",
            "insufficient_credits": "The account has insufficient credits.",
            "voice_not_found": "The selected voice was not found.",
            "voice_access_denied": "The account cannot access the selected voice.",
            "invalid_page_size": "The voice-list page size was rejected.",
        }
        explanation = "Check key permissions, voice access, and credits."
        try:
            error_body = json.loads(exc.read(16384))
            detail = error_body.get("detail", {}) if isinstance(error_body, dict) else {}
            if isinstance(detail, dict):
                code = detail.get("code") or detail.get("status")
                if isinstance(code, str):
                    explanation = explanations.get(code, explanation)
        except (ValueError, UnicodeError):
            explanation = "A non-JSON error page was returned; check key entry and the network connection."
        raise ValueError(f"ElevenLabs HTTP {exc.code}; {explanation} No retry was made.") from None
    except (URLError, TimeoutError):
        raise ValueError("ElevenLabs request failed or timed out. No automatic retry was made; check history before repeating synthesis.") from None
    except (ValueError, UnicodeError):
        raise ValueError("The HTTP request or response was invalid. Check local key entry and request data; no retry was made.") from None
    if not isinstance(result, dict):
        raise ValueError("Unexpected ElevenLabs response format.")
    return result


def configure(args: argparse.Namespace) -> None:
    if not sys.stdin.isatty():
        raise ValueError("Run configure yourself in an interactive terminal; do not pass a key in command arguments.")
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", getpass.GetPassWarning)
            key = getpass.getpass("ElevenLabs API key (hidden; paste once): ")
    except getpass.GetPassWarning:
        raise ValueError("This terminal cannot hide input. Use a normal local PowerShell terminal.") from None
    if not key:
        raise ValueError("No key entered; configuration was not changed.")
    validate_key(key)
    voice_id = args.voice_id or input("Voice ID (optional for now): ").strip()
    sealed = base64.b64encode(dpapi(key.encode("utf-8"))).decode("ascii")
    path = config_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps({"key_dpapi_base64": sealed, "voice_id": voice_id}, indent=2), encoding="utf-8")
    print(f"Saved Windows-user-encrypted credentials to {path}. No API request made.")


def voices(args: argparse.Namespace) -> None:
    key = credential(settings())
    page_token = None
    seen = set()
    while True:
        query = {"page_size": 100}
        if page_token:
            query["next_page_token"] = page_token
        result = api("/v2/voices?" + urlencode(query), key)
        for voice in result.get("voices", []):
            print(f"{voice.get('voice_id', '')}\t{voice.get('name', '')}")
        if not result.get("has_more"):
            break
        page_token = result.get("next_page_token")
        if not page_token or page_token in seen:
            raise ValueError("Voice pagination returned no new token; listing stopped.")
        seen.add(page_token)


def validate_alignment(alignment: dict) -> tuple[str, list[float], list[float]]:
    chars = alignment.get("characters", [])
    starts = alignment.get("character_start_times_seconds", [])
    ends = alignment.get("character_end_times_seconds", [])
    if not chars or not (len(chars) == len(starts) == len(ends)):
        raise ValueError("Speech response lacks usable character timing.")
    if not all(isinstance(c, str) and len(c) == 1 for c in chars):
        raise ValueError("Unexpected character alignment format.")
    previous = 0.0
    for start, end in zip(starts, ends):
        if not isinstance(start, (float, int)) or not isinstance(end, (float, int)):
            raise ValueError("Non-numeric speech timing.")
        if not math.isfinite(start) or not math.isfinite(end) or start < previous or end < start:
            raise ValueError("Invalid speech timing sequence.")
        previous = start
    return "".join(chars), starts, ends


def srt_time(seconds: float) -> str:
    ms = round(seconds * 1000)
    hours, ms = divmod(ms, 3600000)
    minutes, ms = divmod(ms, 60000)
    secs, ms = divmod(ms, 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{ms:03}"


def captions(alignment: dict) -> str:
    text, starts, ends = validate_alignment(alignment)
    words = list(re.finditer(r"\S+", text))
    cues, group = [], []
    for word in words:
        group.append(word)
        phrase = " ".join(m.group() for m in group)
        if len(group) >= 7 or len(phrase) >= 52 or re.search(r"[.!?]$", word.group()):
            cues.append(group)
            group = []
    if group:
        cues.append(group)
    lines = []
    for index, cue in enumerate(cues, 1):
        start, end = starts[cue[0].start()], ends[cue[-1].end() - 1]
        if end <= start:
            raise ValueError("A caption has zero duration; inspect the alignment manually.")
        phrase = " ".join(m.group() for m in cue)
        lines.append(f"{index}\n{srt_time(start)} --> {srt_time(end)}\n" + "\n".join(textwrap.wrap(phrase, width=42)) + "\n")
    return "\n".join(lines)


def speak(args: argparse.Namespace) -> None:
    cfg = settings()
    voice_id = args.voice_id or os.environ.get("ELEVENLABS_VOICE_ID") or cfg.get("voice_id")
    if not voice_id:
        raise ValueError("Choose an ElevenLabs voice; pass --voice-id or configure ELEVENLABS_VOICE_ID.")
    text = args.text_file.read_text(encoding="utf-8-sig").strip()
    if not text:
        raise ValueError("The narration text file is empty.")
    output = args.output.resolve()
    if output.suffix.lower() != ".mp3":
        raise ValueError("Use an .mp3 output filename.")
    timing_path, srt_path = output.with_suffix(".alignment.json"), output.with_suffix(".srt")
    if any(path.exists() for path in (output, timing_path, srt_path)):
        raise ValueError("An output already exists; reuse it or choose a new filename before spending more credits.")
    output.parent.mkdir(parents=True, exist_ok=True)
    key = credential(cfg)
    result = api("/v1/text-to-speech/" + quote(voice_id, safe="") + "/with-timestamps?output_format=mp3_44100_128",
                 key, {"text": text, "model_id": args.model_id})
    audio = base64.b64decode(result.get("audio_base64", ""), validate=True)
    if not audio:
        raise ValueError("ElevenLabs returned no audio; check provider history before repeating.")
    # Preserve paid audio even if timing is missing or malformed.
    output.write_bytes(audio)
    timings = {"voice_id": voice_id, "model_id": args.model_id,
               "alignment": result.get("alignment"), "normalized_alignment": result.get("normalized_alignment")}
    timing_path.write_text(json.dumps(timings, ensure_ascii=False, indent=2), encoding="utf-8")
    alignment = timings["normalized_alignment"] or timings["alignment"]
    if not isinstance(alignment, dict):
        raise ValueError(f"Audio saved to {output}, but no timing was returned. Do not resynthesize automatically.")
    srt_path.write_text(captions(alignment), encoding="utf-8")
    print(f"Saved {output}, {timing_path.name}, and {srt_path.name}. Review pronunciation and caption breaks.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    setup = sub.add_parser("configure", help="Interactively store a key using Windows DPAPI; no API call")
    setup.add_argument("--voice-id")
    setup.set_defaults(func=configure)
    listing = sub.add_parser("voices", help="List account voices using a read-only API request")
    listing.set_defaults(func=voices)
    speech = sub.add_parser("speak", help="Generate speech and spend provider credits")
    speech.add_argument("--text-file", type=Path, required=True)
    speech.add_argument("--output", type=Path, required=True)
    speech.add_argument("--voice-id")
    speech.add_argument("--model-id", default="eleven_multilingual_v2")
    speech.set_defaults(func=speak)
    args = parser.parse_args()
    try:
        args.func(args)
    except (OSError, ValueError, KeyError, TypeError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
