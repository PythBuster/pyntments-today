import frontend
import uvicorn
from fastapi import FastAPI

app = FastAPI()

frontend.init(app)

if __name__ == "__main__":
    uvicorn.run("pyntments_today.main:app", host="0.0.0.0", port=8000)
