from sanic import Sanic
from sanic.response import text

app = Sanic("SimpleAPI")
HOST = "localhost"
PORT = 8000


@app.get("/")
def hello(request):
    return text("Hi 😎")

if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=True)