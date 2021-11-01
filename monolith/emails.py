import smtplib, ssl

port = 587  # For starttls
smtp_server = "smtp.gmail.com"

sender_email = "squad04ase@gmail.com"
password = "Squad-04-ASE"


def send_email(recipient, msg):    
    # Try to log in to server and send email
    try:
        server = smtplib.SMTP(smtp_server,port)
        server.starttls() # Secure the connection
        server.login(sender_email, password)
        server.sendmail(sender_email, recipient, msg)
    except Exception as e:
        # Print any error messages to stdout
        print(e)
    finally:
        server.quit() 