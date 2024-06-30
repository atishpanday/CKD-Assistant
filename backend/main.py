from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import chat

server = FastAPI(root_path="/api")

server.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

server.include_router(chat.router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(server, host="0.0.0.0", port=8000)
