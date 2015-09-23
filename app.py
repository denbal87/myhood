from flask import Flask, jsonify, render_template, request, make_response, send_file
import requests
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc
import uuid
import os
import neighborhoods
from datetime import datetime
from dateutil import tz




app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///myhood.db'

db = SQLAlchemy(app)

hoodList = neighborhoods.hoodList
nycBounds = neighborhoods.nycBounds

# change time to New York loca time
def localtime():
	from_zone = tz.gettz('UTC')
	to_zone = tz.gettz('America/New_York')

	# utc = datetime.utcnow()
	utc = datetime.strptime(datetime.utcnow().strftime('%Y-%m-%d %H:%M'), '%Y-%m-%d %H:%M')

	# Tell the datetime object that it's in UTC time zone since 
	# datetime objects are 'naive' by default
	utc = utc.replace(tzinfo=from_zone)

	# Convert time zone
	central = utc.astimezone(to_zone)
	dateAsString = utc.astimezone(to_zone).strftime('posted on %b %d %Y at %-I:%M%p')
	return {'postDate' : dateAsString,
		'postDay' : central.day,
		'postMonth' : central.month,
		'postYear' : central.year}

# returns a list with the past 7 dates including today
def thisWeek():
	postDict = localtime()
	day = int(postDict['postDay'])
	month = int(postDict['postMonth'])
	year = int(postDict['postYear'])
	dateList = [{'day' : day, 'month' : month, 'year' : year}]
	if year % 4 == 0 or (year % 100 == 0 and year % 400 == 0):
		leap = True
	else:
		leap = False
	prevday = day

	for n in range(0,7):
		prevday = prevday - 1
		if prevday >= 1:
			dateList.append({'day' : prevday, 'month' : month, 'year' : year})
		elif prevday - 1 < 1 and month != 2:
			if (month < 8 and month % 2 != 0) or (month > 7 and month % 2 == 0):
				prevday = 31
			else:
				prevday = 30		
			dateList.append({'day' : prevday, 'month' : month, 'year' : year})	
		elif prevday - 1 < 1 and month == 2:
			if leap:
				prevday = 29
				dateList.append({'day' : prevday, 'month' : month, 'year' : year})
			else:
				prevday = 28
				dateList.append({'day' : prevday, 'month' : month, 'year' : year})	
	return dateList	

# returns a list of posts from this week in a given category
@app.route('/search/<categ>/<subcateg>/<hood>', methods=["GET", "POST"])
def search(categ, subcateg, hood,):
	if request.method == "POST":
		keyWord = request.form["user_input"]
		day = request.form['day']
		month = request.form['month']
		year = request.form['year']		
		postList = []
		dateDict = localtime()
		thisMonth = int(dateDict['postMonth'])
		thisYear = int(dateDict['postYear'])
		
		# if date and month and year are selected
		if day != '-' and month != '-' and year != '-':
			day = int(request.form['day'])
			month = int(request.form['month'])
			year = int(request.form['year'])
			# if keyword is given
			if keyWord != '':
				posts = db.session.query(Post).filter(Post.month == month, Post.day == day, Post.year == year, Post.nh == hood, Post.tag == categ)
				for post in posts:
					if keyWord in post.text or keyWord in post.subcat:
						postList.append({'text' : post.text, 'date' : post.date, 'subcat' : post.subcat, 'id' : post.id, 'tag' : post.tag})
			# keyword is not provided--just show all posts from that day
			else:
				posts = db.session.query(Post).filter(Post.month == month, Post.day == day, Post.year == year, Post.nh == hood, Post.tag == categ)
				for post in posts:
					postList.append({'text' : post.text, 'date' : post.date, 'subcat' : post.subcat, 'id' : post.id, 'tag' : post.tag})

		# date is not selected--show posts from past week
		# filter database for posts from only two past months			
		else:

			if subcateg != 'None':
				# if month is January, prev month is December
				if thisMonth == 1:
					posts = db.session.query(Post).filter((Post.month == 12 or Post.month == thisMonth), Post.year == thisYear, Post.nh == hood,
						Post.tag == categ)
				else:
					posts = db.session.query(Post).filter((Post.month == thisMonth - 1 or Post.month == thisMonth), Post.year == thisYear,
						Post.nh == hood, Post.tag == categ)
			else:
				# if month is January, prev month is December
				if thisMonth == 1:
					posts = db.session.query(Post).filter((Post.month == 12 or Post.month == thisMonth), Post.year == thisYear, Post.nh == hood,
						Post.tag == categ) 
				else:
					posts = db.session.query(Post).filter((Post.month == thisMonth - 1 or Post.month == thisMonth), Post.year == thisYear,
						Post.nh == hood, Post.tag == categ)

			# put posts that match search criteria in postList
			weekList = thisWeek()
			for date in weekList:
				for post in posts:
					if keyWord != '':
						if post.day == int(date['day']) and post.month == int(date['month']) and post.year == int(date['year']) and (keyWord in post.text
							or keyWord in post.subcat):
							postList.append({'text' : post.text, 'date' : post.date, 'subcat' : post.subcat, 'id' : post.id, 'tag' : post.tag})
					else:
						if post.day == int(date['day']) and post.month == int(date['month']) and post.year == int(date['year']):
							postList.append({'text' : post.text, 'date' : post.date, 'subcat' : post.subcat, 'id' : post.id, 'tag' : post.tag})	
		
		return render_template('search_results.html', s = postList, answers = db.session.query(Answer).order_by(Answer.score.desc()), 
			hood = hood, theTag = categ, subcat = subcateg)




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
    date = db.Column(db.String)
    nh = db.Column(db.String)
    tag = db.Column(db.String) # this is the category the post is under
    subcat = db.Column(db.String, default = "None") # this is the tag or subcategory that
    day  = db.Column(db.Integer)
    month = db.Column(db.Integer)
    year = db.Column(db.Integer)
    

    def __init__(self, text, hood, aTag):
        dateDict = localtime()
        self.text = text
        self.nh = hood
        #uncomment to write custom date for testing
        #self.date = 'posted on Sep 20 2015 at 1:04PM'
        self.date = dateDict['postDate']
        self.day = dateDict['postDate']
        self.month = dateDict['postMonth']
        self.year = dateDict['postYear']
        self.tag = aTag

