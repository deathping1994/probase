import requests
import datetime
from requests.auth import HTTPBasicAuth
from elasticsearch import Elasticsearch
import time
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
baseurl="https://api.github.com/repositories?since="
curid=1
requestcount=0
userpass=HTTPBasicAuth('user','302106b123fa77b1a6c31fb69459e1a460aca64c')
while(curid<20000000):
    r=requests.get(baseurl+str(curid),auth=userpass)
    requestcount+=1
    repos=r.json()
    doclist=[]
    doc={}
    print type(repos)
    for repo in repos:
        doc['title']=repo['name']
        doc['description']=repo['description']
        doc['html_url']= repo['html_url']
        lang=requests.get(repo['languages_url'],auth=userpass)
        requestcount+=1
        langs=lang.json()
        langused=[]
        for key in langs:
            langused.append(key)
        doc['lang']=langused
        es.index(index='github_repos',id=str(repo['id']), doc_type='projects', body=doc)
    last=repos[-1]
    curid=int(last['id'])
    print curid
    if(requestcount==4995):
        time.sleep(3700)
        requestcount=0
__author__ = 'gaurav'
