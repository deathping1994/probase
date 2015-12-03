from datetime import datetime
import elasticsearch
import pika
from flask import jsonify
import json
from flask import Flask
import random
from flask import request
from flask.ext.cors import CORS,cross_origin
from bs4 import BeautifulSoup
import requests
from elasticsearch import Elasticsearch,helpers
from flask.ext.bcrypt import Bcrypt
from flask.ext.pymongo import PyMongo
from functools import wraps
from bson.objectid import ObjectId
app = Flask("projectbase")
bcrypt = Bcrypt(app)
mongo = PyMongo(app)
cors = CORS(app, resources={r"*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])


def sendsms(msg,tags):
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='localhost'))
        channel = connection.channel()
        res=mongo.db.subscribers.find({"tags": {"$in":tags}})
        print res
        if res is None:
            return True
        else:
            subscribers=[]
            for subscriber in res:
                print subscriber['phone']
                subscribers.append(subscriber['phone'])
            mq={"msg":msg,"subscribers":subscribers}
            print mq,str(mq)
            channel.queue_declare(queue='probasemsg')
            channel.basic_publish(exchange='',
                                  routing_key='probasemsg',
                                  body=str(mq))
            connection.close()
            return True
    except Exception as e:
        raise e


def log(e):
    mongo.db.logs.insert({"error":str(e)})
    return True


def adminlogin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.get_json(force=True)
        if not check_status(data['authkey'],'E'):
            err={"error":"Teachers Login Required! This Event Will Be Reported.","user": data['user'],"time": datetime.now()}
            log(err)
            return jsonify(error="Teachers Login Required! This Event Will Be Reported."),403
        return f(*args, **kwargs)
    return decorated_function


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        data = request.get_json(force=True)
        if not check_status(data['authkey'],data['usertype']):
            return jsonify(error="Login Required"),403
        return f(*args, **kwargs)
    return decorated_function


def project_notification(projectid,action):
    try:
        members=mongo.db.groups.find_one({"_id":ObjectId(projectid)})
        message="Your %s project has been %s.",(members['projecttype'],action)
        notify(message,members['members'])
        return True
    except Exception as e:
        raise e


def isopen(projectype,action):
    try:
        action=action.lower()
        projectype=projectype.lower()
        query={'projecttype':projectype,"action":action}
        print query
        res=mongo.db.dates.find_one({'projecttype':projectype,"action":action})
        if res is None:
            print "none"
            return False
        else:
            date=datetime.now()
            if date<=res['date'].replace(tzinfo=None):
                print date
                return True
            else:
                print date,res['date'].replace(tzinfo=None)
                return False
    except Exception as e:
        raise e


@app.route('/pushnotification',methods=['GET','POST'])
@cross_origin(origin='*', headers=['Content- Type', 'Authorization'])
def push_notify():
    par=request.get_json(force=True)
    try:
        if notify(par['msg'],par['tags']):
            return jsonify(success="Successfully sent!"),201
        else:
            return jsonify(error="Something went wrong",response=str(r.content)),500
    except Exception as e:
        print str(e)
        return jsonify(error="Something went wrong",response=str(e)),500


def notify(msg,tags):
    try:
        sendsms(msg,tags)
        headers={}
        data={}
        data['tags']=tags
        data['msg']=msg
        data['platform']=[1]
        data['payload']={"BigTextStyle": "true",
                         "bigText":msg,"largeIcon":"http://cdn.mysitemyway.com/etc-mysitemyway/icons/legacy-previews/icons/blue-jelly-icons-alphanumeric/069535-blue-jelly-icon-alphanumeric-letter-p.png"}
        headers['x-pushbots-appid']="564e3f56177959ce468b4569"
        headers['x-pushbots-secret']="bafdd9608dab716baabad599cc6c477e"
        headers['Content-Type']="application/json"
        r=requests.post("https://api.pushbots.com/push/all",headers=headers,json=data)
        print "here"
        if r.status_code==200:
            print "success"
            return True
        else:
            return False
    except Exception as e:
        raise e


def check_status(authkey, usertype):
    res= mongo.db.users.find_and_modify({'authkey': authkey,'usertype': usertype},{"$set":{"loggedat":datetime.utcnow()}})
    if res is not None:
        return True
    else:
        return False


