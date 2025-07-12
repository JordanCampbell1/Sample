from fastapi import FastAPI
from routes import blog_routes, auth_routes
from database import engine
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from contextlib import asynccontextmanager
import uvicorn


# Ensure the .env file is loaded
from dotenv import load_dotenv

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- On Startup ---
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print("✅ Database connection established successfully.")
    except OperationalError as e:
        print("❌ Could not connect to the database.")
        print(f"Error: {e}")
        raise e  # Optionally raise to halt app startup

    yield  # App runs here

    # --- On Shutdown ---
    print("🔻 API shutdown complete.")


app = FastAPI(lifespan=lifespan)

# Include Routers
app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])
app.include_router(blog_routes.router, prefix="/api", tags=["Blogs"])


@app.get("/")
def read_root():
    return {"message": "Welcome to the ZS Sample API!"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
