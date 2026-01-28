from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import home, petitions

app = FastAPI(title="Homelab API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(home.router)
app.include_router(petitions.router)


@app.get("/")
def root():
    return {"message": "Homelab API running", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
