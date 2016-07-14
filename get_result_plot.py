#coding=utf8

from UserAction import UserAction
from ArtistSong import ArtistSong
import matplotlib.pyplot as plt
import scipy.stats as stats
import numpy as np
import os,datetime


#运行参数
global parameters
parameters = {}
songsFileName = 'song_list.csv'
artistFileName = 'artist_list.csv'
day_of_predict = 60
predict_first_day_str = '20150901'

def format_predict():
	"""
	对R保存的结果进行处理，变成单个的csv
	用到的参数：name_file，predictionPath_R，predictionPath
	"""
	global parameters
	#
	name_list = []
	with open(parameters['name_file'], 'r') as f:
		lines = f.readlines()
		for x in lines:
			xs = x.split(',')
			name_list.append(xs[0].strip())
	first_day = datetime.datetime.strptime(predict_first_day_str, '%Y%m%d')
	if os.path.exists(parameters['predictionPath'])==False:
		os.mkdir(parameters['predictionPath'])
	for name in name_list:
		#print name
		read_filename = parameters['predictionPath_R'] + '/' + name + '_predict.dat'
		write_filename = parameters['predictionPath'] + '/' + name + '_predict.csv'
		with open(read_filename, 'r') as fr, open(write_filename, 'w') as fw:
			lines = fr.readlines()
			#第一行是列名，第二行是8.31
			lines = lines[2:]
			day_count = 0
			for w in lines:
				day = first_day + datetime.timedelta(day_count)
				ws = w.split(',')
				fw.write(name.strip()+','+str(int(float(ws[1])))+','+day.strftime('%Y%m%d')+'\n')
				day_count += 1


def get_mean_of_data(file_or_list, subseq=False, from_idx = -1, end_idx = -1):
	"""
	得到某个文件内序列或某个序列的均值，文件格式规定为:xxx_id, ds, play_num, download_num, collect_num
	"""
	count = 0
	li = []
	if isinstance(file_or_list, str):
		with open(file_or_list, 'r') as f:
			line = f.readline()
			while line:
				ws = line.split(',')
				val = int(ws[2])
				if val < 0:
					val = 0
				count += 1
				li.append(val)
				line = f.readline()
	else:
		li = file_or_list
	if (subseq==False):
		from_idx = 0
		end_idx = count	
	sub_li = li[from_idx: end_idx]
	total = 0
	for x in sub_li:
		total += x
	return float(total)/float(len(sub_li))


def combine_result():
	"""
	将产生的各个艺人的每天预测结果合成为一个预测文件
	这里将处理预测值为负数的情况
	用到的参数：name_file，saveFileName，predictionPath_R
	"""
	global parameters
	name_list = []
	with open(parameters['name_file'], 'r') as f:
		lines = f.readlines()
		for x in lines:
			xs = x.split(',')
			name_list.append(xs[0].strip())
	#
	p_first_day = datetime.datetime.strptime(predict_first_day_str, '%Y%m%d')
	fw = open(parameters['saveFileName'], 'w')
	for name in name_list:
		filename = parameters['predictionPath']+'/'+name.strip()+'_predict.csv'
		with open(filename, 'r') as f:
			lines = f.readlines()
			cnt = 0
			for w in lines:
				p_day = p_first_day + datetime.timedelta(cnt)
				ws = w.split(',')
				val = int(float(ws[1]))
				if val < 0:
					val = 0
				fw.write(name.strip()+','+str(val)+','+p_day.strftime('%Y%m%d')+'\n')
				cnt += 1
	fw.close()


def get_song_to_artist():
	"""
	获取歌曲与艺人的对应关系(字典)
	"""
	song_to_artist = {}
	with open(songsFileName, 'r') as f:
		line = f.readline()
		while line:
			ws = line.split(',')
			song_to_artist[ws[0]] = ws[1].strip()
			line = f.readline()
	return song_to_artist


def get_artist_list():
	"""
	从文件中获取艺人列表
	"""
	if os.path.exists(artistFileName)==False:
		print '*** no file *** '+artistFileName+'\n'
		return []
	artist_list  = []
	with open(artistFileName, 'r') as f:
		artist_list = f.readlines()
	return_list = [x.strip() for x in artist_list]
	return return_list


