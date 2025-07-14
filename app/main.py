from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Импортируем наши роутеры
from app.api.routers import auth as auth_router
from app.api.routers import paintings as paintings_router
from app.api.routers import feedback as feedback_router

# Создаем экземпляр приложения
app = FastAPI(
    title="ArtGallery API",
    description="API для веб-приложения картинной галереи.",
    version="1.0.0",
)

# Настройка CORS
origins = [
    "http://localhost",
    "http://localhost:8080",  # Для вашего фронтенда на Vue/React/etc.
    # Добавьте сюда URL вашего реального фронтенда, когда он будет
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роутеры к приложению
app.include_router(auth_router.router, prefix="/api/auth", tags=["Auth"])
app.include_router(paintings_router.router, prefix="/api/paintings", tags=["Paintings"])
app.include_router(feedback_router.router, prefix="/api/feedback", tags=["Feedback"])

# Просто для проверки, что сервер запустился
@app.get("/")
def read_root():
    return {"message": "Welcome to ArtGallery API"}