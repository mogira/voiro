import requests, copy
import datetime, os
import tempfile, wave, time

try:
	import objc_util
except ImportError:
	use_pythonista = False
except:
	raise
else:
	use_pythonista = True



class VoiroVoice:
	def __init__(
		self,
		name : str,
		text : str,
		api_key : str,
		pitch : float = 1.0,
		range : float = 1.0,
		rate : float = 1.0,
		volume : float = 1.0,
		auto_strip : bool = True
	):
		self.api_key = api_key
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
		self.auto_strip = auto_strip

	def request(self):
		data = self.convert_audioL16_to_PCM(
			bytearray(
				request_with_ssml(
					self.api_key,
					self.ssml
		)))
		if self.auto_strip:
			data = self.strip(data)
		self.data = data
		return self

	def getData(self):
		return bytes(self.data)

	def play(
		self,
		blocking : bool = True
	):
		with tempfile.NamedTemporaryFile(suffix='.wav') as tmpf:
			save_as_wav(
				tmpf.name,
				self.getData()
			)
			play_wav(tmpf.name, blocking=blocking)

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
	d = {
		'結月ゆかり': 'sumire',
		'弦巻マキ': 'maki',
		'月読アイ': 'anzu'
	}
	try:
		return d[name]
	except KeyError:
		pass
	if name in d.values():
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
		w.setsampwidth(2) #16bit=2byte
		w.setframerate(16000)
		w.writeframes(data)


def play_wav(
	fname : str,
	blocking : bool = True
):
	if use_pythonista:
		p = objc_util.ObjCClass('AVPlayer').playerWithURL_(objc_util.nsurl(fname))
		duration = (lambda x: x.a / x.b)(p.currentItem().asset().duration())
		p.play()
		if blocking:
			time.sleep(duration)
	else:
		print('Not implemented')


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
	v = VoiroVoice(
		'結月ゆかり',
		'ゆかりさんのテストです、心して聞きなさい。',
		api_key,
		pitch = 1.1,
		range = 1.3,
		rate = 1.2
	)
	v.request()
	v.play(blocking = False)
	print()
	return v

if __name__ == '__main__':
	v = main()

