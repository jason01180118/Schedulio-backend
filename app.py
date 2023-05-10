from sanic import Sanic
from sanic.response import text
from env import HOST, PORT

app = Sanic("SimpleAPI")


@app.get("/")
def hello(request):
    return text("Hi 😎")

if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=True)