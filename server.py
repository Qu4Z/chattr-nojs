#!/usr/bin/env python2

import time
import random
from gevent import monkey; monkey.patch_all()
from threading import Event
import bottle
from bottle import route, request, response

def create_message():
	return { "msg": "", "colour": "", "event": Event() }
def send_message(msg, colour):
	queue.append(create_message())
	queue[-2]["msg"] = msg
	queue[-2]["colour"] = colour
	queue[-2]["event"].set()

def next_colour():
	r = lambda: random.randint(50, 200)
	return '#%02X%02X%02X' % (r(),r(),r())

queue = [create_message()]

@route('/')
def home():
	return bottle.static_file("index.html", root=".")

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

@route("/room")
def sub():
	# if there are already new messages don't do this
	the_msg = queue[-1]
	response.add_header("Access-Control-Allow-Origin", "http://localhost:9090")
	if the_msg["event"].wait(25):
		return {"msg": the_msg["msg"], "colour": the_msg["colour"]}
	return {}

if __name__ == "__main__":
	bottle.run(port=9090, server="gevent")	
	
