class ArtistSong:
	def __init__(self, line=None):
		self.song_id = ''
		self.artist_id = ''
		self.publish_time = ''
		self.song_init_plays = 0
		self.language = ''
		self.gender = ''
		if line:
			self.readFromLine(line)

	def __str__(self):
		return 'test...'

	def readFromLine(self, line):
		words = line.split(',')
		self.song_id = words[0].strip()
		self.artist_id = words[1].strip()
		self.publish_time = words[2].strip()
		self.song_init_plays = int(words[3].strip())
		self.language = words[4].strip()
		self.gender = words[5].strip()