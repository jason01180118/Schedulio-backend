from sanic import Sanic
from sanic.response import text
from env import HOST, PORT
from cors import add_cors_headers

app = Sanic("Schedulio")

# Fill in CORS headers
app.register_middleware(add_cors_headers, "response")

@app.route("/")
def hello(request):
    return text("Hi 😎")


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=True)
