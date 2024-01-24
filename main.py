import setup
from fastapi import FastAPI

from middlewares.cors import add_cors_middleware

from routes.course.router import router as course_router

app = FastAPI()

add_cors_middleware(app)

app.include_router(course_router)


@app.get("/")
def read_root():
    return {"Hello": "World2"}


if __name__ == "__main__":
    # run main.py to debug backend
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
