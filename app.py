from flask import Flask, jsonify, render_template, request, make_response
import requests
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
import uuid



app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myhood.db'

db = SQLAlchemy(app)

#zipcodes = [ Hood("Inwood", ["10034"]), 
#		Hood("Morningside Heights", ["10027", "10015"]),
#		Hood("East Harlem", ["10035", "10029"]),
#		Hood("Upper West Side", ["10024", "10025"]),
#		Hood("Upper West Side", ["10024", "10025"]),
#		Hood("Lincoln Square" : ["10023", "10069"]),
#		Hood("Upper East Side", ["10028", "10162", "10044", "10075", "10128"]),
#		Hood("Lennox Hill", ["10065", "10021"]),
#		Hood("Hell's Kitchen", ["10018", "10036", "10019"]),
#		Hood("Midtown", ["10019", "10022", "10017", "10016"]),
#		Hood("Chelsea", ["10001", "10011"]),
#		Hood("West Village", ["10014"]),
#		Hood("East Village", ["10009"]),
#		Hood("Little Italy", ["10013"]),
#		Hood("Chinatown", ["10013"]), 
#		Hood("Tribeca", ["10013"]),
#		Hood("Lower East Side", ["10002", "10003"]),
#		Hood("Soho", ["10012"]),
#		Hood("Wall Street", ["10038"]),
#		Hood("Southern Tip", ["10004"]) ]

# to use with zipcodes
#class Hood:
#	def __init__(self, name, zips):
#		self.name = name
#		self.zipcodes = zips

class Hood:
	def __init__(self, name, tupleList):
		self.name = name
		self.tupleList = tupleList

