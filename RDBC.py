"""
name: Remote Desktop Browser Controller
author: Bryan Angelo Pedrosa
date started: 3/9/2020
date finished: 3/11/2020
description: A simple web-based remote desktop controller. Yes, it's multiplatform.
"""

from __future__ import division
import os
import sys
import time

# hardware interface
import mouse
import keyboard

# check python version
major_version = sys.version_info.major

# default screenshot name
scr_img = "./scr.png"

# server port
srv_port = 1337

# mouse click buttons
butts = ["left","middle","right"]


if major_version == 2:
  import thread
  import gtk.gdk as Gdk
  from urlparse import urlparse, parse_qsl
  from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
elif major_version == 3:
  import _thread as thread
  from gi.repository import Gdk
  from urllib.parse import urlparse, parse_qsl
  from http.server import BaseHTTPRequestHandler, HTTPServer

# get current screen resolution
w = Gdk.get_default_root_window()
if major_version == 2:
  sz = w.get_size()
elif major_version == 3:
  sz = w.get_geometry()[2:4]

#print("My screen size: {0}".format(sz)) # rubbber ducky:)

def get_screenData():
  while 1:
    # get screenshot data
    if major_version == 2:
      pb = Gdk.Pixbuf(Gdk.COLORSPACE_RGB,False,8,sz[0],sz[1])
      pb = pb.get_from_drawable(w,w.get_colormap(),0,0,0,0,sz[0],sz[1])
    elif major_version == 3:
      pb = Gdk.pixbuf_get_from_window(w, 0, 0, sz[0], sz[1])
    
    # save screenshot
    if pb != None:
      if major_version == 2:
        pb.save("./scr.png","png")
      elif major_version == 3:
        pb.savev("./scr.png","png", [], [])
    
    # delay 1 sec
    time.sleep(0.9)


# run a new thread (screenshot)
thread.start_new_thread(get_screenData,())


# HTTP Server Mainloop
class ServerHandler(BaseHTTPRequestHandler):
  def do_HEAD(self):
    self.send_response(200)
    self.send_header("Content-type", "image/png")
    if os.path.exists(scr_img):
      self.send_header("Content-length", os.stat(scr_img).st_size)
    self.end_headers()
    
  def do_GET(self):
    self.do_HEAD() # set header
    
    # parse url arguments
    url_args = dict(parse_qsl(urlparse(self.path).query))
    
    # if command exists
    if "cmd" in url_args:
      if url_args["cmd"] == "snap":
        # reply with screenshot
        if os.path.exists(scr_img):
          with open(scr_img, 'rb+') as f:
            self.wfile.write(f.read())
      elif url_args["cmd"] == "mouse_position":
        # calculate `client-server` mouse coordinates
        POS_X = float(url_args["pos_x"])
        POS_Y = float(url_args["pos_y"])
        CAX = float(url_args["coord_x"])
        CAY = float(url_args["coord_y"])
        CBX = float(sz[0])
        CBY = float(sz[1])
        
        # precise coordinates ratio
        coord_x = int(round((CBX / CAX) * POS_X))
        coord_y = int(round((CBY / CAY) * POS_Y))
        
        # some rubbber duckies:)
        #print("my coordinates: {0} ; {1}".format(coord_x, coord_y))
        #print(CAX , CBX , CBX , CAX , CBX, POS_X, POS_Y, mouse.get_position())
        
        # move mouse
        mouse.move(coord_x,coord_y)
      elif url_args["cmd"] == "mouse_press":
        button = butts[int(url_args["button"])]
        mouse.press(button)
      elif url_args["cmd"] == "mouse_release":
        button = butts[int(url_args["button"])]
        mouse.release(button)
      elif url_args["cmd"] == "key_presses":
        # press a key (event keycode)
        charkeycode = int(url_args["keycode"])
        keyboard.send(charkeycode)

def run(server_class=HTTPServer, handler_class=ServerHandler, port=srv_port):
  server_address = ('', port)
  print("I'm running on port: {0}".format(srv_port))
  httpd = server_class(server_address, handler_class)
  httpd.serve_forever()


run()


