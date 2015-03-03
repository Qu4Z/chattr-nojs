#!/usr/bin/env python2

import colorsys
import time
import random
from gevent import monkey; monkey.patch_all()
from threading import Event
import bottle
from bottle import route, request, response

latest_message_id = 0
def create_message():
	global latest_message_id
	latest_message_id += 1
	return { "msg": "", "colour": "", "event": Event(), "id": latest_message_id }

def send_message(msg, colour):
	queue.append(create_message())
	queue[-2]["msg"] = msg
	queue[-2]["colour"] = colour
	queue[-2]["event"].set()
	if (len(queue) > 20):
		queue.pop(0)

queue = [create_message()]

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
	return bottle.static_file("index.html", root="static/")

def get_colour(req, resp):
	colour = req.cookies.get("Colour")
	if not colour:
		colour = next_colour()
		resp.set_cookie("Colour", colour)
	return colour

@route("/room", method="POST")
def pub():
	message = request.params.get('message')
	colour = get_colour(request, response)
	send_message(message, colour)
	return "OK"

@route("/<filename>")
def serve_static(filename):
    return bottle.static_file(filename, root="static/")

def format_message(msg):
	return {"msg": msg["msg"], "colour": msg["colour"], "id": msg["id"]}

def all_messages_since(when):
	return {"msgs": [format_message(msg) for msg in queue[:-1] if msg["id"] > when]}

@route("/room")
def sub():
	try:
		lastReceivedMessage = int(request.query['since'])
	except KeyError, ValueError:
		lastReceivedMessage = None # Populate from GET parameter
	the_msg = queue[-1]
	if not lastReceivedMessage or the_msg["id"] - 1 != lastReceivedMessage:
	  return all_messages_since(lastReceivedMessage)
	response.add_header("Cache-Control", "public, max-age=0, no-cache")
	if the_msg["event"].wait(25):
		return {"msgs":[format_message(the_msg)]}
	return {"msgs":[]}

if __name__ == "__main__":
	bottle.run(port=9091, server="gevent")	
	
