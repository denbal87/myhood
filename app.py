from flask import Flask, jsonify, render_template, request, make_response
import requests
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
import uuid
import os

from datetime import datetime
from dateutil import tz




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


# change time to New York loca time
def localTime():
	from_zone = tz.gettz('UTC')
	to_zone = tz.gettz('America/New_York')

	# utc = datetime.utcnow()
	utc = datetime.strptime(datetime.utcnow().strftime('%Y-%m-%d %H:%M'), '%Y-%m-%d %H:%M')

	# Tell the datetime object that it's in UTC time zone since 
	# datetime objects are 'naive' by default
	utc = utc.replace(tzinfo=from_zone)

	# Convert time zone
	central = utc.astimezone(to_zone).strftime('posted on %b %d at %-I:%M%p')
	return central


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
    #date = db.Column(db.DateTime)
    date = db.Column(db.String)
    nh = db.Column(db.String)
    tag = db.Column(db.String) # this is the category the post is under
    subcat = db.Column(db.String, default = "None") # this is the tag or subcategory that
    # users can choose
    

    def __init__(self, text, hood, aTag):
        self.text = text
        self.nh = hood
        self.date = localTime()#datetime.now().strftime('posted on %b %d at %-I:%-M')
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
		((40.846872, -73.928520), (40.828365, -73.934871)), ((40.852910, -73.946888), (40.846937, -73.928606)) ]),

	Hood("Upper West Side", 
		[ ((40.781362, -73.988206), (40.805892, -73.971040)), ((40.776293, -73.976018), (40.781362, -73.988163)), 
		((40.800597, -73.958208), (40.776195, -73.975932)), ((40.805860, -73.971125), (40.800694, -73.958337)) ]),

	Hood("Central Park", 
		[ ((40.768233, -73.981683), (40.800467, -73.958122)), ((40.764528, -73.973100), (40.768201, -73.981898)),
		((40.796959, -73.949368), (40.764463, -73.973057)), ((40.800532, -73.958165), (40.796894, -73.949539)) ]), 

	Hood("Lincoln Square", 
		[ ((40.773141, -73.994128), (40.781460, -73.988163)), ((40.768233, -73.981898), (40.773141, -73.994128)), 
		((40.776261, -73.975889), (40.768103, -73.981983)), ((40.781525, -73.988163), (40.776293, -73.975889)) ]),

	Hood("East Harlem", 
		[ ((40.787992, -73.955853), (40.818106, -73.933837)), ((40.782800, -73.943588), (40.786017, -73.954531)),
		((40.785594, -73.939511), (40.782800, -73.943588)), ((40.794984, -73.929125), (40.785659, -73.939468)),
		((40.801157, -73.929211), (40.794984, -73.929125)), ((40.806088, -73.931691), (40.801150, -73.929288)), 
		((40.818203, -73.933837), (40.805958, -73.932163)) ]), 

	Hood("Yorkville",
		[ ((40.774386, -73.957515), (40.785337, -73.949447)), ((40.770226, -73.947516), (40.774386, -73.957515)),
		((40.773118, -73.944125), (40.773118, -73.944125)), ((40.777896, -73.942237), (40.773118, -73.944125)), 
		((40.782802, -73.943567), (40.777863, -73.942194)), ((40.785337, -73.949404), (40.785337, -73.949404)) ]),

	Hood("Upper East Side",
		[ ((40.777051, -73.963781), (40.787969, -73.955798)), ((40.774353, -73.957515), (40.777051, -73.963781)),
		((40.777051, -73.963781), (40.774386, -73.957515))    
		]), 

	Hood("Upper East Side", 
		[ ((40.772501, -73.967171), (40.777018, -73.963781), ((40.765870, -73.951249), (40.772468, -73.967128)),
		((40.770226, -73.947601), (40.765155, -73.951850)), ((40.777051, -73.963781), (40.770193, -73.947473)))
		]),

	Hood("Lennox Hill", 
		[((40.764315, -73.972995), (40.772473, -73.967116)), ((40.758594, -73.958404), (40.764315, -73.973038)),
		((40.765875, -73.951237), (40.758562, -73.958490)), ((40.772408, -73.967073), (40.765843, -73.951280)) ]), 

	Hood("Hell's Kitchen",
		[ ((40.758269, -74.007885), (40.774033, -73.996684)), ((40.752223, -73.993466), (40.758172, -74.007756)),
		((40.768053, -73.981964), (40.752255, -73.993423)), ((40.774033, -73.996684), (40.768118, -73.981921))   
		]), 

	Hood("Midtown", 
		[ ((40.764188, -73.984980), (40.768251, -73.982062)), ((40.759052, -73.972663), (40.764220, -73.984894)),
		((40.762888, -73.969874), (40.759085, -73.972706)), ((40.768186, -73.982105), (40.762953, -73.969831))    
		]),

	Hood("Midtown", 
		[ ((40.749885, -73.987898), (40.761848, -73.979058)), ((40.746991, -73.981161), (40.749885, -73.987770)),
		((40.759052, -73.972406), (40.746991, -73.981203)), ((40.761880, -73.979058), (40.759020, -73.972363))   
		]),

	Hood("Midtown",
		[ ((40.752225, -73.993606), (40.756126, -73.990902)), ((40.749787, -73.987684), (40.752290, -73.993606)),
		((40.753688, -73.985066), (40.749754, -73.987812)), ((40.756126, -73.990902), (40.753591, -73.984980))   
		]),

	Hood("Theater District",
		[ ((40.756061, -73.990902), (40.764188, -73.984980)), ((40.753688, -73.985109), (40.756159, -73.990902)),
		((40.761880, -73.979101), (40.753721, -73.985066)),  ((40.764220, -73.984980), (40.761880, -73.979101)) 
		]),
	
	Hood("Midtown South", 
		[ ((40.737334, -73.996996), (40.749819, -73.987941)), ((40.734602, -73.990259), (40.737432, -73.996996)),
		((40.747023, -73.981204), (40.734700, -73.990344)), ((40.749819, -73.987812), (40.747071, -73.981334))   
		]), 

	Hood("Chelsea", 
		[ ((40.743508, -74.012189), (40.759178, -74.009657)), ((40.737330, -73.996911), (40.743508, -74.012232)),
		((40.749816, -73.987770), (40.737363, -73.996911)), ((40.758983, -74.009657), (40.749881, -73.987856))   
		]), 

	Hood("Turtle Bay", 
		[ ((40.752137, -73.977929), (40.763060, -73.969904)), ((40.747943, -73.968016), (40.752137, -73.977972)),
		((40.758314, -73.958660), (40.747911, -73.967930)), ((40.763060, -73.969947), (40.758314, -73.958703))
		]),

	Hood("Murray Hill", 
		[ ((40.747127, -73.981612), (40.752329, -73.977878)), ((40.742997, -73.971698), (40.747094, -73.981612)),
		((40.748070, -73.967836), (40.742997, -73.971698)), ((40.752361, -73.977921), (40.748070, -73.967836))   
		]),

	Hood("Kips Bay",
		[ ((40.740158, -73.986678), (40.747247, -73.981528)), ((40.734403, -73.972860), (40.740223, -73.986678)),
		((40.743085, -73.971658), (40.734370, -73.972645)), ((40.747279, -73.981528), (40.743052, -73.971615))   
		]),

	Hood("Gramercy Park", 
		[ ((40.734618, -73.990464), (40.740244, -73.986387)), ((40.731285, -73.982546), (40.734618, -73.990529)),
		((40.736911, -73.978491), (40.731301, -73.982525)), ((40.740260, -73.986387), (40.736927, -73.978469))    
		]),

	Hood("Stuyvesant", 
		[ ((40.731317, -73.982654), (40.736976, -73.978598)), ((40.726683, -73.971645), (40.731350, -73.982675)),
		((40.729301, -73.971452), (40.726667, -73.971581)), ((40.734927, -73.973491), (40.729301, -73.971452)),
		((40.736960, -73.978576), (40.734862, -73.973384))     
		]),

	Hood("Meatpacking",
		[ ((40.739382, -74.012983), (40.743479, -74.012253)), ((40.739382, -74.005344), (40.739334, -74.013004)),
		((40.740927, -74.005065), (40.739399, -74.005344)), ((40.743723, -74.012275), (40.740927, -74.005065))   
		]),

	Hood("West Village", 
		[ ((40.729198, -74.011542), (40.739441, -74.010384)), ((40.728775, -74.006993), (40.729198, -74.011585)),
		 ((40.739409, -74.006436), (40.728775, -74.006993)), ((40.739506, -74.010555), ())
		]),

	Hood("West Village", 
		[ ((40.739465, -74.006500), (40.741042, -74.005406)), ((40.735970, -73.997895), (40.739465, -74.006500)),
		 ((40.737384, -73.996758), (40.735970, -73.997874)), ((40.740994, -74.005384), (40.737417, -73.996780))
		]),

	Hood("West Village", 
		[ ((40.728807, -74.007187), (40.739409, -74.006500)), ((40.728352, -74.002852), (40.728840, -74.007229)),
		 ((40.736092, -73.997831), (40.728352, -74.002895)), ((40.739441, -74.006500), (40.735962, -73.997917))
		])


	#Hood("", 
	#	[ ((), ()), ((), ()), ((), ()), ((), ())
	#	])
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
	return render_template('my_hood.html')

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
			cookies = db.session.query(Cookie).filter(Cookie.answerID == thePostID)
			for cookie in cookies:
				print cookie
				if cookie.value == cookieValue:
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
			cookies = db.session.query(Cookie).filter(Cookie.answerID == thePostID)
			for cookie in cookies:
				if cookie.value == cookieValue:
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
# user is not in NYC
@app.route('/home', methods=["GET", "POST"])
def home():
	if request.method =="POST":
		lat = (request.json["lat"])
		longit = (request.json["longit"])
		for hood in hoodList:
			if containsPoint(hood.tupleList, (40.741099, -74.008603)) > 0:
				theHood = hood.name
				return render_template('whats_good.html', s = (db.session.query(Post).order_by(Post.id.desc())), 
					answers = db.session.query(Answer).order_by(Answer.score.desc()), hood = theHood, 
					theTag = "whats_good", subcat = "None")
		theHood = "Looks like you're not in NYC! We're working hard on bringing MyHood to your city soon!" 
		return render_template("phony.html", hood = theHood)
				#return render_template("not_in_nyc.html"

