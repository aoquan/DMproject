class UserAction:
	def __init__(self, line=None):
		self.user_id = ''
		self.song_id = ''
		self.gmt_create = ''
		self.action_type = ''
		self.ds = ''
		if line:
			self.readFromLine(line)

	def __str__(self):
		return self.user_id+','+self.song_id+","+self.gmt_create+','+self.action_type+','+self.ds

	def readFromLine(self, line):
		words = line.split(',')
		self.user_id = words[0].strip()
		self.song_id = words[1].strip()
		self.gmt_create = words[2].strip()
		self.action_type = words[3].strip()
		self.ds = words[4].strip()
