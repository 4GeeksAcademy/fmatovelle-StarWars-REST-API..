"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for, abort
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Person, Planet, Vehicle
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False

db_url = os.getenv("DATABASE_URL")
if db_url is not None:
    app.config['SQLALCHEMY_DATABASE_URI'] = db_url.replace("postgres://", "postgresql://")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:////tmp/test.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code


# generate sitemap with all your endpoints
# [GET] /people Listar todos los registros de people en la base de datos.

# Endpoint para listar todas las personas
@app.route('/people', methods=['GET'])
def get_people():
    people = Person.query.all()  
    return jsonify([person.serialize() for person in people])  

# # Endpoint para obtener la información de una sola persona por ID
@app.route('/people/<int:people_id>', methods=['GET'])
def get_person_by_id(people_id):
    person = Person.query.get(people_id)  
    if person is None:
        abort(404) 
    return jsonify(person.serialize())  

# # Endpoint para listar todas los planetas
@app.route('/planets', methods=['GET'])
def get_planets():
    planets = Planet.query.all() 
    return jsonify([planet.serialize() for planet in planets])  

# # Endpoint para obtener la información de un solo planet por ID
@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_planet_by_id(planet_id):
    planet = Planet.query.get(planet_id)
    if planet is None:
        abort(404)  
    return jsonify(planet.serialize())

# # Endpoint para listar todas los vehicles
@app.route('/vehicles', methods=['GET'])
def get_vehicles():
    vehicles = Vehicle.query.all() 
    return jsonify([vehicle.serialize() for vehicle in vehicles])  

# # Endpoint para obtener la información de un solo vehicles por ID
@app.route('/vehicles/<int:vehicle_id>', methods=['GET'])
def get_vehicle_by_id(vehicle_id):
    vehicle = Vehicle.query.get(vehicle_id)
    if vehicle is None:
        abort(404)  
    return jsonify(vehicle.serialize())





@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all() 
    return jsonify([user.serialize() for user in users])  

# # [GET] /users/favorites Listar todos los favoritos que pertenecen al usuario actual.

@app.route('/users/favorites', methods=['GET'])
def get_users_favorites():
    users = User.query.all()  
    return jsonify([user.serialize() for user in users])  


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404

    # Añadir el planeta a los favoritos del usuario
    user.planet_favorite.append(planet)
    db.session.commit()

    return jsonify({"message": f"Planet {planet.name} added to favorites."}), 201

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_person(people_id):
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    person = Person.query.get(people_id)
    if not person:
        return jsonify({"error": "Person not found"}), 404

    # Añadir la persona a los favoritos del usuario
    user.person_favorite.append(person)
    db.session.commit()

    return jsonify({"message": f"Person {person.name} added to favorites."}), 201

@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"error": "Planet not found"}), 404

    # Eliminar el planeta de los favoritos del usuario
    if planet in user.planet_favorite:
        user.planet_favorite.remove(planet)
        db.session.commit()
        return jsonify({"message": f"Planet {planet.name} removed from favorites."}), 200
    else:
        return jsonify({"error": "Planet not in user's favorites"}), 404
    

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_person(people_id):
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    person = Person.query.get(people_id)
    if not person:
        return jsonify({"error": "Person not found"}), 404

    # Eliminar la persona de los favoritos del usuario
    if person in user.person_favorite:
        user.person_favorite.remove(person)
        db.session.commit()
        return jsonify({"message": f"Person {person.name} removed from favorites."}), 200
    else:
        return jsonify({"error": "Person not in user's favorites"}), 404







# @app.route('/')
# def sitemap():
#     return generate_sitemap(app)

# @app.route('/user', methods=['GET'])
# def handle_hello():

#     response_body = {
#         "msg": "Hello, this is your GET /user response "
#     }

    return jsonify(response_body), 200

# this only runs if `$ python src/app.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
