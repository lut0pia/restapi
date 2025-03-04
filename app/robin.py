from fastapi import APIRouter, HTTPException
import subprocess
import os

router = APIRouter(prefix="/robin")

@router.post("/render")
async def render(filename : str):
  filebase, ext = os.path.splitext(filename)

  if not ext in [".mid", ".midi"]:
    raise HTTPException(status_code=415, detail=f"File '{filename}' is not a MIDI sequence")

  mid_path = f"tmp/{filename}"
  if not os.path.exists(mid_path):
    raise HTTPException(status_code=404, detail=f"File '{filename}' not found")

  error = subprocess.call(["rbncli", "render", mid_path])
  if error != 0:
    raise HTTPException(status_code=500, detail=f"Robin process returned {error}")

  wav_path = f"tmp/{filebase}.wav"
  mp3_path = f"tmp/{filebase}.mp3"

  error = subprocess.call(["ffmpeg", "-i", wav_path, mp3_path])
  if error != 0:
    raise HTTPException(status_code=500, detail=f"Ffmpeg process returned {error}")

  return {
    "audio": os.path.basename(mp3_path),
  }
