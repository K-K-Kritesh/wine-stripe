from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib as smtp
import ssl

class BusinessMailUtils():
    def __init__(self):
        context = ssl.create_default_context()
        self.s = smtp.SMTP(host = 'smtp.gmail.com', port=587)
        self.s.starttls()
        self.s.login("k39478368@gmail.com", "cnzzdxoweheualjc")

    def forgot_password_send_mail(self,message, To, subject, type, url):
        try:
            msg = MIMEMultipart() 
            message = message
            msg['From']="k39478368@gmail.com"
            msg['To']=To
            msg['Subject']=subject
            if type == 'html':
                msg.attach(MIMEText(f"""\{message}"""[3:-1].replace('reseturl',url), 'html'))
            else:
                msg.attach(MIMEText(message, 'plain'))
            self.s.sendmail("k39478368@gmail.com", To, str(msg))
            del msg
            return "SEND_MSG"
        except Exception as e:
            return str(e) 