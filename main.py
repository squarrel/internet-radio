# -*- coding: utf-8 -*-

# Radio App

__version__ = '1.0.0'

import kivy
kivy.require('1.8.0')
from kivy.app import App
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.properties import StringProperty, ListProperty, NumericProperty
from kivy.uix.widget import Widget
from kivy.uix.textinput import TextInput
from kivy.network.urlrequest import UrlRequest
from kivy.clock import Clock
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.lib import osc
#from kivy.base import EventLoop
from kivy.utils import platform
if platform == 'android':
	from jnius import autoclass
	from android import AndroidService
	

activityport = 3001
serviceport = 3000
active = False

class ImageButton(ButtonBehavior, Image):
	pass

class Menu(TabbedPanel):
	
	boja_play = StringProperty('images/play.png')	
	stanje_snimanja = StringProperty()
	pokretni_tekst = StringProperty("Rotating text")
	pos_x = NumericProperty(.5)	
	
	def __init__(self, **kwargs):
		super(Menu, self).__init__(**kwargs)
		Clock.schedule_interval(self.track_text, .07)
		Clock.schedule_interval(self.check, 1)

	def check(self, dt):
		if platform == 'android':
			App.get_running_app().check_state()			

	def track_text(self, dt):
		self.pos_x -= .005
		if self.pos_x < -.3:
			self.pos_x = 1.1
		if active:
			self.boja_play = 'images/play-active.png'
		else:
			self.boja_play = 'images/play.png'

menu = Menu()			
			
class MyApp(App):
	
	if platform == 'android':
		Wakelock = autoclass('org.myapp.Wakelock')
		wakelock = Wakelock()
	
	def build(self):
		#EventLoop.window.bind(on_keyboard=self.hook_keyboard)
		
		if platform == 'android':
			service = AndroidService('Sister Radio', 'running')
			service.start('service started!')
			self.service = service
			self.wakelock.start()
			
		osc.init()
		oscid = osc.listen(ipAddr='127.0.0.1', port=activityport)
		osc.bind(oscid, self.is_playing, '/is_playing')
		osc.bind(oscid, self.is_stopped, '/is_stopped')
		
		Clock.schedule_interval(lambda *x: osc.readQueue(oscid), 0)	
		
		menu = Menu()
		return menu
	
	def check_state(self):
		osc.sendMsg('/check', ['', ], port=serviceport)
					
	def play_radio(self):
		osc.sendMsg('/play', ['', ], port=serviceport)
				
	def stop_radio(self):
		osc.sendMsg('/stop', ['stop', ], port=serviceport)	
					
	# check if the radio is on, then change the color of the button.						
	def is_playing(self, message, *args):	
		print 'Radio is playing...'
		global active
		active = True
	
	# change the color of the Play button, depending on the state of the radio.
	def is_stopped(self, message, *args):
		print 'Radio is stopped...'
		global active
		active = False
		
	# stop the radio and stop the service.
	def izlaz(self):
		self.stop_radio()
		self.wakelock.release()
		if self.service:
			self.service.stop()
			
	# now turn off the service.
	def off(self, message, *args):
		if self.service:
			self.service.stop()
								
	def on_start(self):
		pass
		
	def on_pause(self):
		return True
	
	def on_resume(self):
		self.check_state()
			
	def on_stop(self):
		pass
		
	def open_settings(self):
		pass
	
	# override the Back hardware key
	'''def hook_keyboard(self, window, key, *largs):
		if key == 27: 
			
			#return True'''


if __name__ == '__main__':
	MyApp().run()
	
