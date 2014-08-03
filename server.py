#!/usr/bin/env python2

import colorsys
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

#@route("/colour-chart")
#def col():
#	global h, v
#	h = float(request.params.get('new_h'))
#	v = 0.1
#	output = ""
#	for i in xrange(30):
#	  output += "<div style='background-color:" + next_colour() + ";min-width=400px;min-height=30px'>&nbsp;</div>"
#	return output

@route("/room")
def sub():
	# if there are already new messages don't do this
	the_msg = queue[-1]
	response.add_header("Cache-Control", "public, max-age=0, no-cache")
	if the_msg["event"].wait(25):
		return {"msg": the_msg["msg"], "colour": the_msg["colour"]}
	return {}

if __name__ == "__main__":
	bottle.run(port=9090, server="gevent")	
	
