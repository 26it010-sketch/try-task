
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from database import get_connection

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class User(BaseModel):
    name: str
    age: int


@app.on_event("startup")
def create_table():
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name VARCHAR(100) NOT NULL,
                age INTEGER NOT NULL
            )
        """)
        connection.commit()
    finally:
        cursor.close()
        connection.close()


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/")
def home():
    return {"message": "FastAPI with PostgreSQL is working"}


@app.post("/users")
def create_user(user: User):
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            INSERT INTO users (name, age)
            VALUES (%s, %s)
            RETURNING id, name, age
            """,
            (user.name, user.age),
        )

        new_user = cursor.fetchone()
        connection.commit()

        return {
            "id": new_user[0],
            "name": new_user[1],
            "age": new_user[2],
        }
    finally:
        cursor.close()
        connection.close()


@app.get("/users")
def get_users():
    connection = get_connection()
    cursor = connection.cursor()

    try:
        cursor.execute(
            "SELECT id, name, age FROM users ORDER BY id"
        )
        rows = cursor.fetchall()

        return [
            {"id": row[0], "name": row[1], "age": row[2]}
            for row in rows
        ]
    finally:
        cursor.close()
        connection.close()


# Serve the built React frontend.
BASE_DIR = Path(__file__).resolve().parent
DIST_DIR = BASE_DIR / "dist"
ASSETS_DIR = DIST_DIR / "assets"

if ASSETS_DIR.is_dir():
    app.mount(
        "/assets",
        StaticFiles(directory=ASSETS_DIR),
        name="assets",
    )


@app.get("/{full_path:path}")
def serve_frontend(full_path: str):
    # Do not return index.html for unknown API routes.
    if full_path == "docs" or full_path.startswith("docs/"):
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Not found")

    if full_path == "openapi.json":
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Not found")

    requested_file = (DIST_DIR / full_path).resolve()

    if (
        DIST_DIR.is_dir()
        and requested_file.is_relative_to(DIST_DIR.resolve())
        and requested_file.is_file()
    ):
        return FileResponse(requested_file)

    if DIST_DIR.is_file():
        return FileResponse(DIST_DIR)

    index_file = DIST_DIR / "index.html"

    if index_file.is_file():
        return FileResponse(index_file)

    from fastapi import HTTPException
    raise HTTPException(status_code=404, detail="Frontend not built")