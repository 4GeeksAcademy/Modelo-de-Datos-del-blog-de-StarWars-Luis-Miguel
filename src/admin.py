import os
from flask_admin import Admin
from models import db, User, Character, Planet, FavoriteCharacter, FavoritePlanet
from flask_admin.contrib.sqla import ModelView

class UserAdminView(ModelView):
    column_list = ['id', 'email', 'is_active']

class CharacterAdminView(ModelView):
    column_list = ['id', 'name', 'gender', 'eye_color']

class PlanetAdminView(ModelView):
    column_list = ['id', 'name', 'climate', 'terrain']

class FavoriteCharacterView(ModelView):
    column_list = ['id', 'user_id', 'character_id']
    form_columns = ['user_id', 'character_id']

class FavoritePlanetView(ModelView):
    column_list = ['id', 'user_id', 'planet_id']
    form_columns = ['user_id', 'planet_id']

def setup_admin(app):
    app.secret_key = os.environ.get('FLASK_APP_KEY', 'sample key')
    app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
    admin = Admin(app, name='4Geeks Admin', template_mode='bootstrap3')

    admin.add_view(UserAdminView(User, db.session))
    admin.add_view(CharacterAdminView(Character, db.session))
    admin.add_view(PlanetAdminView(Planet, db.session))
    admin.add_view(FavoriteCharacterView(FavoriteCharacter, db.session))
    admin.add_view(FavoritePlanetView(FavoritePlanet, db.session))