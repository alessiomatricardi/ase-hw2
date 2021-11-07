import re
import unittest
import datetime
from unittest import result
from warnings import resetwarnings
import os
from monolith import image
from monolith.image import Image
import shutil
#from PIL import Image as Img

#from flask import app 
from flask.signals import message_flashed
from monolith import message_logic
# from flask_wtf.recaptcha.widgets import RECAPTCHA_SCRIPT
from monolith.database import Message_Recipient, User, db, Message
from monolith.message_logic import MessageLogic
from monolith import app as tested_app

m = MessageLogic()

class TestMessage(unittest.TestCase):

    def __init__(self, *args, **kw):
        super(TestMessage, self).__init__(*args, **kw)

    def test_get_list_of_recipients_email(self):
        with tested_app.app_context():
            result = m.get_list_of_recipients_email(1) # retrieve all the users that user 1 can write to
            expected_result = ("prova@mail.com", "prova@mail.com")
            self.assertEqual(result[0], expected_result) # test that only the 1st recipient is correct

    def test_validate_message_fields(self):
        with tested_app.app_context():
            message = Message()
            message.sender_id = 1
            message.content = "Ciao! sono l'utente 1"
            message.deliver_time = datetime.datetime.strptime("2021-11-01T15:45", '%Y-%m-%dT%H:%M')
            result = m.validate_message_fields(message)
            expected_result = True
            self.assertEqual(result, expected_result) # this test should pass

            #
            # TODO add test when the blacklist is implemented
            #

    def test_create_new_message(self):
        with tested_app.app_context():
            message = Message()
            message.sender_id = 1
            message.content = "Ciao! sono l'utente 1"
            message.deliver_time = datetime.datetime.strptime("2021-11-01T15:45", '%Y-%m-%dT%H:%M')
            result = m.create_new_message(message)
            expected_result = db.session.query(Message).filter(Message.id == 8).first() # 8 because there should be 7 default messages in the db
            self.assertEqual(expected_result.sender_id, result['sender_id'])
            self.assertEqual(expected_result.content, result['content'])
            self.assertEqual(expected_result.deliver_time, result['deliver_time'])

    def test_email_to_id(self):
        with tested_app.app_context():
            result = m.email_to_id("prova@mail.com")
            self.assertEqual(2, result)

    def test_create_new_message_recipient(self):
        with tested_app.app_context():
            message_recipient = Message_Recipient()
            message_recipient.id = 8 # create recipients for the previously insterted message
            # message_recipient.read_time = datetime.datetime(2020, 10, 6) # TODO it should be better to set a null vallue, but if done an error occurr
            message_recipient.recipient_id = 2
            result = m.create_new_message_recipient(message_recipient)
            expected_result = db.session.query(Message_Recipient).filter(Message_Recipient.id == 8).first()
            self.assertEqual(expected_result.id, result['id'])
            self.assertEqual(expected_result.recipient_id, result['recipient_id'])
            self.assertEqual(expected_result.is_read, False)

    
    def test_send_bottle(self):
        with tested_app.app_context():
            message = db.session.query(Message).filter(Message.id == 8).first()
            result = m.send_bottle(message)
            expected_result = db.session.query(Message).filter(Message.id == 8).first().is_sent
            self.assertEqual(expected_result, result)


    def test_is_my_message(self):
        with tested_app.app_context():
            # verify that user 4 has rights on message 5 (he should NOT have them)
            result = m.is_my_message(4,5)
            expected_result = []
            self.assertEqual(expected_result, result)
        
            #  # verify that user 4 has rights on message 6 (he should have them)
            result = m.is_my_message(4,6)
            expected_result = db.session.query(Message).filter(Message.id == 6).all()
            self.assertEqual(expected_result, result)


    def test_control_file(self):
        with tested_app.app_context():
            # test that a correct image has been received.
            # NB: to simply perform the test, it has been assumed that an image is represented by an object in the following format
            image = Image()
            image.filename = "IMAGE_NAME.jpg"
            
            # check that the name is correctly returned (so that image.py file is tested)
            self.assertEqual("IMAGE_NAME.jpg", image.get_filename())

            # the content of the file is meaningful for the check

            result = m.control_file(image)
            self.assertEqual(True, result) # we expect that the image is recognized as good

            image.filename = ''
            result = m.control_file(image)
            self.assertEqual(False, result) # we expect that the image is recognized as bad


    def test_control_rights_on_image(self):
        with tested_app.app_context():
            # check that the user 4 has rights to see image (even if not present) of message 1
            # it shouldn't have the privileges, so the check should fail
            result = m.control_rights_on_image(1, 4)
            self.assertEqual(False, result)

            # user 4 has sent message 4, so it should have the privileges to see the image
            result = m.control_rights_on_image(4, 4)
            self.assertEqual(True, result)

            # user 4 has received message 6, so it should have the privileges to see the image
            result = m.control_rights_on_image(6, 4)
            self.assertEqual(True, result)


    def test_delete_message(self):
        with tested_app.app_context():
            
            # create a message to delete
            message = Message()
            message.sender_id = 5
            message.content = 'Marry Christmast'
            message.is_sent = True
            message.is_delivered  = False
            message.deliver_time = datetime.datetime(2021,12,25,7,40)
            db.session.add(message)
            db.session.commit()
            message_recipient = Message_Recipient()
            message_recipient.id = db.session.query(Message).all()[-1].id
            message_recipient.recipient_id = 4
            message_recipient.is_read = False
            db.session.add(message_recipient)
            db.session.commit()

            # retrieve the message from db (so to verify that it has correctly been created)
            message_to_delete = db.session.query(Message).filter(Message.id == message.id).first()
            result = m.delete_message(message_to_delete)
            expected_result = True # the user 5 has 22 points (> 10), so the message can be deleted
            self.assertEqual(expected_result, result)
            

            # create another message with an image to be deleted
            message = Message()
            message.sender_id = 5
            message.content = 'Marry Christmast x2'
            message.is_sent = True
            message.is_delivered  = False
            message.deliver_time = datetime.datetime(2021,12,25,7,40)
            message.image = 'FAKE IMAGE NAME'
            db.session.add(message)
            db.session.commit()
            message_recipient = Message_Recipient()
            id = db.session.query(Message).all()[-1].id
            message_recipient.id = id
            message_recipient.recipient_id = 4
            message_recipient.is_read = False
            db.session.add(message_recipient)
            db.session.commit()

            # create the directory
            os.mkdir(os.path.join(os.getcwd(),'monolith','static','attached',str(id)))
            
            # retrieve the message from db (so to verify that it has correctly been created)
            message_to_delete = db.session.query(Message).filter(Message.id == message.id).first()
            result = m.delete_message(message_to_delete)
            expected_result = True # the user 5 has 12 points (> 10), so the message can be deleted
            self.assertEqual(expected_result, result)


            # create another message to delete
            message = Message()
            message.sender_id = 5
            message.content = 'Marry Christmast x3'
            message.is_sent = True
            message.is_delivered  = False
            message.deliver_time = datetime.datetime(2021,12,25,7,40)
            db.session.add(message)
            db.session.commit()
            message_recipient = Message_Recipient()
            message_recipient.id = db.session.query(Message).all()[-1].id
            message_recipient.recipient_id = 4
            message_recipient.is_read = False
            db.session.add(message_recipient)
            db.session.commit()

            
            # retrieve the message from db (so to verify that it has correctly been created)
            message_to_delete = db.session.query(Message).filter(Message.id == message.id).first()
            result = m.delete_message(message_to_delete)
            expected_result = False # this time user 5 will not have enough points to delete the message
            self.assertEqual(expected_result, result)




    #
    # 
    # TODO test the update of is_delivered attribute
    # TODO test the sending of emails
    #
    #

    def test_rendering(self):
        app = tested_app.test_client()

        # check that if the user is not logged, the rendered page is the login page
        response = app.get("/new_message", content_type='html/text', follow_redirects=True)
        assert b'<h1 class="h3 mb-3 fw-normal">Please sign in</h1>' in response.data

        response = app.get("/delete_message/1", content_type='html/text', follow_redirects=True)
        assert b'<h1 class="h3 mb-3 fw-normal">Please sign in</h1>' in response.data
        

        # do the login otherwise the sending of a new message can't take place
        data = { 'email' : 'prova4@mail.com' , 'password' : 'prova123' } 
        response = app.post(
            "/login", 
            data = data , 
            content_type='application/x-www-form-urlencoded',
            follow_redirects=True
            )

        # test that the new_message.html page is correctly rendered when "New message in a bottle" is clicked on the homepage
        response = app.get("/new_message", content_type='html/text', follow_redirects=True)
        self.assertEqual(response.status_code, 200)

        # test that the new_message.html page is correctly rendered when "Write to" is clicked on the recipient list page
        # in particular, the check verifies that the recipient passed in the URI is checked when the page is rendered
        response = app.get("/new_message?single_recipient=prova@mail.com", content_type='html/text', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        assert b'<input type="checkbox" name="recipients" value=prova@mail.com checked>' in response.data

        # test that if no recipients are selected the page is re-rendered with a warning
        dataForm1 = { 
            'content' : 'ININFLUENT FOR THE TEST',
            'deliver_time' : '2025-11-01T15:45',
            'submit': 'Send bottle'
        }
        response = app.post("/new_message", data = dataForm1, content_type='application/x-www-form-urlencoded', follow_redirects=True)
        #self.assertEqual(400, response.status_code)
        assert b'<p>Please select at least 1 recipient</p>' in response.data

        # test that the message is saved as a draft, so the rendered page is the index.html
        dataForm2 = { 
            'content' : 'ININFLUENT FOR THE TEST' ,
            'deliver_time' : "2021-11-01T15:45",
            'recipients': 'prova@mail.com',
            'submit': 'Save draft'
        }
        response = app.post("/new_message", data = dataForm2, content_type='application/x-www-form-urlencoded', follow_redirects=True)
        assert b'Hi Barbara!' in response.data 

        # test that the message is sent correctly, so the rendered page is the index.html
        dataForm3 = { 
            'content' : 'ININFLUENT FOR THE TEST' ,
            'deliver_time' : "2021-11-25T15:45",
            'recipients': 'prova@mail.com',
            'submit': 'Send bottle'
        }
        response = app.post("/new_message", data = dataForm3, content_type='application/x-www-form-urlencoded', follow_redirects=True)
        assert b'Hi Barbara!' in response.data 


        # a user wants to delete a message but passing an incorrect URI
        response = app.get("/delete_message/INCORRECT", content_type='html/text', follow_redirects=True)
        self.assertEqual(404, response.status_code)

        # remove a non existing message
        response = app.get("/delete_message/20", content_type='html/text', follow_redirects=True)
        self.assertEqual(404, response.status_code)
        
        # user 4 delete the previously sent message (it has 15 points, so he can do it)
        response = app.get(f'/delete_message/{11}', content_type='html/text', follow_redirects=True)
        assert b'Hi Barbara!' in response.data # the rendered page is the homepage

        # add another message to the db
        dataForm4 = { 
            'content' : 'ININFLUENT FOR THE TEST' ,
            'deliver_time' : "2021-11-25T15:45",
            'recipients': 'prova@mail.com',
            'submit': 'Send bottle'
        }
        app.post("/new_message", data = dataForm4, content_type='application/x-www-form-urlencoded', follow_redirects=True)

        # user 4 cannot delete a message because it has no suffcient points
        response = app.get(f'/delete_message/{11}', content_type='html/text', follow_redirects=True)
        assert b'Not enough points to delete a message' in response.data
        


        # test that if the /new_message is called by passing the msg_id argument, the new_message.html is rendered
        # also with a non-empty form.content field
        response = app.get('/new_message?msg_id=6', content_type='html/text', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        expected_result = b'Sent by Carlo Neri' # not all the string has been inserted
        assert expected_result in response.data 

        
        # test that if the /new_message is called by passing a wrong msg_id argument, the new_message.html is rendered
        # with an empty form.content field
        response = app.get('/new_message?msg_id=4', content_type='html/text', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        # assert b'<textarea id="content" name="content" required=""></textarea>' in response.data
        
        #
        # TODO verify why the previous test doesn't work
        #


        """    
        # try to send a message with an incorrect image

        # first, a fake image is created
        directory = os.path.join(os.getcwd(),'monolith','static','attached', '4')
        os.mkdir(directory)
        f = open(directory + "/prova.png","w+")
        f.close()
        
        with Image.open(directory + "/prova.png") as im:

            dataForm5 = { 
                'content' : 'Message with a valid image' ,
                'deliver_time' : "2021-12-18T15:45",
                'recipients': 'prova5@mail.com',
                'attach_image': im,
                'submit': 'Send bottle'
            }

            response = app.post("/new_message", data = dataForm5, content_type='application/x-www-form-urlencoded', follow_redirects=True)
            print(response.data)
            assert b'Insert an image with extention: .png , .jpg, .jpeg, .gif' in response.data 
            
        # remove the image from the server
        directory = os.path.join(os.getcwd(), 'monolith', 'static', 'attached', '4')
        shutil.rmtree(directory, ignore_errors=True) # remove the directory and its content

        
        image2 = Image() # image with filename = ''
        image2.filename = 'image.png'
       
        dataForm5 = { 
            'content' : 'Message with a valid image' ,
            'deliver_time' : "2021-12-18T15:45",
            'recipients': 'prova5@mail.com',
            'attach_image': image2,
            'submit': 'Send bottle'
        }
        response = app.post("/new_message", data = dataForm5, content_type='application/x-www-form-urlencoded', follow_redirects=True)
        print(response.data)
        assert b'Insert an image with extention: .png , .jpg, .jpeg, .gif' in response.data 
        

        # try to send a message with an incorrect image
        image3 = Image() # image with filename = ''
        image3.filename = 'IMG_NON_VALIDA'
        
        dataForm6 = { 
            'content' : 'Message with a non-valid image' ,
            'deliver_time' : "2021-12-18T15:45",
            'recipients': 'prova5@mail.com',
            'attach_image': image3,
            'submit': 'Send bottle'
        }
        response = app.post("/new_message", data = dataForm6, content_type='application/x-www-form-urlencoded', follow_redirects=True)
        print(response.data)
        assert b'Insert an image with extention: .png , .jpg, .jpeg, .gif' in response.data
        """

        # test that a user cannot see an image
        response = app.get('/show/1/prova.png', content_type='html/text', follow_redirects=True)
        self.assertEqual(403, response.status_code)

        # create a fake image to perform the test
        os.mkdir(os.path.join(os.getcwd(),'monolith','static','attached', '4'))
        f = open(os.path.join(os.getcwd(),'monolith','static','attached', '4') + "/prova.png","w+")
        f.close()

        # test that a user can see an image
        response = app.get('/show/4/prova.png', content_type='html/text', follow_redirects=True)
        expected_result = b'' # it is an empty image
        self.assertEqual(expected_result, response.data)

        # remove the image from the server
        directory = os.path.join(os.getcwd(), 'monolith', 'static', 'attached', '4')
        shutil.rmtree(directory, ignore_errors=True) # remove the directory and its content



        # test that neither a get or post request are done
        try:
            response = app.put("/new_message")
        except RuntimeError as e:
            self.assertEqual('This should not happen!', e)
        self.assertEqual(response.status_code, 405)
