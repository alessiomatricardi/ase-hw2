import unittest
from monolith.bottlebox_logic import BottleBoxLogic, DraftLogic
from monolith import app
import datetime
import shutil
import os
from monolith.database import db, Message

class TestDrafts(unittest.TestCase):

    def test_draft_rendering(self):
        tested_app = app.test_client()

        # checking that accessing all bottleboxes redirects to the login page if not already logged in
        response = tested_app.get("/bottlebox/pending", content_type='html/text', follow_redirects=True)
        assert b'<label for="email">E-mail</label>' in response.data 

        response = tested_app.get("/bottlebox/delivered", content_type='html/text', follow_redirects=True)
        assert b'<label for="email">E-mail</label>' in response.data 

        response = tested_app.get("/bottlebox/received", content_type='html/text', follow_redirects=True)
        assert b'<label for="email">E-mail</label>' in response.data 

        response = tested_app.get("/bottlebox/drafts", content_type='html/text', follow_redirects=True)
        assert b'<label for="email">E-mail</label>' in response.data 

        # logging in
        data1 = { 'email' : 'prova4@mail.com' , 'password' : 'prova123' }
        response = tested_app.post("/login", data = data1 , content_type='application/x-www-form-urlencoded', follow_redirects=True)
        assert b'Hi Barbara' in response.data 

        # checking the rendering of drafts bottlebox
        response = tested_app.get("/bottlebox/drafts", content_type='html/text', follow_redirects=True)
        assert b'Drafts Bottlebox' in response.data 

        # accessing to a wrong message route (with a wrong label != pending, received, drafts, delivered) returns an error
        response = tested_app.get("/messages/not_a_label/1", content_type='html/text', follow_redirects=True)
        self.assertEqual(response.status_code,404)

        # only drafts allow POST method
        response = tested_app.post("/messages/pending/1", content_type='html/text', follow_redirects=True)
        self.assertEqual(response.status_code,404) 

        # accessing a message as received if you're not a recipient returns an error
        response = tested_app.get("/messages/received/2", content_type='html/text', follow_redirects=True)
        self.assertEqual(response.status_code,404) 

        # accessing to a owned draft
        response = tested_app.get("/messages/draft/10", content_type='html/text', follow_redirects=True)
        assert b'value="prova@mail.com"' in response.data
        assert b'ININFLUENT FOR THE TEST' in response.data
        assert b'Send bottle' in response.data
        assert b'Save draft changes' in response.data
        assert b'Delete draft' in response.data
        self.assertEqual(response.status_code,200)

        # blocking recipient of draft
        # block existing user 2
        data_block = {'user_id': 2}
        response = tested_app.post(
            "/block",
            data=data_block,
            content_type='application/x-www-form-urlencoded',
            follow_redirects=True
            )
        self.assertEqual(response.status_code, 200)
        assert b'Alessio Bianchi' in response.data

        # reopening the draft and checking that the blocked user is removed from draft recipients
        response = tested_app.get("/messages/draft/10", content_type='html/text', follow_redirects=True)
        assert b'The user prova@mail.com is no longer avaiable' in response.data
        assert b'<input type="checkbox" name="recipients" value=prova@mail.com checked>' not in response.data
        self.assertEqual(response.status_code,200)

        # unblocking blocked user to add it to draft recipients
        data_block = {'user_id': 3}
        response = tested_app.post(
            "/unblock",
            data=data_block,
            content_type='application/x-www-form-urlencoded',
            follow_redirects=True
            )
        self.assertEqual(response.status_code, 200)
        assert b'Damiano Rossi' not in response.data

        # modify recipient, deliver_time, content of draft
        new_deliver_time = datetime.datetime(2025,4,24,17,16).strftime("%Y-%m-%dT%H:%M")
        data_modifying_draft = { 
            'content' : 'NEW MODIFIED TEXT' ,
            'deliver_time' : new_deliver_time,
            'recipients': 'prova2@mail.com',
            'submit': 'Save draft changes',
        }
        response = tested_app.post(
            "/messages/draft/10",
            data=data_modifying_draft,
            content_type='multipart/form-data',
            follow_redirects=True
            )
        self.assertEqual(response.status_code, 200)
        assert b'Hi Barbara' in response.data

        # reopening draft to check changes
        response = tested_app.get("/messages/draft/10", content_type='html/text', follow_redirects=True)
        assert b'value="prova2@mail.com"' in response.data
        assert b'NEW MODIFIED TEXT' in response.data
        assert b'value="2025-04-24T17:16"' in response.data
        assert b'Send bottle' in response.data
        assert b'Save draft changes' in response.data
        assert b'Delete draft' in response.data
        self.assertEqual(response.status_code,200)

        # unblocking recipient
        data_block = {'user_id': 2}
        response = tested_app.post(
            "/unblock",
            data=data_block,
            content_type='application/x-www-form-urlencoded',
            follow_redirects=True
            )
        self.assertEqual(response.status_code, 200)
        assert b'Alessio Bianchi' not in response.data

        # logout
        response = tested_app.get('/logout', content_type = 'html/text', follow_redirects = True)
        assert b'Hi Anonymous' in response.data

        # logging into another account which doesn't own the previous accessed draft
        data1 = { 'email' : 'prova2@mail.com' , 'password' : 'prova123' }
        response = tested_app.post("/login", data = data1 , content_type='application/x-www-form-urlencoded', follow_redirects=True)
        assert b'Hi Damiano' in response.data 

        # accessing to a non-existing draft
        response = tested_app.get("/messages/draft/15", content_type='html/text', follow_redirects=True)
        self.assertEqual(response.status_code,404) 

        # accessing to a non-owned draft
        response = tested_app.get("/messages/draft/10", content_type='html/text', follow_redirects=True)
        self.assertEqual(response.status_code,404) 

        # modifying non-existing draft
        response = tested_app.post("/messages/draft/15", content_type='html/text', follow_redirects=True)
        self.assertEqual(response.status_code,404) 

        # modifying non-owned draft
        response = tested_app.post("/messages/draft/10", content_type='html/text', follow_redirects=True)
        self.assertEqual(response.status_code,404)

        # opening non-owned pending message
        response = tested_app.get('/messages/pending/5',content_type='html/text', follow_redirects=True)
        self.assertEqual(response.status_code,404)

        # opening non-existing pending message
        response = tested_app.get('/messages/pending/100',content_type='html/text', follow_redirects=True)
        self.assertEqual(response.status_code,404)

        # opening non-owned delivered message
        response = tested_app.get('/messages/delivered/4',content_type='html/text', follow_redirects=True)
        self.assertEqual(response.status_code,404)

        # opening non-existing delivered message
        response = tested_app.get('/messages/delivered/100',content_type='html/text', follow_redirects=True)
        self.assertEqual(response.status_code,404)

        # logout
        response = tested_app.get('/logout', content_type = 'html/text', follow_redirects = True)
        assert b'Hi Anonymous' in response.data

        # logging again into Barbara to send draft
        data1 = { 'email' : 'prova4@mail.com' , 'password' : 'prova123' }
        response = tested_app.post("/login", data = data1 , content_type='application/x-www-form-urlencoded', follow_redirects=True)
        assert b'Hi Barbara' in response.data 

        # send draft to Alessio and Damiano
        data_send = {
            'content' : 'NEW MODIFIED TEXT' ,
            'deliver_time' : new_deliver_time,
            'recipients': ['prova@mail.com','prova2@mail.com'],
            'submit': 'Send bottle'
        }
        response = tested_app.post(
            "/messages/draft/10",
            data=data_send,
            content_type='multipart/form-data',
            follow_redirects=True
            )
        self.assertEqual(response.status_code, 200)
        assert b'Hi Barbara' in response.data 

        # Done on 9/11
        # create draft without image
        data_send = { 
            'content' : 'NEW DRAFT' ,
            'deliver_time' : "2021-12-18T15:45",
            'recipients': 'prova@mail.com',
            'attach_image': '',
            'submit': 'Save draft'
        }

        response = tested_app.post("/messages/new", data = data_send, content_type='multipart/form-data', follow_redirects=True)
        assert b'My message in a bottle' in response.data
        self.assertEqual(200, response.status_code)

        # reopening draft 
        response = tested_app.get("/messages/draft/14", content_type='html/text', follow_redirects=True)
        assert b'value="prova@mail.com"' in response.data
        assert b'NEW DRAFT' in response.data
        assert b'value="2021-12-18T15:45"' in response.data
        assert b'Send bottle' in response.data
        assert b'Save draft changes' in response.data
        assert b'Delete draft' in response.data
        self.assertEqual(response.status_code,200)

        # adding test image to draft
        source_path = os.path.join(os.getcwd(), 'monolith', 'static', 'tests')
        target_path = os.path.join(os.getcwd(), 'monolith', 'static', 'attachments', '14')
        '''if not os.path.exists(target_path):
            try:'''
        os.makedirs(target_path)
        '''    except Exception:
                return False'''

        filename = 'test_image.jpg'
        shutil.copyfile(os.path.join(source_path, filename), os.path.join(target_path, filename))
        # setting the image field to the proper file
        with app.app_context():
            db.session.query(Message).filter(Message.id == 14).update({'image': filename})
            db.session.commit()

            message =  db.session.query(Message).filter(Message.id == 14).first()
            self.assertEqual(message.image, filename)
            self.assertEqual(message.content, 'NEW DRAFT')
            
        
        # delete draft with image
        data_send = {
            'content' : 'NEW MODIFIED TEXT' ,
            'deliver_time' : new_deliver_time,
            'recipients': 'prova@mail.com',
            'submit': 'Delete draft'
        }
        response = tested_app.post(
            "/messages/draft/14",
            data=data_send,
            content_type='multipart/form-data',
            follow_redirects=True
            )
        self.assertEqual(response.status_code, 200)
        #assert b'Hi Barbara' in response.data 