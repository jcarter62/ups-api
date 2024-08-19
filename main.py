from uuid import uuid1

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from dotenv import load_dotenv
import os
from db import SystemsDB, admin, SiteData
from snmpread import Sites, Site

app = FastAPI()

app.include_router(admin.router)

load_dotenv()

approot = os.environ.get('APP_ROOT', '')
template_folder = os.path.join(approot, "templates")
templates = Jinja2Templates(directory= template_folder)

@app.get("/")
async def root(request: Request):
    systems = Sites()
    data = []
    n = 100
    for site in systems.sites:
        n += 3
        id = "id" + str(n).zfill(3)
        data.append({
            "id": id,
            "host": site.host,
            "description1": "",
            "description2": "",
            "temperature_f": ""
        })
    return templates.TemplateResponse("home.html", {"request": request, "sites": data})

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

@app.get("/data/log-sites")
async def log_sites():
    devices = Sites()

    for site in devices.sites:
        site.__load_data__()
        print(f"Logging data for {site.host}")
        db = SiteData(host=site.host)
        db.insert_record(host=site.host, temp_f=site.temperature_f)
        db.close()
        db = None
    return {"message": "Data logged"}

@app.get("/data/get-latest/{host}")
async def get_latest(host: str):
    db = SiteData(host=host)
    dat = db.get_most_recent_data()
    db.close()

    sites = Sites()
    data = []
    for oneSite in sites.sites:
        if oneSite.host == host:
            oneSite.__load_data__()
            data = [dat[0], dat[1], oneSite.description2, oneSite.description1, oneSite.temperature_f]
            break
    return {"data": data}

@app.get("/data/get-latest-day/{host}")
async def get_latest_day(host: str):
    db = SiteData(host=host)
    data = db.get_average_hourly(days=1)
    db.close()
    return {"data": data}

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(os.path.join(approot, "images", "favicon.ico"))

@app.get("/i/{image_name}", include_in_schema=False)
async def images(image_name: str):
    return FileResponse(os.path.join(approot, "images", image_name))


@app.get("/site-graph/{host}")
async def site_graph_data(request: Request, host: str):
    db = SiteData(host=host)
    data = db.get_average_hourly(days=7)
    db.close()



    # prepare data for graph
    sitename = host

    labels = []
    datavalues = []
    for one in data:
        labels.append(one['hour'])
        datavalues.append(one['avg_temp'])

    return templates.TemplateResponse(
        "site-graph.html",
        {"request": request, "site": sitename, "labels":labels, "data":datavalues}
    )
