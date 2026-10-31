from functools import lru_cache
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from app.core import Clinic
from pathlib import Path as StaticPath
from fastapi.staticfiles import StaticFiles

app = FastAPI(title="ClinicFlow AI", version="0.1.0")


@lru_cache
def service():
    return Clinic()


class BookRequest(BaseModel):
    slot_id: str
    patient: str = Field(min_length=1, max_length=100)
    request_key: str = Field(min_length=1, max_length=100)
    confirmed: bool = False


class Confirm(BaseModel):
    confirmed: bool = False


class Suggest(BaseModel):
    message: str = Field(min_length=1, max_length=1000)
    mode: str = Field(default="fixture", pattern="^(fixture|local)$")


def call(fn, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except PermissionError as e:
        raise HTTPException(403, str(e)) from e
    except ValueError as e:
        raise HTTPException(409, str(e)) from e


@app.get("/api/slots")
def slots():
    return service().slots()


@app.get("/api/bookings")
def bookings():
    return service().bookings()


@app.post("/api/bookings")
def book(b: BookRequest):
    return call(service().book, **b.model_dump())


@app.post("/api/bookings/{bid}/cancel")
def cancel(bid: str, b: Confirm):
    return call(service().cancel, bid, b.confirmed)


@app.post("/api/suggest")
def suggest(b: Suggest):
    return call(service().suggest, b.message, b.mode)


@app.get("/api/health")
def health():
    return {"status": "ok", "data": "synthetic"}


# Serve the compiled React client after all API routes.

if StaticPath("web/dist").is_dir():
    app.mount("/", StaticFiles(directory="web/dist", html=True), name="web")
