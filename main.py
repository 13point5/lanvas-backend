import setup
from fastapi import FastAPI

from middlewares.cors import add_cors_middleware

from routes.course.router import router as course_router

from fastapi.exceptions import RequestValidationError
from fastapi.responses import PlainTextResponse

app = FastAPI()

add_cors_middleware(app)

app.include_router(course_router)


# @app.exception_handler(RequestValidationError)
# async def validation_exception_handler(request, exc):
#     print("Req", request)
#     print("Exc", exc)
#     return PlainTextResponse(str(exc), status_code=400)


@app.get("/")
def read_root():
    return {"Hello": "World2"}


if __name__ == "__main__":
    # run main.py to debug backend
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
