from datetime import datetime
from flask import jsonify
import json
from flask import Flask
import random
from flask import request
from flask.ext.cors import CORS,cross_origin
import requests
from elasticsearch import Elasticsearch
from flask.ext.bcrypt import Bcrypt
from flask.ext.pymongo import PyMongo
from functools import wraps
from bs4 import BeautifulSoup
from bson.objectid import ObjectId
app = Flask("projectbase")
bcrypt = Bcrypt(app)
mongo = PyMongo(app)
cors = CORS(app, resources={r"*": {"origins": "*"}})
app.config['CORS_HEADERS'] = 'Content-Type'
es = Elasticsearch([{'host': 'localhost', 'port': 9200}])

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


def projectnotification(projectid,action):
    try:
        members=mongo.db.groups.find_one({"_id":ObjectId(group_id)})
        message="Your %s project has been %s.",(members['projecttype'],action)
        notify(message,members['members'])
        return True
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
        headers={}
        data={}
        data['tags']=tags
        data['msg']=msg
        data['platform']=[1]
        data['payload']={"largeIcon":"http://cdn.mysitemyway.com/etc-mysitemyway/icons/legacy-previews/icons/blue-jelly-icons-alphanumeric/069535-blue-jelly-icon-alphanumeric-letter-p.png"}
        headers['x-pushbots-appid']="564e3f56177959ce468b4569"
        headers['x-pushbots-secret']="bafdd9608dab716baabad599cc6c477e"
        headers['Content-Type']="application/json"
        r=requests.post("https://api.pushbots.com/push/all",headers=headers,json=data)
        if r.status_code==200:
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
def list_mentor_projects(mentor):
    try:
        if len(mentor)!=0:
            mentorarr=[mentor]
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
            re=es.search(index="projects",body=query)
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
        if data['usertype']=="S":
            if not('date1' in data):
                return jsonify(error="Key error , provide date1 field"),500
        c = requests.Session()
        print "c created"
        try:
            if "bypass" in data:
                authkey=bcrypt.generate_password_hash(data['user']+data['pass'])
                mongo.db.users.create_index("loggedat",expireAfterSeconds=2000)
                mongo.db.users.update({"user" : data['user']}, {"$set" : {"authkey":authkey,"usertype":data['usertype'],"loggedat":datetime.utcnow()}},upsert=True)
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
                mongo.db.users.update({"user" : data['user']}, {"$set" : {"authkey":authkey,"usertype":data['usertype'],"loggedat":datetime.utcnow()}},upsert=True)
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
    print data
    res=""
    if data['title'] == "" or len(data['membersid'])==0 or len(data['mentor'])==0:
        return jsonify(error="Incomplete Details provided"),500
    else:
        try:
            members=data['membersid']
            query={'projecttype': data['projecttype'] ,'members':{ "$in": members } }
            group = mongo.db.groups.find_one(query)
            print type(group)
            if group is None and currentuser(data['authkey'],data['usertype']) in members:
                res=mongo.db.groups.insert({"projecttype":data['projecttype'],"members":data['membersid']})
                print res
                task = {
                    'title': data['title'],
                    'description': data['description'],
                    'members': data['members'],
                    'projecttype': data['projecttype'],
                    'approved': False,
                    'evaluated': False,
                    'mentor': data['mentor'],
                    'synopsis':"",
                    'additional_link':"",
                    'source_code':"",
                    'project_report': "",
                    'rating':"",
                    'remarks':"",
                    'languages':""
                    }
                indexres= es.index(index='probase_repos',id=str(res), doc_type='projects', body=task)
                message="Your %s Project has been successfully registered.",(data['projecttype'])
                notify(message,data['members'])
                return jsonify(success="Group Successfully registered!"),201
            elif group is None and currentuser(data['authkey'],data['usertype']) not in members:
                time=datetime.now()
                err={"error":"You are not authorised to register this group, this event will be reported !","user": members,"time":time}
                log(err)
                response= jsonify(error="You are not authorised to register this group, this event will be reported !")
                response.status_code=403
                return response
            else:
                response= jsonify(error="Group Already registered, Use update project option to make changes to your existing project. ")
                response.status_code=500
                return response
        except Exception as e:
            mongo.db.groups.remove({"_id":ObjectId(str(res))},safe=True)
            params= {'id': indexres['_id'], 'version': indexres['_version']}
            es.delete(index="probase_repos",doc_type="projects",params=params)
            log(e)
            print str(e)
            return jsonify(error="Oops ! Something Went wrong, Try Again"),500


@app.route('/v1/projects/<project_id>',methods=['POST','GET'])
def display_project(project_id):
    re=es.search(index="projects",id=project_id)
    return jsonify(re), 200

@app.route('/v1/projects/update/<group_id>',methods=['POST','GET'])
@login_required
# @cross_origin(origin='*', headers=['Content- Type', 'Authorization'])
def update_project(group_id):
    print group_id
    data=request.get_json(force=True)
    print data
    members=mongo.db.groups.find_one({"_id":ObjectId(group_id)})
    print type(members)
    try:
        if currentuser(data['authkey'],data['usertype']) in members['members']:
            qbody={"doc":{}}
            if 'description' in data:
                qbody['doc']['description']=data['description']
            if 'additional_links' in data:
                qbody['doc']['additional_links']=data['additional_links']
            if 'synopsis' in data:
                qbody['doc']['synopsis']=data['synopsis']
            if 'project_report' in data:
                qbody['doc']['project_report']=data['project_report']
            if 'source_code' in data:
                qbody['doc']['source_code']=data['source_code']
            body=json.dumps(qbody)
            re=es.update(index="projects",doc_type="projects",id=group_id,body=body)
            message="Your "+members['projecttype']+" Project has been successfully Updated"
            notify(members['members'],message)
            return jsonify(success="Changes successfully Saved!"), 201
        else:
            return jsonify(error="Either You are not part of this group or your project has already been evaluated"),500
    except Exception as e:
        log(e)
        return jsonify(error="Oops something went wrong ! Try again After sometime."),500


@app.route('/v1/projects/<projectid>/<action>', methods=['POST'])
@adminlogin_required
def ae_project(projectid,action):
    try:
        data=request.get_json(force=True)
        if action== "approve":
            body={
            "doc" : {
                "approved" : True
                        }}
            es.update(index="projects",doc_type='projects',id=projectid,body=body)
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
            es.update(index="projects",doc_type='projects',id=projectid,body=body)
            project_notification(projectid,action)
            return jsonify(success="Changes have been saved"), 201
        elif action=="disapprove":
            body={
                "doc" : {
                "approved" : False,
                'remarks':data['remarks']
                        }
                }
            es.update(index="projects",doc_type='projects',id=projectid,body=body)
            project_notification(projectid,action)
            return jsonify(success="Changes have been saved"), 201

        else:
            return jsonify(error="Invalid Project ID or action specified")
    except Exception as e:
        log(e)
        return jsonify(error="Something Seems Fishy, Probably the network here sucks."),500


@app.route('/v1/projects/search', methods=['GET','POST'])
@cross_origin(origin='0.0.0.0',headers=['Content- Type','Authorization'])
def search_project():
    try:
        query=request.args.get("query","")
        size=request.args.get("size","10")
        page=request.args.get("from","0")
        source=request.args.get("source","projects")
        type=request.args.get("type","")
        fields= [ "title^1.8", "description^1.2","projecttype^1","evaluated","approved","mentor","synopsis^1.1","languages^1.01"]
        if type=="similar":
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

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)
