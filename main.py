from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from dotenv import load_dotenv
import os
from db import SystemsDB, admin
from snmpread import Sites
app = FastAPI()

app.include_router(admin.router)

load_dotenv()

approot = os.environ.get('APP_ROOT', '')
template_folder = os.path.join(approot, "templates")
templates = Jinja2Templates(directory= template_folder)


@app.get("/")
async def root(request: Request):
    systems = Sites()
    for site in systems.sites:
        site.__load_data__()
    return templates.TemplateResponse("home.html", {"request": request, "sites": systems.sites})


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}

@app.get("/initdb")
async def initdb():
    db = SystemsDB()
    recs = db.query_all_records()
    for rec in recs:
        print(rec)
    db.close()
    return {"message": "Database initialized"}


@app.get("/sites")
async def sites():
    systems = Sites()
    for site in systems.sites:
        site.__load_data__()

    return {"systems": [site.__dict__ for site in systems.sites] }


@app.get("/status", response_class=HTMLResponse)
async def status(request: Request):
    systems = Sites()
    for site in systems.sites:
        site.__load_data__()

    return templates.TemplateResponse("status.html", {"request": request, "sites": systems.sites})

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(os.path.join(approot, "images", "favicon.ico"))

@app.get("/i/{image_name}", include_in_schema=False)
async def images(image_name: str):
    return FileResponse(os.path.join(approot, "images", image_name))


