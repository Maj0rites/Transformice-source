# -*- coding: utf-8 -*-
import re, struct, random, time

__author__ = "Duxo"
__date__ = "$7/06/2017 13:10:00$"

class Utility:
    def __init__(self, client, server):
        self.client = client
        self.isCommand = False
        self.lastObjID = 0
        self.canExplosion = False
        self.isFireworks = False
        self.conjX = 0
        self.conjY = 0

    def spawnObj(self, objID, posX, posY, angle):
        itemID = random.randint(100, 999)
        objID = int(objID)
        posX = int(posX)
        posY = int(posY)
        data = struct.pack("!ihhhhhbb", itemID, objID, posX, posY, angle, 0, 1, 0)        
        self.client.room.sendAll([5, 20], data)
        self.lastObjID = struct.unpack("!i", data[:4])[0]        

    def removeObj(self):
        self.client.sendPacket([4, 8], struct.pack("!i?", self.lastObjID, True))

    def playerWin(self):
        timeTaken = int((time.time() - (self.client.playerStartTimeMillis if self.client.room.autoRespawn else self.client.room.gameStartTimeMillis)) * 100)
        place = self.client.room.numCompleted
        if place == 0:
            place = place + 1
        self.client.sendPlayerWin(place, timeTaken)

    def buildConj(self):
        if self.isFireworks == True:
            self.client.sendPacket([4, 14], [int(self.conjX), int(self.conjY)])    

    def removeConj(self):
        if self.isFireworks == True:
            self.client.sendPacket([4, 15], [int(self.conjX), int(self.conjY)])

    def newCoordsConj(self):
        self.conjX = random.randint(0, 79)
        self.conjY = random.randint(2, 39)

    def explosionPlayer(self, posX, posY):
        data = struct.pack("!h", int(posX))
        data += "\x00\x842"
        data += struct.pack("!h?", int(posY), True)
        self.client.sendPacket([5, 17], data)
    
    def moreSettings(self, setting):
        if setting == "giveAdmin":
            if not self.client.playerName in self.client.room.adminsRoom:
                self.client.room.adminsRoom.append(self.client.playerName)

        elif setting == "join":
            self.sendMessage("<J>Welcome to #utility!")
            self.consoleChat(1, "", ""+str(self.client.playerName)+" joined the room.")
            self.client.sendPacket([29, 20], "\x00\x00\x1c\x16\x00t<font color=\'#000000\'><p align=\'center\'><b><font size=\'128\' face=\'Soopafresh,Verdana\'>#utility</font></b></p></font>\x00_\x00d\x02X\x00\xc8\x002FP\x00\x00\x00\x00\x00\x01")
            self.client.sendPacket([29, 20], "\x00\x00\x1c{\x00t<font color=\'#000000\'><p align=\'center\'><b><font size=\'128\' face=\'Soopafresh,Verdana\'>#utility</font></b></p></font>\x00i\x00d\x02X\x00\xc8\x002FP\x00\x00\x00\x00\x00\x01")
            self.client.sendPacket([29, 20], "\x00\x00\x1c\xe0\x00t<font color=\'#000000\'><p align=\'center\'><b><font size=\'128\' face=\'Soopafresh,Verdana\'>#utility</font></b></p></font>\x00d\x00_\x02X\x00\xc8\x002FP\x00\x00\x00\x00\x00\x01")
            self.client.sendPacket([29, 20], "\x00\x00\x1dE\x00t<font color=\'#000000\'><p align=\'center\'><b><font size=\'128\' face=\'Soopafresh,Verdana\'>#utility</font></b></p></font>\x00d\x00i\x02X\x00\xc8\x002FP\x00\x00\x00\x00\x00\x01")
            self.client.sendPacket([29, 20], "\xff\xff\xff\xed\x00W<p align=\'center\'><b><font size=\'128\' face=\'Soopafresh,Verdana\'>#utility</font></b></p>\x00d\x00d\x02X\x00\xc8\x002FP\x00\x00\x00\x00\x00\x01")
            self.client.sendPacket([29, 20], "\xff\xff\xff\xf0\x00\x80<p align=\'center\'><a href=\'event:info' target='_blank'><b>?</b></a></p>\x00\x05\x00\x1c\x00\x10\x00\x10\x002FP\x002FPd\x00")
            self.client.sendPacket([29, 20], "\xff\xff\xff\xef\x00><p align=\'center\'><a href=\'event:info\'><b><i>i</i></b></a></p>\x00!\x00\x1c\x00\x10\x00\x10\x002FP\x002FPd\x00")            
    
        elif setting == "removePopups":        
            popupID = [7190, 7291, 7392, 7493, -19]
            for id in popupID:
                self.removePopups(id)        

    def removePopups(self, popupID):
        self.client.sendPacket([29, 22], struct.pack("!i", popupID))
            
    def consoleChat(self, type, username, message):
        for client in self.client.room.clients.values():
            if client.playerName in self.client.room.adminsRoom:                
                if type == 1:
                    prefix = "<font color='#AAAAAA'>Ξ [Utility] "
                elif type == 2:
                    prefix = "<font color='#AAAAAA'>Ξ ["+str(username)+"] "

                elif type == 3:
                    prefix = ""

                message = prefix + message 
                
                client.sendPacket([6, 9], struct.pack("!h", len(message)) + message)

    def sendMessage(self, message):
        self.client.sendPacket([6, 9], struct.pack("!h", len(message)) + message)

    def staffChat(self, username, message):
        for client in self.client.room.clients.values():
            if client.playerName in self.client.room.adminsRoom:
                prefix = "<font color='#00FFFF'>Ξ ["+str(username)+"] "
                client.Utility.sendMessage(prefix + message + "</font>")
    
    def sentCommand(self, command):
        command = command[1:]
        if command == "admins":
            self.consoleChat(2, self.client.playerName, "!" + command)
            admins = ', '.join(self.client.room.adminsRoom)
            self.sendMessage("The current room admins are: "+str(admins)+".")            
            self.isCommand = True

        elif command.startswith("admin "):
            playerName = command.split(" ")[1]
            self.consoleChat(2, self.client.playerName, "!" + command)
            if self.client.playerName in self.client.room.adminsRoom:
                if playerName in self.client.room.adminsRoom:
                    self.sendMessage(""+str(playerName)+" is already an admin.")
                else:
                    self.client.room.adminsRoom.append(playerName)
                    for client in self.client.room.clients.values():
                        client.Utility.sendMessage(""+str(playerName)+" is now an admin.")
            self.isCommand = True

        elif command.startswith("me "):
            message = command.split(" ")[1]
            if not self.client.playerName in self.client.room.playersBan:
                for client in self.client.room.clients.values():
                    client.Utility.sendMessage("<V>*"+str(self.client.playerName)+" <N>"+str(message)+"")
            self.isCommand = True

        elif command.startswith("c "):
            message = command.split(" ")[1]
            self.staffChat(self.client.playerName, message)
            self.isCommand = True

        elif command.startswith("spawn "):
            if self.client.playerName in self.client.room.adminsRoom:
                self.consoleChat(2, self.client.playerName, "!" + command)
                try:
                    objID = command.split(" ")[1]
                except:
                    objID = 0
                try:
                    posX = command.split(" ")[2]
                except:
                    posX = 140
                try:
                    posY = command.split(" ")[3]
                except:
                    posY = 320
                self.spawnObj(objID, posX, posY, 0)
            self.isCommand = True

        elif command == "snow":
            if self.client.playerName in self.client.room.adminsRoom:
                self.consoleChat(2, self.client.playerName, "!" + command)
                self.client.room.sendAll([5, 23], struct.pack("!?h", True, 10))
            self.isCommand = True

        elif command.startswith("snow "):            
            event = command.split(" ")[1]
            if self.client.playerName in self.client.room.adminsRoom:
                self.consoleChat(2, self.client.playerName, "!" + command)
                if event == "on":
                    self.client.room.sendAll([5, 23], struct.pack("!?h", True, 10))
                elif event == "off":
                    self.client.room.sendAll([5, 23], struct.pack("!?h", False, 10))
            self.isCommand = True

        elif command.startswith("time "):
            time = command.split(" ")[1]
            if self.client.playerName in self.client.room.adminsRoom:
                self.consoleChat(2, self.client.playerName, "!" + command)
                try:
                    if time > 32767:
                        time = 32767
                    self.client.room.sendAll([5, 22], struct.pack("!H", int(time)))
                except:
                    time = 32767
                    self.client.room.sendAll([5, 22], struct.pack("!H", int(time)))
            self.isCommand = True

        elif command.startswith("ban "):
            playerName = command.split(" ")[1]
            if self.client.playerName in self.client.room.adminsRoom:
                self.consoleChat(2, self.client.playerName, "!" + command)
                if not playerName in self.client.room.playersBan:
                    if playerName in self.client.room.adminsRoom:
                        self.sendMessage(""+str(playerName)+" is an admin and can't be banned.")
                    else:
                        self.client.room.playersBan.append(playerName)
                        for client in self.client.room.clients.values():
                            client.Utility.sendMessage("<R>"+str(playerName)+" has been banned.")            
                else:
                    self.sendMessage(""+str(playerName)+" is already banned.")
            self.isCommand = True

        elif command.startswith("unban "):
            playerName = command.split(" ")[1]
            self.consoleChat(2, self.client.playerName, "!" + command)
            if self.client.playerName in self.client.room.adminsRoom:
                if playerName in self.client.room.playersBan:
                    num = None
                    for i, x in enumerate(self.client.room.playersBan):
                        if x == playerName:
                            num = i
                    del self.client.room.playersBan[num]
                    for client in self.client.room.clients.values():
                        client.Utility.sendMessage(""+str(playerName)+" has been unbanned.")
            self.isCommand = True

        elif command == "banlist":
            if self.client.playerName in self.client.room.adminsRoom:
                self.consoleChat(2, self.client.playerName, "!" + command)
                banList = ' '.join(self.client.room.playersBan)
                self.sendMessage(str(banList))
            self.isCommand = True

        elif command == "vampire":
            if self.client.playerName in self.client.room.adminsRoom:
                self.consoleChat(2, self.client.playerName, "!" + command)
                self.client.room.sendAll([8, 66], struct.pack("!i", self.client.playerCode))
            self.isCommand = True

        elif command.startswith("vampire "):
            event = command.split(" ")[1]
            if self.client.playerName in self.client.room.adminsRoom:
                self.consoleChat(2, self.client.playerName, "!" + command)
                if not event in ["me", "all"]:
                    for client in self.client.room.clients.values():
                        if event == client.playerName:
                            client.room.sendAll([8, 66], struct.pack("!i", client.playerCode))
                elif event == "me":
                    self.client.room.sendAll([8, 66], struct.pack("!i", self.client.playerCode))
                elif event == "all":
                    for client in self.client.room.clients.values():
                        client.room.sendAll([8, 66], struct.pack("!i", client.playerCode))
            self.isCommand = True

        elif command == "name":
            if self.client.playerName in self.client.room.adminsRoom:
                self.consoleChat(2, self.client.playerName, "!" + command)
                color = "000000"
                data = struct.pack("!i", self.client.playerCode)
                data += struct.pack("!i", int(color, 16))
                self.client.room.sendAll([29, 4], data)
            self.isCommand = True
                
        elif command.startswith("name "):
            event = command.split(" ")[1]
            try:
                color = command.split(" ")[2]
            except:
                color = "000000"                
            if self.client.playerName in self.client.room.adminsRoom:
                self.consoleChat(2, self.client.playerName, "!" + command)
                if not event in ["me", "all"]:
                    for client in self.client.room.clients.values():
                        if event == client.playerName:
                            data = struct.pack("!i", client.playerCode)
                            data += struct.pack("!i", int(color, 16))
                            client.room.sendAll([29, 4], data)                                                        
                elif event == "me":
                    data = struct.pack("!i", self.client.playerCode)
                    data += struct.pack("!i", int(color, 16))
                    self.client.room.sendAll([29, 4], data)
                elif event == "all":
                    for client in self.client.room.clients.values():
                        data = struct.pack("!i", client.playerCode)
                        data += struct.pack("!i", int(color, 16))
                        client.room.sendAll([29, 4], data)                    
            self.isCommand = True

        elif command.startswith("tp "):
            if self.client.playerName in self.client.room.adminsRoom:
                self.consoleChat(2, self.client.playerName, "!" + command)
                try:
                    posX = command.split(" ")[1]
                    posY = command.split(" ")[2]
                    if posX == "all":
                        try:
                            posX = command.split(" ")[2]
                            posY = command.split(" ")[3]
                            for client in self.client.room.clients.values():
                                client.room.sendAll([8, 3], struct.pack("!hhih", int(posX), int(posY), 0, 0))
                        except:
                            pass
                    elif not posX.isdigit():
                        try:
                            playerName = command.split(" ")[1]
                            posX = command.split(" ")[2]
                            posY = command.split(" ")[3]
                            for client in self.client.room.clients.values():
                                if playerName == client.playerName:
                                    client.room.sendAll([8, 3], struct.pack("!hhih", int(posX), int(posY), 0, 0))                                    
                        except:
                            pass
                    elif posX and posY.isdigit():
                        self.client.room.sendAll([8, 3], struct.pack("!hhih", int(posX), int(posY), 0, 0))
                except:
                    pass
            self.isCommand = True

        elif command == "meep":
            self.consoleChat(2, self.client.playerName, "!" + command)
            if self.client.playerName in self.client.room.adminsRoom:
                self.client.sendPacket([8, 39], "\x01")
            self.isCommand = True

        elif command.startswith("meep "):
            event = command.split(" ")[1]
            self.consoleChat(2, self.client.playerName, "!" + command)
            if self.client.playerName in self.client.room.adminsRoom:
                if event == "me":
                    self.client.sendPacket([8, 39], "\x01")
                elif event == "all":
                    for client in self.client.room.clients.values():
                        client.sendPacket([8, 39], "\x01")
                elif not event in ["me", "all"]:
                    for client in self.client.room.clients.values():
                        if event == client.playerName:
                            client.sendPacket([8, 39], "\x01")
            self.isCommand = True

        elif command == "disco":
            self.consoleChat(2, self.client.playerName, "!" + command)
            if self.client.playerName in self.client.room.adminsRoom:
                if self.client.room.discoRoom == False:
                    self.client.room.discoRoom = True
                    for client in self.client.room.clients.values():
                        client.reactorDisco()
                elif self.client.room.discoRoom == True:
                    self.client.room.discoRoom = False
            self.isCommand = True

                    
      

        elif command == "ffa":
            self.consoleChat(2, self.client.playerName, "!" + command)
            if self.client.playerName in self.client.room.adminsRoom:
                self.client.isFFA = True
                self.client.room.bindKeyBoard(self.client.playerName, 40, False, self.client.isFFA)
            self.isCommand = True

        elif command.startswith("ffa "):
            event = command.split(" ")[1]
            self.consoleChat(2, self.client.playerName, "!" + command)
            if self.client.playerName in self.client.room.adminsRoom:
                if event == "me":
                    self.client.isFFA = True
                    self.client.room.bindKeyBoard(self.client.playerName, 40, False, self.client.isFFA)
                elif event == "on":
                    for client in self.client.room.clients.values():
                        client.isFFA = True
                        client.room.bindKeyBoard(client.playerName, 40, False, client.isFFA)
                elif event == "off":
                    for client in self.client.room.clients.values():
                        client.isFFA = False
                if not event in ["me", "on", "off"]:
                    for client in self.client.room.clients.values():
                        if event == client.playerName:
                            client.isFFA = True
                            client.room.bindKeyBoard(client.playerName, 40, False, client.isFFA)
            self.isCommand = True

        elif command == "shaman":
            self.consoleChat(2, self.client.playerName, "!" + command)
            if self.client.playerName in self.client.room.adminsRoom:
                self.client.sendShamanCode(self.client.playerCode, 0)
            self.isCommand = True

        elif command.startswith("shaman "):
            event = command.split(" ")[1]
            self.consoleChat(2, self.client.playerName, "!" + command)
            if self.client.playerName in self.client.room.adminsRoom:
                if event == "me":
                    self.client.sendShamanCode(self.client.playerCode, 0)
                elif event == "all":
                    for client in self.client.room.clients.values():
                        client.sendShamanCode(client.playerCode, 0)
                if not event in ["me", "all"]:
                    for client in self.client.room.clients.values():
                        if event == client.playerName:
                            client.sendShamanCode(client.playerCode, 0)
            self.isCommand = True

        elif command in ["np", "map"]:
            self.consoleChat(2, self.client.playerName, "!" + command)
            if self.client.playerName in self.client.room.adminsRoom:
                self.client.room.mapChange()
            self.isCommand = True

        elif command.startswith("np ") or command.startswith("map "):
            mapCode = command.split(" ")[1]
            self.consoleChat(2, self.client.playerName, "!" + command)
            if self.client.playerName in self.client.room.adminsRoom:
                try:
                    self.client.room.forceNextMap = mapCode
                    self.client.room.mapChange()
                except:
                    pass
            self.isCommand = True

        elif command in ["kill", "mort"]:
            self.consoleChat(2, self.client.playerName, "!" + command)
            if not self.client.isDead:
                self.client.isDead = True
                if not self.client.room.noAutoScore: self.client.playerScore += 1
                self.client.sendPlayerDied()
            self.isCommand = True

        elif command.startswith("kill ") or command.startswith("mort "):
            event = command.split(" ")[1]
            self.consoleChat(2, self.client.playerName, "!" + command)
            if event == "me":
                if not self.client.isDead:
                    self.client.isDead = True
                    if not self.client.room.noAutoScore: self.client.playerScore += 1
                    self.client.sendPlayerDied()
            elif event == "all":
                if self.client.playerName in self.client.room.adminsRoom:
                    for client in self.client.room.clients.values():
                        if not client.isDead:
                            client.isDead = True
                            if not client.room.noAutoScore: client.playerScore += 1
                            client.sendPlayerDied()
            if not event in ["me", "all"]:
                if self.client.playerName in self.client.room.adminsRoom:
                    for client in self.client.room.clients.values():
                        if event == client.playerName:
                            if not client.isDead:
                                client.isDead = True
                                if not client.room.noAutoScore: client.playerScore += 1
                                client.sendPlayerDied()
            self.isCommand = True

        elif command == "cheese":
            self.consoleChat(2, self.client.playerName, "!" + command)
            if self.client.playerName in self.client.room.adminsRoom:
                self.client.room.sendAll([5, 19], [self.client.playerCode])
            self.isCommand = True

        elif command.startswith("cheese "):
            event = command.split(" ")[1]
            self.consoleChat(2, self.client.playerName, "!" + command)
            if self.client.playerName in self.client.room.adminsRoom:
                if event == "me":
                    self.client.room.sendAll([5, 19], [self.client.playerCode])
                elif event == "all":
                    for client in self.client.room.clients.values():
                        client.room.sendAll([5, 19], [client.playerCode])
                if not event in ["me", "all"]:
                    for client in self.client.room.clients.values():
                        if event == client.playerName:
                            client.room.sendAll([5, 19], [client.playerCode])
            self.isCommand = True

        elif command == "explosion":
            self.consoleChat(2, self.client.playerName, "!" + command)
            if self.client.playerName in self.client.room.adminsRoom:
                if self.canExplosion == False:
                    self.client.isExplosion = True
                    self.client.room.bindMouse(self.client.playerName, self.client.isExplosion)
                    self.canExplosion = True
                elif self.canExplosion == True:
                    self.client.isExplosion = False
                    self.client.room.bindMouse(self.client.playerName, self.client.isExplosion)
                    self.canExplosion = False
            self.isCommand = True

        elif command.startswith("explosion "):
            event = command.split(" ")[1]
            self.consoleChat(2, self.client.playerName, "!" + command)
            if self.client.playerName in self.client.room.adminsRoom:
                if event == "me":
                    if self.canExplosion == False:
                        self.client.isExplosion = True
                        self.client.room.bindMouse(self.client.playerName, self.client.isExplosion)
                        self.canExplosion = True
                    elif self.canExplosion == True:
                        self.client.isExplosion = False
                        self.client.room.bindMouse(self.client.playerName, self.client.isExplosion)
                        self.canExplosion = False
                elif event in ["all", "on"]:
                    for client in self.client.room.clients.values():
                        if client.Utility.canExplosion == False:
                            client.isExplosion = True
                            client.room.bindMouse(client.playerName, client.isExplosion)
                            client.Utility.canExplosion = True
                        elif client.Utility.canExplosion == True:
                            client.isExplosion = False
                            client.room.bindMouse(client.playerName, client.isExplosion)
                            client.Utility.canExplosion = False
                elif event == "off":
                    for client in self.client.room.clients.values():
                        client.isExplosion = False
                        client.room.bindMouse(client.playerName, client.isExplosion)
                        client.Utility.canExplosion = False
                if not event in ["me", "all", "on", "off"]:
                    for client in self.client.room.clients.values():
                        if event == client.playerName:
                            if client.Utility.canExplosion == False:
                                client.isExplosion = True
                                client.room.bindMouse(client.playerName, client.isExplosion)
                                client.Utility.canExplosion = True
                            elif client.Utility.canExplosion == True:
                                client.isExplosion = False
                                client.room.bindMouse(client.playerName, client.isExplosion)
                                client.Utility.canExplosion = False
            self.isCommand = True
            
        elif command == "pw":
            self.consoleChat(2, self.client.playerName, "!" + command)
            if self.client.playerName in self.client.room.adminsRoom:
                self.client.room.roomPassword = ""
                for client in self.client.room.clients.values():
                    client.Utility.sendMessage("The room's password has been removed.")
            self.isCommand = True

        elif command.startswith("pw "):
            password = command.split(" ")[1]
            self.consoleChat(2, self.client.playerName, "!" + command)
            if self.client.playerName in self.client.room.adminsRoom:
                self.client.room.roomPassword = str(password)                
                for client in self.client.room.clients.values():
                    client.Utility.sendMessage(""+str(self.client.playerName)+" has set a room password.")
                self.sendMessage("The room's password has been set to: "+str(password)+"")
            self.isCommand = True

        elif command == "win":
            self.consoleChat(2, self.client.playerName, "!" + command)
            if self.client.playerName in self.client.room.adminsRoom:
                self.playerWin()
                self.client.isDead = True
            self.isCommand = True

        elif command.startswith("win "):
            event = command.split(" ")[1]
            self.consoleChat(2, self.client.playerName, "!" + command)
            if self.client.playerName in self.client.room.adminsRoom:
                if event == "me":
                    self.playerWin()
                    self.client.isDead = True
                elif event == "all":
                    for client in self.client.room.clients.values():
                        client.Utility.playerWin()
                        client.isDead = True
                if not event in ["me", "all"]:
                    for client in self.client.room.clients.values():
                        if event == client.playerName:
                            client.Utility.playerWin()
                            client.isDead = True
            self.isCommand = True

        elif command == "fireworks":
            self.consoleChat(2, self.client.playerName, "!" + command)
            if self.client.playerName in self.client.room.adminsRoom:            
                for client in self.client.room.clients.values():
                    client.Utility.isFireworks = True
                    client.fireworksUtility()
            self.isCommand = True

        elif command.startswith("fireworks "):
            event = command.split(" ")[1]
            self.consoleChat(2, self.client.playerName, "!" + command)
            if self.client.playerName in self.client.room.adminsRoom:
                if event == "off":
                    for client in self.client.room.clients.values():
                        client.Utility.isFireworks = False
                elif event != "off":
                    for client in self.client.room.clients.values():
                        client.Utility.isFireworks = True
                        client.fireworksUtility()
            self.isCommand = True
