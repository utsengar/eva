#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 19 07:21:54 2020

@author: averysmith
"""

#library 
import pandas as pd
from datetime import date, datetime, timedelta
import matplotlib.pyplot as plt
import math
import numpy as np
from scipy.interpolate import make_interp_spline, BSpline
import math

# Load in data
df = pd.read_excel('Eva.xlsx',sheet_name='Eva')


# Repshape the data
def return_minute_data(df,act):
    # Subset activities
    df_set = df[df['Activity'] == act].reset_index(drop=True)
    nan_list = [not math.isnan(i) for i in df_set['Duration (min)']]
    df_set = df_set[nan_list].reset_index(drop=True)
    
    # Get min and max dates
    date_max = np.max(df_set['DMY'])
    date_min = np.min(df_set['DMY'])
    
    # List all 15 minut incredment dates betweeen min and max
        all_dates = (pd.DataFrame(columns=['NULL'],index=pd.date_range(date_min, date_max+timedelta(days=1),freq='1T')).index.strftime('%Y-%m-%dT%H:%MZ').tolist())
    
    checks = []
    asleep = np.zeros(len(all_dates))
    for i in range(0,len(df_set)):
        event = df_set['DMY'][i].strftime('%Y-%m-%dT%H:%MZ')
        if event in all_dates:
            checks.append(1)
            event_idx = all_dates.index(event)
            event_idx_end = int(df_set['Duration (min)'][i])

            asleep[event_idx: event_idx+event_idx_end] = 1
        
    events = pd.DataFrame({'Date':all_dates,'Activity':asleep})
    events['Date']= pd.to_datetime(events['Date'])
    events['Year'] = [i.year for i in events['Date'] ]
    events['Month'] = [i.month for i in events['Date'] ]
    events['Day'] = [i.day for i in events['Date'] ]
    events['Hour'] = [i.hour for i in events['Date'] ]
    events['Minute'] = [i.minute for i in events['Date'] ]
    events['weekday'] = pd.DatetimeIndex(events['Date']).weekday
    weekday = {0:'Monday', 1:'Tuesday', 2:'Wednesday',3:'Thursday',4:'Friday',5:'Saturday',6:'Sunday'}
    events['weekday_day'] = events['weekday'].map(weekday)
    
    # add the weeks
    min_in_weeks = 10080
    weeks_in_data = len(events) / min_in_weeks
    
    weeks_repeated = np.repeat(range(1,math.ceil(len(events) / min_in_weeks + 1)),7*24*60)
    weeks_shortened = weeks_repeated[0:len(events)]
    
    events['weeks'] = weeks_shortened
    
    return events


def analyze_minute_data(dfa,days):
    dfa = dfa[dfa['weekday_day'].isin(days)]
    sleep_by_hour = dfa.groupby('Hour').sum()['Activity']
    sleep_by_hour_perc = sleep_by_hour * 100 / dfa.groupby('Hour').count()['Activity'][0]
    return sleep_by_hour_perc

def calulate_smooth(perctages,k):
    xnew = np.linspace(perctages.index.min(), perctages.index.max(), 300) 
    spl = make_interp_spline(perctages.index, perctages, k=k)  # type: BSpline
    smooth = spl(xnew)
    return xnew,smooth



### RUN FUNCTION 1
sleep_df = return_minute_data(df,'Sleep')


# how often is the baby asleep
print('sleep')
sleep_df['Activity'].value_counts(1)


### RUN FUNCTION 2
days = np.unique(sleep_df['weekday_day']) # all  days
days = np.unique(['Saturday','Sunday']) # just weekend
sleep_by_hour_perc = analyze_minute_data(sleep_df,days)


xnew, power_smooth_sleep = calulate_smooth(sleep_by_hour_perc,3)


color_chosen = 'skyblue'
fig= plt.figure(figsize=(12,6))
plt.plot(xnew, power_smooth_sleep,color = color_chosen, label = 'Your Daughter')
plt.fill_between(xnew, power_smooth_sleep,color=color_chosen,alpha=.4)
plt.xlabel('Hour')
plt.ylabel('Probability Asleep (%)')
plt.xticks(sleep_by_hour.index)
plt.savefig('Sleep_FingerPrint_weekend.png')
plt.show()


# add second finger pring
#new_baby = sleep_by_hour_perc + np.random.normal(-12,6,len(sleep_by_hour_perc))
#spl_2 = make_interp_spline(sleep_by_hour.index, new_baby, k=3)  # type: BSpline
#power_smooth_2 = spl_2(xnew)
#color_chosen = 'lightpink'
#plt.figure(1)
#plt.plot(xnew, power_smooth_2,color = color_chosen,alpha=.5, label = 'Average 6-mo Girl')
#plt.fill_between(xnew, power_smooth_2,color=color_chosen,alpha=.3)
#plt.legend()
#plt.savefig('Sleep_FingerPrint_Comparison.png')
#plt.show()



weeks = np.unique(sleep_df['weeks'])

r,c = 4,3
plt.figure(figsize=(24,32))
for i in range(0,len(weeks)):
    plt.subplot(r,c,i+1)
    mask_df = sleep_df[sleep_df['weeks'] == weeks[i]]
    sleep_by_hour_perc_week_i = analyze_minute_data(mask_df,days)
    x, y = calulate_smooth(sleep_by_hour_perc_week_i,1)
    plt.plot(x, y,color = color_chosen, label = 'Your Daughter')
    plt.fill_between(x, y,color=color_chosen,alpha=.4)
    plt.hlines(np.average(y),np.min(x),np.max(x),colors='r',linestyles='dotted')
    plt.xlabel('Hour')
    plt.ylabel('Probability Asleep (%)')
    plt.xticks(sleep_by_hour.index[::2])
    plt.title('Week ' +str(i+1))
        
plt.savefig('Sleep_FingerPrint_over_weeks.png')


