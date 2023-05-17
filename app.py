from sanic import Sanic
from sanic.response import text
from Database import Database
from env import HOST, PORT, DATABASE
from cors import add_cors_headers

app = Sanic("Schedulio")
db = Database(DATABASE)

# Fill in CORS headers
app.register_middleware(add_cors_headers, "response")


@app.route("/")
def hello(request):
    return text("Hi 😎")


@app.route("/sign_up")
def sign_up(request):
    return text(str(db.add_user_and_get_id("test", "test")))


@app.route("/log_in")
def log_in(request):
    return text(str(db.login_and_get_id("test", "test")))


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=True)
