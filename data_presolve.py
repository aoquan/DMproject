#coding=utf8

from UserAction import UserAction
from ArtistSong import ArtistSong
import datetime,os,sys
import scipy.stats as stats
import numpy as np
import matplotlib.pyplot as plt

#原始数据文件
userActionFileName = 'p2_mars_tianchi_user_actions.csv'
songsFileName = 'p2_mars_tianchi_songs.csv'
#按照艺人分割的文件(夹)名
fileArtist = 'artist_list.csv'
pathArtistSongs = 'split_by_artist_songs'
pathArtistUserActions = 'split_by_artist_user_actions'
pathArtistHourUserActions = 'split_by_artist_hour_user_actions'
pathArtistPlayDownloadCollect = 'split_by_artist_play_download_collect'
pathArtistPlayDownloadCollectSmooth = 'split_by_artist_play_download_collect_smooth'
#按照歌曲分割的文件(夹)名
fileSongs = 'song_list.csv'
fileSongsSummary = 'song_summary.csv'
pathSongUserActions = 'split_by_song_user_actions'
pathSongPlayDownloadCollect = 'split_by_song_play_download_collect'
pathSongPlayDownloadCollectSmooth = 'split_by_song_play_download_collect_smooth'

#
pathArtistTraining = 'training_data'
pathArtistPredict = 'predict_data'


def split_data_by_artist():
	"""
	对原始数据按照艺人进行切割，得到三类文件：艺人信息、艺人歌曲(包含在文件夹)、用户行为(包含在文件夹)
	歌手是50个，大概运行时间360s
	"""
	song_to_artist = {}
	#################################################
	# get dict of song_id to artist_id
	#################################################
	with open(songsFileName, 'r') as f:
		line = f.readline()
		while line:
			a = ArtistSong(line)
			song_to_artist[a.song_id] = a.artist_id
			line = f.readline()

	#################################################
	# store artist list to file
	#################################################
	artist_list = []
	for song in song_to_artist.keys():
		artist = song_to_artist[song]
		if artist not in artist_list:
			artist_list.append(artist)
	with open(fileArtist, 'w') as f:
		for artist in artist_list:
			f.write(artist.strip()+'\n')


	#################################################
	# get splited file of songs
	#################################################
	print 'start split songs'
	if os.path.exists(pathArtistSongs)==False:
		os.mkdir(pathArtistSongs)
	#clear brfore write
	for artist in artist_list:
		f = open(pathArtistSongs+'/'+artist+'.csv' , 'w')
		f.close()
	with open(songsFileName, 'r') as f:
		line = f.readline()
		while line:
			a = ArtistSong(line)
			filename = pathArtistSongs+'/'+song_to_artist[a.song_id]+'.csv' 
			fw = open(filename, 'a')
			fw.write(line)
			fw.close()
			line = f.readline()

	#################################################
	# get splited file of user_actions			
	#################################################
	print 'start split user_actions'
	if os.path.exists(pathArtistUserActions)==False:
		os.mkdir(pathArtistUserActions)
	#clear brfore write
	for artist in artist_list:
		f = open(pathArtistUserActions+'/'+artist+'.csv' , 'w')
		f.close()
	with open(userActionFileName, 'r') as f:
		line = f.readline()
		cnt = 0
		while line:
			a = UserAction(line)
			if song_to_artist.has_key(a.song_id)==False:
				print 'ERROR-01:',a.song_id
				continue
			filename = pathArtistUserActions+'/'+song_to_artist[a.song_id]+'.csv' 
			fw = open(filename, 'a')
			fw.write(line)
			fw.close()
			line = f.readline()
			cnt += 1
			if cnt%1000==0:
				print cnt
				sys.stdout.flush()

	################################################
	# get play,download,collect 
	################################################
	get_play_download_collect('artist')



def get_artist_list():
	"""
	从文件中获取艺人列表
	"""
	if os.path.exists(fileArtist)==False:
		print '*** no file *** '+fileArtist+'\n'
		return []
	artist_list  = []
	with open(fileArtist, 'r') as f:
		artist_list = f.readlines()
	return_list = [x.strip() for x in artist_list]
	return return_list


