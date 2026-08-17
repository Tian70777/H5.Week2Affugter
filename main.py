#!/usr/bin/env python3
"""
Fugtstyring - serverdel.

Koer med:  uvicorn main:app --host 0.0.0.0 --port 8000
Docs paa:  http://<ip>:8000/docs

Serveren er en VALGFRI komponent. Falder den ud, fortsaetter
mikrocontrollerens fugtbeskyttelse uaendret - kun prisoptimering,
historik og grafer bortfalder.
"""
from fastapi import FastAPI

from fastapi.responses import FileResponse
from app.routes import arduino, dashboard

app = FastAPI(title="Fugtstyring", version="1.0")

app.include_router(arduino.router)
app.include_router(dashboard.router)


@app.get("/", include_in_schema=False)
def dashboard_page():
    """Selve dashboard-siden. Aabnes paa http://<ip>:8000/"""
    return FileResponse("static/index.html")