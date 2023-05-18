from sqlite3 import IntegrityError

from sanic import Sanic, json
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
    try:
        return text(str(db.add_user_and_get_id("test", "test")))
    except IntegrityError:
        return json({"error": "Account already exists"}, status=409)


@app.route("/log_in")
def log_in(request):
    try:
        return text(str(db.login_and_get_id("test", "test")))
    except:
        return json({"error": "Invalid account or password"}, status=401)


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=True)
