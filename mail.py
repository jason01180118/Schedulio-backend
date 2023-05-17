import aiofiles
import os
from sanic import Sanic
from sanic.response import json
from sanic_mail import Sanic_Mail
from ics import Calendar, Event
import random, string
from env import MAIL_SENDER, MAIL_SENDER_PASSWORD, MAIL_SEND_HOST, MAIL_SEND_PORT, MAIL_TLS, MAIL_START_TLS, MAIL_HOST, MAIL_PORT
from database import TOKEN

from cors import add_cors_headers




app = Sanic(__name__)

# Fill in CORS headers
app.register_middleware(add_cors_headers, "response")
app.config.update({
    'MAIL_SENDER': MAIL_SENDER,
    'MAIL_SENDER_PASSWORD': MAIL_SENDER_PASSWORD,
    'MAIL_SEND_HOST': MAIL_SEND_HOST,
    'MAIL_SEND_PORT': MAIL_SEND_PORT,
    'MAIL_TLS': MAIL_TLS,
    'MAIL_START_TLS': MAIL_START_TLS
})
sender = Sanic_Mail(app)


@app.get('/mail/send')
async def send(request):
    if request.args.get("token") != TOKEN :
        return json({"result": "401 Unauthorized"})
    if request.args.get("email") == None:
        return json({"result": "400 Bad Request"})

    await request.app.ctx.send_email(
        targetlist = request.args.get("email"),
        subject = "測試傳送",
        content = "測試傳送uu"
    )
    return json({"result": "200 OK"})

@app.get('/mail/invite')
async def send_invite(request):
    if request.args.get("token") != TOKEN :
        return json({"result": "401 Unauthorized"})
    if request.args.get("email") == None:
        return json({"result": "400 Bad Request"})

    c = Calendar()
    e = Event()
    e.name = "My cool event"
    e.begin = '2023-05-17 12:00:00' # +8 hours
    e.end = '2023-05-17 13:00:00'   # +8 hours
    c.events.add(e)
    filename = ''.join(random.choice(string.ascii_letters + string.digits) for x in range(10)) + '.ics'
    with open('invitations/'+filename, 'w') as my_file:
        my_file.writelines(c.serialize_iter())

    attachments = {}
    async with aiofiles.open('invitations/'+filename, "rb") as f:
        attachments[e.name+'.ics'] = await f.read()
    await request.app.ctx.send_email(
        targetlist = request.args.get("email"),
        subject = "測試傳送",
        content = "測試傳送uu",
        attachments = attachments
    )
    os.remove('invitations/'+filename)
    return json({"result": "200 OK"})

if __name__ == "__main__":
    app.run(host=MAIL_HOST, port=MAIL_PORT, debug=True)