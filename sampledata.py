import string
from app import mongo,es
import random
import decimal
import xlrd

def create_sample():
    path="Project 2014-15.xlsx"
    book = xlrd.open_workbook(path)
    sheet = book.sheet_by_index(0)

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


__author__ = 'gaurav'



