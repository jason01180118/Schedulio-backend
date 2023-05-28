import os
import random
import string
from sqlite3 import IntegrityError

import aiofiles
from ics import Calendar, Event
from sanic import Sanic, json, Request
from sanic.response import text, redirect
from sanic_mail import Sanic_Mail
from sanic_cors import CORS, cross_origin
from Database import Database
from env import HOST, PORT, FRONTEND_PORT, DATABASE, MAIL_SENDER, MAIL_SENDER_PASSWORD, MAIL_SEND_HOST, MAIL_SEND_PORT, MAIL_TLS, \
    MAIL_START_TLS
from get_calendar import GoogleAPIClient

app = Sanic("Schedulio")
CORS(app, resources={r"/*": {"origins": "*", "supports_credentials": True}})

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


@app.post("/sign_up")
@cross_origin(app)
def sign_up(request: Request):
    try:
        data = request.json.get("data")
        db.sign_up(data["account"], data["password"])
        return json({"result": "200 OK"})
    except IntegrityError:
        return json({"error": "Account already exists"}, status=409)


@app.post("/log_in")
@cross_origin(app)
def log_in(request: Request):
    try:
        data = request.json.get("data")
        return text(db.login_and_get_session(data["account"], data["password"]))
    except TypeError:
        return json({"error": "Invalid account or password"}, status=401)


@app.get("/get_calendar/<account>")
async def view_other_calendar(request: Request, account: str):
    is_not_pass_auth = await check_session(request)
    if is_not_pass_auth:
        return json({"result": "401 Unauthorized"}, status=401)

    googleCalendarAPI = GoogleAPIClient()
    events = googleCalendarAPI.getEvent(account = account)

    email = db.get_first_email_by_account(account)
    viewer_account = db.get_account_by_session(request.args.get("session"))
    await request.app.ctx.send_email(
        targetlist= email,
        subject=f"抓到！{viewer_account} 偷看了你的行事曆！",
        content=f"您好：\n\n請小心 {viewer_account}，因為他看了你的行事曆。\n你也可以查看他的行事曆，因為這樣才公平。\n\n點此查看他的行事曆：http://{HOST}:{FRONTEND_PORT}/{viewer_account}"
    )

    return events


@app.get("/mail/invite")
async def send_invite(request: Request):
    is_not_pass_auth = await check_session(request)
    if is_not_pass_auth:
        return json({"result": "401 Unauthorized"}, status=401)
    if request.args.get("email") is None:
        return json({"result": "400 Bad Request"}, status=400)

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


@app.route("/get_calendar")
def get_calendar(request: Request):
    googleCalendarAPI = GoogleAPIClient()
    events = googleCalendarAPI.getEvent(session= request.args.get("session"))
    return json(events)


@app.route("/add_email")
def add_email(request: Request):
    googleCalendarAPI = GoogleAPIClient()
    googleCalendarAPI.addNewAccountAndGetCalendar(request.args.get("session"))
    return redirect(f"http://{HOST}:{FRONTEND_PORT}/calendar")


async def check_session(request: Request):
    return not db.check_if_session_exist(request.args.get("session"))


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=True)
