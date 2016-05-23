#! /usr/bin/env python
from __future__ import print_function
import httplib2

import sys, os
sys.path.insert(0, os.path.abspath('..'))
import pygame, pygbutton
from pygame.locals import *
from virtualKeyboard import VirtualKeyboard
from Popup import Popup


import email

from apiclient import discovery
import oauth2client
from oauth2client import client
from oauth2client import tools
from apiclient import errors

from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes

import base64
import send
import time
import scan
import printCups
import pdfkit





"""----------------------GMAIL functions----------------------------"""
try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

SCOPES = 'https://www.googleapis.com/auth/gmail.modify'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Gmail API Python Quickstart'

def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'gmail-python-quickstart.json')

    store = oauth2client.file.Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        print('Storing credentials to ' + credential_path)
    return credentials

"""Get a list of Messages from the user's mailbox.
"""

def ListMessagesMatchingQuery(service, user_id, query=''):
    """List all Messages of the user's mailbox matching the query.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        query: String used to filter messages returned.
        Eg.- 'from:user@some_domain.com' for Messages from a particular sender.

    Returns:
        List of Messages that match the criteria of the query. Note that the
        returned list contains Message IDs, you must use get with the
        appropriate ID to get the details of a Message.
    """
    try:
        response = service.users().messages().list(userId=user_id,
                                               q=query).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId=user_id, q=query,
                                         pageToken=page_token).execute()
            messages.extend(response['messages'])

        return messages

    except errors.HttpError, error:
        print('An error occurred: %s' % error)


def ListMessagesWithLabels(service, user_id, label_ids=[]):
    """List all Messages of the user's mailbox with label_ids applied.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        label_ids: Only return Messages with these labelIds applied.

    Returns:
        List of Messages that have all required Labels applied. Note that the
        returned list contains Message IDs, you must use get with the
        appropriate id to get the details of a Message.
    """
    try:
        response = service.users().messages().list(userId=user_id,
                                               labelIds=label_ids).execute()
        messages = []
        if 'messages' in response:
            messages.extend(response['messages'])

        while 'nextPageToken' in response:
            page_token = response['nextPageToken']
            response = service.users().messages().list(userId=user_id,
                                                 labelIds=label_ids,
                                                 pageToken=page_token).execute()
            messages.extend(response['messages'])

        return messages

    except errors.HttpError, error:
        print('An error occurred: %s' % error)

"""Get Message with given ID.
"""

def GetMessage(service, user_id, msg_id):
    """Get a Message with given ID.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
            can be used to indicate the authenticated user.
        msg_id: The ID of the Message required.

    Returns:
        A Message.
    """
    try:
        #take out format='raw' if don't want base64
        message = service.users().messages().get(userId=user_id, id=msg_id, format='raw').execute()

        print('Message snippet: %s' % message['snippet'])

        return message
    except errors.HttpError, error:
        print('An error occurred: %s' % error)


def GetMimeMessage(service, user_id, msg_id):
    """Get a Message and use it to create a MIME Message.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        msg_id: The ID of the Message required.

    Returns:
        A MIME Message, consisting of data from Message.
    """
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id,
                                             format='raw').execute()

        #print('Message snippet: %s' % message['snippet'])
            

        msg_str = base64.urlsafe_b64decode(message['raw'].encode('ASCII'))

       

        mime_msg = email.message_from_string(msg_str)

        return mime_msg
    
    except errors.HttpError, error:
        print('An error occurred: %s' % error)

def GetRawMessageHtml(service, user_id, msg_id):
    """Get a Message and use it to create a MIME Message.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        msg_id: The ID of the Message required.

    Returns:
        An HTML Message as a string, consisting of data from Message.
    """
    try:
        message = service.users().messages().get(userId=user_id, id=msg_id,
                                             format='full').execute()

        #print('Message snippet: %s' % message['snippet'])
        text = ""
        
        payload = message['payload']['parts']
        
        for each in payload:
            if each['mimeType'] == 'text/html':
                text += each['body']['data']

        msg_str = base64.urlsafe_b64decode(text.encode('ASCII'))

        return msg_str
        
            
    
    except errors.HttpError, error:
        print('An error occurred: %s' % error)

