##author:mizukiyuta

import numpy as np

import datetime
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
#%matplotlib inline

from scipy import stats
from scipy.stats import norm

import time
import datetime

import neurokit2 as nk


##---------------------------------------------------
##------------------IMPORTANT------------------------
##---------------------------------------------------
#You should change data's experiment date and collaborator name
##---------------------------------------------------
root="C:/Users/mizukiyuta/Desktop/atmosphere/DATA/"

#date="211223"
date = "12-23"
name="Shiyang"
name1="Miusen"
name2="Shiyang"
base_dir="2021"+"-"+date+"-"+name1+"-"+name2+"/"#"2021-12-23-Miusen-Shiyang/"
dir1=name+"-"+date+"/"#Miusen-12-23
ecg_file_num = 9 # the number of your 09-27df_ecg_polar .csv in rawdata
##---------------------------------------------------
##------------------IMPORTANT------------------------
##---------------------------------------------------

input_dir=""
output_dir1 = "output"
output_dir2 = "output1"

##---------------------------------------------------
#Global data/file/path setting(according to date and name)
##---------------------------------------------------
date_ ="2021-"+date
date_stamp = "2021"+date.replace("-","")

#data_dir_name = "/"+name1+"-"+date #/cuidenwen-09-24
data_dir_name = root+ base_dir + dir1

ecg_file_name = date+"df_ecg_polar"  #09-24df_ecg_polar0.csv
#eeg_file_name = "museMonitor_"+"2021-"+date +"--"  #museMonitor_2021-09-24--0.csv
sr_file_name = name+"-"+date+"SR.csv" #cuidenwen-09-24SR.csv

data_path = data_dir_name
##---------------------------------------------------


##---------------------------------------------------
##read data's info (self-report csv)
print("Read SR csv:",sr_file_name)
sr_df =  pd.read_csv('%s/%s' % (data_path, sr_file_name),encoding='unicode_escape')#SR.csv

print(sr_df)
print("-"*50)
#input(len(sr_df))
##---------------------------------------------------


##---------------------------------------------------
#drop na data in df
##---------------------------------------------------
def drop_na(data):
	df=data
	df.dropna(axis=0, how='any', inplace=True)
	# 因为删除了几行数据,所以index的序列不再连续,需要重新reindex
	df.reset_index(drop=True, inplace=True)
	return df


##---------------------------------------------------
#readcsv function
#read csvs and  concat them into one csv file
##---------------------------------------------------
def readcsv(filepath):
	df = pd.read_csv(filepath,encoding='unicode_escape')
	return df

def read_concat_csv(filepath,file_name,n,file_format):
	#df = None
	frames = []
	for i in range(n):
		#print(i)
		df = readcsv(filepath+file_name+str(i)+file_format)
		frames.append(df)	
	dataframe = pd.concat(frames)
	return dataframe

def savecsv(filepath,data):
    data.to_csv(filepath,index=0)
    print("saved to ",filepath)
    print("-"*50)  
#---------------------------------------------------


##---------------------------------------------------
#concat all ecg data
#then intercept them into 6 csv file according to the starttime and endtime in SR.csv
##---------------------------------------------------
def ecg_intercept():
    input_filepath = data_dir_name+input_dir #/cuidenwen-09-24/rawdata/
    concat_ecg_df = read_concat_csv(filepath=input_filepath,
                                 file_name=ecg_file_name,
                                 n=ecg_file_num,
                                 file_format=".csv")
    concat_ecg_df = drop_na(concat_ecg_df)
    concat_ecg_df['Time'] = pd.to_datetime(concat_ecg_df['Time'])
    print("concat_eeg_df(dropna and resized)")
    print(concat_ecg_df)
    
    
    for i in range(len(sr_df)):
        #print(aa.iloc[i])
        starttime = str(sr_df['StartTime'].iloc[i])
        endtime = str(sr_df['EndTime'].iloc[i])
        starttime= date_ + " " + starttime.strip('PM').strip('AM')
        endtime= date_ + " " + endtime.strip('PM').strip('AM')
        
        # starttime - 2min
        #because we need to calculate LF/HF(which need ecg data 2minutes before)
        starttimeArray = datetime.datetime.strptime(starttime, '%Y-%m-%d %H:%M:%S')
        delta = datetime.timedelta(minutes=2)
        starttime = starttimeArray - delta
        
        print(starttime,endtime)
        
         
        data = concat_ecg_df[(concat_ecg_df['Time'] >=starttime) & (concat_ecg_df['Time'] <= endtime)]
        #print( data)

		##------------------------------------
		##save data to csv
		##------------------------------------
        save_filePath = data_path + output_dir1 +"/"+ "ecg"+str(i)+".csv"
        savecsv(save_filePath,data)

