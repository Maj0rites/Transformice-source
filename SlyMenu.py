#coding: utf-8
import struct, random, time as _time
from twisted.internet import reactor
from utils import Utils

class fullMenu:
    def __init__(self, client, server):
        self.client = client
        self.server = client.server
        self.Cursor = client.Cursor
        currentPage = 1
        
    def sendMenu(self):
        if self.client.privLevel >= 11:
            text = "<a href='event:openPanel'><img src=''></a>"
            self.client.sendAddPopupText(11001, 785, 24, 70, 50, '0000', '0000', 100, str(text))