@app.route('/whats_good/<theHood>/<subcateg>')
def whats_good(theHood, subcateg):
	aList = [1,2,3]
	return render_template('whats_good.html', s = (db.session.query(Post).order_by(Post.id.desc())), 
		answers = db.session.query(Answer).order_by(Answer.score.desc()), hood = theHood, theTag = "whats_good", 
		subcat = subcateg, aList = aList)

@app.route('/help_me_find/<theHood>/<subcateg>')
def help_me_find(theHood, subcateg):
	return render_template('help_me_find.html', s = (db.session.query(Post).order_by(Post.id.desc())), 
		answers = db.session.query(Answer).order_by(Answer.score.desc()), hood = theHood, theTag = "help_me_find",
		subcat = subcateg)	

@app.route('/say_hi')
def say_hi():
	return "Hello!!!!"		


@app.route('/answer/<postID>/<nh>/<tag>/<subcateg>', methods=["GET", "POST"])
def answer(postID, nh, tag, subcateg):
	if request.method == "POST":
		subcategory = "None"
		anAnswer = request.form["user_input"]
		#search database for post with given postID
		thePost = Post.query.get(postID) #will this actually let me add answer to post
		#in database or to its copy?
		
		#add answer to the post's answer field
		theAnswer = Answer(postID, 0, anAnswer)
		db.session.add(theAnswer)
		db.session.commit()
		if subcateg != "None":
			subcategory = subcateg
		
		if tag == "whats_good":
			#return the template with posts and answers for given nh
			return render_template('whats_good.html', s = (db.session.query(Post).order_by(Post.id.desc())), 
			answers = db.session.query(Answer).order_by(Answer.score.desc()), hood = nh, post_copy = thePost, 
			theTag = tag, subcat = subcategory)
		elif tag == "help_me_find":
			#return the template with posts and answers for given nh
			return render_template('help_me_find.html', s = (db.session.query(Post).order_by(Post.id.desc())), 
			answers = db.session.query(Answer).order_by(Answer.score.desc()), hood = nh, post_copy = thePost, 
			theTag = tag, subcat = subcategory)	
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
		
