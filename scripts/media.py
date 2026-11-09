"""Mix a silent Mathvid render with speech and quiet, ducked piano using FFmpeg."""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
import shutil
import subprocess
import sys


def probe(path: Path, ffprobe: str) -> dict:
    result = subprocess.run([ffprobe, "-v", "error", "-show_streams", "-show_format",
                             "-of", "json", str(path.resolve())], check=True, capture_output=True, text=True)
    return json.loads(result.stdout)


def stream(info: dict, kind: str) -> dict:
    for entry in info.get("streams", []):
        if entry.get("codec_type") == kind:
            return entry
    raise ValueError(f"Input has no {kind} stream.")


def duration(info: dict, kind: str) -> float:
    entry = stream(info, kind)
    result = float(entry.get("duration", info.get("format", {}).get("duration", 0)))
    if not math.isfinite(result) or result <= 0:
        raise ValueError(f"Could not determine a positive {kind} duration.")
    return result


def mix_command(args: argparse.Namespace, ffmpeg: str, seconds: float) -> list[str]:
    fade = min(1.5, seconds / 3)
    music = (f"[2:a]atrim=duration={seconds:.6f},asetpts=PTS-STARTPTS,"
             "loudnorm=I=-36:TP=-4:LRA=7,aresample=48000,"
             f"afade=t=in:st=0:d={fade:.6f},afade=t=out:st={seconds-fade:.6f}:d={fade:.6f}[piano]")
    filters = (
        "[1:a]asetpts=PTS-STARTPTS,loudnorm=I=-16:TP=-2:LRA=7,aresample=48000,"
        f"apad,atrim=duration={seconds:.6f},asplit=2[voice][side];"
        + music + ";[piano][side]sidechaincompress=threshold=0.025:ratio=8:attack=15:release=350[ducked];"
        "[voice][ducked]amix=inputs=2:duration=first:normalize=0,"
        "alimiter=limit=0.794328:level=false:latency=true[mix]"
    )
    return [ffmpeg, "-hide_banner", "-nostdin", "-n", "-i", str(args.video.resolve()),
            "-i", str(args.voice.resolve()), "-stream_loop", "-1", "-ss", str(args.music_offset),
            "-i", str(args.music.resolve()), "-filter_complex", filters,
            "-map", "0:v:0", "-map", "[mix]", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
            "-ar", "48000", "-ac", "2", "-t", f"{seconds:.6f}", "-movflags", "+faststart", str(args.output.resolve())]


def mix(args: argparse.Namespace) -> None:
    ffmpeg, ffprobe = shutil.which("ffmpeg"), shutil.which("ffprobe")
    if not ffmpeg or not ffprobe:
        raise ValueError("Both ffmpeg and ffprobe must be available on PATH for mixing.")
    if args.output.exists():
        raise ValueError("Output exists; choose a new filename.")
    if args.output.suffix.lower() != ".mp4":
        raise ValueError("Output must have an .mp4 extension.")
    if not math.isfinite(args.music_offset) or args.music_offset < 0:
        raise ValueError("Music offset must be finite and nonnegative.")
    for path in (args.video, args.voice, args.music):
        if not path.is_file():
            raise ValueError(f"Missing input: {path}")
    video, voice, piano = (probe(p, ffprobe) for p in (args.video, args.voice, args.music))
    video_stream = stream(video, "video")
    if (video_stream.get("width"), video_stream.get("height")) != (1080, 1920):
        raise ValueError("Final assembly expects a 1080x1920 render; rerender at final resolution first.")
    if video_stream.get("codec_name") != "h264":
        raise ValueError("Final assembly expects H.264 video for stream copying.")
    seconds, speech_seconds = duration(video, "video"), duration(voice, "audio")
    if speech_seconds > seconds + 0.03:
        raise ValueError("Speech is longer than the video. Retiming the scene is required; narration will not be cut.")
    if args.music_offset >= duration(piano, "audio"):
        raise ValueError("Music offset lies beyond the track.")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(mix_command(args, ffmpeg, seconds), check=True)
    print(f"Saved {args.output.resolve()}. Listen for intelligibility and loop seams; measure the final encoded mix before claiming loudness compliance.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    command = sub.add_parser("mix")
    for name in ("video", "voice", "music", "output"):
        command.add_argument("--" + name, type=Path, required=True)
    command.add_argument("--music-offset", type=float, default=0)
    args = parser.parse_args()
    try:
        mix(args)
    except (ValueError, OSError, subprocess.CalledProcessError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