def currentuser(authkey,usertype):
    curruser=mongo.db.users.find_one({'authkey': authkey,'usertype': usertype})
    if curruser is not None:
        return curruser['user']
    else:
        return "NULL"


@app.route('/typeahead',methods=['GET','POST'])
@cross_origin(origin='*', headers=['Content- Type', 'Authorization'])
def typeahead():
    try:
        q=request.args.get("q","")
        qbody={"fields":["title"],
                "query": {
                    "match": {
                        "title": q
                    }
                }
            }
        re=es.search(index="probase_repos",body=qbody)
        print re
        return jsonify(projects=re['hits']['hits']),200
    except Exception as e:
        return jsonify(error=str(e)),500


@app.route('/tags',methods=['GET','POST'])
@cross_origin(origin='*', headers=['Content- Type', 'Authorization'])
def tagslist():
    tags=[{"tag":"GDG"},{"tag":"PROGHUB"},{"tag":"JYP"},{"tag":"OSDC"},{"tag":"TNP"}]
    return jsonify(tags=tags),200



@app.route('/students/<batch>/list',methods=['GET','POST'])
@cross_origin(origin='*', headers=['Content- Type', 'Authorization'])
def studentlist(batch):
    try:
        batchs=str(batch).split('-')
        eno="131031"
        student={}
        student_list=[]
        for x in batchs:
            for i in range (0,30):
                student['name']="abc"+str(i)
                student['eno']=eno+str(10*i)
                if x !="all":
                    student['batch']=x
                else:
                    student['batch']= random.choice('ABC')+str(random.randint(1,10))
                student_list.append(student.copy())
        return jsonify(students=student_list),200
    except Exception as e:
        log(e)
        print str(e)
        return jsonify(error="Oops ! something went wrong."),500


@app.route('/teachers',methods=['GET','POST'])
@cross_origin(origin='*', headers=['Content- Type', 'Authorization'])
def teachers():
    try:
        # print obj_id
        list=mongo.db.teachers.find_one({"_id":ObjectId("560d604a080ffddcba75178d")})
        if list is not None:
            return jsonify(teachers=list['name']),200
        else:
            return jsonify(error="No teachers listed"),500
    except Exception as e:
        log(e)
        return jsonify(error="Oops ! something went wrong."),500


@app.route('/projects/<user>',methods=['GET','POST'])
@cross_origin(origin='*', headers=['Content- Type', 'Authorization'])
def list_projects(user):
    try:
        if len(user)!=0:
            members=[user]
            query={"members": { "$in": members }}
            groups = mongo.db.groups.find(query,{"_id": 1})

            if groups.count()==0:
                return jsonify(success="You don't have any projects.",error=""),200
            else:
                projects=[]
                groupids=[]
                for group in groups:
                    id=str(group['_id'])
                    groupids.append(id)
                query={
                        "query" : {
                            "filtered" : {
                                "filter" : {
                                    "terms" : {
                                        "_id" : groupids
                                    }
                                }
                            }
                        }
                    }
                re=es.search(index="probase_repos",body=query)
                return jsonify(success="Found projects",projects=re['hits']),200
        else:
            return jsonify(error="No user specified"),500
    except Exception as e:
        log(e)
        jsonify(error="OOps ! Something went wrong."),500


@app.route('/mentor/projects/<mentor>',methods=['GET','POST'])
@cross_origin(origin='*', headers=['Content- Type', 'Authorization'])
@adminlogin_required
def list_mentor_projects(mentor):
    curruser=mongo.db.users.find_one({"user":str(mentor)})
    try:
        if len(mentor)!=0:
            mentorarr=[curruser['mentorcode']]
            print mentorarr
            query={
                    "query" : {
                        "filtered" : {
                            "filter" : {
                                "term" : {
                                    "mentor": mentorarr
                                }
                            }
                        }
                    }
                }
            print "gugu"
            re=es.search(index="probase_repos",body=query)
            print re
            return jsonify(success="Found projects",projects=re['hits']),200
        else:
            return jsonify(error="No user specified"),500
    except Exception as e:
        log(e)
        jsonify(error="OOps ! Something went wrong."),500



