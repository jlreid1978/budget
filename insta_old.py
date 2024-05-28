import json
import os

follow =[]
following = []


with open('followers_1.json', 'r') as f,open('following.json', 'r') as g, open('followers_2.json') as ff:
  f = json.load(f)
  ff = json.load(ff)
  g = json.load(g)
  for i in f:
    idata = (i.get('string_list_data'))
    for d in idata:
      fls = (d.get('value'))
    follow.append(fls)
    
 
  for ii in ff:
    iidata = (ii.get('string_list_data'))
    for dd in iidata:
      fls2 = (dd.get('value'))
    follow.append(fls2)
  


    
  #for n in g:
  gn = (g.get('relationships_following'))
  for n in gn:
    gdata = n.get('string_list_data')
    for a in gdata:
      flg = a.get('value')
      following.append(flg)
      
      
      
for l in following:
  if l not in follow:
    print(l)