def get_song_list():
	"""
	从文件中获取歌曲列表
	"""
	if os.path.exists(fileSongs)==False:
		print '*** no file *** '+fileSongs+'\n'
		return []
	song_list  = []
	with open(fileSongs, 'r') as f:
		song_list = f.readlines()
	return_list = [x.split(',')[0].strip() for x in song_list]
	return return_list

	
def get_play_download_collect(op_type, smooth=False):
	"""
	获取每个艺人每天的播放次数、下载次数、收藏次数
	"""
	print 'start get_play_download_collect()'
	#
	name_list = []
	read_path = ''
	write_path = ''
	write_smooth_path = ''
	if op_type=='artist':
		name_list = get_artist_list()
		read_path = pathArtistUserActions
		write_path = pathArtistPlayDownloadCollect
		write_smooth_path = pathArtistPlayDownloadCollectSmooth
	elif op_type=='song':
		name_list = get_song_list()
		read_path = pathSongUserActions
		write_path = pathSongPlayDownloadCollect
		write_smooth_path = pathSongPlayDownloadCollectSmooth
	else:
		print 'ERROR-03: wrong type'
		return
	#
	if os.path.exists(write_path)==False:
		os.mkdir(write_path)
	if os.path.exists(write_smooth_path)==False:
		os.mkdir(write_smooth_path)
	#
	for name in name_list:
		record = {}
		if os.path.exists(read_path+'/'+name+'.csv'):
			fr = open(read_path+'/'+name+'.csv', 'r')
			line = fr.readline()
			while line:
				a = UserAction(line)
				if record.has_key(a.ds)==False:
					record[a.ds] = {1:0, 2:0, 3:0}
				d = record[a.ds]
				d[int(a.action_type)] += 1
				line = fr.readline()		
			fr.close()
		#
		first_day_str = '20150301'
		last_day_str = '20150830'
		first_day = datetime.datetime.strptime(first_day_str, '%Y%m%d')
		last_day = datetime.datetime.strptime(last_day_str, '%Y%m%d')
		day_diff = last_day-first_day
		day_count = day_diff.days + 1
		play_list = []
		########
		fw = open(write_path+'/'+name+'.csv', 'w')		
		for x in xrange(day_count):
			day = first_day + datetime.timedelta(x)
			day_str = day.strftime('%Y%m%d')
			d = {}
			if record.has_key(day_str)==False:
				d = {1:0, 2:0, 3:0}
			else:
				d = record[day_str]
			play_list.append(d[1])
			fw.write(name+','+day_str+','+str(d[1])+','+str(d[2])+','+str(d[3])+'\n')
		fw.close()
		#######   add smooth data
		smooth_play_list = play_list
		if smooth==True:
			smooth_play_list = smooth(play_list)
		fw = open(write_smooth_path+'/'+name+'.csv', 'w')		
		for x in xrange(day_count):
			day = first_day + datetime.timedelta(x)
			day_str = day.strftime('%Y%m%d')
			d = {}
			if record.has_key(day_str)==False:
				d = {1:0, 2:0, 3:0}
			else:
				d = record[day_str]
			play_list.append(d[1])
			fw.write(name+','+day_str+','+str(smooth_play_list[x])+','+str(d[2])+','+str(d[3])+'\n')
		fw.close()


def split_data_by_song():
	"""
	将原始数据按照歌曲分割，得到。。。
	歌曲共是10842个，大概运行时间400s
	"""
	song_to_artist = {}
	#################################################
	# get dict of song_id to artist_id
	#################################################
	with open(songsFileName, 'r') as f:
		line = f.readline()
		while line:
			a = ArtistSong(line)
			song_to_artist[a.song_id] = a.artist_id
			line = f.readline()
	
	#################################################
	# store song info
	#################################################
	with open(fileSongs, 'w') as f:
		for k in song_to_artist.keys():
			f.write(k+','+song_to_artist[k]+'\n')

	#################################################
	# store user_actions
	#################################################
	print 'start split user_actions'
	if os.path.exists(pathSongUserActions)==False:
		os.mkdir(pathSongUserActions)
	#clear brfore write
	for song in song_to_artist.keys():
		f = open(pathSongUserActions+'/'+song+'.csv' , 'w')
		f.close()
	with open(userActionFileName, 'r') as f:
		line = f.readline()
		while line:
			a = UserAction(line)
			if song_to_artist.has_key(a.song_id)==False:
				print 'ERROR-02:',a.song_id
				continue
			filename = pathSongUserActions+'/'+a.song_id+'.csv' 
			fw = open(filename, 'a')
			fw.write(line)
			fw.close()
			line = f.readline()

	################################################
	# get play,download,collect 
	################################################
	get_play_download_collect('song')

	################################################
	# summary for song-split
	################################################
	summary_by_song(song_to_artist)


