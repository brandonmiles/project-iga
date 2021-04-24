import smtplib
import ssl

port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = "IntelligentGrader@gmail.com"
password = 'TRzvtuqeLyD8rN'


def send_email(receiver_email, grade, feedback):
    message = f"""\
Subject: Your essay has been graded

Your essay has now been graded. Here are the results:
Grade: {grade}
Feedback: {feedback}
"""
    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, password)
        server.sendmail(sender_email, receiver_email, message)


# send_email('jcg170530@utdallas.edu')
