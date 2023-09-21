#!/usr/bin/env python3

from flask import Flask, make_response, jsonify, request, session
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Article, User

app = Flask(__name__)
app.secret_key = b'Y\xf1Xz\x00\xad|eQ\x80t \xca\x1a\x10K'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

api = Api(app)
test_array = []

class CheckSession(Resource):
    def get(self):
        test_array.append(0)
        if session.get('user_id'):
            test_array.append(1)
            user_id = session.get("user_id")
            user_dict = User.query.filter(User.id == user_id).first().to_dict()
            # Only wants user information, not the articles.
            del user_dict["articles"]
            response = make_response(
                jsonify(user_dict),
                200
            )
        else:
            test_array.append(2)
            response = make_response(
                {},
                401
            )
        return response
    
class ClearSession(Resource):

    def delete(self):

        test_array.append(3)
        print("Deleting the session;  Logging out.")
    
        session['page_views'] = None
        session['user_id'] = None

        return {}, 204

class IndexArticle(Resource):
    
    def get(self):
        articles = [article.to_dict() for article in Article.query.all()]
        return articles, 200

class Login(Resource):
    
    def post(self):
        test_array.append(4)
        # The http request body is in the form {username: user_name}
        login_data = request.get_json()
  
        user = User.query.filter(User.username == login_data["username"]).first().to_dict()

        session['user_id'] = user["id"]
    
        response_dict = {"username" : user["username"], "id" : user["id"]}

        response = make_response(
            jsonify(response_dict),
            200
        )
        return response

class Logout(Resource):
    def delete(self):
        test_array.append(5)
        print("Deleting the session;  Logging out.")
    
        session['page_views'] = None
        session['user_id'] = None

        return {}, 204

class ShowArticle(Resource):

    def get(self, id):
        session['page_views'] = 0 if not session.get('page_views') else session.get('page_views')
        session['page_views'] += 1

        if session['page_views'] <= 3:

            article = Article.query.filter(Article.id == id).first()
            article_json = jsonify(article.to_dict())

            return make_response(article_json, 200)

        return {'message': 'Maximum pageview limit reached'}, 401

api.add_resource(CheckSession, '/check_session')
api.add_resource(ClearSession, '/clear')
api.add_resource(IndexArticle, '/articles')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(ShowArticle, '/articles/<int:id>')



if __name__ == '__main__':
    app.run(port=5555, debug=True)