def get_timedomain_from_ecg(data,rate,isshow):
    # Extract clean EDA and SCR features
    peaks, info = nk.ecg_peaks(data["ECG"], sampling_rate=rate)  
    rv_time = nk.hrv_time(peaks, sampling_rate=rate, show=isshow)
    return rv_time

def get_freq_from_ecg(data,rate,isshow):
    #use two minutes ecg to get LFHF
    # Find peaks
    peaks, info = nk.ecg_peaks(data["ECG"], sampling_rate=rate)   
    rv_freq = nk.hrv_frequency(peaks, sampling_rate=rate, show=isshow)     
    return rv_freq
def duplicate_df(df,times):
    pd2=pd.DataFrame()
    for i in range(len(df)):
        a=df.loc[i]
        d=pd.DataFrame(a).T
        pd2=pd2.append([d]*times)  #每行复制times倍
        #print(df)
    df=pd2
    df.reset_index(drop=True, inplace=True) 
    return df     
def get_rv_use_timewindow(i):
    #we read data from output dir
    file_path = data_dir_name + output_dir1 + "/" #/cuidenwen-09-24/output/ 
    name = "ecg"+str(i)+".csv"
    ecg_file_path = file_path + name

    print(ecg_file_path)
    ecg_df = readcsv(ecg_file_path)
    print(ecg_df)
    print("-"*50)
    #do not forget to convert Time to datetime type
    ecg_df['Time'] = pd.to_datetime(ecg_df['Time'])
    
    #get starttime and endtime in sr csv
    starttime = str(sr_df['StartTime'].iloc[i])
    endtime = str(sr_df['EndTime'].iloc[i])
    starttime= date_ + " " + starttime.strip('PM').strip('AM')
    endtime= date_ + " " + endtime.strip('PM').strip('AM')
        
    # starttime - 2min
    #because we need to calculate LF/HF(which need ecg data 2minutes before)
    starttimeArray = datetime.datetime.strptime(starttime, '%Y-%m-%d %H:%M:%S')
    delta_minute = datetime.timedelta(minutes=1)
    delta_second = datetime.timedelta(seconds=1)
    delta_millisecond = datetime.timedelta(milliseconds=1000)

    start_flag = starttimeArray - delta_minute - delta_minute##14:47:00
    end_flag = start_flag + delta_minute + delta_minute ##14:47:00+00:02:00=>14:49:00
    
    #rv=pd.DataFrame()
    frames=[]
    while(True):
        print("time_windows:",start_flag,end_flag,end_flag-start_flag)
        
        data = ecg_df[(ecg_df['Time'] >=start_flag) & (ecg_df['Time'] <= end_flag)]
        
        rv_time = get_timedomain_from_ecg(data=data,rate=130,isshow=False)
        rv_freq = get_freq_from_ecg(data=data,rate=130,isshow=False)
        
        rv_result = pd.concat([rv_time, rv_freq], axis=1, join='inner')
        
        rv_result['Time']=end_flag
        print(rv_result)
        print("-"*50)
        frames.append(rv_result)
        
        
        start_flag = start_flag + delta_millisecond
        end_flag = end_flag + delta_millisecond


        if(end_flag>=pd.to_datetime(endtime)):
            #print("#$%&'!!!!!!",end_flag,pd.to_datetime(endtime))
            break
        
    dataframe = pd.concat(frames)
    dataframe.reset_index(drop=True, inplace=True) 
    #dataframe = duplicate_df(dataframe,50)
    return dataframe
   
    
def wind():
    for i in range(len(sr_df)):
        dataframe = get_rv_use_timewindow(i)
        save_filePath = data_path + output_dir2 +"/"+ "rv"+str(i)+".csv"
        savecsv(save_filePath,dataframe)

        """to_drop = ['Time']
        save_filePath2 = data_path + output_dir2 +"/"+ "rvv"+str(i)+".csv"
        dataframe = dataframe.drop_duplicates(subset=to_drop)
        savecsv(save_filePath2,dataframe)"""
    pass


if __name__=='__main__':
    #intercept every section to 3minutes 
    #save to save_filePath = data_path + output_dir1 +"/"+ "ecg"+str(i)+".csv"
    ecg_intercept()

    #test
    #main(0)

    #for circle to calculate hrv 
    #save data to save_filePath = data_path + output_dir2 +"/"+ "rv"+str(i)+".csv"
    wind()












