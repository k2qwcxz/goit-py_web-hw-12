from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.orm import Session

from .database import get_db
from .routers.contacts import router as contacts_router
from .routers.auth import router as auth_router

app = FastAPI(
    title="Contacts API",
    version="1.0.0",
    description="REST API для управління контактами з аутентифікацією"
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Підключення маршрутів
app.include_router(auth_router)
app.include_router(contacts_router, prefix="/api")


@app.get("/")
def index():
    """Root endpoint"""
    return {
        "message": "Contacts API with Authentication",
        "docs": "/api/docs",
        "version": "1.0.0"
    }


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    """Перевірка здоров'я API та підключення до БД"""
    try:
        result = db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(
                status_code=500,
                detail="Database is not configured correctly"
            )
        return {"message": "Welcome to Contacts API!"}
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=500,
            detail="Error connecting to the database"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)