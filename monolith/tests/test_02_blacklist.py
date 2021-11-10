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

        data_block = { 'user_id' : 10 }

        # block unexisting user
        response = app.post(
            "/block",
            data=data_block,
            content_type='application/x-www-form-urlencoded',
            follow_redirects=True
            )
        self.assertEqual(response.status_code, 400)
        assert b'You are trying to block a non existing user!' in response.data

        data_block = {'user_id': 5}

        # block existing user 6
        response = app.post(
            "/block",
            data=data_block,
            content_type='application/x-www-form-urlencoded',
            follow_redirects=True
            )
        self.assertEqual(response.status_code, 200)
        assert b'Carlo Neri' in response.data

        # block again same user
        response = app.post(
            "/block",
            data=data_block,
            content_type='application/x-www-form-urlencoded',
            follow_redirects=True
            )
        self.assertEqual(response.status_code, 200)
        assert b'Carlo Neri' in response.data

        # block request with a missing value for user_id
        data_block = {'user_id': ''}
        response = app.post(
            "/block",
            data=data_block,
            content_type='application/x-www-form-urlencoded',
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 400)

        # block request with a wrong format for user_id
        data_block = {'user_id': 'not_an_integer'}
        response = app.post(
            "/block",
            data=data_block,
            content_type='application/x-www-form-urlencoded',
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 400)

        # unblock request with a missing value for user_id
        data_unblock = {'user_id': ''}
        response = app.post(
            "/unblock",
            data=data_unblock,
            content_type='application/x-www-form-urlencoded',
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 400)

        # unblock request with a wrong format for user_id
        data_unblock = {'user_id': 'not_an_integer'}
        response = app.post(
            "/unblock",
            data=data_unblock,
            content_type='application/x-www-form-urlencoded',
            follow_redirects=True
        )
        self.assertEqual(response.status_code, 400)

        # check rendering

        # check that the recipients list is now empty (user 3 has blocked everyone)
        response = app.get("/users", content_type='html/text', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        assert b'Carlo Neri' not in response.data
        assert b'Alessio Bianchi' not in response.data

        # logging out
        response = app.get("/logout", content_type='html/text', follow_redirects=True)
        assert b'Hi Anonymous' in response.data

        # trying to access the blacklist while not being logged in
        response = app.get("/blacklist", content_type='html/text', follow_redirects=True)
        assert b'<input class="form-control" id="email" name="email" placeholder="nothing" required type="email" value="">' in response.data

        # trying to block a user while not being logged in
        data_block = {'user_id': 6}

        # block existing user 6
        response = app.post("/block",
                            data=data_block,
                            content_type='application/x-www-form-urlencoded',
                            follow_redirects=True)
        assert b'<input class="form-control" id="email" name="email" placeholder="nothing" required type="email" value="">' in response.data

        # restoring the db to the previous form
        with tested_app.app_context():

            db.session.query(Blacklist).where(and_(Blacklist.blocking_user_id==3,Blacklist.blocked_user_id==5)).delete()
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
            result = bl.check_existing_user(5)
            self.assertEqual(result,True)

            # adding a blacklist istance to db
            bl.add_to_blackist(3,5)
            result = db.session.query(Blacklist).where(Blacklist.blocking_user_id == 3)
            result = [(ob.blocking_user_id,ob.blocked_user_id) for ob in result]
            expected_result = [ (3,2),(3,5) ]
            self.assertEqual(result,expected_result)

            # removing the previously created istance from blacklist table
            db.session.query(Blacklist).where(and_(Blacklist.blocking_user_id==3,Blacklist.blocked_user_id==5)).delete()
            db.session.commit()

            # checking the istances on database
            result = db.session.query(Blacklist).where(Blacklist.blocking_user_id == 3)
            result = [(ob.blocking_user_id,ob.blocked_user_id) for ob in result]
            expected_result = [ (3,2) ]
            self.assertEqual(result,expected_result)