from abc import ABC, abstractmethod

class WavPlayer(ABC):
	@abstractmethod
	def setFilePath(self, fpath : str):
		pass

	@abstractmethod
	def isDone(self):
		pass

	@abstractmethod
	def play(self, blocking : bool):
		pass

