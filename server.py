#!/usr/bin/env python2

import colorsys
import time
import random
from gevent import monkey; monkey.patch_all()
from threading import Event, Timer
from collections import defaultdict

import bottle
from bottle import route, request, response, redirect, template

bottle.TEMPLATE_PATH = ["static/"]

latest_message_id = 0
def create_message():
	global latest_message_id
	latest_message_id += 1
	return { "msg": "", "colour": "", "event": Event(), "id": latest_message_id}

def send_message(msg, colour, room):
	queue[room]["msgs"].append(create_message())
	queue[room]["msgs"][-2]["msg"] = msg
	queue[room]["msgs"][-2]["colour"] = colour
	queue[room]["msgs"][-2]["event"].set()
	if (len(queue[room]["msgs"]) > 20):
		queue[room]["msgs"].pop(0)
	queue[room]["last"] = int(time.time())

queue = defaultdict(lambda: {"msgs": [create_message()], "last": 0})

def purge_dead_rooms(every=43200, ttl=259200): #43200s = 12h, 259200s = 72h = 3d
	for room in list(room for room in queue if queue[room]["last"] != 0 and queue[room]["last"] < int(time.time()) - ttl):
		del queue[room]
	Timer(every, purge_dead_rooms).start()

current_colour = (0.2, 0.1)
def next_colour():
	global current_colour
	(h, v) = current_colour
	h += 0.38194
	v += (1.0 - v) * 0.02
	rgb = colorsys.hsv_to_rgb(h, 1, 1.0 - v)
	current_colour = (h, v)
	return '#%02X%02X%02X' % tuple([ int(quant * 256) for quant in rgb ])

@route('/robots.txt')
def serve_robots():
	return bottle.static_file('robots.txt', root='static/')

@route('/favicon.ico')
def serve_facicon():
	return bottle.static_file('favicon.ico', root='static/')

@route('/')
def home():
	redirect('/-/')

@route('/<room>')
def trailing_slashfix(room):
	redirect("/{}/".format(room))

@route('/<room>/')
def room_home(room):
	return template("index.html", room=room)

def get_colour(req, resp):
	colour = req.cookies.get("Colour")
	if not colour:
		colour = next_colour()
		resp.set_cookie("Colour", colour, path="/", httponly=True)
	return colour

@route("/<room>/room", method="POST")
def pub(room):
	message = request.params.get('message')
        message = message[:1000] if message else ""
	colour = get_colour(request, response)
	send_message(message, colour, room)
	return "OK"

def format_message(msg):
	return {"msg": msg["msg"], "colour": msg["colour"], "id": msg["id"]}

def all_messages_since(when, room):
	return {"msgs": [format_message(msg) for msg in queue[room]["msgs"][:-1] if msg["id"] > when]}

@route("/<room>/room")
def sub(room):
	try:
		lastReceivedMessage = int(request.query['since'])
	except KeyError, ValueError:
		lastReceivedMessage = None
	response.add_header("Cache-Control", "public, max-age=0, no-cache")

	the_msg = queue[room]["msgs"][-1]
	if not lastReceivedMessage or the_msg["id"] - 1 != lastReceivedMessage:
		if len(queue[room]["msgs"]) > 1: return all_messages_since(lastReceivedMessage, room)
	if the_msg["event"].wait(25):
		return {"msgs":[format_message(the_msg)]}
	return {"msgs":[]}

if __name__ == "__main__":
	purge_dead_rooms()
	bottle.run(port=9092, server="gevent")

