from pathlib import Path

import json

spec_tag_freq = {}
for name in Path('./jsons').glob('*'):
  obj = json.load(name.open())
  if obj.get('href') is None:
    continue

  #print(obj)
  for spec in ['ボーイズラブ', 'レディースコミック', 'ガールズラブ', 'ティーンズラブ', 'アダルト']:
    if spec_tag_freq.get(spec) is None:
      spec_tag_freq[spec] = {}

    if spec in obj['tags']:
      
      for tag in obj['tags']:
        if spec_tag_freq[spec].get(tag) is None:
          spec_tag_freq[spec][tag] = 0
        spec_tag_freq[spec][tag] += 1

json.dump(spec_tag_freq, fp=open('spec_tag_freq.json', 'w'), indent=2, ensure_ascii=False)

commons = set()
for spec, tag_freq in spec_tag_freq.items():
  _common = set( [tag for tag, freq in sorted(tag_freq.items(), key=lambda x:x[1]*-1)[:10]] )
  if commons == set():
    commons = _common
  else:
    commons = _common & commons
  print(commons) 

print(commons)
for spec, tag_freq in spec_tag_freq.items():
  for index, (tag, freq) in enumerate(sorted(tag_freq.items(), key=lambda x:x[1]*-1)[:50]):
    if tag in commons:
      continue
    print(spec, index, tag, freq)