#@app.route("/post/<nh>/<tag>", methods=["GET", "POST"])
#def post(nh, tag):
#    if request.method == "POST":
#		post = Post(request.form["user_input"], nh, tag)
#		db.session.add(post)
#		db.session.commit()

#		return render_template('whats_good.html', s = (db.session.query(Post).order_by(Post.id.desc())), 
#		answers = db.session.query(Answer).order_by(Answer.score.desc()), hood = nh, theTag = tag)
#    else:
#    	return render_template("search.html")

@app.route("/post", methods=["GET", "POST"])
def post():
	if request.method =="POST":
		nh = request.json["theHood"]
		categ = request.json["category"]
		user_text = request.json["text"]
		subcateg = request.json["subcategory"]
		post = Post(user_text, nh, categ)
		post.subcat = subcateg
		db.session.add(post)
		db.session.commit()


		if categ == "whats_good":
			return render_template('whats_good.html', s = (db.session.query(Post).order_by(Post.id.desc())), 
			answers = db.session.query(Answer).order_by(Answer.score.desc()), hood = nh, theTag = categ, 
			subcat = "None")
		elif categ == "help_me_find":
			return render_template('help_me_find.html', s = (db.session.query(Post).order_by(Post.id.desc())), 
			answers = db.session.query(Answer).order_by(Answer.score.desc()), hood = nh, theTag = categ, 
			subcat = "None")

@app.route("/load_posts/<theHood>/<tag>")
def load_posts(theHood, tag):
	nh = theHood
	categ = tag
	if categ == "whats_good":
		return render_template('whats_good.html', s = (db.session.query(Post).order_by(Post.id.desc())), 
		answers = db.session.query(Answer).order_by(Answer.score.desc()), hood = nh, theTag = categ, 
		subcat = "None")
	elif categ == "help_me_find":
		return render_template('help_me_find.html', s = (db.session.query(Post).order_by(Post.id.desc())), 
		answers = db.session.query(Answer).order_by(Answer.score.desc()), hood = nh, theTag = categ, 
		subcat = "None")

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
		url = "http://open.mapquestapi.com/nominatim/v1/reverse.php?lat=" + lat + "&lon="
		+ long + "&format=json"
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