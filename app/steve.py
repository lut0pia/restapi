from fastapi import APIRouter, HTTPException, Request
import json
import subprocess
import os
import uuid

router = APIRouter(prefix="/steve")

CFG_DIR = "/usr/local/steve/cfg"
CFG_NAMES = list(map(lambda c: c.removesuffix('.steve.json'), os.listdir(CFG_DIR)))

@router.get("/configurations")
async def get_configurations():
  """Get all available configuration names."""
  return CFG_NAMES

@router.post("/generate")
async def generate(configuration: str):
  """Generate a MIDI sequence using the named configuration."""
  config_path = f"{CFG_DIR}/{configuration}.steve.json"
  if not os.path.exists(config_path):
    raise HTTPException(status_code=404, detail=f"Configuration '{configuration}' not found")
  return await generate_internal(config_path)

@router.post("/generate/custom")
async def generate_custom(request: Request):
  """Generate a MIDI sequence using the custom configuration passed in the body of the request."""
  try:
    config = json.loads((await request.body()).decode())
  except Exception:
    raise HTTPException(status_code=415, detail=f"Request body couldn't be made into JSON configuration")
  if "parents" in config and isinstance(config["parents"], list):
    config["parents"] = list(map(lambda p: f"{CFG_DIR}/{p}.steve.json", config["parents"]))

  config_path = f"tmp/{str(uuid.uuid4())}.steve.json"
  with open(config_path, "w") as config_file:
    json.dump(config, config_file)

  return await generate_internal(config_path)

async def generate_internal(config_path):
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
