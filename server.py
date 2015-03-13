#!/usr/bin/env python2

import colorsys
import time
import random
from gevent import monkey; monkey.patch_all()
from threading import Event
from collections import defaultdict

import bottle
from bottle import route, request, response, redirect

latest_message_id = 0
def create_message():
	global latest_message_id
	latest_message_id += 1
	return { "msg": "", "colour": "", "event": Event(), "id": latest_message_id }

def send_message(msg, colour, room):
	queue[room].append(create_message())
	queue[room][-2]["msg"] = msg
	queue[room][-2]["colour"] = colour
	queue[room][-2]["event"].set()
	if (len(queue[room]) > 20):
		queue[room].pop(0)

queue = defaultdict(lambda: [create_message()])

current_colour = (0.2, 0.1)
def next_colour():
	global current_colour
	(h, v) = current_colour
	h += 0.38194
	v += (1.0 - v) * 0.02
	rgb = colorsys.hsv_to_rgb(h, 1, 1.0 - v)
	current_colour = (h, v)
	return '#%02X%02X%02X' % tuple([ int(quant * 256) for quant in rgb ])

@route('/')
def home():
	redirect('/r/-/')

@route('/r/<room>/')
def room_home(room):
	return bottle.static_file("index.html", root="static/")

@route('/r/<room>')
def trailing_slashfix(room):
	redirect("/r/{}/".format(room))

def get_colour(req, resp):
	colour = req.cookies.get("Colour")
	if not colour:
		colour = next_colour()
		resp.set_cookie("Colour", colour, path="/r/", httponly=True)
	return colour

@route("/r/<room>/room", method="POST")
def pub(room):
	message = request.params.get('message')
        message = message[:1000] if message else ""
	colour = get_colour(request, response)
	send_message(message, colour, room)
	return "OK"

def format_message(msg):
	return {"msg": msg["msg"], "colour": msg["colour"], "id": msg["id"]}

def all_messages_since(when, room):
	return {"msgs": [format_message(msg) for msg in queue[room][:-1] if msg["id"] > when]}

@route("/r/<room>/room")
def sub(room):
	try:
		lastReceivedMessage = int(request.query['since'])
	except KeyError, ValueError:
		lastReceivedMessage = None
	response.add_header("Cache-Control", "public, max-age=0, no-cache")

	the_msg = queue[room][-1]
	if not lastReceivedMessage or the_msg["id"] - 1 != lastReceivedMessage:
		return all_messages_since(lastReceivedMessage, room)
	if the_msg["event"].wait(25):
		return {"msgs":[format_message(the_msg)]}
	return {"msgs":[]}

if __name__ == "__main__":
	bottle.run(port=9092, server="gevent")

