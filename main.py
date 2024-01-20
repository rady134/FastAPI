from fastapi import FastAPI

app = FastAPI()

@app.get("/")
async def root():
    return {"greeting": "Hello, World!", "message": "Welcome to FastAPI!"}


@app.get('/get_full_link/')
def get_full_link(url: str):
    full_link = f"https://{url}"  # Assuming HTTP for simplicity
    return {"full_link": full_link}
