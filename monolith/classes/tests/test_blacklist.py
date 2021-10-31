import unittest
from monolith.blacklist_logic import BlacklistLogic
from monolith import app as tested_app
from monolith.database import Blacklist, db

from sqlalchemy.sql import and_

bl = BlacklistLogic()

class TestBlacklist(unittest.TestCase):
    def test_blacklist_rendering(self):
        app = tested_app.test_client()
        data2 = { 'email' : 'prova2@mail.com' , 'password' : 'prova123' } 
        response = app.post(
            "/login", 
            data = data2 , 
            content_type='application/x-www-form-urlencoded',
            follow_redirects=True
            )
        assert b'Hi Damiano' in response.data 

        # block unexisting user
        response = app.get("/block_user?target=10", 
            content_type='html/text',
            follow_redirects=True
            )
        self.assertEqual(response.status_code, 400)
        assert b'You are trying to block a non existing user!' in response.data
 
        # block existing user 6
        response = app.get("/block_user?target=6", content_type='html/text', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        assert b'Carlo Neri' in response.data

        # block again same user
        response = app.get("/block_user?target=6", content_type='html/text', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        assert b'Carlo Neri' in response.data

        # check rendering

        # check that the recipients list is now empty (user 3 has blocked everyone)
        response = app.get("/recipients_list", content_type='html/text', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        assert b'Carlo Neri' not in response.data
        assert b'Alessio Bianchi' not in response.data
        
        # logging out
        response = app.get("/logout", content_type='html/text', follow_redirects=True)
        assert b'Hi Anonymous' in response.data

        # trying to access the blacklist while not being logged in
        response = app.get("/blacklist", content_type='html/text', follow_redirects=True)
        assert b'<label for="email">email</label>' in response.data 

        # trying to block a user while not being logged in
        response = app.get("/block_user?target=6", content_type='html/text', follow_redirects=True)
        assert b'<label for="email">email</label>' in response.data 

        # restoring the db to the previous form
        with tested_app.app_context():

            db.session.query(Blacklist).where(and_(Blacklist.blocking_user_id==3,Blacklist.blocked_user_id==6)).delete()
            db.session.commit()
            result = db.session.query(Blacklist).where(Blacklist.blocking_user_id == 3)
            result = [(ob.blocking_user_id,ob.blocked_user_id) for ob in result]
            expected_result = [ (3,2) ]
            self.assertEqual(result,expected_result)


    def test_blacklist_logic(self):

        # testing blacklist logic
        with tested_app.app_context():

            # retrieving a non existing user
            result = bl.check_existing_user(10)
            self.assertEqual(result, False)

            # retrieving existing user
            result = bl.check_existing_user(6)
            self.assertEqual(result,True)    

            # adding a blacklist istance to db
            bl.add_to_blackist(3,6)      
            result = db.session.query(Blacklist).where(Blacklist.blocking_user_id == 3)
            result = [(ob.blocking_user_id,ob.blocked_user_id) for ob in result]
            expected_result = [ (3,2),(3,6) ]
            self.assertEqual(result,expected_result)

            # removing the previously created istance from blacklist table
            db.session.query(Blacklist).where(and_(Blacklist.blocking_user_id==3,Blacklist.blocked_user_id==6)).delete()
            db.session.commit()
 
            # checking the istances on database
            result = db.session.query(Blacklist).where(Blacklist.blocking_user_id == 3)
            result = [(ob.blocking_user_id,ob.blocked_user_id) for ob in result]
            expected_result = [ (3,2) ]
            self.assertEqual(result,expected_result)