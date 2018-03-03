
from pathlib import Path

import json

import MeCab

import sys

import pickle


if '--step1' in sys.argv:
  type_occs = {} 

  violences = set()
  for line in open('./utils/violence-words.txt'):
    line = line.strip()
    words = line.split('、')
    for word in words:
      violences.add(word)

  m = MeCab.Tagger('-Owakati')
  data = []
  for name in Path('./jsons').glob('*'):
    obj = json.load(name.open())
    if obj.get('detail') is None:
      continue
    detail = set(m.parse(obj['detail']).strip().split())
   
    if obj.get('fav') is not None:
        occ = len(detail & violences)
        #print('For men', occ)
        if type_occs.get('formen') is None:
          type_occs['formen'] = []
        type_occs['formen'].append( occ )
      
    for type in ['ボーイズラブ', 'ガールズラブ', 'レディースコミック'] :
      if type in obj['tags']:
        occ = len(detail & violences)
        if type_occs.get(type) is None:
          type_occs[type] = []
        type_occs[type].append( occ )
        #print(type, occ)

  json.dump(type_occs, fp=open('type_occs.json', 'w') )

import statistics
if '--step2' in sys.argv:
  type_occs = json.load(fp=open('type_occs.json'))

  for type, occs in type_occs.items():
    print(type, len(occs), statistics.mean(occs))

from scipy import stats
if '--step3' in sys.argv:
  type_occs = json.load(fp=open('type_occs.json'))

  alls = [0, 0]
  for occs in type_occs.values():
    for occ in occs:
      if occ == 0:
        alls[0] += 1
      else:
        alls[1] += occ
  lcs = [0, 0]
  for occ in type_occs['レディースコミック']:
    if occ == 0:
      lcs[0] += 1
    else:
      lcs[1] += occ
  lcs = list(map(lambda x:x, lcs))
  alls = [ a/sum(alls)*sum(lcs) for a in alls]
  print(f'全体 {alls}')
  print(f'レディコミ {lcs}')
  
  chisq,p = stats.chisquare(lcs,alls)
  print(f'chisq={chisq}, p={p}')

if '--step4' in sys.argv:
  type_occs = json.load(fp=open('type_occs.json'))

  bls = [0, 0]
  for occ in type_occs['ボーイズラブ']:
    if occ == 0:
      bls[0] += 1
    else:
      bls[1] += occ
  fms = [0, 0]
  for occ in type_occs['formen']:
    if occ == 0:
      fms[0] += 1
    else:
      fms[1] += occ

  fms = [ a/sum(fms)*sum(bls) for a in fms]
  print(f'ボーイズラブ {bls}')
  print(f'男性向け {fms}')
  
  chisq,p = stats.chisquare(fms,bls)
  print(f'chisq={chisq}, p={p}')
