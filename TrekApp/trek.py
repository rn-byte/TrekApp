#Importing Flask
from flask import Flask,render_template,request,session,redirect,jsonify

#For Database
from flask_mysqldb import MySQL

#For Session
from flask_session import Session

#For Unique ID
import uuid

#Initializing app 
app = Flask(__name__)
#Database setting for mysql
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] =''
app.config['MYSQL_DB'] ='dbase_trekapp'

mysql=MySQL(app)

#Session setting for session
app.config["SESSION_PARMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)


@app.route('/')
def home():
	#return "<h1>This is the Homepage for the App!</h1>"
	logged_in_user=None
	if session.get('email'):
		logged_in_user=session["email"]
	return render_template('index.html',result={'logged_in_user':logged_in_user})
@app.route('/path')
def pathTest():
	return "<h1>This is the Path</h1>"

@app.route('/register')
def register():
	return render_template('register.html')

@app.route('/login')
def login():
	return render_template('login.html')


@app.route('/doLogin',methods=['POST'])
def doLogin():
	email =request.form['email']
	password=request.form['psw']

	cursor = mysql.connection.cursor()  #cursor provide flask to interact with Database
	#resp=cursor.execute('''SELECT * FROM user WHERE email=%s and password=%s;''',(email,password))
	resp=cursor.execute('''SELECT id,email,full_name,password FROM user WHERE email=%s and password=%s;''',(email,password))
		
	user=cursor.fetchone()
	print(user)
	cursor.close()
	#print(cursor.fetchone())
	#this command will fetch all the Data of the user whose email and password is Provided
	#The Scope of cursor command end after executing one command
	#print(cursor.fetchall())
	#print(resp)
	# print(type(resp))

	#if email == "ram.171326@ncit.edu.np" and password == "12345":
	if resp==1: #if email and password exist in the Database then It would lets you to  Login and return value 1 in the Variable Resp
		session['email']=email  
		session['userId']= user[0]
		logged_in_user=session.get('email')
		return render_template('home.html',result={'logged_in_user':logged_in_user})
	else:
		return render_template('login.html',result="Invalid Credentials")


@app.route('/doRegister',methods=['POST'])
def doRegister():
	full_name=request.form['full_name']
	email=request.form['email']
	phone_number=request.form['phone_number']
	address=request.form['address']
	password=request.form['psw']

	cursor = mysql.connection.cursor()
	cursor.execute('''INSERT INTO user VALUES(NULL,%s,%s,%s,%s,%s);''',(full_name,address,email,phone_number,password))
	mysql.connection.commit()
	cursor.close()
	return render_template('login.html',result="Register Successfull!! Please Login To Continue.....")

@app.route('/treks')
def allTreks():

	cursor = mysql.connection.cursor()  #cursor provide flask to interact with Database
	cursor.execute('''SELECT td.id as 'SNO',td.title as 'Title',td.days as 'Days',td.difficulty as 'Difficulty',td.total_cost as 'Total Cost',td.upvotes as 'Upvotes',u.full_name as 'Full Name',u.id as 'User Id' FROM `trek_destination` as td join `user` as u on td.user_id = u.id;''')
	treks = cursor.fetchall()
	# print(treks)
	cursor.close()

	logged_in_user=None
	if session.get('email'):
		logged_in_user=session["email"]

	if session.get('userId'):
		userId=session.get('userId')
	return render_template('listing.html',result={"treks":treks,"logged_in_user":logged_in_user,"userId":userId})

@app.route('/trek/<int:trekId>')
def getTrekbyId(trekId):

	cursor = mysql.connection.cursor()  #cursor help flask to interact with Database
	cursor.execute('''SELECT td.id as 'SNO',td.title as 'Title',td.days as 'Days',td.difficulty as 'Difficulty',td.total_cost as 'Total Cost',td.upvotes as 'Upvotes',u.full_name as 'Full Name' FROM `trek_destination` as td join `user` as u on td.user_id = u.id WHERE td.id=%s;''',(trekId,))
	trek = cursor.fetchone()
	cursor.close()

	cursor = mysql.connection.cursor()  #cursor provide flask to interact with Database
	cursor.execute('''SELECT * FROM `iternaries` WHERE trek_destination_id=%s;''',(trekId,)) 
	iternaries = cursor.fetchall()
	print(iternaries)
	cursor.close()
	return render_template('trekdetail.html',result={"trek":trek,"iternaries":iternaries})

@app.route('/logout')
def logout():
	session["email"]=None
	session["userId"]=None
	return redirect ('/')

@app.route('/addTrek')
def addTrek():
	logged_in_user=None
	if session.get('email'):
		logged_in_user=session["email"]

	return render_template('addTreks.html',result={'logged_in_user':logged_in_user})

@app.route('/doAddTrek',methods=['POST'])
def doAddTrek():
	logged_in_user=None
	if session.get('email'):
		logged_in_user=session["email"]

	title=request.form['title']
	days=request.form['days']
	difficulty=request.form['difficulty']
	total_cost=request.form['total_cost']
	upvotes=0

	cursor = mysql.connection.cursor()
	cursor.execute('''SELECT id FROM `user` WHERE `email`=%s;''',(logged_in_user,))
	user = cursor.fetchone()
	#print(user,title,days,difficulty,total_cost)
	cursor.close()

	userID=user[0]

	cursor = mysql.connection.cursor()
	cursor.execute('''INSERT INTO trek_destination VALUES(NULL,%s,%s,%s,%s,%s,%s);''',(title,days,difficulty,total_cost,upvotes,userID))
	mysql.connection.commit()
	cursor.close()

	return redirect ('/treks')

@app.route('/editTrek/<int:trekId>')
def editTrek(trekId):
	logged_in_user=None
	if session.get('email'):
		logged_in_user=session["email"]
	
	cursor = mysql.connection.cursor()  #cursor help flask to interact with Database
	cursor.execute('''SELECT td.id as 'SNO',td.title as 'Title',td.days as 'Days',td.difficulty as 'Difficulty',td.total_cost as 'Total Cost',td.upvotes as 'Upvotes',u.full_name as 'Full Name' FROM `trek_destination` as td join `user` as u on td.user_id = u.id WHERE td.id=%s;''',(trekId,))
	trek = cursor.fetchone()
	cursor.close()
	
	return render_template('editTrek.html',result={"trek":trek,"logged_in_user":logged_in_user})


@app.route('/doUpdateTrek',methods=['POST'])
def doUpdateTrek():
	logged_in_user=None
	if session.get('email'):
		logged_in_user=session["email"]

	title=request.form['title']
	days=request.form['days']
	difficulty=request.form['difficulty']
	total_cost=request.form['total_cost']
	trekId=request.form['trekId']


	cursor = mysql.connection.cursor()
	cursor.execute('''UPDATE `trek_destination` SET `title` = %s,`days`=%s,`difficulty`=%s,`total_cost`=%s WHERE `id` = %s;''',(title,days,difficulty,total_cost,trekId))
	mysql.connection.commit()
	cursor.close()

	return redirect ('/treks')

@app.route('/doDeleteTrek/<int:trekId>')
def doDeleteTrek(trekId):
	
	cursor = mysql.connection.cursor()
	cursor.execute('''DELETE FRoM `trek_destination` WHERE `id` = %s;''',(trekId,))
	mysql.connection.commit()
	cursor.close()

	return redirect ('/treks')

@app.route('/addItenary')
def addItenary():
	logged_in_user=None
	if session.get('email'):
		logged_in_user=session["email"]

	cursor=mysql.connection.cursor()
	userId=None
	if session.get('userId'):
		userId=session.get('userId')
	cursor.execute('''SELECT id, title FROM `trek_destination` where user_id=%s;''',(userId,))
	treaks=cursor.fetchall()
	cursor.close()

	return render_template('addItenary.html',result={"treks":treaks,"logged_in_user":logged_in_user})

@app.route('/doAddIternary',methods=['POST'])
def doAddIternary():
	logged_in_user=None
	if session.get('email'):
		logged_in_user=session["email"]

	trek_destination_id	= request.form['trek_destination_id']
	day=request.form['day']

	title= request.form['title']
	start_place= request.form['start_place']

	end_place=request.form['end_place']
	description=request.form['description']
	duration=request.form['duration']
	cost=request.form['cost']

	cursor =mysql.connection.cursor()
	cursor.execute('''INSERT INTO `iternaries` VALUES(null,%s,%s,%s,%s,%s,%s,%s,%s)''',(title,day,start_place,end_place,description,duration,cost,trek_destination_id))
	mysql.connection.commit()
	cursor.close()

	return redirect('/treks')

@app.route('/itenary/<int:trekId>')
def getItenaryByTrekId(trekId):

	cursor = mysql.connection.cursor()  #cursor provide flask to interact with Database
	cursor.execute('''SELECT * FROM `iternaries` WHERE trek_destination_id=%s;''',(trekId,)) 
	iternaries = cursor.fetchall()
	cursor.close()
	return render_template('itenary.html',result={"trekId":trekId,"iternaries":iternaries})

@app.route('/myTreks/<string:param>')
def getTreksbyUser(param):
	userId=None
	if session.get('email'):
		logged_in_user=session["email"]

	if session.get('userId'):
		userId=session.get('userId')

	cursor = mysql.connection.cursor()  #cursor provide flask to interact with Database
	if param == "user":
		cursor.execute('''SELECT * FROM `trek_destination` WHERE user_id=%s;''',(userId,)) 
	else:
		cursor.execute('''SELECT * FROM `trek_destination`;''') 
	treks = cursor.fetchall()
	#print(treks)
	cursor.close()

	return render_template('mytreks.html',result={"treks":treks,"userId":userId})


# SEARCHING FUNCTION
#@app.route('/treks/search/<string:keyword>')# one method of route for searching
@app.route('/treks/search')
# def search(keyword):
def search():
	keyword=request.args.get("keyword")
	cursor = mysql.connection.cursor() 
	searchString = "%" + keyword + "%"
	cursor.execute('''SELECT * FROM `trek_destination` WHERE `title` LIKE %s;''',(searchString,))
	treks = cursor.fetchall()
	cursor.close()

	logged_in_user=None
	if session.get('email'):
		logged_in_user=session["email"]

	if session.get('userId'):
		userId=session.get('userId')
	
	result={"treks":treks,"logged_in_user":logged_in_user}

	return render_template('mytreks.html',result={"treks":treks,"userId":userId})



"""
APT Interfaces defined from here
"""

@app.route('/api/doRegister',methods=['POST'])
def doRegisterAPI():
	
	full_name=request.json['full_name']
	email=request.json['email']
	phone_number=request.json['phone_number']
	address=request.json['address']
	password=request.json['psw']

	cursor = mysql.connection.cursor()
	cursor.execute('''INSERT INTO user VALUES(NULL,%s,%s,%s,%s,%s);''',(full_name,address,email,phone_number,password))
	mysql.connection.commit()
	cursor.close()
	#return render_template('login.html',result="Register Successfull!! Please Login To Continue.....")
	return jsonify({"result":"Register Successfull!! Please Login To Continue....."})

# @app.route('/api/treks')
@app.route('/rest/treks')
def allTreksAPI():

	cursor = mysql.connection.cursor()  #cursor provide flask to interact with Database
	cursor.execute('''SELECT td.id as 'SNO',td.title as 'Title',td.days as 'Days',td.difficulty as 'Difficulty',td.total_cost as 'Total Cost',td.upvotes as 'Upvotes',u.full_name as 'Full Name' FROM `trek_destination` as td join `user` as u on td.user_id = u.id;''')
	treks = cursor.fetchall()
	# print(treks)
	cursor.close()

	logged_in_user=None
	if session.get('email'):
		logged_in_user=session["email"]
	
	result={"treks":treks,"logged_in_user":logged_in_user}
	#return render_template('listing.html',result={"treks":treks,"logged_in_user":logged_in_user})
	return jsonify(result)


@app.route('/api/doLogin',methods=['POST'])
def doLoginAPI():
	email =request.json['email']
	password=request.json['psw']

	cursor = mysql.connection.cursor()  #cursor provide flask to interact with Database
	#resp=cursor.execute('''SELECT * FROM user WHERE email=%s and password=%s;''',(email,password))
	resp=cursor.execute('''SELECT id,email,full_name,password FROM user WHERE email=%s and password=%s;''',(email,password))
		
	user=cursor.fetchone()
	print(user)
	cursor.close()

	token=""
	if resp==1: #if email and password exist in the Database then It would lets you to  Login and return value 1 in the Variable Resp
		session['email']=email  
		session['userId']= user[0]
		logged_in_user=session.get('email')
		token=str(uuid.uuid4())

		cursor = mysql.connection.cursor()
		cursor.execute('''UPDATE user SET `token`=%s WHERE `email`=%s;''',(token,email))
		mysql.connection.commit()
		cursor.close()

		return jsonify({"message":"Login Successfull!!","loggedin":True,"token":token})
	else:
		return jsonify({"message":"Login Unsuccessfull!! Check your email and password","loggedin":False})

# @app.route('/api/doAddTrek',methods=['POST'])
@app.route('/rest/treks',methods=['POST'])
def doAddTrekAPI():
	logged_in_user=None
	if session.get('email'):
		logged_in_user=session["email"]

	title=request.json['title']
	days=request.json['days']
	difficulty=request.json['difficulty']
	total_cost=request.json['total_cost']
	token=request.json['token'] or None
	userID = __validate_token(token)
	if userID == 0:
		return jsonify({"message":"Please Enter valid Token"})
	upvotes=0

	cursor = mysql.connection.cursor()
	cursor.execute('''INSERT INTO trek_destination VALUES(NULL,%s,%s,%s,%s,%s,%s);''',(title,days,difficulty,total_cost,upvotes,userID))
	mysql.connection.commit()
	cursor.close()

	return jsonify({"message":"Trek has been added successfully!!"})

# @app.route('/api/doUpdateTrek',methods=['PUT'])
@app.route('/rest/treks',methods=['PUT'])
def doUpdateTrekAPI():
	title=request.json['title']
	days=request.json['days']
	difficulty=request.json['difficulty']
	total_cost=request.json['total_cost']
	trekId=request.json['trekId']
	token=request.json['token'] or None
	userID = __validate_token(token)
	if userID == 0:
		return jsonify({"message":"Please Enter valid Token"})

	cursor = mysql.connection.cursor()
	cursor.execute('''UPDATE `trek_destination` SET `title` = %s,`days`=%s,`difficulty`=%s,`total_cost`=%s WHERE `id` = %s;''',(title,days,difficulty,total_cost,trekId))
	mysql.connection.commit()
	cursor.close()

	return jsonify({"message":"Trek has been updated successfully!!"})

# @app.route('/api/doDeleteTrek',methods=['DELETE'])
@app.route('/rest/treks',methods=['DELETE'])
def doDeleteTrekAPI():

	trekId=request.json['trekId']
	token=request.json['token'] or None
	userID = __validate_token(token)
	if userID == 0:
		return jsonify({"message":"Please Enter valid Token"})

	cursor = mysql.connection.cursor()
	resp=cursor.execute('''DELETE FRoM `trek_destination` WHERE `id` = %s and `user_id`=%s;''',(trekId,userID))
	if resp==0:
		return jsonify({"message":"You Cannot Delete someone else Trek!!"})
	mysql.connection.commit()
	cursor.close()

	return jsonify({"message":"Trek has been deleted successfully!!"})
	

def __validate_token(token):
	cursor = mysql.connection.cursor()
	cursor.execute('''SELECT id FROM `user` WHERE `token`=%s;''',(token,))
	user = cursor.fetchone()
	cursor.close()
	userID = 0
	if user is not None:
		userID=user[0]

	return userID



# SEARCHING FUNCTION
#@app.route('/treks/search/<string:keyword>')# one method of route for searching
@app.route('/api/treks/search')
# def search(keyword):
def searchAPI():
	keyword=request.args.get("keyword")
	cursor = mysql.connection.cursor() 
	searchString = "%" + keyword + "%"
	cursor.execute('''SELECT * FROM `trek_destination` WHERE `title` LIKE %s;''',(searchString,))
	treks = cursor.fetchall()
	cursor.close()

	logged_in_user=None
	if session.get('email'):
		logged_in_user=session["email"]
	
	result={"treks":treks,"logged_in_user":logged_in_user}

	return jsonify(result)

if __name__=='__main__':
	app.run(debug=True)