#!/usr/bin/env python

"""
# Send email to yourself!
Usage:
sendclipboard [-t email] (sends the clipboard to the default address in MAIL_TO or to the specified addresses)
sendclipboard -g (open GTK window to choose the emails and change the clipboard text)
"""

import pygtk
pygtk.require('2.0')
 
import gtk
import sys
import os
import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEBase import MIMEBase
from email.MIMEText import MIMEText
from email.Utils import COMMASPACE, formatdate
from email import Encoders
import argparse
 
MAIL_FROM = 'test@test.com'
MAIL_TO = ['test@test.com']



def send_mail(send_from, send_to, subject, text, files=[], server="localhost", port=25):
    assert type(send_to)==list
    assert type(files)==list

    # We must choose the body charset manually
    for body_charset in 'US-ASCII', 'ISO-8859-1', 'UTF-8':
        try:
            text.encode(body_charset)
        except UnicodeError:
            pass
        else:
            break

    msg = MIMEMultipart()
    msg['From'] = send_from
    msg['To'] = COMMASPACE.join(send_to)
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject

    msg.attach( MIMEText(text.encode(body_charset), 'plain', body_charset) )

    for f in files:
        part = MIMEBase('application', "octet-stream")
        part.set_payload( open(f,"rb").read() )
        Encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment; filename="%s"' % os.path.basename(f))
        msg.attach(part)

    smtp = smtplib.SMTP(host=server, port=port, local_hostname='cked.es')
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()

def getArguments():
    argparser = argparse.ArgumentParser(description='Send files to an address')
    argparser.add_argument('-t','--to',
                        metavar='<MAIL_ADDRESS>',
                        nargs='+',
                        dest='mail_to',
                        action='store',
                        type=str,
                        default=MAIL_TO,
                        help='Send to email')
    argparser.add_argument('-g','--gtk',
                        dest='gtk',
                        action='store_true',
                        help='Open GTK Window')
    args = argparser.parse_args()
    return args

def getClipboard():
    clipboard = gtk.clipboard_get()
    clipboard_text = clipboard.wait_for_text()
    return clipboard_text

def sendclipboard(mail_to, clipboard_text):
    send_mail(MAIL_FROM, 
          mail_to, 
          'Send Clipboard', 
          clipboard_text, 
          files=[],
          server='127.0.0.1',
          port='25')
 
class Application():
 
    def __init__(self, mail_to_init):
        self.window = gtk.Window()
        self.window.set_title("Mail Clipboard")
        self.mail_to_init = mail_to_init
 
        self.create_widgets()
        self.connect_signals()
 
        self.window.show_all()
        gtk.main()
 
 
    def create_widgets(self):
        self.vbox = gtk.VBox(spacing=10)
 
        self.hbox_1 = gtk.HBox(spacing=10)
        self.label = gtk.Label("Send clipboard to:")
        self.hbox_1.pack_start(self.label)
        self.mail_to = gtk.Entry()
        self.mail_to.set_text(','.join(self.mail_to_init))
        self.hbox_1.pack_start(self.mail_to)

        """
        self.hbox_clipboard = gtk.HBox(spacing=10)
        self.clipboard = gtk.Entry()
        self.clipboard.set_text(getClipboard())
        self.hbox_clipboard.pack_start(self.clipboard)
        """
        self.hbox_clipboard = gtk.HBox(spacing=10)
        self.clipboard = gtk.TextBuffer()
        self.clipboard.set_text(getClipboard())
        self.textview = gtk.TextView(buffer=self.clipboard)
        self.textview.set_editable(True)
        self.hbox_clipboard.pack_start(self.textview)

        self.hbox_2 = gtk.HBox(spacing=10)
        self.button_ok = gtk.Button("OK")
        self.hbox_2.pack_start(self.button_ok)
        self.button_exit = gtk.Button("Exit")
        self.hbox_2.pack_start(self.button_exit)
 
        self.vbox.pack_start(self.hbox_1)
        self.vbox.pack_start(self.hbox_2)
        self.vbox.pack_start(self.hbox_clipboard)
 
        self.window.add(self.vbox)
 
 
    def connect_signals(self):
        self.button_ok.connect("clicked", self.callback_ok)
        self.button_exit.connect("clicked", self.callback_exit)
        self.mail_to.connect("activate", self.callback_ok)
 
 
    def callback_ok(self, widget, callback_data=None):
        mail_to_text = self.mail_to.get_text()
        mail_to = mail_to_text.replace(';',',').replace(' ',',').split(',')
        #clipboard_text = self.clipboard.get_text()
        clipboard_text = self.clipboard.get_text(*self.clipboard.get_bounds())
        sendclipboard(mail_to, clipboard_text)
        gtk.main_quit()
 
 
    def callback_exit(self, widget, callback_data=None):
        gtk.main_quit()
 
 
if __name__ == "__main__":
    args = getArguments()
    
    mail_to = args.mail_to
    if args.gtk:
        app = Application(mail_to)
    else:
        sendclipboard(mail_to, getClipboard())
