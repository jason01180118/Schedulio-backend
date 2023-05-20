from sqlite3 import IntegrityError

from sanic import Sanic, json
from sanic.response import text
from Database import Database
from env import HOST, PORT, DATABASE
from cors import add_cors_headers

app = Sanic("Schedulio")
app.register_middleware(add_cors_headers, "response")
db = Database(DATABASE)


@app.get("/")
def hello(request):
    return text("Hi 😎")


@app.route("/sign_up", methods=["POST"])
def sign_up(request):
    try:
        return text(str(db.add_user_and_get_id(request.form.get("account"), request.form.get("password"))))
    except IntegrityError:
        return json({"error": "Account already exists"}, status=409)


@app.route("/log_in", methods=["POST"])
def log_in(request):
    try:
        return text(str(db.login_and_get_id(request.form.get("account"), request.form.get("password"))))
    except TypeError:
        return json({"error": "Invalid account or password"}, status=401)


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=True)