def summary_by_song(song_to_artist):
	"""
	按照歌曲分割时，很多歌曲的播放次数很少，做个总结
	"""
	fw = open(fileSongsSummary, 'w')
	for song in song_to_artist.keys():
		d = {1:0, 2:0, 3:0}
		if os.path.exists(pathSongUserActions+'/'+song+'.csv'):	
			with open(pathSongUserActions+'/'+song+'.csv', 'r') as f:
				line = f.readline()
				while line:
					a = UserAction(line)
					d[int(a.action_type)] += 1
					line = f.readline()
		fw.write(song+','+str(d[1])+','+str(d[2])+','+str(d[3])+'\n')
	fw.close()


def prepare_data_for_randomfprest():
	"""
	给随机森林算法生成训练数据:f1,f2,...,fk,label
	生成预测数据
	"""
	#
	gap = 31
	#训练数据的长度
	train_len = 20
	#
	if os.path.exists(pathArtistTraining)==False:
		os.mkdir(pathArtistTraining)
	if os.path.exists(pathArtistPredict)==False:
		os.mkdir(pathArtistPredict)
	#
	artist_list = get_artist_list()
	for artist in artist_list:
		filename = pathArtistPlayDownloadCollect + '/' + artist + '.csv'
		play_list = []
		with open(filename, 'r') as f:
			line = f.readline()
			while line:
				ws = line.split(',')
				play_list.append(int(ws[2]))
				line = f.readline()
		#
		filename_train = pathArtistTraining + '/' + artist + '.csv'
		filename_pre = pathArtistPredict + '/' + artist + '.csv'
		f_train = open(filename_train, 'w')
		f_pre = open(filename_pre, 'w')
		total = len(play_list)
		for i in xrange(total):
			if i+train_len >= total:
				break
			if i+train_len+gap >= total:
				s = ''
				for k in xrange(train_len):
					s += str(play_list[i+k]) + '\t'
				s += '\n'
				f_pre.write(s)
			else:			
				s = ''
				for k in xrange(train_len):
					s += str(play_list[i+k]) + '\t'
				s += str(play_list[i+train_len+gap])+'\n'
				f_train.write(s)
		f_train.close()
		f_pre.close()
	return


def smooth(x):
	"""
	对列表做平滑处理,最后返回正整数序列
	"""
	#d>0, d * delta < 3
	d = 4
	idx = [-(d-i) for i in range(d)] + [0] + [i+1 for i in range(d)]
	delta = 0.7
	mean = 0
	sigma = 1
	#
	norm_x = np.arange(-delta*d, delta*d+0.05, delta)
	norm_y = stats.norm.pdf(norm_x, mean, sigma)

	#print norm_y

	x_ret = []
	for i in xrange(len(x)):
		s_w = 0
		s_x = 0
		for k in xrange(len(idx)):
			if i+idx[k]>=0 and i+idx[k]<len(x):
				s_w += norm_y[k]
				s_x += norm_y[k] * x[i+idx[k]]

		new_x = float(s_x) / s_w
		x_ret.append(new_x)
	#
	x_ret_2 = [int(i) for i in x_ret]
	x_ret_3 = [max(0, i) for i in x_ret_2]
	#
	return x_ret_3


def timestamp_to_datetime(timestamp):
	return datetime.datetime.fromtimestamp(int(timestamp))



