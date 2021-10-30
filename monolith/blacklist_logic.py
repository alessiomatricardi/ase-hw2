from monolith.database import db, User, Blacklist

class BlacklistLogic:
    
    def __init__(self):
        pass
    
    def check_existing_user(self,id):
        result = db.session.query(User).where(User.id == id)

        if result is None:
            return False
        else: 
            return True

    def add_to_blackist(self,blocking,blocked):
        blacklist = Blacklist()

        blacklist.blocking_user_id = blocking
        blacklist.blocked_user_id = blocked

        db.session.add(blacklist)
        db.session.commit()

        return blacklist

    def retrieving_blacklist(self,current_user_id):

        blacklist = db.session.query(Blacklist).where(Blacklist.blocking_user_id == current_user_id)
        
        return [ob for ob in blacklist]