from fastapi import APIRouter, HTTPException
import subprocess
import os
import uuid

router = APIRouter(prefix="/steve")

CFG_DIR = "/usr/local/steve/cfg"

@router.get("/configurations")
async def get_configurations():
  return list(map(lambda c: c.removesuffix('.steve.json'), os.listdir(CFG_DIR)))

@router.post("/generate")
async def generate(configuration: str):
  config_path = f"{CFG_DIR}/{configuration}.steve.json"
  if not os.path.exists(config_path):
    raise HTTPException(status_code=404, detail=f"Configuration '{configuration}' not found")

  filename = str(uuid.uuid4())
  output_path = f"tmp/{filename}"
  error = subprocess.call([
    "steve",
    "-mj",
    "--random",
    f"--out={output_path}",
    f"--config={config_path}"
  ])
  if error != 0:
    raise HTTPException(status_code=500, detail=f"Steve process returned {error}")

  return {
    "sequence": f"{filename}.mid",
    "description": f"{filename}.json",
  }
