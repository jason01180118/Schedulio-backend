import os
import random
import string
from sqlite3 import IntegrityError

import aiofiles
from ics import Calendar, Event
from sanic import Sanic, json, Request
from sanic.response import text
from sanic_mail import Sanic_Mail
from sanic_cors import CORS, cross_origin
from Database import Database
from env import HOST, PORT, DATABASE, MAIL_SENDER, MAIL_SENDER_PASSWORD, MAIL_SEND_HOST, MAIL_SEND_PORT, MAIL_TLS, \
    MAIL_START_TLS

app = Sanic("Schedulio")
CORS(app, resources={r"/*":{"origins":"*"}})

app.config.update({
    "MAIL_SENDER": MAIL_SENDER,
    "MAIL_SENDER_PASSWORD": MAIL_SENDER_PASSWORD,
    "MAIL_SEND_HOST": MAIL_SEND_HOST,
    "MAIL_SEND_PORT": MAIL_SEND_PORT,
    "MAIL_TLS": MAIL_TLS,
    "MAIL_START_TLS": MAIL_START_TLS
})
sender = Sanic_Mail(app)
db = Database(DATABASE)


@app.get("/")
def hello(request: Request):
    return text("Hi 😎")


@app.route("/sign_up", methods=["POST"])
@cross_origin(app)
def sign_up(request: Request):
    try:
        return text(db.sign_up_and_get_token(request.form.get("account"), request.form.get("password")))
    except IntegrityError:
        return json({"error": "Account already exists"}, status=409)


@app.route("/log_in", methods=["POST"])
@cross_origin(app)
def log_in(request: Request):
    try:
        return text(db.login_and_get_token(request.form.get("account"), request.form.get("password")))
    except TypeError:
        return json({"error": "Invalid account or password"}, status=401)


@app.get("/mail/send")
async def send(request: Request):
    if db.check_if_token_exist(request.cookies.get('token')):
        return json({"result": "401 Unauthorized"})
    if request.args.get("email") is None:
        return json({"result": "400 Bad Request"})

    await request.app.ctx.send_email(
        targetlist=request.args.get("email"),
        subject="測試傳送",
        content="測試傳送uu"
    )
    return json({"result": "200 OK"})


@app.get("/mail/invite")
async def send_invite(request):
    if db.check_if_token_exist(request.cookies.get('token')):
        return json({"result": "401 Unauthorized"})
    if request.args.get("email") is None:
        return json({"result": "400 Bad Request"})

    c = Calendar()
    e = Event()
    e.name = "My cool event"
    e.begin = "2023-05-17 12:00:00"  # +8 hours
    e.end = "2023-05-17 13:00:00"  # +8 hours
    c.events.add(e)
    filename = "".join(random.choice(string.ascii_letters + string.digits) for _ in range(10)) + ".ics"
    with open("invitations/" + filename, "w") as my_file:
        my_file.writelines(c.serialize_iter())

    attachments = {}
    async with aiofiles.open("invitations/" + filename, "rb") as f:
        attachments[e.name + ".ics"] = await f.read()
    await request.app.ctx.send_email(
        targetlist=request.args.get("email"),
        subject="測試傳送",
        content="測試傳送uu",
        attachments=attachments
    )
    os.remove("invitations/" + filename)
    return json({"result": "200 OK"})

if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=True)
