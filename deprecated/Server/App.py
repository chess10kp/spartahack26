from pydantic import BaseModel
from fastapi import FastAPI

app = FastAPI()

@app.get("/hi")
def say_hi():
    return {"message": "Hello, World!", "status": 200}