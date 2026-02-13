from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.auth.routers import router as auth_router
from backend.users.routers import router as users_router

app = FastAPI(title="Smart Notes API")

# -------- CORS --------
origins = settings.CORS_ORIGIN_LIST.copy()
origins.append("null")  # важно для фронта запускаемого как file://

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],   # для OPTIONS
    allow_headers=["*"],   # для Content-Type и Authorization
)

# -------- РОУТЫ --------
app.include_router(auth_router, prefix="/auth")
app.include_router(folders_router, prefix="/api/folders")
app.include_router(notes_router, prefix="/api/notes")
app.include_router(users_router, prefix="/api/users")

# здесь ВАЖНО — НЕ добавляем prefix="/api/ai",
# потому что он уже прописан ВНУТРИ ai_router
app.include_router(ai_router)

# -------- Корень --------
@app.get("/")
def root():
    return {"message": "Smart Notes API работает!"}