db.create_all()


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


@app.route('/scroller')
def scroller():
	return render_template('iscroll.html')

@app.route('/make_posts')
def make_posts():
	for a in range(0, 10):
		dateDict = localtime()
		theDate = dateDict['postDate']
		nh = "Morningside Heights"
		categ = "whats_good"
		user_text = "what the heck?"
		subcateg = 'events'
		post = Post(user_text, nh, categ)
		post.subcat = subcateg
		post.day = 20
		post.month = 9
		post.year = 2015
		db.session.add(post)
		db.session.commit()	
	return "Posts have been posted!"	

@app.route('/')
def page():
	return render_template('my_hood.html')

@app.route('/check_key', methods=["GET", "POST"])
def check_key():
	if request.method == "POST":
		key = request.form["key"]
		if key == "znamensk87":
			return render_template("my_hood.html")
		else:
			return render_template("home.html")


@app.route('/my_hood')
def my_hood():
	return render_template('my_hood.html')

@app.route('/map/<neighborhood>')
def map(neighborhood):
	return render_template('map.html', nh = neighborhood)
	#return send_file('static/nh_map_small.jpg', mimetype='image/gif')

@app.route('/check_key_not_nyc', methods=["GET", "POST"])
def check_key_not_nyc():
	if request.method == "POST":
		key = request.form["key"]
		if key == "znamensk87":
			return render_template("map.html")
		else:
			return render_template("not_in_nyc.html")


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
			if containsPoint(hood.tupleList, (lat, longit)) > 0:
				theHood = hood.name
				return theHood
		if containsPoint(nycBounds.tupleList, (lat, longit)) > 0:		 
			return "in nyc"
		else:
			return "not in nyc"


@app.route('/not_in_nyc')
def not_in_nyc():
	return render_template('not_in_nyc.html')

@app.route('/in_nyc')
def in_nyc():
	return render_template('in_nyc.html')



@app.route('/whats_good/<theHood>/<subcateg>')
def whats_good(theHood, subcateg):
	dateDict = localtime()
	theDate = dateDict['postDate']
	aList = [1,2,3]
	return render_template('whats_good.html', s = (db.session.query(Post).order_by(Post.id.desc())), 
		answers = db.session.query(Answer).order_by(Answer.score.desc()), hood = theHood, theTag = "whats_good", 
		subcat = subcateg, aList = aList, date = theDate)

@app.route('/help_me_find/<theHood>/<subcateg>')
def help_me_find(theHood, subcateg):
	dateDict = localtime()
	theDate = dateDict['postDate']
	return render_template('help_me_find.html', s = (db.session.query(Post).order_by(Post.id.desc())), 
		answers = db.session.query(Answer).order_by(Answer.score.desc()), hood = theHood, theTag = "help_me_find",
		subcat = subcateg, date = theDate)		


@app.route('/answer/<postID>/<nh>/<tag>/<subcateg>', methods=["GET", "POST"])
def answer(postID, nh, tag, subcateg):
	if request.method == "POST":
		dateDict = localtime()
		theDate = dateDict['postDate']
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
			theTag = tag, subcat = subcategory, date = theDate)
		elif tag == "help_me_find":
			#return the template with posts and answers for given nh
			return render_template('help_me_find.html', s = (db.session.query(Post).order_by(Post.id.desc())), 
			answers = db.session.query(Answer).order_by(Answer.score.desc()), hood = nh, post_copy = thePost, 
			theTag = tag, subcat = subcategory, date = theDate)	
	else:
		return render_template("search.html")

		

@app.route("/post", methods=["GET", "POST"])
def post():
	if request.method =="POST":
		dateDict = localtime()
		theDate = dateDict['postDate']
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
			subcat = "None", date = theDate)
		elif categ == "help_me_find":
			return render_template('help_me_find.html', s = (db.session.query(Post).order_by(Post.id.desc())), 
			answers = db.session.query(Answer).order_by(Answer.score.desc()), hood = nh, theTag = categ, 
			subcat = "None", date = theDate)

@app.route("/load_posts/<theHood>/<tag>")
def load_posts(theHood, tag):
	dateDict = localtime()
	theDate = dateDict['postDate']
	nh = theHood
	categ = tag
	if categ == "whats_good":
		return render_template('whats_good.html', s = (db.session.query(Post).order_by(Post.id.desc())), 
		answers = db.session.query(Answer).order_by(Answer.score.desc()), hood = nh, theTag = categ, 
		subcat = "None", date = theDate)
	elif categ == "help_me_find":
		return render_template('help_me_find.html', s = (db.session.query(Post).order_by(Post.id.desc())), 
		answers = db.session.query(Answer).order_by(Answer.score.desc()), hood = nh, theTag = categ, 
		subcat = "None", date = theDate)

@app.errorhandler(404)
def nope(error):
	return render_template("error.html");	

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