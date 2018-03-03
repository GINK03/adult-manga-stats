from pathlib import Path

import bs4

import gzip

import MeCab

import concurrent.futures

import json

import lxml

import hashlib
def _map(arg):
  key, names = arg

  m = MeCab.Tagger('-Owakati')

  for name in names:
    try:
      html = gzip.decompress(name.open('rb').read()).decode()
      soup = bs4.BeautifulSoup(html, 'lxml')
      
      title = soup.find('h1', {'class':'m-boxDetailProduct__info__ttl'})
      if title is None:
        continue
      title = title.text
      print(title)
      
      ls = list(filter(lambda x:x.get('rel') == ['canonical'] , soup.find_all('link')))
      if ls == []:
        continue
      href = ls.pop().get('href')
      
      
      pubdate = soup.find('dd', {'class':'m-boxDetailProductInfo__list__description'})
      if pubdate is None:
        continue
      pubdate = pubdate.text.strip()

      #fav = soup.find('span', {'class':'m-txtDetailProductInfoFavoriteNum'})
      
      #fav.text.strip().replace(',', '')
      #fav = int(fav)

      detail = soup.find('div', {'class':'m-boxDetailProduct__info__story'})
      detail = detail.text.strip()

      _tags = soup.find_all('li', {'class':'m-boxDetailProductInfo__list__description__item'})

      tags = [] 
      for tag in _tags:
        for _tag in m.parse(tag.text.strip()).strip().split():
          tags.append(_tag)

      #obj = {'tags':tags, 'title': title, 'href':href, 'pubdate':pubdate, 'fav':fav, 'detail':detail }
      obj = {'tags':tags, 'title': title, 'href':href, 'pubdate':pubdate, 'detail':detail }
      
      print(href, obj)
      h   = hashlib.sha256(bytes(href, 'utf8')).hexdigest()
      json.dump(obj, fp=open(f'jsons/{h}.json', 'w'), indent=2, ensure_ascii=False)
    except Exception as ex:
      print(ex)
      ...



args = {}
for index, name in enumerate(Path('../scraping-designs/dmm-book-scrape/htmls').glob('*')):
  key = index%16
  if args.get(key) is None:
    args[key] = []
  args[key].append( name )
args = [(key,names) for key, names in args.items()]
#_map(args[0])
with concurrent.futures.ProcessPoolExecutor(max_workers=32) as exe:
  exe.map(_map, args)
