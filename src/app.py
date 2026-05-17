"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, User, Character, Planet, FavoriteCharacter, FavoritePlanet

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

@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

@app.route('/')
def sitemap():
    return generate_sitemap(app)


@app.route('/users', methods=['GET'])
def get_users():
    users = User.query.all()
    all_users = [user.serialize() for user in users]
    return jsonify(all_users), 200

@app.route('/users/favorites', methods=['GET'])
def get_user_favorites():
    current_user_id = 1
    user = User.query.get(current_user_id)
    
    if not user:
        return jsonify({"msg": "Usuario no encontrado"}), 404
        
    fav_planets = [fav.serialize() for fav in user.favorite_planets]
    fav_characters = [fav.serialize() for fav in user.favorite_characters]
    
    return jsonify({
        "favorite_planets": fav_planets,
        "favorite_characters": fav_characters
    }), 200


@app.route('/people', methods=['GET'])
def get_all_people():
    characters = Character.query.all()
    all_characters = [char.serialize() for char in characters]
    return jsonify(all_characters), 200

@app.route('/people/<int:people_id>', methods=['GET'])
def get_one_person(people_id):
    character = Character.query.get(people_id)
    if not character:
        return jsonify({"msg": "Personaje no encontrado"}), 404
    return jsonify(character.serialize()), 200


@app.route('/planets', methods=['GET'])
def get_all_planets():
    planets = Planet.query.all()
    all_planets = [planet.serialize() for planet in planets]
    return jsonify(all_planets), 200

@app.route('/planets/<int:planet_id>', methods=['GET'])
def get_one_planet(planet_id):
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"msg": "Planeta no encontrado"}), 404
    return jsonify(planet.serialize()), 200


@app.route('/favorite/planet/<int:planet_id>', methods=['POST'])
def add_favorite_planet(planet_id):
    current_user_id = 1
    
    planet = Planet.query.get(planet_id)
    if not planet:
        return jsonify({"msg": "El planeta no existe"}), 404
        
    exists = FavoritePlanet.query.filter_by(user_id=current_user_id, planet_id=planet_id).first()
    if exists:
        return jsonify({"msg": "Este planeta ya está en tus favoritos"}), 400

    new_favorite = FavoritePlanet(user_id=current_user_id, planet_id=planet_id)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify({"msg": f"Planeta {planet.name} añadido a favoritos"}), 201

@app.route('/favorite/people/<int:people_id>', methods=['POST'])
def add_favorite_person(people_id):
    current_user_id = 1
    
    character = Character.query.get(people_id)
    if not character:
        return jsonify({"msg": "El personaje no existe"}), 404
        
    exists = FavoriteCharacter.query.filter_by(user_id=current_user_id, character_id=people_id).first()
    if exists:
        return jsonify({"msg": "Este personaje ya está en tus favoritos"}), 400

    new_favorite = FavoriteCharacter(user_id=current_user_id, character_id=people_id)
    db.session.add(new_favorite)
    db.session.commit()
    return jsonify({"msg": f"Personaje {character.name} añadido a favoritos"}), 201


@app.route('/favorite/planet/<int:planet_id>', methods=['DELETE'])
def delete_favorite_planet(planet_id):
    current_user_id = 1
    
    favorite = FavoritePlanet.query.filter_by(user_id=current_user_id, planet_id=planet_id).first()
    if not favorite:
        return jsonify({"msg": "El planeta no está en tus favoritos"}), 404
        
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"msg": "Planeta eliminado de favoritos"}), 200

@app.route('/favorite/people/<int:people_id>', methods=['DELETE'])
def delete_favorite_person(people_id):
    current_user_id = 1
    
    favorite = FavoriteCharacter.query.filter_by(user_id=current_user_id, character_id=people_id).first()
    if not favorite:
        return jsonify({"msg": "El personaje no está en tus favoritos"}), 404
        
    db.session.delete(favorite)
    db.session.commit()
    return jsonify({"msg": "Personaje eliminado de favoritos"}), 200

if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)