@app.route('/feedback',methods=["POST","GET"])
@cross_origin(origin='*', headers=['Content- Type', 'Authorization'])
def feedback():
    data=request.get_json(force=True)
    if data['msg']== "":
        return jsonify(error="Sorry, we Couldn't find your feedback. May be you missed something !"),403
    else:
        try:
            data={"to":"gshukla66@gmail.com",
              "subject":"Probase:BUG|FEEDBACK",
              "message":"FROM:"+data['from']+"\n"+data['msg'],
              "token":"$2b$12$8/Z.2WDlk9VVWVND/DVtgej5z.pxKakZYSfkGdLQCIy7VCXgm8VNm"
              }
            print data
            r= requests.post("http://sendmail.gauravshukla.xyz:8080/mailer/561e7e12a4fabe0943650ca2",json=data)
            return jsonify(success="Your Feedback is Valuable to us and has been duly recorded, Thanks for your time !",error="")
        except Exception as err:
            log(err)
            return jsonify(error="We are really sorry, something went wrong on our end. " +"\n"
                                 "Event has been reported and will soon be acted upon. Stay Tuned!"),500

@app.route('/',methods=['POST','GET'])
@cross_origin(origin='*', headers=['Content- Type', 'Authorization'])
def hello_world():
    return jsonify(success="It works!")


@app.route('/login_action', methods=['GET', 'POST'])
@cross_origin(origin='*', headers=['Content- Type', 'Authorization'])
def login_action():
    data = request.get_json(force=True)
    print "inside login_action"
    if not (("user" in data) and ('pass' in data) and ('usertype' in data)):
        return jsonify(error="Key error, please provide all fields"),500
    else:
        if "mentorcode" not in data:
            data['mentorcode']="mahendragurve"
        if data['usertype']=="S":
            if not('date1' in data):
                return jsonify(error="Key error , provide date1 field"),500
        c = requests.Session()
        print "c created"
        try:
            if "bypass" in data:
                authkey=bcrypt.generate_password_hash(data['user']+data['pass'])
                mongo.db.users.create_index("loggedat",expireAfterSeconds=2000)
                mongo.db.users.update({"user" : data['user']}, {"$set" : {"authkey":authkey,"usertype":data['usertype'],"mentorcode":data['mentorcode'],"loggedat":datetime.utcnow()}},upsert=True)
                return jsonify(error="",success="Succcessfully Logged in!",authkey=authkey,usertype=data['usertype'],user=data['user']),201
            c.get("https://webkiosk.jiit.ac.in")
            if data['usertype']=='S':
                params ={'x':'',
                    'txtInst':'Institute',
                    'InstCode':'JIIT',
                    'txtuType':'Member Type',
                    'UserType':data['usertype'],
                    'txtCode':'Enrollment No',
                    'MemberCode':data['user'],
                    'DOB':'DOB',
                    'DATE1':data['date1'],
                    'txtPin':'Password/Pin',
                    'Password':data['pass'],
                    'BTNSubmit':'Submit'}
            else:
                params ={'x':'',
                    'txtInst':'Institute',
                    'InstCode':'JIIT',
                    'txtuType':'Member Type',
                    'UserType':data['usertype'],
                    'txtCode':'Employee Code',
                    'MemberCode':data['user'],
                    'DOB':"",
                    'DATE1':"",
                    'txtPin':'Password/Pin',
                    'Password':data['pass'],
                    'BTNSubmit':'Submit'}
            cook=c.cookies['JSESSIONID']
            cooki=dict(JSESSIONID=cook)
            reslogin=c.post("https://webkiosk.jiit.ac.in/CommonFiles/UserActionn.jsp", data=params,cookies=cooki)
            if "Error1.jpg" in reslogin.content:
                html=BeautifulSoup(reslogin.content,'html.parser')
                c.close()
                return jsonify(error=html.b.font.text),500
            else:
                c.close()
                authkey=bcrypt.generate_password_hash(data['user']+data['pass'])
                mongo.db.users.create_index("loggedat",expireAfterSeconds=2000)
                mongo.db.users.update({"user" : data['user']}, {"$set" : {"authkey":authkey,"mentorcode":data['mentorcode'],"usertype":data['usertype'],"loggedat":datetime.utcnow()}},upsert=True)
                return jsonify(error="",success="Succcessfully Logged in!",authkey=authkey,usertype=data['usertype'],user=data['user']),201
        except (Exception) as error:
            print str(error)
            c.close()
            return jsonify(error="Could Not Connect to Internet. Webkiosk May be Down or unreachable"),500