def CreateMessageWithAttachment(
    sender, to, subject, message_text, file_dir, filename):
    """Create a message for an email.

    Args:
        sender: Email address of the sender.
        to: Email address of the receiver.
        subject: The subject of the email message.
        message_text: The text of the email message.
        file_dir: The directory containing the file to be attached.
        filename: The name of the file to be attached.

    Returns:
        An object containing a base64url encoded email object.
    """
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    msg = MIMEText(message_text)
    message.attach(msg)

    path = os.path.join(file_dir, filename)
    content_type, encoding = mimetypes.guess_type(path)

    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)
    if main_type == 'text':
        fp = open(path, 'rb')
        msg = MIMEText(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == 'image':
        fp = open(path, 'rb')
        msg = MIMEImage(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == 'audio':
        fp = open(path, 'rb')
        msg = MIMEAudio(fp.read(), _subtype=sub_type)
        fp.close()
    else:
        fp = open(path, 'rb')
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
        fp.close()

    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(msg)

    return {'raw': base64.urlsafe_b64encode(message.as_string())}

def SendMessage(service, user_id, message):
    """Send an email message.

    Args:
        service: Authorized Gmail API service instance.
        user_id: User's email address. The special value "me"
        can be used to indicate the authenticated user.
        message: Message to be sent.

    Returns:
        Sent Message.
    """
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError, error:
        print('An error occurred: %s' % error)


"""----------------------Misc functions----------------------------"""
    

def getPayload(inputMessage):
    
    text = ""
    for part in inputMessage.walk():
        #each part is either non-multipart, or another multi-part message
        #that contains more parts... tree message
        if part.get_content_type()== 'text/html':
            text += part.get_payload()

    return text

def decodeBase64(data):
    """Decode base64, padding being optional
    Parameters:
        data: Base 64 data as a string

    Returns the decoded byte string
    """
    missing_padding = 4 - len(data)%4
    if missing_padding:
        data += b'='* missing_padding

    return base64.decodestring(data)

def writeFile(data, name, ext):
    fileName = name + "." + ext
    with open(fileName, 'wb') as f:
        f.write(data)
        f.close()
    return


"""----------------------Main Method----------------------------"""
def main():
    """Shows basic usage of the Gmail API.

    Creates a Gmail API service object and outputs a list of label names
    of the user's Gmail account.
    """
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http)

    results = service.users().labels().list(userId='me').execute()
    labels = results.get('labels', [])

    FPS = 30
    WINDOWWIDTH = 480
    WINDOWHEIGHT = 320

    WHITE = (255, 255, 255)
    RED = (255, 0, 0)
    BLUE = (0, 0, 255)
    GREEN = (0, 255, 0)
    BLACK = (0, 0, 0)
    LIGHTGREEN = (53, 230, 97)
    LIGHTBLUE = (53, 156, 230)
    LIGHTORANGE = (242, 109, 19)

    windowBgColor = WHITE

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURFACE = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('PLUTO')

    myfont = pygame.font.Font(None, 30)
    label = myfont.render("<-- Enter address", 1, BLACK)

    buttonEnterEmail  = pygbutton.PygButton((10, 10, 100, 80), 'Enter Email', bgcolor=LIGHTORANGE)
    buttonScan = pygbutton.PygButton((10, 100, 225, 210), 'Scan and Send', bgcolor=LIGHTGREEN, font=myfont)
    buttonReceive = pygbutton.PygButton((245, 100, 225, 210), 'Receive and Print', bgcolor=LIGHTBLUE, font=myfont)
    buttonPrintICR = pygbutton.PygButton((370, 10, 100, 80), 'Letterhead', bgcolor=RED)
    winBgButtons = (buttonEnterEmail, buttonScan, buttonReceive, buttonPrintICR)

    allButtons = winBgButtons

    userinput = ""

    while True:
        for event in pygame.event.get(): # event handling loop
            
            if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
                pygame.quit()
                sys.exit()

            if 'click' in buttonReceive.handleEvent(event): #User called for printing of file
                
                idenListCurr = ListMessagesMatchingQuery(service, 'me', 'in:inbox')
                idenListLast = None
        
                #if idenListLast != idenListCurr: #to be used in future with inbox functionality

                    #msgList = [] #should be a way to do this where only add the new messages
                    
                    #for each in idenListCurr:
                        #iden = each[u'id']
                        #mimeMsg = GetMimeMessage(service, 'me', iden)
                        
                        #msgList.append(mimeMsg)

                    #idenListLast = idenListCurr
                

                #displayInterface(msgList)
                htmlMsg = GetRawMessageHtml(service, 'me', idenListCurr[0][u'id'])
                writeFile(htmlMsg, "temp", "html")
                    
                try:
                    pdfkit.from_file("/home/pi/git/PlutoTest/temp.html", "temp.pdf") #change to your directory
                except IOError:
                    pass
            
                popup = Popup(DISPLAYSURFACE)
                tempInput = popup.run("Your message will print")
                printCups.executePrint("/home/pi/git/PlutoTest/temp.pdf") #change to your directory
                os.remove("/home/pi/git/PlutoTest/temp.pdf") #change to your directory
                os.remove("/home/pi/git/PlutoTest/temp.html") #change to your directory
                time.sleep(5)
                        
            if 'click' in buttonScan.handleEvent(event):#user called for scanning and sending of file
                scan.executeScan("temp")
                
                message = CreateMessageWithAttachment("example.pluto.email@gmail.com", userinput, "Hello from Pluto!", "Enjoy!",
                                                      "/home/pi/git/PlutoTest/", "temp.png") #change to your email, directory
                SendMessage(service, 'me', message)
                
                
                os.remove("/home/pi/git/PlutoTest/temp.png") #change to your directory
                popup = Popup(DISPLAYSURFACE)
                tempInput = popup.run("Your message has been sent")
                print("sent")
                time.sleep(5)
                
            if 'click' in buttonEnterEmail.handleEvent(event): #user called to enter e-mail address
                vkeybd = VirtualKeyboard(DISPLAYSURFACE)
                tempInput = vkeybd.run("...")
                if tempInput != "...":
                    userinput = tempInput
                label = myfont.render("To: " + userinput, 1, BLACK)
                
            if 'click' in buttonPrintICR.handleEvent(event): #user called to print letterhead
                popup = Popup(DISPLAYSURFACE)
                tempInput = popup.run("The letterhead will print")
                printCups.executePrint("/home/pi/git/PlutoTest/DemoPaper.png") #change to your directory
                time.sleep(5)


        DISPLAYSURFACE.fill(windowBgColor)

        for b in allButtons:
            b.draw(DISPLAYSURFACE)

        # draw the text onto the surface
        DISPLAYSURFACE.blit(label, (120, 35, 350, 80))

        pygame.display.update()
        FPSCLOCK.tick(FPS)


    


if __name__ == '__main__':
    main()
