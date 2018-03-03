from pathlib import Path

import json

import MeCab

import sys

import pickle

if '--step1' in sys.argv:
  m = MeCab.Tagger('-Owakati')

  data = []
  for name in Path('./jsons').glob('*'):
    obj = json.load(name.open())
    if obj.get('fav') is None:
      continue
    detail = m.parse(obj['detail']).strip().split()
    fav    = obj['fav']
    data.append( (fav, detail) )
  pickle.dump(data, open('data.pkl', 'wb'))

if '--step2' in sys.argv:
  data = pickle.load(open('data.pkl', 'rb'))
  term_freq = {}
  for fav, detail in data:
    for term in detail:
      if term_freq.get(term) is None:
        term_freq[term] = 0
      term_freq[term] += 1 
  
  term_freq = {term:freq for term, freq in sorted(term_freq.items(), key=lambda x:x[1]*-1)[:15000] }
  json.dump(term_freq, open('term_freq.json', 'w'), indent=2, ensure_ascii=False)

if '--step3' in sys.argv:
  data = pickle.load(open('data.pkl', 'rb'))
  
  term_freq = json.load(open('./term_freq.json'))

  term_index = {}
  for fav, detail in data:
    for term in detail:
      if term not in term_freq:
        continue
      if term_index.get(term) is None:
        term_index[term] = len(term_index)

  json.dump(term_index, open('term_index.json', 'w'), indent=2, ensure_ascii=False)

import numpy as np
from   collections import Counter
import math
if '--step4' in sys.argv:
  data = pickle.load(open('data.pkl', 'rb'))
  
  term_index = json.load(open('term_index.json'))

  Xs, Ys = np.zeros((len(data), len(term_index)), dtype=float), np.zeros((len(data)), dtype=float)
  for index, (fav, detail) in enumerate(data):
    detail = dict(Counter(detail)) 
    
    Ys[index] = fav
    for term, freq in detail.items():
      if term not in term_index:
        continue
      Xs[index, term_index[term] ] = math.log(freq+1)

  np.save('Xs', Xs);np.save('Ys', Ys)

import random
from sklearn.linear_model import ElasticNet
from sklearn.metrics import mean_absolute_error as mae

if '--step5' in sys.argv:
  Xs, Ys = np.load('./Xs.npy'), np.load('./Ys.npy')
  
  size = len(Xs)

  Xs, Ys, Xst, Yst = Xs[:int(size*0.8)], Ys[:int(size*0.8)], Xs[int(size*0.8):], Ys[int(size*0.8):]

  def _search(arg):
    alpha, l1_ratio = arg
    elasticnet = ElasticNet(alpha=alpha, l1_ratio=l1_ratio, selection='random', random_state=0)
    elasticnet.fit(Xs,Ys)
    yps = elasticnet.predict(Xst)
    name = (f'mae={mae(Yst, yps):018.09f}_alpha={alpha:0.4f}_l1_ratio={l1_ratio:0.4f}')
    print(name)
    open(f'models/{name}', 'wb').write( pickle.dumps(elasticnet) )

  alphas    = [0.1*i for i in range(1, 13)]
  l1_ratios = [0.2*i for i in range(1,5)]
  params = []
  for alpha in alphas:
    for l1_ratio in l1_ratios:
      params.append( (alpha, l1_ratio) )
  params = random.sample(params, len(params))
  [_search(param) for param in params] 

import pickle
from pathlib import Path
import json
if '--step6' in sys.argv:
  best = sorted(Path('models/').glob('*')).pop(0)
  elastic = pickle.load(best.open('rb'))

  term_id = json.load(fp=open('./term_index.json'))
  id_term = { id:term for term, id in term_id.items() }

  term_weight = {}
  for index, weight in enumerate(elastic.coef_.tolist()):
    term = id_term[index]   
    if abs(weight) > 0.01:
      term_weight[term] = weight

  for term, weight in sorted(term_weight.items(), key=lambda x:x[1]*-1):
    print(term, weight)