def split_by_artist_by_hour():
	"""
	"""
	song_to_artist = {}
	#################################################
	# get dict of song_id to artist_id
	#################################################
	with open(songsFileName, 'r') as f:
		line = f.readline()
		while line:
			a = ArtistSong(line)
			song_to_artist[a.song_id] = a.artist_id
			line = f.readline()
	#
	artist_list = []
	for song in song_to_artist.keys():
		artist = song_to_artist[song]
		if artist not in artist_list:
			artist_list.append(artist)

	#################################################
	# get splited file of user_actions			
	#################################################
	print 'start split user_actions artist_hour'
	if os.path.exists(pathArtistHourUserActions)==False:
		os.mkdir(pathArtistHourUserActions)
	#clear brfore write
	for artist in artist_list:
		f = open(pathArtistHourUserActions+'/'+artist+'.csv' , 'w')
		f.close()
	for artist in artist_list:
		d_hour = {}

		fr = open(pathArtistUserActions+'/'+artist+'.csv' , 'r')
		for line in fr:
			ls = line.split(',')
			time = timestamp_to_datetime(ls[2])
			op_type = int(ls[3])
			if d_hour.has_key(time.hour)==False:
				d_hour[time.hour] = {1:0, 2:0, 3:0}
			d = d_hour[time.hour]
			d[op_type] += 1
		fr.close()
		#
		fw = open(pathArtistHourUserActions+'/'+artist+'.csv' , 'w')
		for k in range(24):
			d = d_hour[k]
			fw.write(str(d[1])+','+str(d[2])+','+str(d[3])+'\n')
		fw.close()
	

def draw_artist_hour_play():
	"""
	画图，按照每个艺人每个小时来画图
	"""
	print 'draw_artist_hour_play'

	figure_path = 'figure_artist_hour'
	if os.path.exists(figure_path)==False:
		os.mkdir(figure_path)
	#
	artist_list = get_artist_list()
	for artist in artist_list:
		play, download, collect = [], [], []
		f = open(pathArtistHourUserActions+'/'+artist+'.csv' , 'r')
		for line in f:
			ls = line.strip().split(',')
			play.append(int(ls[0]))
			download.append(int(ls[1]))
			collect.append(int(ls[2]))
		f.close()
		x = range(24)

		plt.clf()

		plt.plot(x, play, 'r')
		plt.plot(x, download, 'b')
		plt.plot(x, collect, 'g')

		plt.savefig(figure_path+'/'+artist+'.jpg')

def split_by_daypart():
	"""
	把一天分为几个部分，分别得到按照时间的文件(也按歌手分)
	"""
	read_path = pathArtistUserActions
	write_path = 'split_artist_daypart'

	#
	day_part = 3
	for i in range(day_part):
		path = write_path+'_'+str(i)
		if os.path.exists(path)==False:
			os.mkdir(path)
	#
	name_list = get_artist_list()
	#
	for name in name_list:
		record = {}
		for i in range(day_part):
			record[i] = {}
		gap = 24 / day_part
		if os.path.exists(read_path+'/'+name+'.csv'):
			fr = open(read_path+'/'+name+'.csv', 'r')
			line = fr.readline()
			while line:
				a = UserAction(line)
				d_time = timestamp_to_datetime(a.gmt_create)
				hour = d_time.hour / gap
				rd = record[hour]
				if rd.has_key(a.ds)==False:
					rd[a.ds] = {1:0, 2:0, 3:0}
				d = rd[a.ds]
				d[int(a.action_type)] += 1
				line = fr.readline()		
			fr.close()
		#
		first_day_str = '20150301'
		last_day_str = '20150830'
		first_day = datetime.datetime.strptime(first_day_str, '%Y%m%d')
		last_day = datetime.datetime.strptime(last_day_str, '%Y%m%d')
		day_diff = last_day-first_day
		day_count = day_diff.days + 1
		########
		for i in range(day_part):
			fw = open(write_path+'_'+str(i)+'/'+name+'.csv', 'w')		
			for x in xrange(day_count):
				day = first_day + datetime.timedelta(x)
				day_str = day.strftime('%Y%m%d')
				d = {}
				rd = record[i]
				if rd.has_key(day_str)==False:
					d = {1:0, 2:0, 3:0}
				else:
					d = rd[day_str]
				fw.write(name+','+day_str+','+str(d[1])+','+str(d[2])+','+str(d[3])+'\n')
			fw.close()
		print name
		#break

if __name__ == '__main__':
	#
	#split_by_artist_by_hour()
	#draw_artist_hour_play()
	#
	split_by_daypart()
	#
	#split_data_by_artist()
	#get_play_download_collect('artist')
	#
	#split_data_by_song()
	#
	#prepare_data_for_randomfprest()