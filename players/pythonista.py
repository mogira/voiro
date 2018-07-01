import objc_util
import ctypes
import os, sys, time

if __name__ == '__main__':
	from abcplayer import WavPlayer
else:
	from .abcplayer import WavPlayer


class AVAudioPlayer(WavPlayer):
	def __init__(self, fpath : str = ''):
		self.player = None
		self.isPlayed = False
		if fpath != '':
			self.setFilePath(fpath)

	def setFilePath(self, fpath : str):
		if not os.path.exists(fpath):
			ex_fpath = os.path.expanduser(fpath)
			if os.path.exists(ex_fpath):
				fpath = ex_fpath
			else:
				raise FileNotFoundError(fpath)
		self.player = objc_util.ObjCClass('AVAudioPlayer').alloc()
		self.player.initWithContentsOfURL_error_(objc_util.nsurl(fpath), None)
		self.fpath = fpath
		self.isPlayed = False

	def isDone(self):
		return (self.player is not None and not self.player.isPlaying() and self.isPlayed)

	def play(
		self,
		blocking : bool = True,
		sleep_rate : float = 0.1
	):
		self.isPlayed = True
		self.player.play()
		if blocking:
			while not self.isDone():
				time.sleep(sleep_rate)


def main():
	return AVAudioPlayer('~/Documents/180525_083755.wav')

if __name__ == '__main__':
	p = main()