def combine_song_to_artist():
	"""
	把按歌曲预测的结果转为按艺人的预测结果
	结合时，处理歌曲预测中的负数
	"""
	#
	if os.path.exists(parameters['predictionPathNew'])==False:
		os.mkdir(parameters['predictionPathNew'])
	song_to_artist = get_song_to_artist()
	artist_predict = {}
	for song in song_to_artist.keys():
		read_filename = parameters['predictionPath'] + '/' + song + '_predict.csv'
		if artist_predict.has_key(song_to_artist[song])==False:
			li = [0 for i in xrange(day_of_predict)]
			artist_predict[song_to_artist[song]] = li
		old_li = artist_predict[song_to_artist[song]]
		with open(read_filename, 'r') as f:
			idx = 0
			line = f.readline()
			while line:
				ws = line.split(',')
				val = int(ws[1])
				if val < 0:
					val = 0
				old_li[idx] += val
				idx += 1
				line = f.readline()
		#
	artist_list = get_artist_list()
	for artist in artist_list:
		write_filename = parameters['predictionPathNew'] + '/' + artist + '_predict.csv'
		li = []
		if artist_predict.has_key(artist):
			li = artist_predict[artist]
		else:
			li = [0 for i in xrange(day_of_predict)]
		data_mean = get_mean_of_data('split_by_artist_play_download_collect/'+artist+'.csv', True, -10, -1)
		dif = li[0] - data_mean
		new_li = [x-dif for x in li]
		with open(write_filename, 'w') as f:
			first_day = datetime.datetime.strptime(predict_first_day_str, '%Y%m%d')
			for i in xrange(day_of_predict):
				day = first_day + datetime.timedelta(i)
				day_str = day.strftime('%Y%m%d')
				f.write(artist+','+str(new_li[i])+','+day_str+'\n')


def compare_plot(smooth_compare=False):
	"""
	可视化展示训练数据和预测结果，保存为图片
	用到的参数：name_file，figurePath，historyPath，predictionPath
	"""
	#
	global parameters
	name_list = []
	with open(parameters['name_file'], 'r') as f:
		lines = f.readlines()
		for x in lines:
			xs = x.split(',')
			name_list.append(xs[0].strip())
	#
	if os.path.exists(parameters['figurePath'])==False:
		os.mkdir(parameters['figurePath'])

	cnt = 0
	for name in name_list:
		y1, y2 = [], []
		with open(parameters['historyPath']+'/'+name+'.csv', 'r') as f:
			w = f.readline()
			while w:
				ws = w.split(',')
				val = int(float(ws[2]))
				y1.append(val)
				w = f.readline()
		x1 = range(len(y1))
		with open(parameters['predictionPath']+'/'+name+'_predict.csv', 'r') as f:
			w = f.readline()
			while w:
				ws = w.split(',')
				val = int(float(ws[1]))
				y2.append(val)
				w = f.readline()
		x2 = [len(y1)+i for i in range(len(y2))]

		
		#
		plt.clf()
		plt.plot(x1, y1, 'b')
		#plt.plot(x2, y2, 'r')
		if smooth_compare:
			x3 = x1
			y3 = smooth(y1)
			x4 = x2
			y4 = []
			with open(parameters['predictionPath_R_smooth']+'/'+name+'_predict.dat', 'r') as f:
				lines = f.readlines()
				lines = lines[1: -1]
				for w in lines:
					ws = w.split(',')
					val = int(float(ws[1]))
					y4.append(val)
					w = f.readline()

			plt.plot(x3, y3, 'g')
			plt.plot(x4, y4, 'g')
			
		#plt.plot(x3, y3, 'g')
		#plt.show()
		plt.savefig(parameters['figurePath']+'/'+name+'.jpg')
		cnt +=1
		#if cnt>20:
		#	break


