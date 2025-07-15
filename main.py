from fastapi import FastAPI
from routes import blog_routes, auth_routes, sse_routes
from database import engine
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from contextlib import asynccontextmanager
import uvicorn
from fastapi.middleware.cors import CORSMiddleware  



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

# Include CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development; restrict in production
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)


# Include Routers
app.include_router(auth_routes.router, prefix="/auth", tags=["Authentication"])
app.include_router(blog_routes.router, prefix="/api", tags=["Blogs"])
app.include_router(sse_routes.router, prefix="/api", tags=["SSE"])


@app.get("/")
def read_root():
    return {"message": "Welcome to the ZS Sample API!"}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
