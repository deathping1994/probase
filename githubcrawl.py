import random
import decimal
import string
import requests
import datetime
from requests.auth import HTTPBasicAuth
from elasticsearch import Elasticsearch
import time
from app import app,mongo
from pymongo import MongoClient
mongo = MongoClient()
db=mongo.projectbase
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])
mentor=[
        "sanjeevsharma",
        "sanjeevksharma",
        "sanjaygupta",
        "Sanjay Goel",
        "sangeetamittal",
        "sangeeta",
        "sandeepsingh",
        "sanchikagupta",
        "samiyakhan",
        "samirdevgupta",
        "sakshiagarwal",
        "rubybeniwal",
        "rohitpalsingh",
        "rkdwivedi",
        "riteshsharma",
        "richagupta",
        "reemagabrani",
        "reemabudhiraja",
        "rcjain",
        "ravishanker",
        "ravindrakumar",
        "rakhibansal",
        "rajnishmisra",
        "Rajkumartiwari",
        "rajeshdubey",
        "rajalakshmi",
        "RAHULSHARMA",
        "rahulkaushik",
        "radhikakhanna",
        "rachana",
        "purteekohli",
        "puneetrana",
        "puneetpannu",
        "priyankaarora",
        "priyadarshini",
        "pratibhayadav",
        "prashantkaushik",
        "prakashkumar",
        "pawanupadhyay",
        "patokumari",
        "parulpuri",
        "parulagarwal",
        "parmeetkaur",
        "papiachowdhury",
        "pankajyadav",
        "pankajpachauri",
        "pammigauba",
        "padamkumar",
        "niyatiaggrawal",
        "nitinchanderwal",
        "nidhisinha",
        "nidhigupta",
        "nfaruqui",
        "nehasrivastava",
        "neetusingh",
        "neetusardana",
        "neerjapande",
        "neerajwadhwa",
        "navneetsharma",
        "navendugoswami",
        "naseemabidi",
        "namitasinghal",
        "muktamani",
        "muktagoyal",
        "mukeshkumar",
        "mudayabanu",
        "mstyagi",
        "mrbehera",
        "moonisshakeel",
        "monikajiit",
        "monicachaudhary",
        "minakshigujral",
        "megharathi",
        "mc srivastava",
        "masanjeev",
        "manojsahni",
        "manojchauhan",
        "manishthakur",
        "MANISHkumar",
        "anirban pathak",
        "anilkumargupta",
        "amrishaggarwal",
        "amrinakausar",
        "amitverma",
        "amanpreetkaur",
        "alokchauhan",
        "alkasharma",
        "Alka Choubey",
        "akvadehra",
        "adwitiyasinha",
        "aditisharma",
        "aditijain",
        "adarshkumar",
        "abhinavgupta",
        "abbhattacharyya",
        "aayusheegupta",
        "ankitagupta",
        "ankitawadhwa",
        "ankurbhardwaj",
        "anshubanwari",
        "anuja",
        "anujbhardwaj",
        "anujgupta",
        "aradhanagoyal",
        "archanapurwar",
        "arpitajadhav",
        "ashishgoel",
        "ashokwahi",
        "ashwanimathur",
        "asitbandyopadhayay",
        "atulsrivastava",
        "ayushi gupta",
        "badribajaj",
        "bani singh",
        "BhagwatiPrasad",
        "bharatgupta",
        "bhawnagupta",
        "bhubeshjoshi",
        "chakreshjain",
        "chetnadabas",
        "chetnagupta",
        "debdeepde",
        "deepaksharma",
        "deepaliverma",
        "deependerdabas",
        "dhanalekshmig",
        "dharmveerrajpoot",
        "divakaryadav",
        "gagandeepkaur",
        "Gagandeepsingh",
        "garimakapur",
        "garimamathur",
        "gauravverma",
        "gkagarwal",
        "gssrivastava",
        "heman",
        "hemantmeena",
        "himagupta",
        "hsdagar",
        "indirasarethy",
        "induchawla",
        "ipsitanandi",
        "jasminesaini",
        "jhumursengupta",
        "jitendramishra",
        "jpgupta",
        "juhi",
        "kamalrawal",
        "kanishksingh",
        "kanupriyamisra",
        "kashavajmera",
        "kavitapandey",
        "kc mathur",
        "kenandini",
        "kirmendersingh",
        "kishorekumar",
        "kishorethapliyal",
        "krishna asawa",
        "krishnagopal",
        "krishnasundari",
        "kuldeepsingh",
        "lokendrakumar",
        "madhujain",
        "mahendragurve",
        "maneeshakarn",
        "manishasingh",
        "santosh dev",
        "santoshisen",
        "satishchandra",
        "sbhattacharya",
        "scsaxena",
        "shalinimani",
        "shamimakhter",
        "shardhaporwal",
        "sharmistha",
        "shikhajain",
        "shikhamehta",
        "shirinalavi",
        "shradhasaxena",
        "shrirampurankar",
        "shrutisabharwal",
        "shubhanginirathore",
        "shwetadang",
        "skkhanna",
        "skraina",
        "smritibhatnagar",
        "smritigaur",
        "somyajain",
        "sppurohit",
        "sreejithr",
        "ssuresh",
        "sudhasrivastava",
        "sujatakapoor",
        "sujatamohanty",
        "sumadawn",
        "sumeghayadav",
        "supratimdas",
        "supreetkaurbakshi",
        "sushantsadotra",
        "sushilkumar",
        "swatirawal",
        "swatisharma",
        "tajalam",
        "tanujchauhan",
        "tribhuwantewari",
        "tushitashukla",
        "vandanaahuja",
        "vibhagupta",
        "vibharani",
        "vijaykhare",
        "vikaspandey",
        "vikassaxena",
        "vikramkarwal",
        "vimalkumar",
        "vineetkhandelwal",
        "Vinkysharma",
        "vishalsaxena",
        "VivekDwivedi",
        "vivekmishra",
        "viveksajal",
        "yajmedury",
        "yashikarustagi",
        "yogeshgupta",
        "yogeshsingh"
    ]