def main(optype, model=None):
	global parameters
	#画图50张大概 10s
	if optype=='artist':
		parameters['name_file'] = 'artist_list.csv'
		parameters['predictionPath_R'] = 'play_artist_predict_R'
		parameters['predictionPath'] = 'play_artist_predict'
		parameters['predictionPath_R_smooth'] = 'play_artist_predict_R_smooth'
		parameters['predictionPath_smooth'] = 'play_artist_predict_smooth'
		
		parameters['figurePath'] = 'figure_artist'
		parameters['historyPath'] = 'split_by_artist_play_download_collect'
		parameters['historyPathSmooth'] = 'split_by_artist_play_download_collect_smooth'
		parameters['saveFileName'] = 'mars_tianchi_artist_plays_predict_artist.csv'
	#画图10000+张大概 2100sec = 35min
	elif optype=='song':
		parameters['name_file'] = 'song_list.csv'
		parameters['predictionPath_R'] = 'play_song_predict_R'
		parameters['predictionPath'] = 'play_song_predict'
		parameters['figurePath'] = 'figure_song'
		parameters['historyPath'] = 'split_by_song_play_download_collect'
		parameters['saveFileName'] = 'mars_tianchi_artist_plays_predict_song.csv'
	else:
		print 'ERROR-05: wrong type'
		return
	parameters['type'] = optype
	if model:
		parameters['predictionPath_R'] = 'play_' + model + '_R'
		parameters['predictionPath'] = 'play_' + model
	#
	format_predict()
	#
	combine_result()
	#
	if optype=='artist':
		#compare_plot(True)
		compare_plot(False)
	elif optype=='song':
		#画图10000+张，太多直接化最后艺人的
		#compare_plot()
		#转为按艺人的结果
		parameters['predictionPathNew'] = 'play_song_predict_artist'
		#
		combine_song_to_artist()
		#
		parameters['predictionPath'] = parameters['predictionPathNew']
		parameters['type'] = 'artist'
		parameters['saveFileName'] = 'mars_tianchi_artist_plays_predict_song_artist.csv'
		parameters['figurePath'] = 'figure_song_artist'
		parameters['name_file'] = 'artist_list.csv'
		parameters['historyPath'] = 'split_by_artist_play_download_collect'
		#
		combine_result()
		#
		compare_plot()
	#

def do_for_artist_for_daypart():
	#得到同意的R预测后文件
	day_part = 3
	total_predict = 60
	artist_list = get_artist_list()
	#clear result
	for artist in artist_list:
		fw = open('play_artist_predict_R'+'/'+artist+'_predict.dat', 'w')
		fw.close()
	#
	for artist in artist_list:
		play = [0 for i in range(total_predict)]
		for i in range(day_part):
			fr = open('play_artist_predict_R_daypart_'+str(i)+'/'+artist+'_predict.dat', 'r')
			lines = fr.readlines()
			lines = lines[1:]
			for x in xrange(total_predict):
				s = lines[x].split(',')
				play[x] += int(float(s[1]))
			fr.close()
		#
		fw = open('play_artist_predict_R'+'/'+artist+'_predict.dat', 'a')
		fw.write('header\n')
		for x in play:
			fw.write('xxx,'+str(x)+'\n')
		fw.close()
	#
	global parameters
	#画图50张大概 10s
	parameters['name_file'] = 'artist_list.csv'
	parameters['predictionPath_R'] = 'play_artist_predict_R'
	parameters['predictionPath'] = 'play_artist_predict'
	parameters['predictionPath_R_smooth'] = 'play_artist_predict_R_smooth'
	parameters['predictionPath_smooth'] = 'play_artist_predict_smooth'
	
	parameters['figurePath'] = 'figure_artist'
	parameters['historyPath'] = 'split_by_artist_play_download_collect'
	parameters['historyPathSmooth'] = 'split_by_artist_play_download_collect_smooth'
	parameters['saveFileName'] = 'mars_tianchi_artist_plays_predict_artist.csv'
	#
	format_predict()
	#
	combine_result()
	#
	compare_plot(False)
	


def plot_original(smooth_compare=False):
	"""
	可视化展示训练数据
	"""
	#
	name_list = []
	with open('artist_list.csv', 'r') as f:
		lines = f.readlines()
		for x in lines:
			xs = x.split(',')
			name_list.append(xs[0].strip())
	#
	read_path = 'split_by_artist_play_download_collect'
	write_path = 'figure_original'

	if os.path.exists(write_path)==False:
		os.mkdir(write_path)
	cnt = 0
	for name in name_list:
		y1, y2,y3 = [], [], []
		with open(read_path+'/'+name+'.csv', 'r') as f:
			w = f.readline()
			while w:
				ws = w.split(',')
				y1.append(int(float(ws[2])))
				y2.append(int(float(ws[3])))
				y3.append(int(float(ws[4])))
				w = f.readline()
		x1 = range(len(y1))
		#
		plt.clf()
		plt.plot(x1, y1, 'b', label='play')
		plt.plot(x1, y2, 'r', label='download')
		plt.plot(x1, y3, 'g', label='collect')
		plt.legend()
		plt.title(name)
		plt.savefig(write_path+'/'+name+'.jpg')
		cnt +=1
		#if cnt>20:
		#	break


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



if __name__ == '__main__':
	plot_original()
	#
	#main('artist')
	#
	#do_for_artist_for_daypart()
	#
	#main('artist', 'randomforest')
	#
	#main('song')
	#