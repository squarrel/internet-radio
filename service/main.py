from time import sleep, time
from kivy.lib import osc
from kivy.utils import platform
from jnius import autoclass

serviceport = 3000
activityport = 3001
radio_played = 'http://bumbum-stream.netlogic.rs:8000/'

if platform == 'android':
	MediaPlayer = autoclass('android.media.MediaPlayer')
	mPlayer = MediaPlayer()
	mPlayer.setDataSource(radio_played)

def check_state(message, *args):
	if mPlayer.isPlaying():
		osc.sendMsg('/is_playing', ['is playing', ], port=activityport)
	elif not mPlayer.isPlaying():
		osc.sendMsg('/is_stopped', ['is stopped', ], port=activityport)

def exit_service():
	osc.sendMsg('/off', ['exit service', ], port=activityport)

def start(message, *args):
	if not mPlayer.isPlaying():
		mPlayer.prepare() #prepareAsync()
		mPlayer.start()
		print 'Start'

def stop(message, *args):
	if mPlayer.isPlaying():
		mPlayer.stop()
		print 'Stop'

if __name__ == '__main__':
	osc.init()
	oscid = osc.listen(ipAddr='127.0.0.1', port=serviceport)
	osc.bind(oscid, start, '/play')
	osc.bind(oscid, stop, '/stop')
	osc.bind(oscid, check_state, '/check')
	
	while True:
		osc.readQueue(oscid)
		sleep(.1)
