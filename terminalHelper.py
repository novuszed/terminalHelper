import email
import smtplib
from pprint import pprint
import sys
import imaplib
import getpass
import datetime
import mailbox
from email.header import decode_header
from email.parser import HeaderParser
import re
__author__ = 'zihaozhu'
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
def fetchSubjectToFrom(M,folder,uid):
    M.select(folder)
    print(M, folder, uid)

    typ, msg_data = M.fetch(uid, '(RFC822)')
    for response_part in msg_data:
        if isinstance(response_part, tuple):
            msg = email.message_from_string(response_part[1].decode("utf-8"))
            for header in [ 'subject', 'to', 'from' ]:
                print('%-8s: %s' % (header.upper(), msg[header]))

def checkMailBox(M):
    typ, mail = M.list()
    for box in mail:
        mailbox_name=parse_list_response(box)
        "List of Inboxes: "
        M.select(mailbox_name)
        stat, data = M.select(mailbox_name)
        if(stat=="OK"):
            print(mailbox_name+" contains "+str(bytes.decode(data[0]))+" mail")
            #need to fix the time to only a week prior
            stats,unseenMail= M.search(None,'(UNSEEN)','(SINCE 05-May-2016)')
            #print(unseenMail)
            unseenMail=unseenMail[0].split()
            print("There are "+str(len(unseenMail))+" unseen mail.")
            if(len(unseenMail)==0):
                continue
            for mail in unseenMail:
                fetchSubjectToFrom(M,mailbox_name,mail)
M = imaplib.IMAP4_SSL('imap.gmail.com')
try:
    M.login('zihaozhu@utexas.edu',getpass.getpass())
except imaplib.IMAP4.error:
    print("Login failed")
    exit(1)

checkMailBox(M)

