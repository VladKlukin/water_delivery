from fastapi import FastAPI
import uvicorn
from sqlalchemy import text
from .models import Orders
from .database import SessionLocal
app = FastAPI()



if __name__ == "__main__":   
    uvicorn.run("app.main:app",reload=True)