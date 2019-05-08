#!/usr/bin/env python2
import colorsys
import random
from datetime import datetime, timedelta
from gevent import monkey; monkey.patch_all()
from threading import Event, Timer
from collections import defaultdict
from bottle import run, route, request, response, redirect, static_file, error

queue = defaultdict(lambda: {"msgs": [], "last_msg_time": datetime.now(), "current_colour": 0.2, "last_msg_id": 0, "event": Event()})

def send_message(msg, colour, room):
	queue[room]["last_msg_id"] += 1
	queue[room]["msgs"].append({"msg": msg, "colour": colour, "id": queue[room]["last_msg_id"]})
	queue[room]["event"].set()
	queue[room]["event"] = Event()
	if (len(queue[room]["msgs"]) > 20):
		queue[room]["msgs"].pop(0)
	queue[room]["last_msg_time"] = datetime.now()

def purge_dead_rooms(every=43200, ttl=259200): #43200s = 12h, 259200s = 72h = 3d
	for room in [room for room in queue if queue[room]["last_msg_time"] < datetime.now() - timedelta(seconds=ttl)]:
		del queue[room]
	Timer(every, purge_dead_rooms).start()

def next_colour(room):
	queue[room]["current_colour"] += 0.38194 * (1 + int(random.random() * 3))
	rgb = colorsys.hls_to_rgb(queue[room]["current_colour"], 0.80, 1)
	return '#%02X%02X%02X' % tuple([ int(quant * 255) for quant in rgb ])

@route('<file:re:^/(robots\\.txt|favicon\\.ico|style\\.css)$>')
def serve_static_routes(file):
	return static_file(file, root='static/')

@error(404)
def notfound404(error):
	return static_file('404.html', root='static/')

@route('/')
def home():
	return static_file('index.html', root='static/')

@route('/s/<file:path>')
def serve_static_resources(file):
	return static_file(file, root='static/client/')

@route('/<room>')
@route('/<room>/')
@route('/r/<room>')
def canonicalise_room_url(room):
	redirect("/r/{}/".format(room), 301)

@route('/r/<room>/')
def room_home(room):
        html = ""
        with open('static/room.html', 'r') as htmlfile:
            html = htmlfile.read()
	yield html

        last_message = 0
        while True:
            for msg in all_messages_since(last_message, room):
                yield msgtohtml(msg)
            last_message = queue[room]["last_msg_id"]
            if not queue[room]["event"].wait(25):
                yield " "

def msgtohtml(msg):
    return '<div style="color:' + msg["colour"] + '">' + msg["msg"] + '</div>\n'

def get_colour(req, room, resp):
	colour = req.cookies.get("Colour")
	if not colour:
		colour = next_colour(room)
		resp.set_cookie("Colour", colour, httponly=True)
	return colour

@route("/r/<room>/room", method="POST")
def pub(room):
	message = request.params.get('message')
	message = message[:1000] if message else ""
	colour = get_colour(request, room, response)
	send_message(message, colour, room)
	redirect("/r/{}/chatbox".format(room), 302)

def format_message(msg):
	return {"msg": msg["msg"], "colour": msg["colour"], "id": msg["id"]}

def all_messages_since(when, room):
	return [format_message(msg) for msg in queue[room]["msgs"] if msg["id"] > when]

@route("/r/<room>/room")
def sub(room):
	try:
		lastReceivedMessage = int(request.query['since'])
	except KeyError, ValueError:
		lastReceivedMessage = None
	response.add_header("Cache-Control", "public, max-age=0, no-cache")

	if not lastReceivedMessage or queue[room]["last_msg_id"] > lastReceivedMessage:
		if len(queue[room]["msgs"]) > 0: return all_messages_since(lastReceivedMessage, room)
	if queue[room]["event"].wait(25):
		return {"msgs":[format_message(queue[room]["msgs"][-1])]}
	return {"msgs":[]}

@route("/r/<room>/chatbox")
def chatbox(room):
    return static_file('chatbox.html', root='static/')

if __name__ == "__main__":
	purge_dead_rooms()
	run(port=9092, server="gevent")
