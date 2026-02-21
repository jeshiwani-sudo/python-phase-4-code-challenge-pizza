#!/usr/bin/env python3
from models import db, Restaurant, RestaurantPizza, Pizza
from flask_migrate import Migrate
from flask import Flask, request
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI",
    f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"
)

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.json.compact = False

db.init_app(app)
migrate = Migrate(app, db)
api = Api(app)


class RestaurantList(Resource):
    def get(self):
        restaurants = Restaurant.query.all()
        return [
            r.to_dict(only=("id", "name", "address"))
            for r in restaurants
        ], 200


class RestaurantByID(Resource):
    def get(self, id):
        restaurant = db.session.get(Restaurant, id)

        if not restaurant:
            return {"error": "Restaurant not found"}, 404

        return restaurant.to_dict(), 200

    def delete(self, id):
        restaurant = db.session.get(Restaurant, id)

        if not restaurant:
            return {"error": "Restaurant not found"}, 404

        db.session.delete(restaurant)
        db.session.commit()

        return {}, 204


class PizzaList(Resource):
    def get(self):
        pizzas = Pizza.query.all()
        return [
            p.to_dict(only=("id", "name", "ingredients"))
            for p in pizzas
        ], 200


class RestaurantPizzaCreate(Resource):
    def post(self):
        data = request.get_json()

        try:
            rp = RestaurantPizza(
                price=data.get("price"),
                pizza_id=data.get("pizza_id"),
                restaurant_id=data.get("restaurant_id")
            )

            db.session.add(rp)
            db.session.commit()

            return rp.to_dict(), 201

        except Exception:
            return {"errors": ["validation errors"]}, 400



api.add_resource(RestaurantList, "/restaurants")
api.add_resource(RestaurantByID, "/restaurants/<int:id>")
api.add_resource(PizzaList, "/pizzas")
api.add_resource(RestaurantPizzaCreate, "/restaurant_pizzas")



if __name__ == "__main__":
    app.run(port=5555, debug=True)