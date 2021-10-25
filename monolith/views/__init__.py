from .auth import auth
from .home import home
from .users import users
from .list import list
from .bottlebox import bottlebox
from .unregister import unregister

blueprints = [home, auth, users, list, bottlebox, unregister]
