from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
import uvicorn
import os

from .database import get_db, create_tables
from .routers import chef, customer, admin

# Create FastAPI app
app = FastAPI(title="Tabble - Hotel Management App")

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins since frontend and backend are on different ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Setup templates
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(chef.router)
app.include_router(customer.router)
app.include_router(admin.router)

# Create database tables
create_tables()

# Check if we have the React build folder
react_build_dir = "frontend/build"
has_react_build = os.path.isdir(react_build_dir)

if has_react_build:
    # Mount the React build folder
    app.mount("/", StaticFiles(directory=react_build_dir, html=True), name="react")

# Root route - serve React app in production, otherwise serve index.html template
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    if has_react_build:
        return FileResponse(f"{react_build_dir}/index.html")
    return templates.TemplateResponse("index.html", {"request": request})

# Chef page
@app.get("/chef", response_class=HTMLResponse)
async def chef_page(request: Request):
    return templates.TemplateResponse("chef/index.html", {"request": request})

# Chef orders page
@app.get("/chef/orders", response_class=HTMLResponse)
async def chef_orders_page(request: Request):
    return templates.TemplateResponse("chef/orders.html", {"request": request})

# Customer login page
@app.get("/customer", response_class=HTMLResponse)
async def customer_login_page(request: Request):
    return templates.TemplateResponse("customer/login.html", {"request": request})

# Customer menu page
@app.get("/customer/menu", response_class=HTMLResponse)
async def customer_menu_page(request: Request, table_number: int, unique_id: str):
    return templates.TemplateResponse(
        "customer/menu.html",
        {"request": request, "table_number": table_number, "unique_id": unique_id}
    )

# Admin page
@app.get("/admin", response_class=HTMLResponse)
async def admin_page(request: Request):
    return templates.TemplateResponse("admin/index.html", {"request": request})

# Admin dishes page
@app.get("/admin/dishes", response_class=HTMLResponse)
async def admin_dishes_page(request: Request):
    return templates.TemplateResponse("admin/dishes.html", {"request": request})

import os

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000)
