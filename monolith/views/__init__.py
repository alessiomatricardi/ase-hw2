from .auth import auth
from .home import home
from .users import users
from .list import list
from .bottlebox import bottlebox
from .unregister import unregister
from .messages import messages

blueprints = [home, auth, users, messages, list, bottlebox, unregister]

#
# TODO remember to add the new blueprint in creating a new view
#