baseurl="https://api.github.com/repositories?since="
def github():
    curid=400000
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

def probase():
    curid=300000
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
            doc['mentor']=[random.choice(mentor)]
            doc['title']=repo['name']
            doc['description']=repo['description']
            doc['source_code']= repo['html_url']
            doc['projecttype']=random.choice(["major","minor"])
            doc['approved']=random.choice([True,False])
            doc['evaluated']=random.choice([True,False])
            doc['remarks']=random.choice(["Good work","Excellent","Bad","Could have been better"])
            doc['rating']=decimal.Decimal(random.randrange(1000))/100
            memberlist=[]
            membersid=[]
            member={}
            for i in range(0,3):
                member['eno']=''.join(random.choice(string.digits) for _ in range(8))
                membersid.append(member['eno'])
                member['name']=repo['owner']['login'] + str(i)
                member['email']=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(7)) + "@gmail.com"
                memberlist.append(member.copy())

            lang=requests.get(repo['languages_url'],auth=userpass)
            requestcount+=1
            langs=lang.json()
            langused=[]
            for key in langs:
                langused.append(key)
            doc['lang']=langused
            if doc['description'] is not None:
                doc['synopsis-text']="http://random.org"+doc['description']
                doc['synopsis']="## This is markdown" +"\n" + doc['description']
            else:
                doc['synopsis-text']="http://random.org"
                doc['synopsis']="## This is markdown but no synopsis"
            members=[]
            day=datetime.datetime.now()
            try:
                res=db.groups.insert({"projecttype":doc['projecttype'],
                                        "members":membersid,"semester":random.choice(['4','5','6','7','8']),
                                        'evaluated':doc['evaluated'],
                                            'approved':doc['approved'],"registeredBy":"DUMMY","registeredOn":str(day)})
                es.index(index='probase_repos',id=str(res), doc_type='projects', body=doc)
            except Exception as e:
                pass
        last=repos[-1]
        curid=int(last['id'])
        print curid
        if(requestcount==4995):
            time.sleep(3700)
            requestcount=0

def main():
    choice=input("Enter 1 for github and 2 for probase:")
    if choice=='1':
        github()
    else:
        probase()

if __name__ == "__main__":
    main()
__author__ = 'gaurav'
