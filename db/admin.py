import os
from fastapi import APIRouter, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from . import SystemsDB
from dotenv import load_dotenv


router = APIRouter(
    prefix="/admin",
    tags=["admin"],
)

load_dotenv()
approot = os.environ.get('APP_ROOT', '')
template_folder = os.path.join(approot, "db", "templates")
templates = Jinja2Templates(directory= template_folder)

db = SystemsDB()

@router.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    records = db.query_all_records()
    return templates.TemplateResponse("index.html", {"request": request, "records": records})


@router.get("/add", response_class=HTMLResponse)
async def add_form(request: Request):
    return templates.TemplateResponse("add_form.html", {"request": request})


@router.post("/add", response_class=HTMLResponse)
async def add_record(request: Request, IP: str = Form(...), Desc1_oid: str = Form(...), Desc2_oid: str = Form(...), Temp_f_oid: str = Form(...)):
    db.insert_record(IP, Desc1_oid, Desc2_oid, Temp_f_oid)
    return RedirectResponse(url="/admin", status_code=303)


@router.get("/edit/{ip}", response_class=HTMLResponse)
async def edit_form(request: Request, ip: str):
    record = db.query_record_by_ip(ip)
    return templates.TemplateResponse("edit_form.html", {"request": request, "record": record})


@router.post("/edit/{ip}", response_class=HTMLResponse)
async def edit_record(request: Request, ip: str, Desc1_oid: str = Form(...), Desc2_oid: str = Form(...), Temp_f_oid: str = Form(...)):
    db.update_record(ip, Desc1_oid, Desc2_oid, Temp_f_oid)
    return RedirectResponse(url="/admin", status_code=303)


@router.post("/delete/{ip}", response_class=HTMLResponse)
async def delete_record(request: Request, ip: str):
    db.delete_record(ip)
    return RedirectResponse(url="/admin", status_code=303)
