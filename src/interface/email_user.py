import smtplib
import ssl
import urllib.parse
from cryptography.fernet import Fernet

port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = 'IntelligentGrader@gmail.com'
key = b'lYJzFVOf9A3zGHVVcqgdch3chXf-tkt9ET5bxCmPe7k='
cipher_suite = Fernet(key)
# decrypt password
with open('email_info', 'rb') as file_object:
    for line in file_object:
        encrypted = line
decrypted_bytes = (cipher_suite.decrypt(encrypted))
password = bytes(decrypted_bytes).decode("utf-8") #convert to string


def send_email(receiver_email, date):
    message = f"""\
Subject: Your essay has been graded

Your essay has now been graded. To view the results, click the following link:
http://ec2-23-21-141-182.compute-1.amazonaws.com:5000/results?email={urllib.parse.quote(receiver_email)}&date={urllib.parse.quote(date)}

This essay will be removed from our database in 7 days. At that point, you will no longer be able to view it with the above link.
"""
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)


# send_email('jcg170530@utdallas.edu')
