"""Report Mathvid's local prerequisites without contacting services or revealing keys."""
import importlib.metadata
import json
import os
import shutil
import sys
from pathlib import Path

try:
    renderer = importlib.metadata.version("manimgx")
except importlib.metadata.PackageNotFoundError:
    renderer = None
config_file = Path(os.environ.get("LOCALAPPDATA", ".")) / "Mathvid" / "elevenlabs.json"
config = {}
try:
    if config_file.is_file():
        config = json.loads(config_file.read_text(encoding="utf-8"))
        if not isinstance(config, dict):
            config = {}
except (OSError, ValueError):
    config = {}
music_dir = os.environ.get("MATHVID_MUSIC_DIR", "").strip()
report = {
    "python": sys.version.split()[0],
    "python_3_13_or_3_14": sys.version_info[:2] in ((3, 13), (3, 14)),
    "manimgx_version_in_this_python": renderer,
    "manimgx_cli": shutil.which("manimgx"),
    "ffmpeg_cli_for_mixing": shutil.which("ffmpeg"),
    "ffprobe_cli_for_review": shutil.which("ffprobe"),
    "elevenlabs_key_present_not_authenticated": bool(os.environ.get("ELEVENLABS_API_KEY") or config.get("key_dpapi_base64")),
    "elevenlabs_voice_id_present": bool(os.environ.get("ELEVENLABS_VOICE_ID") or config.get("voice_id")),
    "music_folder_configured": bool(music_dir),
    "music_folder_exists": bool(music_dir and Path(music_dir).expanduser().is_dir()),
}
print(json.dumps(report, indent=2))