class Cookie(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	answerID = db.Column(db.Integer)
	value = db.Column(db.String)

	def __init__(self, answerID, value):
		self.answerID = answerID
		self.value = value

class Answer(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	postID = db.Column(db.Integer)
	count = db.Column(db.Integer)
	text = db.Column(db.String)
	score = db.Column(db.Integer, default = 0)
	
	def __init__(self, postID, count, text):
		self.postID = postID
		self.count = count
		self.text = text
		self.cookies = []

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String)
    date = db.Column(db.DateTime)
    nh = db.Column(db.String)
    tag = db.Column(db.String)
    

    def __init__(self, text, hood, aTag):
        self.text = text
        self.nh = hood
        self.date = datetime.now()
        self.tag = aTag

db.create_all()

# neighborhood lists
hoodList = [ Hood('Harlem', 
		[ ( (40.819173, -73.961564), (40.834565, -73.950492) ), 
		( (40.810143, -73.955212), (40.819043, -73.961478) ), ( (40.801243, -73.959418), (40.809884, -73.955298) ),
		( (40.797084, -73.949204), (40.801308, -73.959504) ), ( (40.818003, -73.934012), (40.797084, -73.949290) ), 
		( (40.828006, -73.934441), (40.818133, -73.933926) ), ( (40.834435, -73.950406), (40.828136, -73.934699) ) ] ), 
	
	Hood('Morningside Heights', 
		[ ((40.806108, -73.971176), (40.818028, -73.962035)), ((40.801982, -73.961177), (40.806108, -73.971090)),
		((40.810038, -73.957100), (40.801885, -73.961134)), ((40.813384, -73.956370), (40.810136, -73.957100)), 
		((40.818093, -73.962078),(40.813416, -73.956370)) ]),

	Hood("Inwood", 
		[ ( (40.867686, -73.934026), (40.877875, -73.927503) ), ( (40.856261, -73.922439), (40.868205, -73.933855) ),
		((40.872099, -73.909221), (40.855871, -73.922525)), ((40.878394, -73.926130), (40.872878, -73.909135)) ]),

	Hood("Fort George", 
		[ ((40.852228, -73.944742), (40.870404, -73.932640)), ((40.847034, -73.928520), (40.852228, -73.944828)),
		((40.859304, -73.920280), (40.847099, -73.928262)), ((40.870663, -73.932382), (40.858980, -73.919937)) ]),

	Hood("Washington Heights", 
		[ ((40.834599, -73.950235), (40.852585, -73.947059)), ((40.828235, -73.934871), (40.834989, -73.949978)),
		((40.846872, -73.928520), (40.828365, -73.934871)), ((40.852910, -73.946888), (40.846937, -73.928606)) ])
	
	]
# takes a list someList containing polygon edge values
# and a point somePoint. returns 1 if the polygon
# contains the point and -1 if it does not
def containsPoint(someList, somePoint):
		i = 0
		for aTuple in someList:
			a = -(aTuple[1][1] - aTuple[0][1])
			b = aTuple[1][0] - aTuple[0][0]
			c = -((a * aTuple[0][0]) + (b * aTuple[0][1]))
			d = (a * somePoint[0]) + (b * somePoint[1]) + c
			if d < 0:
				print "edge " + str(i) + " didn't pass the test"
				return -1
			else:
				print "edge " + str(i) + " passed the test"
				i = i+1
				continue
		print "exited the foor loop with i = " + str(i)
		return 1



#method for determining neighborhood based on zipcode
#returns a tuple containing the neighborhood/s	
#def get_nh(zipcode, lat, longitude):	
#	
#	for neighborhood in zipcodes:
#		if zipcode in neighborhood.zipcodes:
#			
#			if neighborhood.name == "Morningside Heights" || neighborhood.name == "Harlem":
#				if longitude < -73.957534:
#					return "Morningside Heights"
#				elif:
#					return "Harlem"
#			
#			if neighborhood.name == ""		 
#			
#			return element	

#uncoment to delete entries in database
#for entry in db.session.query(Post).order_by(Post.id):
	#db.session.delete(entry)
	#db.session.commit()

@app.route('/')
def page():
	return render_template('home.html')
	
# upvote a post
@app.route('/upvote',  methods=["GET", "POST"])
def upvote():
	if request.method =="POST":
		thePostID = int(request.json["id"])
		thePost = Answer.query.get(thePostID)
		
		# check if user's browser has already received a
		# cookie
		if 'myhoodid' in request.cookies:
			cookieValue = request.cookies.get('myhoodid')
			
			# check if this answer has this cookie associated
			# with it. if yes, reject upvote
			cookies = db.session.query(Cookie)
			for cookie in cookies:
				if cookie.answerID == thePostID and cookie.value == cookieValue:
					return '0'

			# if no, add this cookie to this answer
			# and send go ahead signal
			theCookie = Cookie(thePostID, cookieValue)
			db.session.add(theCookie)
			thePost.score += 1
			db.session.commit()
			return '1'
		else:
			# generate a unique cookie value
			# add it to the current user
			# return go ahead signal
			newCookie = str(uuid.uuid4())
			resp = make_response('1')
			resp.set_cookie('myhoodid', newCookie)
			theCookie = Cookie(thePostID, newCookie)
			db.session.add(theCookie)
			thePost.score += 1
			db.session.commit()
			return resp

# downvote an post
@app.route('/downvote',  methods=["GET", "POST"])
def downvote():
	if request.method =="POST":
		thePostID = int(request.json["id"])
		thePost = Answer.query.get(thePostID)
		
		# check if user's browser has already received a
		# cookie
		if 'myhoodid' in request.cookies:
			cookieValue = request.cookies.get('myhoodid')
			
			# check if this answer has this cookie associated
			# with it. if yes, reject upvote
			cookies = db.session.query(Cookie)
			for cookie in cookies:
				if cookie.answerID == thePostID and cookie.value == cookieValue:
					return '0'

			# if no, add this cookie to this answer
			# and send go ahead signal
			theCookie = Cookie(thePostID, cookieValue)
			db.session.add(theCookie)
			thePost.score -= 1
			db.session.commit()
			return '1'
		else:
			# generate a unique cookie value
			# add it to the current user
			# return go ahead signal
			newCookie = str(uuid.uuid4())
			resp = make_response('1')
			resp.set_cookie('myhoodid', newCookie)
			theCookie = Cookie(thePostID, newCookie)
			db.session.add(theCookie)
			thePost.score -= 1
			db.session.commit()
			return resp

# determines if current location is within the bounds
# of the NYC neighborhoods
# !!! need to make a page that will display a message if
#user is not in NYC
@app.route('/phony', methods=["GET", "POST"])
def phony():
	if request.method =="POST":
		lat = (request.json["lat"])
		longit = (request.json["longit"])
		for hood in hoodList:
			if containsPoint(hood.tupleList, (lat, longit)) > 0:
				theHood = hood.name
				break
			else:	
				theHood = "Looks like you're not in NYC! We're working hard on bringing MyHood to your city soon!"
				# return render_template("not_in_nyc.html")
	return render_template("phony.html", hood = theHood)
		


@app.route('/answer/<postID>/<nh>/<tag>', methods=["GET", "POST"])
def answer(postID, nh, tag):
	if request.method == "POST":
		anAnswer = request.form["user_input"]
		#search database for post with given postID
		thePost = Post.query.get(postID) #will this actually let me add answer to post
		#in database or to its copy?
		
		#add answer to the post's answer field
		theAnswer = Answer(postID, 0, anAnswer)
		db.session.add(theAnswer)
		db.session.commit()
		#return the template with posts and answers for given nh
		return render_template('whats_good.html', s = (db.session.query(Post).order_by(Post.id.desc())), 
		answers = db.session.query(Answer).order_by(Answer.score.desc()), hood = nh, post_copy = thePost, theTag = tag)
	else:
		return render_template("search.html")
		
@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        url = "https://api.github.com/search/repositories?q=" + request.form["user_search"]
        response_dict = requests.get(url).json()
        return render_template('results.html', api_data=response_dict)
    else: # request.method == "GET"
        return render_template("search.html")
		
@app.route("/post/<nh>/<tag>", methods=["GET", "POST"])
def post(nh, tag):
    if request.method == "POST":
		post = Post(request.form["user_input"], nh, tag)
		db.session.add(post)
		db.session.commit()

		return render_template('whats_good.html', s = (db.session.query(Post).order_by(Post.id.desc())), 
		answers = db.session.query(Answer).order_by(Answer.score.desc()), hood = nh, theTag = tag)
    else:
    	return render_template("search.html")


@app.errorhandler(404)
def nope(error):
	return "We ain't got what yo looking for, fool!", 404	

#get neighborhood list from lat and long values
@app.route('/getgeo')
def getgeo():
	nh_file = open('nh_list.txt', 'w')
	url_file = open('url.txt', 'w')
	lat_file = open('latfile.txt', 'r')
	long_file = open('longfile.txt', 'r')
	lat = lat_file.readline().rstrip()
	long = long_file.readline().rstrip()
	while lat:
		url = "http://open.mapquestapi.com/nominatim/v1/reverse.php?lat=" + lat + "&lon=" + long + "&format=json"
		url_file.write(url + "\n")
		nh_dict = requests.get(url).json()
		#nh_list.append(nh_dict["address"]["neighbourhood"]
		try: nh_file.write(nh_dict["address"]["neighbourhood"] + "\n")
		except KeyError: pass #nh_file.write(nh_dict["address"]["suburb"] + "\n")
		lat = lat_file.readline().rstrip()
		long = long_file.readline().rstrip()
	return "Done!"	
		

#take out all repeats from neighborhood list
#to get a list of neighborhoods
@app.route('/nh_list')
def nh_list():
	nh_ready_file = open('neighborhoods.txt', 'w')
	nh_file = open('nh_list.txt', 'r')
	nh = nh_file.readline()
	a_list = ["Harlem"]
	while nh:
		if nh not in a_list:
			a_list.append(nh)
			nh = nh_file.readline()
		else:
			nh = nh_file.readline()
	for item in a_list:
		nh_ready_file.write(item)
	return "Ready!"	
	



if __name__ == '__main__':
	app.run(host='0.0.0.0')