from .auth import auth
from .home import home
from .users import users
from .messages import messages

blueprints = [home, auth, users, messages]

#
# TODO remember to add the new blueprint in creating a new view
#