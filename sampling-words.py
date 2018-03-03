
from pathlib import Path

import json

import MeCab

fp = open('corpus.txt', 'w')
m = MeCab.Tagger('-Owakati')
for name in Path('./jsons').glob('*'):
  obj = json.load(name.open())
  if obj.get('detail') is None:
    continue
  t = m.parse(obj['detail']).strip()
  fp.write( f'{t}\n' )
