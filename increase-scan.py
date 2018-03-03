

from pathlib import Path

import json

import datetime

import pickle

import sys

import math

if '--make_hist' in sys.argv:
  tag_stamp_freq = {}

  stamp_basefreq = {}
  for name in Path('./jsons').glob('*'):
    obj = json.load(name.open())

    try:
      pubdate = obj['pubdate']
      splits = pubdate.split('/')
      year, month = splits[0], splits[1]
      # 粒度は年、月
      dt   = datetime.datetime.strptime(f'{year} {month}', '%Y %m')  
    except Exception as ex:
      print(ex)
      continue
    tags = obj['tags']
    stamp = (int(dt.timestamp()))
    if stamp_basefreq.get(stamp) is None:
      stamp_basefreq[stamp] = 0
    stamp_basefreq[stamp] += 1

    for tag in tags:
      if tag_stamp_freq.get(tag) is None:
        tag_stamp_freq[tag] = {}
      if tag_stamp_freq[tag].get(stamp) is None:
        tag_stamp_freq[tag][stamp] = 0
      tag_stamp_freq[tag][stamp] += 1
  pickle.dump(tag_stamp_freq, open('tag_stamp_freq.pkl', 'wb'))
  pickle.dump(stamp_basefreq, open('stamp_basefreq.pkl', 'wb'))

from scipy import stats
if '--step2' in sys.argv:
  tag_stamp_freq = pickle.load(open('tag_stamp_freq.pkl', 'rb'))
  stamp_basefreq = pickle.load(open('stamp_basefreq.pkl', 'rb'))

  data = []
  for tag, stamp_freq in tag_stamp_freq.items():

    # サンプリングバイアスを解消
    #Ys = [ freq/stamp_basefreq[stamp] for stamp, freq in stamp_freq.items() ] 
    Ys = [ freq for stamp, freq in stamp_freq.items() ] 
    if len(Ys) < 5:
      continue
    Xs = [ math.log(stamp) for stamp, freq in stamp_freq.items() ] 
    if sum(Xs) < 500:
      continue
    slope, intercept, r_value, p_value, std_err = stats.linregress(Xs,Ys)
    data.append( (tag, slope, intercept, r_value**2, std_err) )

  for data in sorted(data, key=lambda x:x[1]):
    tag, slope, intercept, r_pow, stderr = (data)
    print(f'tag={tag} 傾き={slope} inercept={intercept} r-pow={r_pow} stderr={stderr}')

if '--step3' in sys.argv:
  tag_stamp_freq = pickle.load(open('tag_stamp_freq.pkl', 'rb'))
  stamp_basefreq = pickle.load(open('stamp_basefreq.pkl', 'rb'))
 
  for tag in ['女装', 'BL', '不倫']:
    stamp_freq = tag_stamp_freq[tag]
    for stamp, freq in sorted(stamp_freq.items(), key=lambda x:x[0]):
      day = datetime.datetime.fromtimestamp(stamp).strftime('%Y-%m')
      print(tag, day, stamp, freq/stamp_basefreq[stamp])
