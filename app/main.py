from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from threading import Timer
import os
import steve
import robin

programs = [steve, robin]

update_timer = None
@asynccontextmanager
async def lifespan(app: FastAPI):
  yield
  update_timer.cancel()

app = FastAPI(lifespan=lifespan)
for program in programs:
  app.include_router(program.router)

allow_origins = [
  "https://lutopia.net",
  "https://radio.lutopia.net"
]
if os.getenv("DEBUG"):
  print("Running in debug mode")
  allow_origins.append("*")

app.add_middleware(
  CORSMiddleware,
  allow_origins=allow_origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

os.makedirs("tmp", exist_ok=True)
app.mount("/tmp", StaticFiles(directory="tmp"), name="tmp")

def update(iteration = 0):
  global update_timer
  if (iteration % 60) == 0:
    os.system(f"find tmp -type f -mmin +5 -delete")
  update_timer = Timer(1, update, [iteration + 1])
  update_timer.start()

update()
