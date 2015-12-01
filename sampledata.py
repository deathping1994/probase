import string
from app import mongo,es,ObjectId,datetime
import random
import decimal
import xlrd

def create_sample():
    try:
        path="Project 2014-15.xlsx"
        book = xlrd.open_workbook(path)
        sheet = book.sheet_by_index(0)
        print "Reading from excel file"
        for row in range (5,20):
            jsonobj={}
            members=[]

            member={}
            mentor=[]
            membersid=[]
            jsonobj['projecttype']=random.choice(["major","minor"])
            jsonobj['lang']=random.choice(["C++","Perl","Ruby","Python","Java",".Net","ASP","PHP","C"])
            jsonobj['approved']=random.choice([True,False])
            jsonobj['evaluated']=random.choice([True,False])
            jsonobj['source_code']="http://random.org"
            jsonobj['synopsis']="http://random.org"
            jsonobj['remarks']=random.choice(["Good work","Excellent","Bad","Could have been better"])
            jsonobj['rating']=decimal.Decimal(random.randrange(1000))/100
            data=sheet.cell_value(row,10)
            jsonobj["title"]=str(data)
            data=sheet.cell_value(row,9)
            jsonobj["description"]=data
            data=sheet.cell_value(row,8)
            member['eno']=str(data)[:-2]
            member['name']=""
            member['email']=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(7)) + "@gmail.com"
            members.append(member.copy())
            membersid.append(str(data)[:-2])
            data=sheet.cell_value(row,7)
            member['eno']=str(data)[:-2]
            member['name']=""
            member['email']=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(7)) + "@gmail.com"
            members.append(member.copy())
            membersid.append(str(data)[:-2])
            data=sheet.cell_value(row,3)
            member['eno']=str(data)[:-2]
            member['name']=""
            member['email']=''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(7)) + "@gmail.com"
            members.append(member.copy())
            membersid.append(str(data)[:-2])
            data=sheet.cell_value(row,5)
            mentor.append(data)
            jsonobj['members']=members
            jsonobj['mentor']=mentor
            print jsonobj
            res=mongo.db.groups.insert({"projecttype":jsonobj['projecttype'],"members":membersid})
            es.index(index='probase_repos',id=str(res), doc_type='projects', body=jsonobj)
            members=[]

        print("Inserting Dates")
        doc={
            "_id" : ObjectId("565dbe993fb58bb4129af671"),
            "projecttype" : "minor",
            "action" : "registration",
            "date" : datetime(2016,10,01,0,0)
            }
        res=mongo.db.dates.insert(doc)
        doc={
            "projecttype" : "major",
            "action" : "registration",
            "date" : datetime(2016,12,01,0,0)
            }
        res=mongo.db.dates.insert(doc)

        print("inserting teachers")
        doc={
                "_id" : ObjectId("560d604a080ffddcba75178d"),
                "name" : [
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
            }
        res=mongo.db.teachers.insert(doc)
    except Exception as e:
        raise e

__author__ = 'gaurav'



