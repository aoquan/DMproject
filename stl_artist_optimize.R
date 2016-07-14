library('forecast')
library('fpp')

script.dir <- dirname(sys.frame(1)$ofile)
setwd(script.dir)
predict_num = 61
feq = 7

name_list_file = 'artist_list.csv'
read_path = 'split_by_artist_play_download_collect'
write_path = 'play_artist_predict_R'

#获取x的预测,x是平稳序列
get_stl_predict <- function(x, forest_num) {
  x_timeseries <- ts(x, frequency = feq, start=c(2010, 1))
  x_compents <- stl(x_timeseries, s.window="periodic") 
  x_forecast <- forecast(x_compents, h=forest_num)
  plot(x_forecast)
  
  total <- length(x_forecast[[2]])
  x_ret <- rep(0, total)
  for (i in 1:total){
    x_ret[i] = x_forecast[[2]][i]
  }
  
  #mean fix,考虑全部的均值
  x_weight_mean <- mean(x)
  x_ret_mewn <- mean(x_ret)
  
  #print(x_ret)
  x_ret = x_ret - (x_ret_mewn-x_weight_mean)
  
  #print(x_ret)
  
  #
  return(x_ret)
}


#解决问题入口
solve <- function() {
  if (dir.exists(write_path)==F) {
    dir.create(write_path)
  }
  ############  数据按照艺人进行分割
  artists <- scan(name_list_file, what = (""))
  for (art in artists) {
    print(art)
    ##########  read data
    filename <- paste(read_path, "/", art, ".csv", sep="")
    play_data_original <- read.csv(filename, header = FALSE)
    play_data <- play_data_original[[3]]
    
    ##########  一阶差分，预测并还原
    play_diff_1 <- diff(play_data)
    first_1 <- play_data[length(play_data)]
    play_diff_1_predict <- get_stl_predict(play_diff_1, predict_num-1)
    back_1 <- rep(0, predict_num)
    back_1[1] = first_1 + play_diff_1_predict[1]
    for (i in 2:length(back_1)) {
      back_1[i] <- back_1[i-1] + play_diff_1_predict[i-1]
    }
    
    ##########  二阶差分，预测并还原
    #play_diff_2 <- diff(play_diff_1)
    #first_2 <- first_1[1]
    #play_diff_2_predict <- get_stl_predict(play_diff_2, predict_num-2)
    #back_2 <- rep(0, predict_num-1)
    #back_2[1] = first_2
    #for (i in 2:length(back_2)) {
    #  back_2[i] = back_2[i-1] + play_diff_2_predict[i-1]
    #}
    #back_1 <- rep(0, predict_num)
    #back_1[1] = first_1 + back_2[1]
    #for (i in 2:length(back_1)) {
    #  back_1[i] <- back_1[i-1] + back_2[i-1]
    #}
    
    #weighted mean fix,考虑最近一个月
    play_total = length(play_data)
    weight <- rep(0, play_total)
    for (i in 0:15){
      weight[play_total-i] <- 1.25 
    }
    for (i in 15:30) {
      weight[play_total-i] <- 1
    }
    back_1_mean <- mean(back_1)
    play_data_mean <- sum(play_data*weight)/sum(weight)
    
    back_1 <- back_1 - 0.5 * (back_1_mean - play_data_mean)
    back_1_mean <- mean(back_1)
    part_mean_1 = mean(play_data[(play_total-30) : (play_total)])
    part_mean_2 = mean(play_data[(play_total-60) : (play_total-30)])
    if (part_mean_1>part_mean_2 && part_mean_1>1000) {
      delta = min(0.5 * max(0, part_mean_1-back_1_mean), 30)
      print(delta)
      
      back_1 <- back_1 + delta
    }
        
    ############
    predict_timeseries <- ts(back_1, frequency = feq, start = c(2010, 1))
    
    
    #########  保存
    savefilename <- paste(write_path, "/", art, "_predict.dat", sep="")
    write.csv(predict_timeseries, file=savefilename)

    #print(predict_timeseries)
    #break()
  }
}


feq = 30

read_path = 'split_artist_daypart_0'
write_path = 'play_artist_predict_R_daypart_0'
solve()

read_path = 'split_artist_daypart_1'
write_path = 'play_artist_predict_R_daypart_1'
solve()

read_path = 'split_artist_daypart_2'
write_path = 'play_artist_predict_R_daypart_2'
solve()


#feq = 30
#read_path = 'split_by_artist_play_download_collect_smooth'
#write_path = 'play_artist_predict_R_smooth'
#solve()
