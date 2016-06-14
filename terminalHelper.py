import email
import smtplib
from pprint import pprint
import sys
import imaplib
import getpass
import smtplib
from email.mime.text import MIMEText
from bs4 import BeautifulSoup as bs
import datetime
import mailbox
from email.header import decode_header
from email.parser import HeaderParser
import email.message
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from email.mime.base import MIMEBase
import re
import time
__author__ = 'zihaozhu'

def read(M,mailbox,e_id):
    M.select(mailbox)
    M.store(e_id,'+FLAGS','\Seen')
def delete(M,mailbox,e_id):
    M.select(mailbox)
    M.store(e_id,'+FLAGS','\\Deleted')
def writeMsg(receiver, message, subject):
    fromAddr = "zihaozhu@utexas.edu"
    toAddr = receiver
    msg = MIMEMultipart()
    msg['From']=fromAddr
    msg['To']=toAddr
    #test subject
    msg['Subject'] = subject
    body = message
    msg.attach(MIMEText(body,'plain'))

    ##for attachments
    """
    filename = "name of the file"
    attachment = open("path to the file", "rb")
    part = MIMEBase('application','octet-stream')
    part.set_payload((attachment).read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition',"attachment; filename=%s" %filename)

    msg.attach(part)
"""
    server = smtplib.SMTP('smtp.gmail.com',587)
    server.starttls()
    server.login(fromAddr,getpass.getpass())
    text = msg.as_string()
    server.sendmail(fromAddr, toAddr,text)
    server.quit()

def process_mailBox(M):
    #search for matching messages, this case: none
    rv, data = M.search(None,"ALL")
    for message in data[0].split():
        typ, data = M.fetch(message, '(RFC822')
        print('Message %s\n%s\n'%(message,data[0][1]))

def parse_list_response(line):
    list_response_pattern = re.compile(b'\((?P<flags>.*?)\) "(?P<delimiter>.*)" (?P<name>.*)')
    flags, delimiter, mailbox_name = list_response_pattern.match(line).groups()
    #mailbox_name=bytes(mailbox_name.strip('"'))
    #print(bytes.decode(mailbox_name))
    #print(type(bytes.decode(mailbox_name)))
    return (bytes.decode(mailbox_name))
def fetchBody(M, folder,uid):
    M.select(folder,readonly=True)
    typ, msg = M.fetch(uid,'(RFC822)')
    emailBody= msg[0][1]
    mail = email.message_from_string(emailBody.decode(encoding='UTF-8'))
    print(mail.get_payload()[0].get_payload())
def fetchSubjectToFrom(M,folder,uid):
    M.select(folder,readonly=True)
    #print(M, folder, uid)

    typ, msg_data = M.fetch(uid, '(RFC822)')
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            msg = email.message_from_string(response_part[1].decode("utf-8"))
            for header in [ 'subject', 'to', 'from' ]:
                print('%-8s: %s' % (header.upper(), msg[header]))
def printFolders(M):
    typ, mail = M.list()
    for box in mail:
        print(parse_list_response(box))
def checkMailBox(M,date):
    typ, mail = M.list()
    print("List of available mailboxes: ")
    for box in mail:
        mailbox_name=parse_list_response(box)
        M.select(mailbox_name)
        stat, data = M.select(mailbox_name)
        if(stat=="OK"):
            #print(mailbox_name+" contains "+str(bytes.decode(data[0]))+" mail")
            stats,unseenMail= M.search(None,'(UNSEEN)','(SINCE %s)'% date)
            unseenMail=unseenMail[0].split()
            if(len(unseenMail)==0):
                continue
            print("There are "+str(len(unseenMail))+" unseen mail in %s" %mailbox_name)
            for i in unseenMail:
                print("E_Id: %s" %i)
                fetchSubjectToFrom(M,mailbox_name,i)

                #fetchBody(M,mailbox_name,mail)

def main():

    print("#########################################")
    print("Enter password: ")
    M = imaplib.IMAP4_SSL('imap.gmail.com')
    try:
        M.login('zihaozhu@utexas.edu',getpass.getpass())
    except imaplib.IMAP4.error:
        print("Login failed")
        exit(1)
    print("#########################################")
    while(True):
        print(" [C] - to check mail")
        print(" [W] - to write mail")
        print(" [Q] - to exit program")
        print(" [B] - to check body text")
        print(" [MB] - to check mail boxes")
        print(" [R] - mark as read")
        print(" [D] - delete message")
        i=input("Enter your choice: ")
        if i=='Q':
            exit(1)
        elif i=='W':
            receiver = input("Enter recipient you would like to email: ")
            subject = input("Enter the subject: ")
            message = input("Enter the message you would like to send: " )

            choice = input("Are you sure this is what you want to send? Subject: %s Message: %s: [Y/N]" %(subject,message))
            if(choice=='N'):
                continue
            else:
                writeMsg(receiver,message,subject)
        elif i=='C':
            date = input("Enter date of email to check in this format DD-Mth-YYY: ")
            checkMailBox(M,date)
        elif i=="B":
            folder = input("Enter folder name exactly as you see it: ")
            E_id = input("Enter email ID: ")
            fetchBody(M,folder,E_id)
        elif i=="MB":
            printFolders(M)
        elif i=='R':
            mailbox = input("Mailbox it belongs to: ")
            e_id = input("Enter email ID to be marked as read: ")
            read(M,mailbox,e_id)
        elif i=='D':
            mailbox = input("Mailbox it belongs to: ")
            e_id = input("Enter email ID to be marked as read: ")
            delete(M,mailbox,e_id)

main()