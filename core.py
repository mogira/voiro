import requests, copy
import datetime, os
import tempfile, wave, time
from concurrent import futures


class VoiroVoiceQueue:
	def __init__(
		self,
		name : str,
		api_key : str,
		executor : futures.Executor,
		player_class : type,
		pitch : float = 1.0,
		range : float = 1.0,
		rate : float = 1.0,
		volume : float = 2.0 #volume=1.0 is too small!!
	):
		lc = locals()
		for a in [
			'name', 'api_key',
			'executor', 'player_class',
			'pitch', 'range', 'rate',
			'volume'
		]:
			setattr(self, a, lc[a])
		self.list = []

	def push(self, text : str):
		v = VoiroVoice(
			name = self.name,
			text = text,
			api_key = self.api_key,
			player_class = self.player_class,
			pitch = self.pitch,
			range = self.range,
			rate = self.rate,
			volume = self.volume
		)
		self.list.append(
			self.executor.submit(v.request)
		)

	def play_all(
		self,
		blocking : bool = True,
		sleep_rate : float = 0.1
	):
		for s in self.list:
			vv = s.result()
			vv.play(blocking, sleep_rate)


class VoiroVoice:
	def __init__(
		self,
		name : str,
		text : str,
		api_key : str,
		player_class : type,
		pitch : float = 1.0,
		range : float = 1.0,
		rate : float = 1.0,
		volume : float = 2.0 #volume=1.0 is too small!!
	):
		self.api_key = api_key
		self.player = player_class()
		self.name = normVoiroName(name)
		self.text = text
		self.ssml = (
			'<?xml version="1.0" encoding="utf-8" ?>'
			+ '<speak version="1.1">'
			+ '<voice name="%s">'
			+ '<prosody'
			+ ' pitch="%s"'
			+ ' range="%s"'
			+ ' rate="%s"'
			+ ' volume="%s"'
			+ '>'
			+ '%s'
			+ '</prosody>'
			+ '</voice>'
			+ '</speak>'
		) % (
			self.name, pitch, range, rate, volume, text
		)

	def request(self):
		data = self.convert_audioL16_to_PCM(
			bytearray(
				request_with_ssml(
					self.api_key,
					self.ssml
		)))
		data = self.strip(data)
		self.data = data
		return self

	def getData(self):
		return bytes(self.data)

	def isDone(self):
		return self.player.isDone()

	def play(
		self,
		blocking : bool = True,
		sleep_rate : float = 0.1
	):
		with tempfile.NamedTemporaryFile(suffix='.wav') as tmpf:
			save_as_wav(
				tmpf.name,
				self.getData()
			)
			self.player.setFilePath(tmpf.name)
			self.player.play(blocking, sleep_rate)

	def save(
		self,
		fname : str = '',
		path : str = ''
	):
		if fname == '':
			fname = datetime.datetime.now().strftime('%y%m%d_%H%M%S') + '.wav'
		if path == '':
			path = home_dir()
		fpath = os.path.join(path, fname)
		save_as_wav(
			fpath, 
			self.getData()
		)
		return fpath

	@staticmethod
	def convert_audioL16_to_PCM(
		data : bytearray
	):
		#audio/L16 responce data is 16bit(2byte) BIG endian, so convert to 16bit LITTLE endian
		half_len = int(len(data) / 2)
		for i in range(half_len):
			data[i*2], data[i*2+1] = data[
				i*2+1], data[i*2]
		return data

	@staticmethod
	def strip(
		data : bytearray
	):
		l = len(data)-1
		while data[l] == 0:
			l -= 1
		return data[:l]


def normVoiroName(name : str):
	conv_list = {
		'結月ゆかり': 'sumire',
		'弦巻マキ': 'maki',
		'月読アイ': 'anzu'
	}
	name_list = [
		"nozomi", "seiji", "akari",
		"anzu", "hiroshi", "kaho",
		"koutarou", "maki", "nanako",
		"osamu", "sumire"
	]
	try:
		return conv_list[name]
	except KeyError:
		pass
	if name in name_list:
		return name
	raise ValueError('"%s" is not in' % name)


def home_dir():
	return os.path.expanduser('~' if not use_pythonista else '~/Documents')


def save_as_wav(
	fpath : str,
	data : bytes
):
	with wave.open(fpath, 'w') as w:
		w.setnchannels(1) #monoral only
		w.setsampwidth(2) #16bit = 2byte
		w.setframerate(16000)
		w.writeframes(data)


def request_with_ssml(
	api_key : str,
	ssml : str
):
	payload = ssml.encode('utf-8')
	header = {
		'Content-Type':
			'application/ssml+xml',
		'Accept':
			'audio/L16',
		'Content-Length':
			str(len(payload))
	}
	r = requests.post(
		'https://api.apigw.smt.docomo.ne.jp/aiTalk/v1/textToSpeech?APIKEY=%s' % api_key,
		data = payload,
		headers = header
	)
	if r.status_code != 200:
		s = 'status_code = %d\n' % r.status_code
		s += 'headers = {\n'
		for k,v in header.items():
			s += (
				'\t"%s":\n'
				+ '\t\t"%s"\n'
			) % (k, v)
		s += '}\n'
		s += "payload = '''\n"
		s += '%s\n' % payload.decode('utf-8')
		s += "'''"
		raise Exception(s)
	return r.content



def main():
	api_key = 'YOUR_API_KEY'

	vv = VoiroVoice(
		'結月ゆかり',
		'発声テストです。',
		api_key,
		AVAudioPlayer,
		pitch = 1.1,
		range = 1.3,
		rate = 1.2
	)
	vv.request()
	vv.play(blocking = True)

	vvq = VoiroVoiceQueue(
		'結月ゆかり',
		api_key,
		futures.ThreadPoolExecutor(),
		AVAudioPlayer,
		pitch = 1.1,
		range = 1.3,
		rate = 1.2
	)
	vvq.push('発声テストです')
	vvq.push('テストテスト')
	vvq.push('test_text')
	vvq.play_all(blocking = True)
	

if __name__ == '__main__':
	from players.pythonista import AVAudioPlayer
	main()

