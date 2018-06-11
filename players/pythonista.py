import objc_util
import ctypes
import os, sys, time

sys.path.append('..')
from core import WavPlayer


class CMTime(objc_util.Structure):
	_fields_ = [
		('value', ctypes.c_int64),
		('timescale', ctypes.c_int32),
		('flags', ctypes.c_uint32),
		('epoch', ctypes.c_int64)
	]

objc_util.c.CMTimeMakeWithSeconds.argtypes = [
	ctypes.c_double, ctypes.c_int32
]
objc_util.c.CMTimeMakeWithSeconds.restype = CMTime


class AVPlayer(WavPlayer):
	def __init__(self, fpath : str = ''):
		if fpath != '':
			self.setFilePath(fpath)

	def setFilePath(self, fpath : str):
		if not os.path.exists(fpath):
			raise FileNotFoundError(fpath)
		self.player = objc_util.ObjCClass('AVPlayer').playerWithURL_(objc_util.nsurl(fpath))
		self.fpath = fpath

	def isDone(self):
		return (self.player.rate() == 0.0)

	def seekHead(self):
		self.player.seekToTime_(
			objc_util.c.CMTimeMakeWithSeconds(0, 1),
			argtypes = [CMTime],
			restype = None
		)


	def play(
		self,
		blocking : bool = True,
		sleep_rate : float = 0.1
	):
		self.seekHead()
		self.player.play()
		if blocking:
			while not self.isDone():
				time.sleep(sleep_rate)



def main():
	a = AVPlayer(os.path.expanduser('~/Documents/180525_083755.wav'))
	a.play()

if __name__ == '__main__':
	main()