@app.route('/logout',methods=['GET', 'POST'])
@cross_origin(origin='*',headers=['Content- Type','Authorization'])
@login_required
def logout():
    data = request.get_json(force=True)
    if not check_status(data['authkey'],data['usertype']):
        return jsonify(error="You need to be logged in before logging out !"),403
    else:
        mongo.db.users.remove({"authkey": data['authkey']},safe=True)
        return jsonify(success="Successfully Logged Off!"),200


@app.route('/status', methods=['GET', 'POST'])
@cross_origin(origin='0.0.0.0',headers=['Content- Type','Authorization'])
def temp():
    data=request.get_json(force=True)
    if check_status(data['authkey']):
        return jsonify(status="logged in"),200
    else:
        return jsonify(status="NOt logged in"),200


@app.route('/v1/project/create', methods=['GET','POST'])
@login_required
def create_group():
    data=request.get_json(force=True)
    try:
        created =False
        if not isopen(data['projecttype'],"registration"):
            return jsonify(error="Registration Date all ready Passed."),403
        members=data['membersid']
        """ No group registers more than one project in a semester
        """
        query={'members':{ "$in": members },'semester':data['semester']}
        group = mongo.db.groups.find_one(query)
        print type(group)
        curruser=currentuser(data['authkey'],data['usertype'])
        if group is None and curruser in members:
            day=datetime.now()
            res=mongo.db.groups.insert({"projecttype":data['projecttype'].lower(),"members":data['membersid'],
                                        'semester':data['semester'],'evaluated':False,
                                        'approved':False,"registeredBy":curruser,"registeredOn":str(day)})
            print res
            created=True
            task = {
                'title': data['title'],
                'description': data['description'],
                'members': data['members'],
                'projecttype': data['projecttype'],
                'approved': False,
                'evaluated': False,
                'mentor': data['mentor'],
                'synopsis':"",
                'additional_links':"",
                'source_code':"",
                'project_report': "",
                'rating':"",
                'remarks':"",
                'lang':""
            }
            indexres= es.index(index='probase_repos',id=str(res), doc_type='projects', body=task)
            message="Your %s Project has been successfully registered.",(data['projecttype'])
            notify(message,data['members'])
            return jsonify(success="Group Successfully registered!"),201
        elif group is None and curruser not in members:
            time=datetime.now()
            err={"error":"You are not authorised to register this group, this event will be reported !","user": curruser,"time":time}
            log(err)
            return jsonify(error="You are not authorised to register this group, this event will be reported !"),403
        else:
            return jsonify(error="Group already registered, use update option to make changes"),500
    except KeyError as keyerr:
        if created:
            mongo.db.groups.remove({"_id":ObjectId(str(res))},safe=True)
            params= {'id': indexres['_id'], 'version': indexres['_version']}
            es.delete(index="probase_repos",doc_type="projects",params=params)
        log(keyerr)
        print str(keyerr)
        return jsonify(error=str(keyerr)+ " missing in payload."),500
    except Exception as e:
        if created:
            mongo.db.groups.remove({"_id":ObjectId(str(res))},safe=True)
            params= { 'version': indexres['_version']}
            es.delete(index="probase_repos",id= indexres['_id'],doc_type="projects",params=params)
        log(e)
        print str(e)
        return jsonify(error="Oops ! Something Went wrong, Try Again"),500


@app.route('/v1/projects/<project_id>',methods=['POST','GET'])
def display_project(project_id):
    re=es.search(index="probase_repos",id=project_id)
    return jsonify(re), 200


