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

    def __init__(self, text, hood):
        self.text = text
        self.nh = hood
        self.date = datetime.now()

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
		

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        url = "https://api.github.com/search/repositories?q=" + request.form["user_search"]
        response_dict = requests.get(url).json()
        return render_template('results.html', api_data=response_dict)
    else: # request.method == "GET"
        return render_template("search.html")
		
@app.route("/post_wg", methods=["GET", "POST"])
def post_wg():
    if request.method == "POST":
	
		#get zipcode from client's IP
		client_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
		url = "http://ip-api.com/json/" + "129.236.235.231"
		location_dict = requests.get(url).json()
		zip = location_dict["zip"]
		
		hood_tuple = get_nh(zip) #need to know how many items in tuple
		
		#if len(hood_tuple) > 1:
			
		
		post = Post(request.form["user_input"], hood_tuple)
		db.session.add(post)
		db.session.commit()

		return render_template('whats_good.html', s = (db.session.query(Post).order_by(Post.id.desc())), nh_tuple = hood_tuple)
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