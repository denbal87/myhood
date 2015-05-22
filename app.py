from flask import Flask, jsonify, render_template, request
import requests
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import desc



app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///example.db'


db = SQLAlchemy(app)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String)
    date = db.Column(db.DateTime)
    nh = db.Column(db.String)
    isAnswer = db.Column(db.Integer)
    answer = db.Column(db.String)		

    def __init__(self, text, hood, ans):
        self.text = text
        self.nh = hood
        self.date = datetime.now()
	self.isAnswer = ans
	self.answer = 'none'

db.create_all()

#method for determining neighborhood based on zipcode
#returns a tuple containing the neighborhood/s	
def get_nh(zipcode):
	zipcodes = { "Inwood" : ["10034"], 
		("Washington Heights") : ["10040", "10033", "10032"],
		("Hamilton Heights") : ["10039"],
		("Harlem") : ["10027", "10026", "10030", "10037", "10039"],
		("Morningside Heights") : ["10027"],
		("East Harlem") : ["10035", "10029"],
		("Upper West Side", "hi") : ["10024", "10025"],
		("Lincoln Square") : ["10023"],
		("Upper East Side") : ["10021", "10028", "10044", "10065", "10075", "10128"],
		("Hell's Kitchen") : ["10018", "10036", "10019"],
		("Midtown") : ["10019", "10022", "10017", "10016"],
		("Chelsea") : ["10001", "10011"],
		("West Village") : ["10014"],
		("East Village") : ["10009"],
		("Little Italy", "Chinatown", "Tribeca") : ["10013"],
		("Lower East Side") : ["10002", "10003"],
		("Soho") : ["10012"],
		("Wall Street") : ["10038"],
		("Southern Tip") : ["10004"],}
		
	for element in zipcodes:
		if zipcode in zipcodes[element]:
			return element	

#uncoment to delete entries in database
#for entry in db.session.query(Post).order_by(Post.id):
	#db.session.delete(entry)
	#db.session.commit()

@app.route('/')
def page():
	return render_template('home.html')

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
	

@app.route('/phony')
def phony():
	query = request.query_string #args.get('theString')
	url = "http://open.mapquestapi.com/nominatim/v1/reverse.php?" + query
	location_dict = requests.get(url).json()
	zip = location_dict["address"]["postcode"]
	
	hood_tuple = get_nh(zip) #need to know how many items in tuple
	
	#determinine number of itemps in hood_tuple 
	#if number_items > 1
	#	look up "neighbourhood" to pass to the page template
	#else
	#	pass hood_tuple
	
	return render_template("phony.html", location_data = location_dict)
		
#@app.route('/food/<nh>')
#def food(nh):


@app.route('/<postID>/<nh>', methods=["GET", "POST"])
def answer(postID, nh):
	if request.method == "POST":
		anAnswer = request.form["user_input"]
		#search database for post with given postID
		thePost = Post.query.get(postID) #will this actually let me add answer to post
		#in database or to its copy?
		
		#add answer to the post's answer field
		thePost.answer = anAnswer
		db.session.commit()
		#return the template with posts and answers for given nh
		return render_template('whats_good.html', s = (db.session.query(Post).order_by(Post.id.desc())), hood = nh, post_copy = thePost)
	
		
@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        url = "https://api.github.com/search/repositories?q=" + request.form["user_search"]
        response_dict = requests.get(url).json()
        return render_template('results.html', api_data=response_dict)
    else: # request.method == "GET"
        return render_template("search.html")
		
@app.route("/post_wg/<nh>", methods=["GET", "POST"])
def post_wg(nh):
    if request.method == "POST":
		post = Post(request.form["user_input"], nh, 0)
		db.session.add(post)
		db.session.commit()

		return render_template('whats_good.html', s = (db.session.query(Post).order_by(Post.id.desc())), hood = nh)
    else:
    	return render_template("search.html")


@app.route('/add/<x>/<y>')
def add(x, y):
	return str(int(x) + int(y))

@app.errorhandler(404)
def nope(error):
	return "We ain't got what yo looking for, fool!", 404	


if __name__ == '__main__':
	app.run(host='0.0.0.0')
