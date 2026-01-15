#!/usr/bin/env python3

from flask import Flask, request, make_response
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_restful import Api, Resource

from models import db, Newsletter

# -------------------- APP SETUP --------------------

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///newsletters.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

db.init_app(app)
migrate = Migrate(app, db)
ma = Marshmallow(app)
api = Api(app)

# -------------------- SCHEMA --------------------

class NewsletterSchema(ma.SQLAlchemySchema):
    class Meta:
        model = Newsletter
        load_instance = True

    title = ma.auto_field()
    published_at = ma.auto_field()

    url = ma.Hyperlinks({
        "self": ma.URLFor("newsletterbyid", values=dict(id="<id>")),
        "collection": ma.URLFor("newsletters")
    })

# Instantiate schemas
newsletter_schema = NewsletterSchema()
newsletters_schema = NewsletterSchema(many=True)

# -------------------- RESOURCES --------------------

class Index(Resource):
    def get(self):
        response_dict = {"index": "Welcome to the Newsletter RESTful API"}
        return make_response(response_dict, 200)

api.add_resource(Index, '/')

class Newsletters(Resource):
    def get(self):
        newsletters = Newsletter.query.all()
        return make_response(newsletters_schema.dump(newsletters), 200)

    def post(self):
        new_record = Newsletter(
            title=request.form['title'],
            body=request.form['body']
        )
        db.session.add(new_record)
        db.session.commit()
        return make_response(newsletter_schema.dump(new_record), 201)

api.add_resource(Newsletters, '/newsletters', endpoint="newsletters")

class NewsletterByID(Resource):
    def get(self, id):
        record = Newsletter.query.get(id)
        if not record:
            return {"error": "Newsletter not found"}, 404
        return make_response(newsletter_schema.dump(record), 200)

    def patch(self, id):
        record = Newsletter.query.get(id)
        if not record:
            return {"error": "Newsletter not found"}, 404

        for attr in request.form:
            setattr(record, attr, request.form[attr])

        db.session.commit()
        return make_response(newsletter_schema.dump(record), 200)

    def delete(self, id):
        record = Newsletter.query.get(id)
        if not record:
            return {"error": "Newsletter not found"}, 404

        db.session.delete(record)
        db.session.commit()
        return '', 204

api.add_resource(NewsletterByID, '/newsletters/<int:id>', endpoint="newsletterbyid")

# -------------------- RUN SERVER --------------------

if __name__ == '__main__':
    app.run(port=5555, debug=True)
