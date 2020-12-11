#	IMPORTS:

from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from pymongo import MongoClient
import bcrypt
import spacy

#	INITIALIZATIONS:
app = Flask(__name__)
api = Api(app)
client = MongoClient("mongodb://db:27017")
db = client.SimilarityDB
users = db["Users"]
admins = db["Administrators"]


#	CLASS RESOURCES:
#	register user and allot 6 tokens
class Register(Resource):
	def post(self):

		#	fetch
		postedData = request.get_json()

		#	verify
		username = postedData["username"]
		password = postedData["password"].encode('utf-8')
		# this is separated as a function in the tutorial.
		if users.find({"Username": username}).count() > 0:
			returnJSON = {
				"Message": "Username already taken, please enter a new one.",
				"Status Code": 300
			}

			return jsonify(returnJSON)

		#	insert into db

		hashed_pw = bcrypt.hashpw(password, bcrypt.gensalt())

		users.insert_one({"Username": username,
						  "password": hashed_pw,
						  "Tokens": 6
						  })

		#	return ok status
		returnJSON = {
			"Message": "Successfully registered user " + str(username),
			"Status Code": 200
		}

		return jsonify(returnJSON)

#	API for refilling tokens:
class Refill(Resource):
	def post(self):
		# ---------------- P R E P R O C E S S I N G
		#	fetch data
		postedData = request.get_json()

		username = postedData["username"]
		admin_password = postedData["admin_pw"]
		amount_to_add = postedData["refill"]

		#	verify/authenticate
		#	validate username:
		if users.find({"Username": username}).count() == 0:
			returnJSON = {
				"Message": "User " + username + " does not exist.",
				"Status Code": 300
			}
			return jsonify(returnJSON)

		#	FETCH ADMIN PW:
			""" THIS IS A SIMPLIFICATION, DO NOT DO THIS FOR
				PRODUCTION!!! """
		admin_key = "asdf1234"
		if admin_password != admin_key:
			returnJSON = {
				"Message": "This purchase is not verified by an admin, please contact support",
				"Status Code": 300
			}
			return jsonify(returnJSON)

		#	add tokens:
		curr_token_count = users.find({"Username":username})[0]["Tokens"]

		users.update({"Username":username},
			         {"$set": {"Tokens":curr_token_count + amount_to_add}})

		#	send success message:
		returnJSON = {
				"Message": "Added " + str(amount_to_add) + " tokens to account",
				"Status Code": 200
			}
		return jsonify(returnJSON)


#	similarity detection API:
class Detect(Resource):
	def post(self):
		# ---------------- P R E P R O C E S S I N G
		#	fetch data
		postedData = request.get_json()
		username = postedData["username"]
		password = postedData["password"].encode('utf-8')
		text1 = postedData["text1"]
		text2 = postedData["text2"]

		#	verify/authenticate
		#	validate username:
		if users.find({"Username": username}).count() == 0:
			returnJSON = {
				"Message": "User " + username + " does not exist.",
				"Status Code": 300
			}

			return jsonify(returnJSON)

		#	validate password:
		hashed_pw = users.find({"Username":username})[0]["password"] 
		if bcrypt.hashpw(password, hashed_pw) != hashed_pw:
			returnJSON = {
				"Message": "Provided Username and password is incorrect",
				"Status Code": 300
			}

			return jsonify(returnJSON)

		#	validate token allowance:
		num_tokens = users.find({"Username":username})[0]["Tokens"]
		if  num_tokens <= 0:
			returnJSON = {
				"Message": "Insufficient tokens",
				"Status Code": 300
			}

			return jsonify(returnJSON)

		# ---------------------------- M A I N
		#calculate the edit distance:
		nlp = spacy.load('en_core_web_sm')	#initi spacy model
		text1 = nlp(text1)	# transform to nlp model sentence
		text2 = nlp(text2)

		#calc similarity ratio, closer to 1 == more similar
		ratio = text1.similarity(text2)

		#return and update tokens:
		returnJSON = {
			"Message": "Similarity ratio calculated successfully.",
			"Similarity ratio": ratio,
			"Status Code": 200	
		}

		users.update({"Username":username},
			         {"$set": {"Tokens":num_tokens-1}})

		return jsonify(returnJSON)

#	add resources:
api.add_resource(Register, "/register")
api.add_resource(Refill, "/refill")
api.add_resource(Detect, "/detect")

#	RUN:
if __name__ == "__main__":
	app.run(host='0.0.0.0')