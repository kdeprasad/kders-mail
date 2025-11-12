import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from . import database  # noqa: E402
from .routes_auth import router as auth_router  # noqa: E402
from .routes_mail import router as mail_router  # noqa: E402
from .routes_groups import router as groups_router  # noqa: E402
from .routes_ai import router as ai_router  # noqa: E402

app = FastAPI(title="kders-mail-backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(auth_router, prefix="/api", tags=["api"])  # For /api/users/search
app.include_router(mail_router, prefix="/mail", tags=["mail"])
app.include_router(mail_router, prefix="/api/mail", tags=["mail"])  # For frontend /api/mail paths
app.include_router(groups_router, prefix="/groups", tags=["groups"])
app.include_router(groups_router, prefix="/api/groups", tags=["groups"])  # For frontend /api/groups paths
app.include_router(ai_router, prefix="/ai", tags=["ai"])

@app.on_event("startup")
async def startup():
    await database.init_db()

@app.get("/")
async def root():
    return {"status": "ok", "service": "kders-mail-backend"}