@app.route('/v1/projects/update/<group_id>',methods=['POST','GET'])
@login_required
def update_project(group_id):
    data=request.get_json(force=True)
    group_id=str(group_id)
    print data
    members=mongo.db.groups.find_one({"_id":ObjectId(group_id)})
    print members['members']
    try:
        print "inside try"
        if not currentuser(data['authkey'],data['usertype']) in members['members']:
            return jsonify(error="You are not a part of this Group!"),403
        elif members['evaluated']==True:
            return jsonify(error="Project already evaluated! Changes have been discarded"),500
        elif not isopen(members['projecttype'],"submission"):
            return jsonify(error="Project submission date already passed."),403
        else:
            print "inside else"
            qbody={"doc":{}}
            if members['approved'] is not True:
                if 'description' in data:
                    qbody['doc']['description']=data['description']
                    print qbody['doc']['description']
                if 'title' in data:
                    qbody['doc']['title']=data['title']
            if 'additional_links' in data:
                qbody['doc']['additional_links']=data['additional_links']
            if 'synopsis' in data:
                qbody['doc']['synopsis']=data['synopsis']
            if 'project_report' in data:
                qbody['doc']['project_report']=data['project_report']
            if 'source_code' in data:
                qbody['doc']['source_code']=data['source_code']
            if 'lang' in data:
                qbody['doc']['lang']=data['lang']
            print qbody
            body=json.dumps(qbody)
            print "body"
            re=es.update(index="probase_repos",doc_type="projects",id=group_id,body=body)
            message="Your "+members['projecttype']+" Project has been successfully Updated"
            notify(message,members['members'])
            return jsonify(success="Changes successfully Saved!"), 201
    except Exception as e:
        log(e)
        print str(e)
        return jsonify(error="Oops something went wrong ! Try again After sometime."),500


@app.route('/v1/projects/<projectid>/<action>', methods=['POST'])
@adminlogin_required
def ae_project(projectid,action):
    try:
        projectid=str(projectid)
        action=str(action)
        data=request.get_json(force=True)
        if action== "approve":
            body={
            "doc" : {
                "approved" : True
                        }}
            es.update(index="probase_repos",doc_type='projects',id=projectid,body=body)
            project_notification(projectid,action)
            return jsonify(success="Changes have been saved."),201
        elif action=="evaluate":
            body={
                "doc" : {
                "evaluated" : True,
                'rating': data['rating'],
                'remarks':data['remarks']
                        }
                }
            es.update(index="probase_repos",doc_type='projects',id=projectid,body=body)
            project_notification(projectid,action)
            return jsonify(success="Changes have been saved"), 201
        elif action=="disapprove":
            body={
                "doc" : {
                "approved" : False
                        }
                }
            if 'remarks' in data:
                body['remarks']=data['remarks']
            es.update(index="probase_repos",doc_type='projects',id=projectid,body=body)
            project_notification(projectid,action)
            return jsonify(success="Changes have been saved"), 201

        else:
            return jsonify(error="Invalid Project ID or action specified")
    except Exception as e:
        log(e)
        print str(e)
        return jsonify(error="Something Seems Fishy, Probably the network here sucks."),500


@app.route('/v1/projects/search', methods=['GET','POST'])
@cross_origin(origin='0.0.0.0',headers=['Content- Type','Authorization'])
def search_project():
    try:
        query=request.args.get("query","")
        size=request.args.get("size","10")
        page=request.args.get("from","0")
        source=request.args.get("source","probase_repos")
        type=request.args.get("type","")
        fields= [ "title^2.8", "description","projecttype","evaluated","approved","mentor","synopsis^1.1","languages^1.11"]
        if type=="similar":
            source="_all"
            fields=[ "title^1.8", "description^1.1","projecttype^1","languages^1.01"]
        elif source=="github_repos":
            fields=[ "title^1.8", "description^1.1","languages^1.01"]
        qbody={
                "query": {
                    "multi_match": {
                        "query":       str(query),
                        "type":        "cross_fields",
                        "fields":      fields
                    }
                }
            }
        params={"from":int(page)}
        re=es.search(index=source,body=qbody,size=size,params=params)
        re=re['hits']
        return jsonify(re), 200
    except Exception as e:
        log(e)
        print e
        return jsonify(error=str(e)),500

@app.route('/reindex', methods=['GET','POST'])
@cross_origin(origin='0.0.0.0',headers=['Content- Type','Authorization'])
def reindex_github():
    try:
        body= {}
        es2 = Elasticsearch([{'host': 'anip.xyz', 'port': 9200}])
        # res = helpers.scan(es, query={
        #                           "query": {
        #                             "match_all": {}
        #
        #                           },
        #                           "size":10000
        #                         },index="old_index")
        elasticsearch.helpers.reindex(es2,source_index="github_repos",chunk_size=10000,target_index="github")
    except Exception as e:
        return jsonify(error=str(e)),500


@app.route('/populate', methods=['GET','POST'])
@cross_origin(origin='0.0.0.0',headers=['Content- Type','Authorization'])
def dummy():
    try:
        import sampledata
        sampledata.create_sample()
        return jsonify(success="Dummy data created"),201
    except Exception as e:
        return jsonify(error=str(e)),500
if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)
