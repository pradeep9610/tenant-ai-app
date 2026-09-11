from fastapi import FastAPI

app = FastAPI(title="Tenant Screening AI API")

@app.get("/")
def read_root():
    return {"message": "Welcome to Tenant Screening AI SaaS API!"}