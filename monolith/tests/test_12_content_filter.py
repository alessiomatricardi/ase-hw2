import unittest
from monolith import app
from monolith.database import Message_Recipient, db, Message, User
from monolith.message_logic import MessageLogic 
import datetime


class TestContentFilter(unittest.TestCase):


    def test_rendering_content_filter(self):

        msg_logic   = MessageLogic()
        tested_app  = app.test_client()

        with app.app_context():

            # login with user 4
            data = { 'email' : 'prova4@mail.com' , 'password' : 'prova123' } 
            response = tested_app.post(
                "/login", 
                data = data , 
                content_type='application/x-www-form-urlencoded',
                follow_redirects=True
                )
            assert b'Hi Barbara' in response.data

            #create a bad message from user 4 to user 2
            message                 = Message()
            message.sender_id       = 4
            message.content         = 'I like boobs'
            message.is_sent         = True
            message.is_delivered    = False
            message.deliver_time    = datetime.datetime.strptime("2021-11-30T15:45", '%Y-%m-%dT%H:%M')

            # send message in db
            message = msg_logic.create_new_message(message)

            message_recipient = Message_Recipient()
            message_recipient.id = 14 # create recipients for the previously insterted message
            message_recipient.recipient_id = 2

            # send message_rec in db 
            result = msg_logic.create_new_message_recipient(message_recipient)




            # activate filter for user 4
            db.session.query(User).filter(User.id == 4).update({'content_filter_enabled': True})
            db.session.commit()


            # user 4 accesses to message pending 
            # with filtered content
            
            response = tested_app.get('/bottlebox/pending', content_type = 'html/text', follow_redirects = True)
            assert b'I like boobs' not in response.data
            assert b'I like *****' in response.data

            response = tested_app.get('/messages/pending/14', content_type = 'html/text', follow_redirects = True)
            assert b'I like boobs' not in response.data
            assert b'I like *****' in response.data

            # deliver bad message
            db.session.query(Message).filter(Message.id == 14).update({'is_delivered': 1})
            db.session.commit()

            
            # user 4 access to message delivered 
            # with filter content

            response = tested_app.get('/bottlebox/delivered', content_type = 'html/text', follow_redirects = True)
            assert b'I like boobs' not in response.data
            #print(response.data)
            assert b'I like *****' in response.data
            
            response = tested_app.get('/messages/delivered/14', content_type = 'html/text', follow_redirects = True)
            assert b'I like boobs' not in response.data
            assert b'I like *****' in response.data

        

            # logout from user 4
            response = tested_app.get('/logout', content_type = 'html/text', follow_redirects = True)
            assert b'Hi Anonymous' in response.data

            # login with user 2
            data = { 'email' : 'prova@mail.com' , 'password' : 'prova123' } 
            response = tested_app.post(
                "/login", 
                data = data , 
                content_type='application/x-www-form-urlencoded',
                follow_redirects=True
                )
            assert b'Hi Alessio' in response.data


            # activate filter for user 2
            db.session.query(User).filter(User.id == 2).update({'content_filter_enabled': True})
            db.session.commit()


            # user 2 accesses to message received 
            # with filtered content
            response = tested_app.get('/bottlebox/received', content_type = 'html/text', follow_redirects = True)
            assert b'I like boobs' not in response.data
            
            response = tested_app.get('/messages/received/14', content_type = 'html/text', follow_redirects = True)
            assert b'I like boobs' not in response.data
        
