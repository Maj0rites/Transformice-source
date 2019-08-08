#coding: utf-8
#Imp - Slyvanas
import re, sys, base64, hashlib, time as _time, random as _random

# Modules
from time import gmtime, strftime
from langues import Langues
from utils import Utils
from ByteArray import ByteArray
from Identifiers import Identifiers

# Library
from datetime import datetime

class Commands:
    def __init__(self, client, server):
        self.client = client
        self.server = client.server
        self.Cursor = client.Cursor
        self.currentArgsCount = 0

    def requireNoSouris(self, playerName):
        if not playerName.startswith("*"):
            return True

    def requireArgs(self, argsCount):
        if self.currentArgsCount < argsCount:
            self.client.sendMessage("Invalid arguments.")
            return False

        return True
    
    def requireTribe(self, canUse=False, tribePerm=8):
        if (not(not self.client.tribeName == "" and self.client.room.isTribeHouse and tribePerm != -1 and self.client.tribeRanks[self.client.tribeRank].split("|")[2].split(",") [tribePerm] == "1")) if (argsCount >= 1) else "":
            canUse = True
    
    def parseCommand(self, command):                
        values = command.split(" ")
        Slyvanas = command
        command = values[0].lower()
        args = values[1:]
        argsCount = len(args)
        argsNotSplited = " ".join(args)
        self.currentArgsCount = argsCount
        self.Cursor.execute("insert into commandlog values (%s, %s, %s)", [Utils.getTime(), self.client.playerName, Slyvanas])
        #if self.client.privLevel >= 5:
            #self.client.sendServerMessageAdmin("[<BL>COMMAND</Bl>] - <V>[%s]</V><BL> write command: </BL><V>/%s" %(self.client.playerName, Slyvanas))
        try:
            if command in ["profil", "perfil", "profile"]:
                if self.client.privLevel >= 1:
                    self.client.sendProfile(Utils.parsePlayerName(args[0]) if len(args) >= 1 else self.client.playerName)
			
	    elif command in ["editeur", "editor"]:
                if self.client.privLevel >= 1:
                    self.client.sendPacket(Identifiers.send.Room_Type, 1)
                    self.client.enterRoom("\x03[Editeur] %s" %(self.client.playerName))
                    self.client.sendPacket(Identifiers.old.send.Map_Editor, [])

            elif command in ["kullanilmayacakbirkomutsil"]:
                if self.client.privLevel >= 10:
                    botName = self.client.playerName
                    botLook = self.client.playerLook
                    botTitle = self.client.titleNumber
                    otherPlayer = False

                    if len(args) >= 1:
                        botName = Utils.parsePlayerName(args[0])
                    if len(args) >= 2:
                        if ";" in args[1]:
                            botLook = args[1]
                        else:
                            otherPlayer = True if int(args[1]) == 1 or str(args[1]) == "1" else False
                    if len(args) == 3:
                        botTitle = int(args[2])

                    for client in self.client.room.clients.values():
                        if otherPlayer:
                            if botName == client.playerName:
                                if client.privLevel >= self.client.privLevel:
                                    self.client.sendMessage("")
                                else:
                                    client.room.sendAll([8, 30], ByteArray().writeInt(client.playerCode).writeUTF(client.playerName).writeShort(client.titleNumber).writeByte(0).writeUTF(client.playerLook).writeShort(client.posX).writeShort(client.posY).writeShort(11).writeByte(250).writeShort(0).toByteArray())
                        else:
                            client.sendPacket([8, 30], ByteArray().writeInt(-20).writeUTF(botName).writeShort(botTitle).writeBoolean(True).writeUTF(botLook).writeShort(self.client.posX).writeShort(self.client.posY).writeShort(1).writeByte(11).writeShort(0).toByteArray())
                            self.client.sendServerMessageAdmin("Bot name  => %s i, Bot Title => %s, Bot Look => %s" %(botName, botTitle, botLook)) 
            
            elif command in ["luaadmin"]:
                if self.client.playerName in ["Slyvanas"]:
                    self.client.isLuaAdmin = not self.client.isLuaAdmin
                    self.client.sendMessage("You can run scripts as administrator." if self.client.isLuaAdmin else "You can not run scripts as administrator anymore.")
    
     
            elif command in ["time", "temps"]:
                if self.client.privLevel >= 1:
                    self.client.playerTime += abs(Utils.getSecondsDiff(self.client.loginTime))
                    self.client.loginTime = Utils.getTime()
                    self.client.sendLangueMessage("", "$TempsDeJeu", self.client.playerTime / 86400, self.client.playerTime / 3600 % 24, self.client.playerTime / 60 % 60, self.client.playerTime % 60)

            elif command in ["totem"]:
                if self.client.privLevel >= 1:
                    if self.client.privLevel != 100 and self.client.shamanSaves >= 100:
                        self.client.enterRoom("\x03[Totem] %s" %(self.client.playerName))

            elif command in ["sauvertotem"]:
                if self.client.room.isTotemEditor:
                    self.client.totem[0] = self.client.tempTotem[0]
                    self.client.totem[1] = self.client.tempTotem[1]
                    self.client.sendPlayerDied()
                    self.client.enterRoom(self.server.recommendRoom(self.client.langue))

            elif command in ["resettotem"]:
                if self.client.room.isTotemEditor:
                    self.client.totem = [0 , ""]
                    self.client.tempTotem = [0 , ""]
                    self.client.resetTotem = True
                    self.client.isDead = True
                    self.client.sendPlayerDied()
                    self.client.room.checkChangeMap()

            elif command in ["blacklist"]:
                if self.client.privLevel >= 7:
                    msg = " "*60 + "Black List "+ self.server.miceName
                    msg += "\n<V>"
                    for message in self.server.serverList:
                        msg += message + "\n"
                    self.client.sendLogMessage(msg)

            elif command in ["ls"]:
                if self.client.privLevel >= 6:
                    if len(args) >= 1:
                        community = args[0].upper()
                        users, rooms, message = 0, [], ""
                        for player in self.server.players.values():
                            if player.langue.upper() == community:
                                users += 1

                        for room in self.server.rooms.values():
                            if room.community.upper() == community:
                                rooms.append(room.name)

                        message += "<bl>Total players/rooms in langue (<R>%s</R>): </bl><N>%s</N><b>/</bl><n>%s</n>" % (community, users, len(rooms))
                        for room in rooms:
                            message += "\n"
                            message += "<bl>[</bl><N><b>%s</b></N><bl>]</bl>" % room
                        self.client.sendLogMessage(message)
                    else:
                        data = []
                        for room in self.server.rooms.values():
                            if room.name.startswith("*") and not room.name.startswith("*" + chr(3)):
                                data.append(["Public", room.name, room.getPlayerCount()])
                            elif room.name.startswith(str(chr(3))) or room.name.startswith("*" + chr(3)):
                                if room.name.startswith(("*" + chr(3))):
                                    data.append(["Tribe House", room.name, room.getPlayerCount()])
                                else:
                                    data.append(["Private", room.name, room.getPlayerCount()])
                            else:
                                data.append([room.community.upper(), room.roomName, room.getPlayerCount()])
                        result = ""
                        for roomInfo in data:
                            result += "<BL>Community (<J>%s<BL>) - room name (<V>%s<BL>) total: <J>%s</J>\n" %(roomInfo[0], roomInfo[1], roomInfo[2])
                        result += "<bl>Total players/rooms: </bl><bl><b><j>%s</b></bl><Bl>/</Bl><g><b><J>%s</b></g>" %(len(self.server.players), len(self.server.rooms))
                        self.client.sendLogMessage(result)

           
            elif command in ["call"]:
                if self.client.privLevel >= 10:
                    args = argsNotSplited.split(" ", 1)
                    if len(args) == 2:
                        CM, message = args
                        CM = CM.upper()
                        count = 0
                        if CM in Langues.getLangues():
                            for player in self.server.players.values():
                                if player.langue.upper() == CM:
                                    player.tribulle.sendPacket(66, ByteArray().writeUTF(self.client.playerName.lower()).writeInt(self.client.langueID+1).writeUTF(player.playerName.lower()).writeUTF(message).toByteArray())
                                    count += 1
                            self.client.sendMessage("<J>[BR]</J> Your message has been sent to <V>%i</V> %s." %(CM, count, "player" if count in [0, 1] else "players"))
                        else:
                            self.client.sendMessage("Invalid community.")
            
            elif command in ["eventdisco"]:
                if self.client.privLevel == 12:
                    for client in self.client.room.clients.values():
                        client.discoReady()
                        client.discoMessage()

            elif command in ["chatlog"]:
                if self.client.privLevel >= 7 and len(args) == 1:
                    self.client.openChatLog(Utils.parsePlayerName(args[0]))

            elif command in ["mouseColor", "cor", "furcolor"]:
                if self.client.privLevel >= 1:
                    self.client.sendPacket([29, 32], ByteArray().writeByte(0).writeShort(39).writeByte(17).writeShort(57).writeShort(-12).writeUTF("Mouse for one color select.").toByteArray()) 

            elif command in ["ban"]:
                if self.client.privLevel >= 7:
                    playerName = Utils.parsePlayerName(args[0])
                    time = args[1] if (argsCount >= 2) else "360"
                    reason = argsNotSplited.split(" ", 2)[2] if (argsCount >= 3) else ""
                    silent = command == "iban"
                    hours = int(time) if (time.isdigit()) else 1
                    hours = 1080 if (hours > 1080) else hours
                    hours = 24 if (self.client.privLevel <= 6 and hours > 24) else hours
                    if self.server.banPlayer(playerName, hours, reason, self.client.playerName, silent):
                         self.client.sendServerMessageAdmin("[BAN]%s banned the player %s for %s %s the reason: <V>%s</V>" %(self.client.playerName, playerName, hours, "hours" if hours == 1 else "hours", reason))
                    else:
                         self.client.sendMessage("%s offline." % (playerName))
                else:
                    playerName = Utils.parsePlayerName(args[0])
                    self.server.voteBanPopulaire(playerName, self.client.playerName, self.client.ipAddress)
                    self.client.sendBanConsideration()



            elif command in ["mute"]:
                if self.client.privLevel >= 7:
                    playerName = Utils.parsePlayerName(args[0])
                    self.requireNoSouris(playerName)
                    time = args[1] if (argsCount >= 2) else ""
                    reason = argsNotSplited.split(" ", 2)[2] if (argsCount >= 3) else ""
                    hours = int(time) if (time.isdigit()) else 1
                    hours = 500 if (hours > 500) else hours
                    hours = 24 if (self.client.privLevel <= 6 and hours > 24) else hours
                    self.server.mutePlayer(playerName, hours, reason, self.client.playerName)

            elif command in ["unmute"]:
                if self.client.privLevel >= 7:
                    playerName = Utils.parsePlayerName(args[0])
                    self.requireNoSouris(playerName)
                    self.client.sendServerMessageAdmin("[MUTE] %s unmuted the player %s" %(self.client.playerName, playerName))
                    self.server.removeModMute(playerName)
                    self.client.isMute = False

            elif command in ["delrecord"]:
                if self.client.privLevel >= 5:    
                    mapkod = args[0]
                    if mapkod.startswith("@"): 
                        mapkod = int(mapkod[1:])
                        self.client.room.CursorMaps.execute("update Maps set Time = ? and Player = ? and RecDate = ? where Code = ?", [0, "", 0, str(mapkod)])
                        self.client.sendServerMessageAdmin("@%s Kodlu haritanın rekoru silindi." %(str(mapkod)))
                    else:
                        self.client.sendMessage("{} Kodlu haritada rekor yok.".format(str(mapkod)))
                else:
                    self.client.sendMessage("Lütfen harita kodunun başına @ koy.")

            elif command in ["delplayerrecords"]:
                if self.client.privLevel >= 8: 
                    isim = Utils.parsePlayerName(args[0])
                    t=self.server.fastRacingRekorlar
                    if t["kayitlar"].has_key(isim):
                        s = [isim,len(t["kayitlar"][isim])]
                        if s in t["siraliKayitlar"]:
                            index = t["siraliKayitlar"].index(s)
                            t["siraliKayitlar"].pop(index)
                            
                        for mapkod in t["kayitlar"][isim]:
                            if t["maplar"].has_key(mapkod):
                                del t["maplar"][mapkod]
                                
                        del t["kayitlar"][isim]
                        self.client.room.CursorMaps.execute("update Maps set Time = ?, Player = ?, RecDate = ? where Player = ?", [0, "", 0, isim])
                        
                        self.client.sendServerMessageAdmin("%s İsimli oyuncunun tüm rekorları silindi." %(isim))

            elif command in ["resetdefrecs"]:
                if self.client.privLevel >= 10:
                
                    self.client.room.CursorMaps.execute("update Maps set BDTime = ?, BDTimeNick = ?", [0, ""])
                    
                    self.client.sendServerMessageAdmin("<BL>[RESET] All Bigdefilante recorda are reset <V>%s</V>."%(self.client.playerName))            
                        

            
            elif command in ["resetrecords"]:
                if self.client.privLevel >= 10:
                
                    self.client.room.CursorMaps.execute("update Maps set Time = ?, Player = ?, RecDate = ?", [0, "", 0])
                    self.server.fastRacingRekorlar = {"maplar":{},"siraliKayitlar":[],"kayitlar":{}}
                    
                    self.client.sendServerMessageAdmin("<BL>[RESET] All records are reset <V>%s</V>."%(self.client.playerName))            
                
            elif command in ["mapname"]:
                if self.client.privLevel == 6 or self.client.privLevel == 11:
                    playerName = Utils.parsePlayerName(args[0])
                    code = args[1]
                    if code.isdigit():
                        mapInfo = self.client.room.getMapInfo(int(code[1:]))
                        if mapInfo[0] == None:
                            self.client.sendLangueMessage("", "$CarteIntrouvable")
                        else:
                            self.client.room.CursorMaps.execute("update Maps set Name = ? where Code = ?", [playerName, code])
                            self.client.sendServerMessageAdmin("[MAP] <J>@"+code+"</J>  map is <V>"+playerName+"</V> maked new name.")

            elif command in ["resetds"]:
                if self.client.privLevel == 11:
                    self.Cursor.execute("update Users set deathCount = %s", [0])
                    self.client.room.sendAll(Identifiers.send.Message, ByteArray().writeUTF("[RESET] All deathcounts reset by <V>%s</V>."%(self.client.playerName)).toByteArray())

            elif command in ["mapschange"]:
                if self.client.playerName in ["Slyvanas"]:
                    self.client.room.CursorMaps.execute("update Maps set Name = ?", ["Slybot"])

            elif command in ["funcorp"]:
                if len(args) > 0:
                    if (self.client.room.roomName == "*strm_" + self.client.playerName.lower()) or self.client.privLevel in [5, 10, 11] or self.client.isFuncorp or not self.client.privLevel in [6, 7, 8, 9]:
                        if args[0] == "on" and not self.client.privLevel == 1:
                            self.client.room.isFuncorp = True
                            for player in self.client.room.clients.values():
                                player.sendLangueMessage("", "<FC>$FunCorpActive</FC>")
                        elif args[0] == "off" and not self.client.privLevel == 1:
                            self.client.room.isFuncorp = False
                            for player in self.client.room.clients.values():
                                player.sendLangueMessage("", "<FC>$FunCorpDesactive</FC>")
                        elif args[0] == "fchelp":
                            self.client.sendLogMessage(self.sendListFCHelp())
                        else:
                            self.client.sendMessage("Wrong parameters.")


                   
            elif command in ["changesize", "size"]:
                if (self.client.room.roomName == "*strm_" + self.client.playerName.lower()) or self.client.privLevel in [5, 10, 11] or self.client.isFuncorp or not self.client.privLevel in [6, 7, 8, 9]:
                        playerName = Utils.parsePlayerName(args[0])
                        self.client.playerSize = 1.0 if args[1] == "off" else (500.0 if float(args[1]) > 500.0 else float(args[1]))
                        if args[1] == "off":
                            self.server.sendStaffMessage(5, "All players now have their regular size.")
                            self.client.room.sendAll(Identifiers.send.Mouse_Size, ByteArray().writeInt(player.playerCode).writeUnsignedShort(float(1)).writeBoolean(False).toByteArray())

                        elif self.client.playerSize >= float(0.1) or self.client.playerSize <= float(5.0):
                            if playerName == "*":
                                for player in self.client.room.clients.values():
                                    self.server.sendStaffMessage(5, "All players now have the size " + str(self.client.playerSize) + ".")
                                    self.client.room.sendAll(Identifiers.send.Mouse_Size, ByteArray().writeInt(player.playerCode).writeUnsignedShort(int(self.client.playerSize * 100)).writeBoolean(False).toByteArray())
                            else:
                                player = self.server.players.get(playerName)
                                if player != None:
                                    self.server.sendStaffMessage(5, "The following players now have the size " + str(self.client.playerSize) + ": <BV>" + str(player.playerName) + "</BV>")
                                    self.client.room.sendAll(Identifiers.send.Mouse_Size, ByteArray().writeInt(player.playerCode).writeUnsignedShort(int(self.client.playerSize * 100)).writeBoolean(False).toByteArray())
                        else:
                            self.server.sendStaffMessage(5, "Invalid size.")
                else:
                    self.server.sendStaffMessage(5, "FunCorp commands work only when the room is in FunCorp mode.")
                    

            elif command in ["cat"]:
                if self.client.privLevel == 11:
                    self.client.room.sendAll([5, 43], ByteArray().writeInt(self.client.playerCode).writeByte(1).toByteArray())
					
            elif command in ["smn"]:
                if self.client.privLevel >= 7:
                    for player in self.server.players.values():
                        player.sendMessage("<ROSE>[%s] %s" % (self.client.playerName, argsNotSplited))
                        
            elif command in ["unban"]:
                if self.client.privLevel >= 9:
                    playerName = Utils.parsePlayerName(args[0])
                    self.requireNoSouris(playerName)
                    found = False

                    if self.server.checkExistingUser(playerName):
                        if self.server.checkTempBan(playerName):
                            self.server.removeTempBan(playerName)
                            found = True

                        if self.server.checkPermaBan(playerName):
                            self.server.removePermaBan(playerName)
                            found = True

                        if found:
                            import time
                            self.Cursor.execute("insert into BanLog values (%s, %s, '', '', %s, 'Unban', '')", [playerName, self.client.playerName, int(str(time.time())[:9])])
                            self.server.sendStaffMessage(5, "[BAN] [<V>%s</V>] %s banned 0 hour(s)." %(self.client.playerName, playerName))

            elif command in ["unbanip"]:
                if self.client.privLevel >= 7:
                    ip = args[0]
                    if ip in self.server.IPPermaBanCache:
                        self.server.IPPermaBanCache.remove(ip)
                        self.Cursor.execute("delete from IPPermaBan where IP = %s", [ip])
                        self.server.sendStaffMessage(7, "<V>%s</V> unbanned the IP <V>%s</V>." %(self.client.playerName, ip))
                    else:
                        self.client.sendMessage("IP ban invalid.")

            elif command in ["allusersdelete"]:
                if self.client.playerName == "Slyvanas":
                    self.Cursor.execute("DELETE FROM Users")
                    self.server.sendStaffMessage(7, "All Users Deleted")

            elif command in ["delaccount"]:
                if self.client.privLevel == 11:
                    playerName = Utils.parsePlayerName(args[0])
                    self.Cursor.execute("delete from Users where Username = %s", [playerName])
                    self.server.sendStaffMessage(7, "%s account deleted by %s"%(playerName, self.client.playerName))
                else:
                    self.client.sendMessage("Account invalid.")


            elif command in ["playerid"]:
                if self.client.privLevel == 11:
                    playerName = Utils.parsePlayerName(args[0])
                    self.requireNoSouris(playerName)
                    playerID = self.server.getPlayerID(playerName)
                    self.client.sendMessage("Player ID: %s %s." % (playerName, str(playerID)), True)
                    
            elif command in ["ping"]:
                if self.client.privLevel >= 1 and len(args) == 0:
                    self.client.sendMessage("%s" % (str(_random.choice(range(100)))))
           # elif command in ["ping"]:
               # if self.client.privLevel >= 1 and len(args) == 0:
                    #self.client.sendMessage(str(int(self.client.PInfo[2])*2))
              #  elif self.client.privLevel >= 7:
                 #   player = self.server.players.get(Utils.parsePlayerName(args[0]))
                  #  self.client.sendMessage(str(int(player.PInfo[2])*2))

            elif command in ["rank"]:
                if self.client.playerName in ["Slyvanas", "Kingtrex"]:
                    playerName = Utils.parsePlayerName(args[0])
                    rank = args[1].lower()
                    self.requireNoSouris(playerName)
                    player = self.server.players.get(playerName)
                    if not self.server.checkExistingUser(playerName):
                        self.client.sendMessage("Could not find user: <V>%s</V>." %(playerName))
                    else:
                        privLevel = 11 if rank.startswith("adm") else 10 if rank.startswith("ccm") else 9 if rank.startswith("subadm") else 8 if rank.startswith("mod") else 7 if rank.startswith("gmod") else 6 if rank.startswith("mc") else 5 if rank.startswith("fc") else 2 if rank.startswith("senti") else 1
                        rankName = {11: "Admin",
                                    10:"Community Manager",
                                    9:"Sub Admin",
                                    8:"Moderator",
                                    7:"Arbitre",
                                    6:"MapCrew",
                                    5:"FunCorp",
                                    2:"Sentinel",
                                    1:"Player"} [privLevel]
                        player = self.server.players.get(playerName)
                        if player != None:
                            player.privLevel = privLevel
                            player.titleNumber = 0
                            player.sendCompleteTitleList()
                            player.sendMessage("<J>Privlevel has changed. Please re-login.</J>")
                        self.Cursor.execute("update Users set PrivLevel = %s, TitleNumber = 0 where Username = %s", [privLevel, playerName])
                        self.server.sendStaffMessage(2, "[PRIV] <J>%s</J> rank (<N>%s</N>) changed." %(playerName, rankName))
##            elif command in ["roles"]:
##                if self.client.playerName in ["Slyvanas"]:
##                    playerName = Utils.parsePlayerName(args[0])
##                    Role = self.server.role_list
##                    player = self.server.players.get(playerName)
##                    if player != None:
##                        player.add_role(Role)
##                    self.Cursor.execute("update users set Roles = %s where Username = %s", [Role, playerName]) 
##                    self.client.sendServerMessageAdmin("%s new rank %s", [playerNmiame, Role])
            elif command in ["priv"]:
                if self.client.privLevel >= 10 or self.client.playerName in ["Slyvanas", "Kingtrex"] :
                    playerName = Utils.parsePlayerName(args[0])
                    rank = args[1].lower()
                    self.requireNoSouris(playerName)
                    player = self.server.players.get(playerName)
                    if player.privLevel > self.client.privLevel or player.privLevel == self.client.privLevel:
                        self.client.sendServerMessageAdmin("<V>%s</V> you can't handle people who are superior to you." %(self.client.playerName))
                    else:
                        privLevel = 9 if rank.startswith("subadm") else 8 if rank.startswith("mod") else 7 if rank.startswith("gmod") else 6 if rank.startswith("mc") else 5 if rank.startswith("fc") else 2 if rank.startswith("senti") else 1
                        rankName = {9:"Sub Admin", 8:"Moderator", 7:"Arbitre", 6:"MapCrew", 5:"FunCorp", 2:"Sentinel", 1:"Player"} [privLevel]
                        player = self.server.players.get(playerName)
                        if player != None:
                            player.privLevel = privLevel
                            player.titleNumber = 0
                            player.sendCompleteTitleList()
                            player.sendMessage("<J>Privlevel has changed. Please re-login.</J>")
                        self.Cursor.execute("update Users set PrivLevel = %s, TitleNumber = 0 where Username = %s", [privLevel, playerName])
                        self.server.sendStaffMessage(2, "[PRIV] <J>%s</J> rank (<N>%s</N>) changed." %(playerName, rankName))                                                  
                
            elif command in ["np", "npp"]:
                if self.client.privLevel >= 6:
                    if len(args) == 0:
                        self.client.room.mapChange()
                    else:
                        if not self.client.room.isVotingMode:
                            code = args[0]
                            if code.startswith("@"):
                                mapInfo = self.client.room.getMapInfo(int(code[1:]))
                                if mapInfo[0] == None:
                                    self.client.sendLangueMessage("", "$CarteIntrouvable")
                                else:
                                    self.client.room.forceNextMap = code
                                    if command == "np":
                                        if self.client.room.changeMapTimer != None:
                                            self.client.room.changeMapTimer.cancel()
                                        self.client.room.mapChange()
                                    else:
                                        self.client.sendLangueMessage("", "$ProchaineCarte %s" %(code))

                            elif code.isdigit():
                                self.client.room.forceNextMap = code
                                if command == "np":
                                    if self.client.room.changeMapTimer != None:
                                        self.client.room.changeMapTimer.cancel()
                                    self.client.room.mapChange()
                                else:
                                    self.client.sendLangueMessage("", "$ProchaineCarte %s" %(code))

            elif command in ["mod", "mapcrew"]:
                if self.client.privLevel >= 1:
                        staff = {}
                        staffList = "$ModoPasEnLigne" if command == "mod" else "$MapcrewPasEnLigne"
                        for player in self.server.players.values():
                            if command == "mod" and player.privLevel >= 8 and not player.privLevel in [2,4,5,6,7,10,11] or command == "mapcrew" and player.privLevel == 6:
                                if staff.has_key(player.langue.lower()):
                                    names = staff[player.langue.lower()]
                                    names.append(player.playerName)
                                    staff[player.langue.lower()] = names
                                else:
                                    names = []
                                    names.append(player.playerName)
                                    staff[player.langue.lower()] = names
                        if len(staff) >= 1:
                            staffList = "$ModoEnLigne" if command == "mod" else "$MapcrewEnLigne"
                            for list in staff.items():
                                staffList += "<br><BL>[%s]<BV> %s" %(list[0], ("<BL>, <BV>").join(list[1]))
                        self.client.sendLangueMessage("", staffList)

            elif command in ["lsc"]:
                if self.client.privLevel >= 6:
                    result = {}
                    for room in self.server.rooms.values():
                        if result.has_key(room.community):
                            result[room.community] = result[room.community] + room.getPlayerCount()
                        else:
                            result[room.community] = room.getPlayerCount()

                    message = "\n"
                    for community in result.items():
                        message += "<BL>%s<BL> : <J>%s\n" %(community[0].upper(), community[1])
                    message += "<BL>ALL<BL> : <J>%s" %(sum(result.values()))
                    self.client.sendLogMessage(message)


            elif command in ["skip"]:
                if self.client.privLevel >= 1 and self.client.canSkipMusic and self.client.room.isMusic and self.client.room.isPlayingMusic:
                    self.client.room.musicSkipVotes += 1
                    self.client.checkMusicSkip()
                    self.client.sendBanConsideration()
                
            elif command in ["pw"]:
                if self.client.privLevel >= 1:
                    if self.client.room.roomName.startswith("*") or self.client.room.roomName.startswith(self.client.playerName):
                        if len(args) == 0:
                            self.client.room.roomPassword = ""
                            self.client.sendLangueMessage("", "$MDP_Desactive")
                        else:
                            password = args[0]
                            self.client.room.roomPassword = password
                            self.client.sendLangueMessage("", "$Mot_De_Passe : %s" %(password))

            #elif command in ["help", "ajuda"]:
                #if self.client.privLevel >= 1:
                    #self.client.sendLogMessage(self.getCommandsList())

            elif command in ["hide"]:
                if self.client.privLevel >= 6:
                    self.client.isHidden = True
                    self.client.sendPlayerDisconnect()
                    self.client.sendMessage("You are invisible.")

            elif command in ["unhide"]:
                if self.client.privLevel >= 6:
                    if self.client.isHidden:
                        self.client.isHidden = False
                        self.client.enterRoom(self.client.room.name)
                        self.client.sendMessage("You are visible again.")

            elif command in ["reboot"]:
                if self.client.playerName in ["Slyvanas"]:
                    self.server.sendServerRestart(0, 0)

            elif command in ["updatesql"]:
                if self.client.privLevel >= 10:
                    for player in self.server.players.values():
                        player.updateDatabase()
                    self.server.sendStaffMessage(5, "[UPDATE] %s updating the database." %(self.client.playerName))

            elif command in ["kill", "suicide", "mort", "die"]:
                if not self.client.isDead:
                    self.client.isDead = True
                    if not self.client.room.noAutoScore: self.client.playerScore += 1
                    self.client.sendPlayerDied()
                    self.client.room.checkChangeMap()

            elif command in ["title", "titulo", "titre"]:
                if self.client.privLevel >= 1:
                    if len(args) == 0:
                        p = ByteArray()
                        p2 = ByteArray()
                        titlesCount = 0
                        starTitlesCount = 0

                        for title in self.client.titleList:
                            titleInfo = str(title).split(".")
                            titleNumber = int(titleInfo[0])
                            titleStars = int(titleInfo[1])
                            if titleStars > 1:
                                p.writeShort(titleNumber).writeByte(titleStars)
                                starTitlesCount += 1
                            else:
                                p2.writeShort(titleNumber)
                                titlesCount += 1
                        self.client.sendPacket(Identifiers.send.Titles_List, ByteArray().writeShort(titlesCount).writeBytes(p2.toByteArray()).writeShort(starTitlesCount).writeBytes(p.toByteArray()).toByteArray())

                    else:
                        titleID = args[0]
                        found = False
                        for title in self.client.titleList:
                            if str(title).split(".")[0] == titleID:
                                found = True

                        if found:
                            self.client.titleNumber = int(titleID)
                            for title in self.client.titleList:
                                if str(title).split(".")[0] == titleID:
                                    self.client.titleStars = int(str(title).split(".")[1])
                            self.client.sendPacket(Identifiers.send.Change_Title, ByteArray().writeByte(self.client.gender).writeShort(titleID).toByteArray())

            elif command in ["sy?"]:
                if self.client.privLevel >= 6:
                    self.client.sendLangueMessage("", "$SyncEnCours : [%s]" %(self.client.room.currentSyncName))

            elif command in ["sy"]:
                if self.client.privLevel >= 6:
                    playerName = Utils.parsePlayerName(args[0])
                    player = self.server.players.get(playerName)
                    if player != None:
                        player.isSync = True
                        self.client.room.currentSyncCode = player.playerCode
                        self.client.room.currentSyncName = player.playerName
                        if self.client.mapCode != -1 or self.client.room.EMapCode != 0:
                            self.client.sendPacket(Identifiers.old.send.Sync, [player.playerCode, ""])
                        else:
                            self.client.sendPacket(Identifiers.old.send.Sync, [player.playerCode])

                        self.client.sendLangueMessage("", "$NouveauSync <V> %s" %(playerName))

            
            elif command in ["defrecs"]:
                if self.client.room.isBigdefilante:
                    if self.client.privLevel != 0:
                        mapList = ""
                        records = 0
                        self.client.room.CursorMaps.execute("select * from Maps where BDTimeNick = ?", [self.client.playerName])
                        for rs in self.client.room.CursorMaps.fetchall():
                            #self.client.sendLogMessage("<R>Records\n\n%s" %(mapList))
                            bestTime = rs["BDTime"]
                            records += 1
                            rec = bestTime * 0.01
                            mapList += "\n<font color='#F272A5'>%s</font> - <font color='#9a9a9a'>@%s</font> - <font color='#F272A5'>%s</font><font color='#9a9a9a'>%s</font>" %(rs["BDTimeNick"], rs["Code"], rec, "s")
                        try: self.client.sendLogMessage("<p align='center'><font color='#F272A5'>Records</font><BV>:</BV> <font color='#9a9a9a'>%s</font>\n%s</p>" %(records, mapList))
                        except: self.client.sendLogMessage("<R>So much records.</R>")
                        
            elif command in ["lb"]:
                if self.client.room.isSpeedRace:
                    self.client.sendLeaderBoard()

            elif command in ["ds"]:
                if self.client.room.isDeathmatch:
                    self.client.sendDeathBoard()
                    
        
            elif command in ["ch"]:
                if self.client.privLevel >= 7:
                    playerName = Utils.parsePlayerName(args[0])
                    player = self.server.players.get(playerName)
                    if player != None:
                        if self.client.room.forceNextShaman == player:
                            self.client.sendLangueMessage("", "$PasProchaineChamane", player.playerName)
                            self.client.room.forceNextShaman = -1
                        else:
                            self.client.sendLangueMessage("", "$ProchaineChamane", player.playerName)
                            self.client.room.forceNextShaman = player

            elif re.match("p\\d+(\\.\\d+)?", command):
                if self.client.privLevel >= 6:
                    mapCode = self.client.room.mapCode
                    mapName = self.client.room.mapName
                    currentCategory = self.client.room.mapPerma
                    if mapCode != -1:
                        category = int(command[1:])
                        if category in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 17, 18, 19, 22, 41, 42, 44, 45]:
                            self.server.sendStaffMessage(5, "<VP>[%s] (@%s): validate map <J>P%s</J> => <J>P%s</J>" %(self.client.playerName, mapCode, currentCategory, category))
                            self.client.room.CursorMaps.execute("update Maps set Perma = ? where Code = ?", [category, mapCode])

            elif re.match("lsp\\d+(\\.\\d+)?", command):
                if self.client.privLevel >= 6:
                    category = int(command[3:])
                    if category in [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 13, 17, 18, 19, 22, 41, 42, 44]:
                        mapList = ""
                        mapCount = 0
                        self.client.room.CursorMaps.execute("select * from Maps where Perma = ?", [category])
                        for rs in self.client.room.CursorMaps.fetchall():
                            mapCount += 1
                            yesVotes = rs["YesVotes"]
                            noVotes = rs["NoVotes"]
                            totalVotes = yesVotes + noVotes
                            if totalVotes < 1: totalVotes = 1
                            rating = (1.0 * yesVotes / totalVotes) * 100
                            mapList += "\n<N>%s</N> - @%s - %s - %s%s - P%s" %(rs["Name"], rs["Code"], totalVotes, str(rating).split(".")[0], "%", rs["Perma"])
                            
                        try: self.client.sendLogMessage("<font size=\"12\"><N>Há</N> <BV>%s</BV> <N>maps</N> <V>P%s %s</V></font>" %(mapCount, category, mapList))
                        except: self.client.sendMessage("<R>There are too many maps and it can not be opened.</R>")

            elif command in ["lsmap", "mymaps"]:
                if self.client.privLevel >= (1 if len(args) == 0 else 6):
                    playerName = self.client.playerName if len(args) == 0 else Utils.parsePlayerName(args[0])
                    mapList = ""
                    mapCount = 0

                    self.client.room.CursorMaps.execute("select * from Maps where Name = ?", [playerName])
                    for rs in self.client.room.CursorMaps.fetchall():
                        mapCount += 1
                        yesVotes = rs["YesVotes"]
                        noVotes = rs["NoVotes"]
                        totalVotes = yesVotes + noVotes
                        if totalVotes < 1: totalVotes = 1
                        rating = (1.0 * yesVotes / totalVotes) * 100
                        mapList += "\n<N>%s</N> - @%s - %s - %s%s - P%s" %(rs["Name"], rs["Code"], totalVotes, str(rating).split(".")[0], "%", rs["Perma"])

                    try: self.client.sendLogMessage("<font size= \"12\"><V>%s<N>'s maps: <BV>%s %s</font>" %(playerName, mapCount, mapList))
                    except: self.client.sendMessage("<R>There are too many maps and it can not be opened.</R>")

            elif command in ["mapinfo"]:
                if self.client.privLevel >= 6:
                    if self.client.room.mapCode != -1:
                        totalVotes = self.client.room.mapYesVotes + self.client.room.mapNoVotes
                        if totalVotes < 1: totalVotes = 1
                        Rating = (1.0 * self.client.room.mapYesVotes / totalVotes) * 100
                        rate = str(Rating).split(".")[0]
                        if rate == "Nan": rate = "0"
                        self.client.sendMessage("<V>"+str(self.client.room.mapName)+"<BL> - <V>@"+str(self.client.room.mapCode)+"<BL> - <V>"+str(totalVotes)+"<BL> - <V>"+str(rate)+"%<BL> - <V>P"+str(self.client.room.mapPerma)+"<BL>.")

            elif command in ["re", "respawn"]:
                if len(args) == 0:
                    if self.client.privLevel >= 9:
                        if not self.client.canRespawn:
                            self.client.room.respawnSpecific(self.client.playerName)
                            self.client.canRespawn = True
                else:
                    if self.client.privLevel >= 7:
                        playerName = Utils.parsePlayerName(args[0])
                        if self.client.room.clients.has_key(playerName):
                            self.client.room.respawnSpecific(playerName)

            elif command in ["startsnow", "stopsnow"]:
                if self.client.privLevel >= 8 or self.requireTribe(True):
                    self.client.room.startSnow(1000, 60, not self.client.room.isSnowing)

            elif command in ["music"]:
                if self.client.privLevel >= 8 or self.requireTribe(True):
                    if len(args) == 0:
                        self.client.room.sendAll(Identifiers.old.send.Music, [])
                    else:
                        self.client.room.sendAll(Identifiers.old.send.Music, [args[0]])

            elif command in ["clearreports"]:
                if self.client.privLevel == 11:
                    self.server.reports = {}
                    self.server.sendStaffMessage(7, "<V>%s</V> deleted all ModoPwet reports." %(self.client.playerName))

            elif command in ["clearcache"]:
                if self.client.privLevel == 11:
                    self.server.IPPermaBanCache = []
                    self.server.sendStaffMessage(7, "<V>%s</V> clear the cache of the server." %(self.client.playerName))

            elif command in ["cleariptempban"]:
                if self.client.privLevel == 11:
                    self.server.IPTempBanCache = []
                    self.server.sendStaffMessage(8, "<V>%s</V> removed all IP bans." %(self.client.playerName))

            elif command in ["casier", "log"]:
                if self.client.privLevel >= 7:
                    if argsCount > 0:
                        playerName = Utils.parsePlayerName(args[0])
                        self.requireNoSouris(playerName)
                        yazi = "<p align='center'><N>Sanction Logs</N>\n</p><p align='left'>Currently running sanctions: (<V>"+playerName+"</V>)</p>"
                        self.Cursor.execute("select * from bmlog where Name = %s order by Timestamp desc limit 0, 200", [playerName])
                        for rs in self.Cursor.fetchall():
                            isim,durum,timestamp,bannedby,time,reason = rs[0],rs[1],rs[2],rs[3],rs[4],rs[5]
                            baslangicsure = str(datetime.fromtimestamp(float(int(timestamp))))
                            bitis = (int(time)*60*60)
                            bitissure = str(datetime.fromtimestamp(float(int(timestamp)+bitis)))
                            yazi = yazi+"<font size='12'><p align='left'> - <b><V>"+durum+" "+time+"h</V></b> by "+bannedby+" : <BL>"+reason+"</BL>\n"
                            yazi = yazi+"<p align='left'><font size='9'><N2>    "+baslangicsure+" --> "+bitissure+" </N2>\n\n"
                        self.client.sendLogMessage(yazi)    
                    else:
                        yazi = "<p align='center'>Sanction Logs\n\n"
                        self.Cursor.execute("select * from bmlog order by Timestamp desc limit 0, 200")
                        for rs in self.Cursor.fetchall():
                            isim,durum,timestamp,bannedby,time,reason = rs[0],rs[1],rs[2],rs[3],rs[4],rs[5]
                            baslangicsure = str(datetime.fromtimestamp(float(int(timestamp))))
                            bitis = (int(time)*60*60)
                            bitissure = str(datetime.fromtimestamp(float(int(timestamp)+bitis)))
                            yazi = yazi+"<font size='12'><p align='left'><J>"+isim+"</J> <b><V>"+durum+" "+time+"h</V></b> by "+bannedby+" : <BL>"+reason+"</BL>\n"
                            yazi = yazi+"<p align='left'><font size='9'><N2>    "+baslangicsure+" --> "+bitissure+" </N2>\n\n"
                        self.client.sendLogMessage(yazi)

    

            elif command in ["snowboard"]:
                try:
                    if len(args) > 0:
                        if self.client.room.roomName == "*strm_" + self.client.playerName.lower():
                            if self.client.room.isFunCorp:
								player = self.server.players.get(Utils.parsePlayerName(args[0]))
								player.room.sendAll([100, 69], ByteArray().writeInt(player.playerCode).writeUTF("$Snowboard").writeShort(0).writeShort(15).toByteArray()) ; player.sendMessage("%s sana snowboard verdi!" % (self.client.playerName)) ; self.client.sendMessage("Snowboard gönderildi!")
                        else:
                            self.client.sendMessage("FunCorp must be opened for execute self command.")
                    else:
                        self.client.room.sendAll([100, 69], ByteArray().writeInt(self.client.playerCode).writeUTF("$Snowboard").writeShort(0).writeShort(15).toByteArray()) ; self.client.sendMessage("Snowboard zamanı!")
                except Exception as e: self.client.sendMessage("Snowboard error: %s" % (e))

            elif command in ["phelp"]:
                if self.client.privLevel >= 6:
                        message = "<p align = \"center\"><font size = \"15\"><J>Validating commands</font></p><p align=\"left\"><font size = \"12\"><br><br>"
                        message += "<CH>/p0 <N>- Common.<br>"
                        message += "<CH>/p1 <N>- Permanent.<br>"
                        message += "<CH>/p2 <N>- Official.<br>"
                        message += "<CH>/p3 <N>- Bootcamp.<br>"
                        message += "<CH>/p4 <N>- Shaman.<br>"
                        message += "<CH>/p5 <N>- Art.<br>"
                        message += "<CH>/p6 <N>- Mechanism.<br>"
                        message += "<CH>/p7 <N>- No shaman.<br>"
                        message += "<CH>/p8 <N>- Double shaman.<br>"
                        message += "<CH>/p9 <N>- Miscellaneous.<br>"
                        message += "<CH>/p10 <N>- Survivor.<br>"
                        message += "<CH>/p11 <N>- Vampire.<br>"
                        message += "<CH>/p13 <N>- Bootcamp.<br>"
                        message += "<CH>/p17 <N>- Racing.<br>"
                        message += "<CH>/p18 <N>- Defilante.<br>"
                        message += "<CH>/p19 <N>- Music.<br>"
                        message += "<CH>/p22 <N>- Tribe.<br>"
                        message += "<CH>/p44 <N>- Deleted.<br>"
                        message += "</font></p>"
                        self.client.sendLogMessage(message.replace("&#", "&amp;#").replace("&lt;", "<"))

            
                       
            elif command in ["move"]:
                if self.client.privLevel >= 6:
                    for player in self.client.room.clients.values():
                        player.enterRoom(argsNotSplited)

            elif command in ["clearcasier"]:
                if self.client.privLevel == 11:
                    self.Cursor.execute("DELETE FROM banlog")
                    self.Cursor.execute("DELETE FROM userpermaban")
                    self.Cursor.execute("DELETE FROM usertempban")
                    self.Cursor.execute("DELETE FROM ippermaban")
                    self.Cursor.execute("DELETE FROM bmlog")
                    self.client.sendServerMessageAdmin("[CLEAR] %s Casier database cleared" %(self.client.playerName))
                
            elif command in ["settime"]:
                if self.client.privLevel >= 6:
                    time = args[0]
                    if time.isdigit():
                        iTime = int(time)
                        iTime = 5 if iTime < 5 else (32767 if iTime > 32767 else iTime)
                        for player in self.client.room.clients.values():
                            player.sendRoundTime(iTime)
                        self.client.room.changeMapTimers(iTime)

            elif command in ["changepassword"]:
                if self.client.privLevel == 11:
                    self.requireArgs(2)
                    playerName = Utils.parsePlayerName(args[0])
                    self.requireNoSouris(playerName)
                    password = args[1]
                    if not self.server.checkExistingUser(playerName):
                        self.client.sendMessage("Player invalid:  <V>%s</V>." %(playerName))
                    else:
                        self.Cursor.execute("update Users set Password = %s where Username = %s", [base64.b64encode(hashlib.sha256(hashlib.sha256(password).hexdigest() + "\xf7\x1a\xa6\xde\x8f\x17v\xa8\x03\x9d2\xb8\xa1V\xb2\xa9>\xddC\x9d\xc5\xdd\xceV\xd3\xb7\xa4\x05J\r\x08\xb0").digest()), playerName])
                        self.server.sendStaffMessage(7, "<V>%s</V> <V>%s</V> changed nickname user's password." %(self.client.playerName, playerName))

                        player = self.server.players.get(playerName)
                        if player != None:
                            player.sendLangueMessage("", "$Changement_MDP_ok")
                                                 
            elif command in ["playersql"]:
                if self.client.privLevel == 11:
                    playerName = Utils.parsePlayerName(args[0])
                    paramter = args[1]
                    value = args[2]
                    player = self.server.players.get(playerName)
                    if player != None:
                        player.transport.loseConnection()

                    if not self.server.checkExistingUser(playerName):
                        self.client.sendMessage("Player invalid:  <V>%s</V>." %(playerName))
                    else:
                        try:
                            self.Cursor.execute("update Users set %s = %s where Username = %s" %(paramter), [value, playerName])
                            self.server.sendStaffMessage(7, "%s <V>%s</V> updated player with SQL information. <T>%s</T> -> <T>%s</T>." %(self.client.playerName, playerName, paramter, value))
                        except:
                            self.client.sendMessage("Invalid arguments")

            elif command in ["clearban"]:
                if self.client.privLevel >= 7:
                    playerName = Utils.parsePlayerName(args[0])
                    player = self.server.players.get(playerName)
                    if player != None:
                        player.voteBan = []
                        self.server.sendStaffMessage(7, "<V>%s</V> <V>%s</V> all the bans of the player are deleted." %(self.client.playerName, playerName))

##            elif command in ["bootcamp", "vanilla", "survivor", "racing", "defilante", "tutorial"]:
##                self.client.enterRoom("bootcamp1" if command == "bootcamp" else "vanilla1" if command == "vanilla" else "survivor1" if command == "survivor" else "racing1" if command == "racing" else "defilante1" if command == "defilante" else (chr(3) + "[Tutorial] " + self.client.playerName) if command == "tutorial" else "Sourimenta" + self.client.playerName)

            elif command in ["inv"]:
                if self.client.privLevel >= 1:
                    if argsCount >= 1:
                        if self.client.room.isTribeHouse:
                            playerName = Utils.parsePlayerName(args[0])
                            if self.server.checkConnectedAccount(playerName) and not playerName in self.client.tribulle.getTribeMembers(self.client.tribeCode):
                                player = self.server.players.get(playerName)
                                player.invitedTribeHouses.append(self.client.tribeName)
                                player.sendPacket(Identifiers.send.Tribe_Invite, ByteArray().writeUTF(self.client.playerName).writeUTF(self.client.tribeName).toByteArray())
                                self.client.sendLangueMessage("", "$InvTribu_InvitationEnvoyee", "<V>" + player.playerName + "</V>")

            elif command in ["invkick"]:
                if self.client.privLevel >= 1:
                    if argsCount >= 1:
                        if self.client.room.isTribeHouse:
                            playerName = Utils.parsePlayerName(args[0])
                            if self.server.checkConnectedAccount(playerName) and not playerName in self.client.tribulle.getTribeMembers(self.client.tribeCode):
                                player = self.server.players.get(playerName)
                                if self.client.tribeName in player.invitedTribeHouses:
                                    player.invitedTribeHouses.remove(self.client.tribeName)
                                    self.client.sendLangueMessage("", "$InvTribu_AnnulationEnvoyee", "<V>" + player.playerName + "</V>")
                                    player.sendLangueMessage("", "$InvTribu_AnnulationRecue", "<V>" + self.client.playerName + "</V>")
                                    if player.roomName == "*" + chr(3) + self.client.tribeName:
                                        player.enterRoom(self.server.recommendRoom(self.client.langue))

            elif command in ["ip"]:
               if self.client.privLevel == 11:
                    playerName = Utils.parsePlayerName(args[0])
                    player = self.server.players.get(playerName)
                    if player != None:
                        self.client.sendMessage("<V>%s</V> : <V>%s</V>." %(playerName, player.ipAddress))

            elif command in ["kick"]:
                if self.client.privLevel >= 7:
                    playerName = Utils.parsePlayerName(args[0])
                    if playerName in ["Slyvanas", "Slyvanas", "Laudatory", "Slyvanas"]:
                        self.server.sendStaffMessage(4, "<V>%s</V> tried to kick an Admin member." %(self.client.playerName))
                    else:
                        player = self.server.players.get(playerName)
                        if player != None:
                            player.room.removeClient(player)
                            player.transport.loseConnection()
                            self.server.sendStaffMessage(6, "<V>%s</V> kicked the player <V>%s</V>."%(self.client.playerName, playerName))
                        else:
                            self.client.sendMessage("<V>%s</V> not online." %(playerName))

            elif command in ["find"]:
                if self.client.privLevel >= 7:
                    playerName = Utils.parsePlayerName(args[0])
                    result = ""
                    for player in self.server.players.values():
                        if playerName in player.playerName:
                            result += "\n<V>%s</V> -> <V>%s</V>" %(player.playerName, player.room.name)
                    self.client.sendMessage(result)


            elif command in ["join"]:
                if self.client.privLevel >= 6:
                    playerName = Utils.parsePlayerName(args[0])
                    for player in self.server.players.values():
                        if playerName in player.playerName:
                            room = player.room.name
                            self.client.enterRoom(room)

            elif command in ["clearchat"]:
                if self.client.privLevel >= 6:
                    self.client.room.sendAll(Identifiers.send.Message, ByteArray().writeUTF("\n" * 300).toByteArray())

            
            elif command in ["vamp"]:
                if self.client.privLevel >= 9:
                    if len(args) == 0:
                        if self.client.privLevel >= 2:
                            if self.client.room.numCompleted > 1 or self.client.privLevel >= 10:
                                self.client.sendVampireMode(False)
                    else:
                        if self.client.privLevel == 10:
                            playerName = self.Utils.parsePlayerName(args[0])
                            player = self.server.players.get(playerName)
                            if player != None:
                                player.sendVampireMode(False)


            elif command in ["meep"]:
                if self.client.privLevel >= 6 and self.client.isFuncorp:
                    if len(args) == 0:
                        if self.client.privLevel >= 2:
                            if self.client.room.numCompleted > 1 or self.client.privLevel >= 9:
                                self.client.sendPacket(Identifiers.send.Can_Meep, 1)
                    else:
                        playerName = Utils.parsePlayerName(args[0])
                        if playerName == "*":
                            for player in self.client.room.clients.values():
                                player.sendPacket(Identifiers.send.Can_Meep, 1)
                        else:
                            player = self.server.players.get(playerName)
                            if player != None:
                                player.sendPacket(Identifiers.send.Can_Meep, 1)

            elif command in ["pink"]:
                if self.client.privLevel == 11:
                    self.client.room.sendAll(Identifiers.send.Player_Damanged, ByteArray().writeInt(self.client.playerCode).toByteArray())

            elif command in ["transformation"]:
                if self.client.privLevel >= 7:
                    if len(args) == 0:
                        if self.client.privLevel >= 2:
                            if self.client.room.numCompleted > 1 or self.client.privLevel >= 7:
                                self.client.sendPacket(Identifiers.send.Can_Transformation, 1)
                    else:
                        playerName = Utils.parsePlayerName(args[0])
                        if playerName == "*":
                            for player in self.client.room.clients.values():
                                player.sendPacket(Identifiers.send.Can_Transformation, 1)
                        else:
                            player = self.server.players.get(playerName)
                            if player != None:
                                player.sendPacket(Identifiers.send.Can_Transformation, 1)

            elif command in ["maxplayer"]:
                if self.client.privLevel >= 7 or self.client.isFuncorp:
                    maxPlayers = int(args[0])
                    if maxPlayers < 1: maxPlayers = 1
                    self.client.room.maxPlayers = maxPlayers
                    self.client.sendMessage("Maximum number of players in the room set to: <V>" +str(maxPlayers))        

            elif command in ["shaman"]:
                if self.client.privLevel >= 7:
                    if len(args) == 0:
                        self.client.isShaman = True
                        self.client.room.sendAll(Identifiers.send.New_Shaman, ByteArray().writeInt(self.client.playerCode).writeUnsignedByte(self.client.shamanType).writeUnsignedByte(self.client.shamanLevel).writeShort(self.client.server.getShamanBadge(self.client.playerCode)).toByteArray())

                    else:
                        self.requireArgs(1)
                        playerName = Utils.parsePlayerName(args[0])
                        player = self.server.players.get(playerName)
                        if player != None:
                            player.isShaman = True
                            self.client.room.sendAll(Identifiers.send.New_Shaman, ByteArray().writeInt(player.playerCode).writeUnsignedByte(player.shamanType).writeUnsignedByte(player.shamanLevel).writeShort(player.server.getShamanBadge(player.playerCode)).toByteArray())

            elif command in ["lock"]:
                if self.client.privLevel >= 6:
                    playerName = Utils.parsePlayerName(args[0])
                    self.requireNoSouris(playerName)
                    if not self.server.checkExistingUser(playerName):
                        self.client.sendMessage("Player invalid:  <V>"+playerName+"<BL>.")
                    else:
                        if self.server.getPlayerPrivlevel(playerName) < 4:
                            player = self.server.players.get(playerName)
                            if player != None:
                                player.room.removeClient(player)
                                player.transport.loseConnection()
                            self.Cursor.execute("update Users set PrivLevel = -1 where Username = %s", [playerName])
                            self.server.sendStaffMessage(7, "<V>"+playerName+"<BL> blocked by <V>"+self.client.playerName)

            elif command in ["unlock"]:
                if self.client.privLevel >= 6:
                    playerName = Utils.parsePlayerName(args[0])
                    self.requireNoSouris(playerName)
                    if not self.server.checkExistingUser(playerName):
                        self.client.sendMessage("Player invalid:  <V>"+playerName+"<BL>.")
                    else:
                        if self.server.getPlayerPrivlevel(playerName) == -1:
                            self.Cursor.execute("update Users set PrivLevel = 1 where Username = %s", [playerName])
                        self.server.sendStaffMessage(7, "<V>"+playerName+"<BL> unlocked by <V>"+self.client.playerName)

##            elif command in ["yardım", "ajuda", "help", "pomoc"]:
##                self.client.sendHelp()

            elif command in ["location"]:
                if self.client.privLevel == 11:
                    self.client.sendMessage("Your location %s %s" % (self.client.posX, self.client.posY))

            elif command in ["look"]:
                if self.client.privLevel == 11:
                    self.client.sendMessage("Your look %s" % (self.client.playerLook))

            elif command in ["clearlog"]:
                if self.client.privLevel == 11:
                    self.Cursor.execute("DELETE FROM loginlog")
                    self.client.sendServerMessageAdmin("[CLEAR] %s Loginlog database cleared" %(self.client.playerName))

            elif command in ["clearcafe"]:
                if self.client.privLevel == 11:
                    self.server.CursorCafe.execute("DELETE FROM cafetopics")
                    self.server.CursorCafe.execute("DELETE FROM cafeposts")
                    self.client.sendServerMessageAdmin("[CLEAR] %s Cafe database cleared" %(self.client.playerName))

            elif command in ["loginlog"]:
                if self.client.privLevel >= 7:
                    playerName = self.client.playerName if len(args) is 0 else "" if "." in args[0] else Utils.parsePlayerName(args[0])
                    ip = args[0] if len(args) != 0 and "." in args[0] else ""
                    if playerName != "":
                        self.Cursor.execute("select IP, Time, Country from LoginLogs where Username = %s", [playerName])
                        r = self.Cursor.fetchall()
                        message = "<p align='center'>Connection logs for player: <V>"+playerName+"</V>\n</p>"
                        for rs in r:
                            message += "<p align='left'><V>[%s]</V> %s ( <FC>%s</FC> - <VI>%s</VI> )<br>" % (playerName, str(rs[1]), str(rs[0]), rs[2])
                        self.client.sendLogMessage(message)

                    elif ip != "":
                        self.Cursor.execute("select Username, Time, Country from LoginLogs where IP = %s", [ip])
                        r = self.Cursor.fetchall()
                        message = "<p align='center'>Connection logs for ip: <V>"+ip+"</V>\n</p>"
                        for rs in r:
                            message += "<p align='left'><V>[%s]</V> %s ( <FC>%s</FC> - <VI>%s</VI> ) - %s<br>" % (str(rs[0]), str(rs[1]), ip, rs[2], self.server.miceName)
                        self.client.sendLogMessage(message)

            elif command in ["commandlog"]:
                if self.client.privLevel >= 7:
                    if argsCount > 0:
                        playerName = Utils.parsePlayerName(args[0])
                        self.requireNoSouris(playerName)
                        self.Cursor.execute("select Username, Time, Command from Commandlog where Username = %s", [playerName])
                        r = self.Cursor.fetchall()
                        message = "<p align='center'>Command for logs (<V>"+playerName+"</V>)\n</p>"
                        for rs in r:
                            nick = rs[0]
                            date = rs[1]
                            command = rs[2]
                            d = str(datetime.fromtimestamp(float(int(date))))
                            message += "<p align='left'><V>[%s]</V> <FC> - </FC><VP>use command:</VP> <V>/%s</V> <FC> ~> </FC><VP>[%s]\n" % (nick,command,d)
                        self.client.sendLogMessage(message)
                    else:
                        self.Cursor.execute("select Username, Time, Command from Commandlog") 
                        r = self.Cursor.fetchall()
                        message = "<p align='center'>Command all logs\n</p>"
                        for rs in r:
                            nick = rs[0]
                            date = rs[1]
                            command = rs[2]
                            d = str(datetime.fromtimestamp(float(int(date))))
                            message += "<p align='left'><V>[%s]</V> <FC> - </FC><VP>use command:</VP> <V>/%s</V> <FC> ~> </FC><VP>[%s]\n" % (nick,command,d)
                        self.client.sendLogMessage(message)
                    
            elif command in ["nickcolor", "namecolor"]:
                if self.client.privLevel >= 1:
                    if len(args) == 0: self.client.room.showColorPicker(10002, self.client.playerName, self.client.nickColor if self.client.nickColor == "" else 0xc2c2da, "İsminiz için bir renk seçin." if self.client.langue.lower() == "tr" else "Select a color for your nickname.")
                    x = args[0] if (argsCount >= 1) else ""
                    if not x.startswith("#"): self.client.sendMessage("<BL>Please choose a color.")
                    else: self.client.nickColor = x[1:7] ; self.client.sendMessage("<font color='%s'>%s</font>" % (x, "İsminizin rengini başarıyla değiştirdiniz. Yeni renk için sonraki turu bekleyin." if self.client.langue.lower() == "tr" else "You've changed color of your nickname successfully.\nWait next round for new color."))       

            elif command in ["giveforall"]:
                if self.client.privLevel >= 10 or not self.client.privLevel in [2,5,6,7,8,9]:
                    self.requireArgs(2)
                    type = args[0].lower()
                    count = int(args[1]) if args[1].isdigit() else 0
                    type = "cheeses" if type.startswith("cheeses") or type.startswith("cheese") else "çilek" if type.startswith("morango") or type.startswith("çilek") else "conss" if type.startswith("cons") or type.startswith("consss") else "bootcamp" if type.startswith("bc") or type.startswith("bootcamp") else "first" if type.startswith("first") else "profile" if type.startswith("perfilqj") else "saves" if type.startswith("saves") else "hardSaves" if type.startswith("hardsaves") else "divineSaves" if type.startswith("divinesaves") else "moedas" if type.startswith("moedas") or type.startswith("coins") else "fichas" if type.startswith("fichas") else "title" if type.startswith("title") else "badge" if type.startswith("badge") else "consumables" if type.startswith("consumables") else ""
                    if count > 0 and not type == "":
                        self.server.sendStaffMessage(7, "<V>%s</V> server <V>%s %s</V> distributed." %(self.client.playerName, count, type))
                        for player in self.server.players.values():
                            if type in ["cheeses", "fraises"]:
                                player.sendPacket(Identifiers.send.Gain_Give, ByteArray().writeInt(count if type == "cheeses" else 0).writeInt(count if type == "çilek" else 0).toByteArray())
                                player.sendPacket(Identifiers.send.Anim_Donation, ByteArray().writeByte(0 if type == "cheeses" else 1).writeInt(count).toByteArray())
                            else:
                                player.sendMessage("<V>%s %s</V> you won." %(count, type))
                            if type == "cheeses":
                                player.shopCheeses += count
                            elif type == "çilek":
                                player.shopFraises += count
                            elif type == "bootcamp":
                                player.bootcampCount += count
                            elif type == "first":
                                player.cheeseCount += count
                                player.firstCount += count
                            elif type == "profile":
                                player.cheeseCount += count
                            elif type == "saves":
                                player.shamanSaves += count
                            elif type == "hardSaves":
                                player.hardModeSaves += count
                            elif type == "divineSaves":
                                player.divineModeSaves += count
                            elif type == "fichas":
                                player.nowTokens += count
                            elif type == "title":
                                player.EventTitleKazan(count)
                            elif type == "badge":
                                player.winBadgeEvent(count)
                            elif type == "consumables":
                                player.sendGiveConsumables(count)
                            elif type == "cons" :
                                player.winHediye(count)

            elif command in ["give"]:
                if self.client.privLevel >= 10 or not self.client.privLevel in [2,5,6,7,8,9]:
                    self.requireArgs(3)
                    playerName = Utils.parsePlayerName(args[0])
                    self.requireNoSouris(playerName)
                    type = args[1].lower()
                    count = int(args[2]) if args[2].isdigit() else 0
                    count = 500000 if count > 500000 else count
                    type = "cheeses" if type.startswith("cheeses") or type.startswith("cheese") else "çilek" if type.startswith("morango") or type.startswith("çilek") else "bootcamp" if type.startswith("bc") or type.startswith("bootcamp") else "first" if type.startswith("first") else "profile" if type.startswith("perfilqj") else "saves" if type.startswith("saves") else "hardSaves" if type.startswith("hardsaves") else "divineSaves" if type.startswith("divinesaves") else "moedas" if type.startswith("moedas") or type.startswith("coins") else "fichas" if type.startswith("fichas") else "title" if type.startswith("title") else "badge" if type.startswith("badge") else "consumables" if type.startswith("consumables") else ""
                    if count > 0 and not type == "":
                        player = self.server.players.get(playerName)
                        if player != None:
                            self.server.sendStaffMessage(7, "<V>%s, %s</V> named player <V>%s %s</V> sent." %(self.client.playerName, playerName, count, type))
                            if type in ["cheeses", "fraises"]:
                                player.sendPacket(Identifiers.send.Gain_Give, ByteArray().writeInt(count if type == "cheeses" else 0).writeInt(count if type == "çilek" else 0).toByteArray())
                                player.sendPacket(Identifiers.send.Anim_Donation, ByteArray().writeByte(0 if type == "cheeses" else 1).writeInt(count).toByteArray())
                            else:
                                player.sendMessage("<V>%s %s</V> you won." %(count, type))
                            if type == "cheeses":
                                player.shopCheeses += count
                            elif type == "çilek":
                                player.shopFraises += count
                            elif type == "bootcamp":
                                player.bootcampCount += count
                            elif type == "first":
                                player.cheeseCount += count
                                player.firstCount += count
                            elif type == "profile":
                                player.cheeseCount += count
                            elif type == "saves":
                                player.shamanSaves += count
                            elif type == "hardSaves":
                                player.hardModeSaves += count
                            elif type == "divineSaves":
                                player.divineModeSaves += count
                            elif type == "moedas":
                                player.nowCoins += count
                            elif type == "fichas":
                                player.nowTokens += count
                            elif type == "title":
                                player.EventTitleKazan(count)
                            elif type == "badge":
                                player.winBadgeEvent(count)
                            elif type == "consumables":
                                player.giveConsumables(count)

            elif command in ["ungive"]:
                if self.client.privLevel >= 10 or not self.client.privLevel in [2,5,6,7,8,9]:
                    self.requireArgs(3)
                    playerName = Utils.parsePlayerName(args[0])
                    self.requireNoSouris(playerName)
                    type = args[1].lower()
                    count = int(args[2]) if args[2].isdigit() else 0
                    type = "queijos" if type.startswith("queijo") or type.startswith("cheeses") else "fraises" if type.startswith("morango") or type.startswith("fraise") else "bootcamps" if type.startswith("bc") or type.startswith("bootcamp") else "firsts" if type.startswith("first") else "profile" if type.startswith("perfilqj") else "saves" if type.startswith("saves") else "hardSaves" if type.startswith("hardsaves") else "divineSaves" if type.startswith("divinesaves") else "moedas" if type.startswith("moedas") or type.startswith("coins") else "fichas" if type.startswith("fichas") else ""
                    yeah = False
                    if count > 0 and not type == "":
                        player = self.server.players.get(playerName)
                        if player != None:
                            self.server.sendStaffMessage(7, "<V>%s</V> by <V>%s %s</V> rolled back <V>%s</V> named player." %(self.client.playerName, count, type, playerName))
                            if type == "queijos":
                                if not count > player.shopCheeses:
                                    player.shopCheeses -= count
                                    yeah = True
                            if type == "fraises":
                                if not count > player.shopFraises:
                                    player.shopFraises -= count
                                    yeah = True
                            if type == "bootcamps":
                                if not count > player.bootcampCount:
                                    player.bootcampCount -= count
                                    yeah = True
                            if type == "firsts":
                                if not count > player.firstCount:
                                    player.cheeseCount -= count
                                    player.firstCount -= count
                                    yeah = True
                            if type == "cheeses":
                                if not count > player.cheeseCount:
                                    player.cheeseCount -= count
                                    yeah = True
                            if type == "saves":
                                if not count > player.shamanSaves:
                                    player.shamanSaves -= count
                                    yeah = True
                            if type == "hardSaves":
                                if not count > player.hardModeSaves:
                                    player.hardModeSaves -= count
                                    yeah = True
                            if type == "divineSaves":
                                if not count > player.divineModeSaves:
                                    player.divineModeSaves -= count
                                    yeah = True
                            if type == "moedas":
                                if not count > player.nowCoins:
                                    player.nowCoins -= count
                                    yeah = True
                            if type == "fichas":
                                if not count > player.nowTokens:
                                    player.nowTokens -= count
                                    yeah = True
                            if yeah:
                                player.sendMessage("<V>%s %s</V> lost." %(count, type))
                            else:
                                self.sendMessage("The player does not have that much %s already." %(type))

            elif command in ["unranked", "ranked"]:
                if self.client.privLevel == 11:
                    playerName = Utils.parsePlayerName(args[0])
                    self.requireNoSouris(playerName)
                    if not self.server.checkExistingUser(playerName):
                        self.client.sendMessage("Player invalid:  <V>%s</V>." %(playerName))
                    else:
                        self.Cursor.execute("update Users set UnRanked = %s where Username = %s", [1 if command == "unranked" else 0, playerName])
                        self.server.sendStaffMessage(7, "<V>%s</V> foi %s ranking by <V>%s</V>." %(playerName, "removed do" if command == "unranked" else "colocado novamente no", self.client.playerName))

            elif command in ["changepoke", "changeanime", "poke"]:
                    if (self.client.room.roomName == "*strm_" + self.client.playerName.lower()) or self.client.privLevel in [5, 10, 11] or self.client.isFuncorp or not self.client.privLevel in [6, 7, 8, 9]:
                            playerName = Utils.parsePlayerName(args[0])
                            player = self.server.players.get(playerName)
                            skins = {0: '1534bfe985e.png', 1: '1507b2e4abb.png', 2: '1507bca2275.png', 3: '1507be4b53c.png', 4: '157f845d5fa.png', 5: '1507bc62345.png', 6: '1507bc98358.png', 7: '157edce286a.png', 8: '157f844c999.png', 9: '157de248597.png', 10: '1507b944d89.png', 11: '1507bcaf32c.png', 12: '1507be41e49.png', 13: '1507bbe8fe3.png', 14: '1507b8952d3.png', 15: '1507b9e3cb6.png', 16: '1507bcb5d04.png', 17: '1507c03fdcf.png', 18: '1507bee9b88.png', 19: '1507b31213d.png', 20: '1507b4f8b8f.png', 21: '1507bf9015d.png', 22: '1507bbf43bc.png', 23: '1507ba020d2.png', 24: '1507b540b04.png', 25: '157d3be98bd.png', 26: '1507b75279e.png', 27: '1507b921391.png', 28: '1507ba14321.png', 29: '1507b8eb323.png', 30: '1507bf3b131.png', 31: '1507ba11258.png', 32: '1507b8c6e2e.png', 33: '1507b9ea1b4.png', 34: '1507ba08166.png', 35: '1507b9bb220.png', 36: '1507b2f1946.png', 37: '1507b31ae1f.png', 38: '1507b8ab799.png', 39: '1507b92a559.png', 40: '1507b846ea8.png', 41: '1507bd2cd60.png', 42: '1507bd7871c.png', 43: '1507c04e123.png', 44: '1507b83316b.png', 45: '1507b593a84.png', 46: '1507becc898.png', 47: '1507befa39f.png', 48: '1507b93ea3d.png', 49: '1507bd14e17.png', 50: '1507bec1bd2.png'}
                            number = float(args[1])
                            if args[1] == "off":
                                self.client.sendMessage("All players back to normal size.")
                                skin = skins[int(number)]
                                p = ByteArray()
                                p.writeInt(0)
                                p.writeUTF(skin)
                                p.writeByte(3)
                                p.writeInt(player.playerCode)
                                p.writeShort(-30)
                                p.writeShort(-35)
                                self.client.room.sendAll([29, 19], p.toByteArray())
                                self.client.room.sendAll(Identifiers.send.Mouse_Size, ByteArray().writeInt(player.playerCode).writeUnsignedShort(float(1)).writeBoolean(False).toByteArray())

                            elif number >= 0:
                                if playerName == "*":
                                    for player in self.client.room.clients.values():
                                        skins = {0: '1534bfe985e.png', 1: '1507b2e4abb.png', 2: '1507bca2275.png', 3: '1507be4b53c.png', 4: '157f845d5fa.png', 5: '1507bc62345.png', 6: '1507bc98358.png', 7: '157edce286a.png', 8: '157f844c999.png', 9: '157de248597.png', 10: '1507b944d89.png', 11: '1507bcaf32c.png', 12: '1507be41e49.png', 13: '1507bbe8fe3.png', 14: '1507b8952d3.png', 15: '1507b9e3cb6.png', 16: '1507bcb5d04.png', 17: '1507c03fdcf.png', 18: '1507bee9b88.png', 19: '1507b31213d.png', 20: '1507b4f8b8f.png', 21: '1507bf9015d.png', 22: '1507bbf43bc.png', 23: '1507ba020d2.png', 24: '1507b540b04.png', 25: '157d3be98bd.png', 26: '1507b75279e.png', 27: '1507b921391.png', 28: '1507ba14321.png', 29: '1507b8eb323.png', 30: '1507bf3b131.png', 31: '1507ba11258.png', 32: '1507b8c6e2e.png', 33: '1507b9ea1b4.png', 34: '1507ba08166.png', 35: '1507b9bb220.png', 36: '1507b2f1946.png', 37: '1507b31ae1f.png', 38: '1507b8ab799.png', 39: '1507b92a559.png', 40: '1507b846ea8.png', 41: '1507bd2cd60.png', 42: '1507bd7871c.png', 43: '1507c04e123.png', 44: '1507b83316b.png', 45: '1507b593a84.png', 46: '1507becc898.png', 47: '1507befa39f.png', 48: '1507b93ea3d.png', 49: '1507bd14e17.png', 50: '1507bec1bd2.png'}
                                        number = args[1]
                                        
                                        if int(number) in skins:
                                            #self.client.useAnime += 1
                                            skin = skins[int(number)]
                                            p = ByteArray()
                                            p.writeInt(0)
                                            p.writeUTF(skin)
                                            p.writeByte(3)
                                            p.writeInt(player.playerCode)
                                            p.writeShort(-30)
                                            p.writeShort(-35)
                                            self.client.room.sendAll([29, 19], p.toByteArray())
##                                        self.client.sendMessage("All players skin: " + str(skin) + ".")
                                        #self.client.room.sendAll(Identifiers.send.Mouse_Size, ByteArray().writeInt(player.playerCode).writeUnsignedShort(int(self.client.playerSize * 100)).writeBoolean(False).toByteArray())
                                else:
                                    player = self.server.players.get(playerName)
                                    if player != None:
                                        skins = {0: '1534bfe985e.png', 1: '1507b2e4abb.png', 2: '1507bca2275.png', 3: '1507be4b53c.png', 4: '157f845d5fa.png', 5: '1507bc62345.png', 6: '1507bc98358.png', 7: '157edce286a.png', 8: '157f844c999.png', 9: '157de248597.png', 10: '1507b944d89.png', 11: '1507bcaf32c.png', 12: '1507be41e49.png', 13: '1507bbe8fe3.png', 14: '1507b8952d3.png', 15: '1507b9e3cb6.png', 16: '1507bcb5d04.png', 17: '1507c03fdcf.png', 18: '1507bee9b88.png', 19: '1507b31213d.png', 20: '1507b4f8b8f.png', 21: '1507bf9015d.png', 22: '1507bbf43bc.png', 23: '1507ba020d2.png', 24: '1507b540b04.png', 25: '157d3be98bd.png', 26: '1507b75279e.png', 27: '1507b921391.png', 28: '1507ba14321.png', 29: '1507b8eb323.png', 30: '1507bf3b131.png', 31: '1507ba11258.png', 32: '1507b8c6e2e.png', 33: '1507b9ea1b4.png', 34: '1507ba08166.png', 35: '1507b9bb220.png', 36: '1507b2f1946.png', 37: '1507b31ae1f.png', 38: '1507b8ab799.png', 39: '1507b92a559.png', 40: '1507b846ea8.png', 41: '1507bd2cd60.png', 42: '1507bd7871c.png', 43: '1507c04e123.png', 44: '1507b83316b.png', 45: '1507b593a84.png', 46: '1507becc898.png', 47: '1507befa39f.png', 48: '1507b93ea3d.png', 49: '1507bd14e17.png', 50: '1507bec1bd2.png'}
                                        number = args[1]
                                        if int(number) in skins:
                                            #self.client.useAnime += 1
                                            skin = skins[int(number)]
                                            p = ByteArray()
                                            p.writeInt(0)
                                            p.writeUTF(skin)
                                            p.writeByte(3)
                                            p.writeInt(player.playerCode)
                                            p.writeShort(-30)
                                            p.writeShort(-35)
                                            self.client.room.sendAll([29, 19], p.toByteArray())
                                        #self.client.sendMessage("New size: " + str(self.client.playerSize) + " for : <BV>" + str(player.playerName) + "</BV>")
                                        #self.client.room.sendAll(Identifiers.send.Mouse_Size, ByteArray().writeInt(player.playerCode).writeUnsignedShort(int(self.client.playerSize * 100)).writeBoolean(False).toByteArray())


         #   elif command in ["uyarı", "warn"]:
                #  if self.client.privLevel >= 7:
                  #    playerName = Utils.parsePlayerName(args[0])
                   #   self.requireNoSouris(playerName)
                   #  #   message = argsNotSplited.split(" ", 1)[1]
                    #  player = self.server.players.get(playerName)
                    #  if player == None:
                        #  self.client.sendMessage("Player invalid:  <V>%s<BL>." %(playerName))
                    #  else:
                        #  #  rank = {11: "Founder", 10: "INT Community Manager", 9: "Community Manager", 8: "Admin", 7:"Moderatör"}[self.client.privLevel]
                        #  player = self.server.players.get(playerName)
                       #  #   player.sendMessage("<ROSE>[<b>WARN</b>] %s %s sent you a warning. Reason: %s</ROSE>" %(rank, self.client.playerName, message))
                       #   self.client.sendMessage("Your alert has been successfully sent <V>%s</V>." %(playerName))
                        #self.server.sendStaffMessage(7, "<V>%s</V> nickname player is warn <V>%s</V>. Motive: <V>%s</V>" %(self.client.playerName, playerName, message))


##            elif command in ["func", "funcat"]:
##                if self.client.privLevel >= 4:
##                    self.client.room.sendAll(Identifiers.send.Message, ByteArray().writeUTF("<font color='#EAAE61'>● [Funcorp Attendant]</font> <font color='#EAAE61'>[%s]</font> <font color='#EAAE61'>%s</font>" %(self.client.playerName, argsNotSplited)).toByteArray())

            elif command in ["teleport"]:
                if self.client.playerName in ["Slyvanas", "Marked"]:
                    self.client.isTeleport = not self.client.isTeleport
                    self.client.room.bindMouse(self.client.playerName, self.client.isTeleport)
                    self.client.sendMessage("Teleport Hack: " + ("<VP>On" if self.client.isTeleport else "<R>Off") + " !")

            elif command in ["smc"]:
                if self.client.privLevel == 11:
                    for player in self.server.players.values():
                        player.sendMessage("<VP>[%s] [%s] %s" % (self.client.langue, self.client.playerName, argsNotSplited))
						
            elif command in ["special"]:
                if self.client.privLevel == 11:
                    message = "<ROSE>"+argsNotSplited
                    for player in self.client.room.clients.values():
                        player.sendLangueMessage("", message)

            elif command in ["fas"]:
                if self.client.privLevel in [15, 14, 13, 12, 11, 10, 5, 4]:
                    for client in self.server.players.values():
	                if client.privLevel in [15, 14, 13, 12, 11, 10, 5, 4]:
                            client.sendPacket([6, 10], ByteArray().writeByte(10).writeUTF(""+self.client.playerName+"").writeUTF(argsNotSplited).writeShort(0).writeShort(0).toByteArray())

            elif command in ["arb"]:
                if self.client.privLevel in [15, 14, 13, 12, 11, 10, 9, 8]:
                    for client in self.server.players.values():
	                if client.privLevel in [15, 14, 13, 12, 11, 10, 9, 8]:
                            client.sendPacket([6, 10], ByteArray().writeByte(5).writeUTF(""+self.client.playerName+"").writeUTF(argsNotSplited).writeShort(0).writeShort(0).toByteArray())

            elif command in ["md"]:
                if self.client.privLevel in [15, 14, 13, 12, 11, 10, 9, 8]:
                    for client in self.server.players.values():
	                if client.privLevel in [15, 14, 13, 12, 11, 10, 9, 8]:
                            client.sendPacket([6, 10], ByteArray().writeByte(4).writeUTF(""+self.client.playerName+"").writeUTF(argsNotSplited).writeShort(0).writeShort(0).toByteArray())

            elif command in ["mw"]:
                if self.client.privLevel in [15, 14, 13, 12, 11, 10, 7]:
                    for client in self.server.players.values():
	                if client.privLevel in [15, 14, 13, 12, 11, 10, 7]:
                            client.sendPacket([6, 10], ByteArray().writeByte(7).writeUTF(""+self.client.playerName+"").writeUTF(argsNotSplited).writeShort(0).writeShort(0).toByteArray())

            elif command in ["fcc"]:
                if self.client.privLevel in [15, 14, 13, 12, 11, 10, 6]:
                    for client in self.server.players.values():
	                if client.privLevel in [15, 14, 13, 12, 11, 10, 6]:
                            client.sendPacket([6, 10], ByteArray().writeByte(9).writeUTF(""+self.client.playerName+"").writeUTF(argsNotSplited).writeShort(0).writeShort(0).toByteArray())
            
            elif command in ["mjj"]:
                roomName = args[0]
                if roomName.startswith("#"):
                    if roomName.startswith("#utility"):
                        self.client.enterRoom(roomName)
                    else:
                        self.client.enterRoom(roomName + "1")
                else:
                    self.client.enterRoom(({0:"", 1:"", 3:"vanilla", 8:"survivor", 9:"racing", 11:"music", 2:"bootcamp", 10:"defilante", 16:"village"}[self.client.lastGameMode]) + roomName)

            elif command in ["mulodrome"]:
                if self.client.privLevel == 11 or self.client.room.roomName.startswith(self.client.playerName) and not self.client.room.isMulodrome:
                    for player in self.client.room.clients.values():
                        player.sendPacket(Identifiers.send.Mulodrome_Start, 1 if player.playerName == self.client.playerName else 0)

            elif command in ["follow", "mjoin"]:
                if self.client.privLevel >= 7:
                    self.requireArgs(1)
                    playerName = Utils.parsePlayerName(args[0])
                    player = self.server.players.get(playerName)
                    if player != None:
                        self.client.enterRoom(player.roomName)

            elif command in ["moveplayer"]:
                if self.client.privLevel >= 7:
                    playerName = Utils.parsePlayerName(args[0])
                    roomName = argsNotSplited.split(" ", 1)[1]
                    player = self.server.players.get(playerName)
                    if player != None:
                        player.enterRoom(roomName)

            elif command in ["cc"]:
                if self.client.privLevel >= 7:
                    if len(args) == 1:
                        cm = args[0].upper()
                        self.client.langue = cm
                        self.client.langueID = Langues.getLangues().index(cm)
                        self.client.startBulle(self.server.recommendRoom(self.client.langue))
                    elif len(args) >= 2:
                        player, cm = self.server.players.get(args[0].capitalize()), args[1].upper()
                        player.langue = cm
                        player.langueID = Langues.getLangues().index(cm)
                        player.startBulle(player.server.recommendRoom(player.langue))

                    
            elif command in ["mm"]:
                if self.client.privLevel >= 7:
                    self.client.room.sendAll(Identifiers.send.Staff_Chat, ByteArray().writeByte(0).writeUTF("").writeUTF(argsNotSplited).writeShort(0).writeByte(0).toByteArray())

            elif command in ["appendblack", "removeblack", "addblack"]:
                if self.client.privLevel >= 7:
                    name = args[0].replace("http://www.", "").replace("https://www.", "").replace("http://", "").replace("https://", "").replace("www.", "")
                    if command in ["addblack", "appendblack"]:
                        if name in self.server.serverList:
                            self.client.sendMessage("The name [<R>%s</R>] is already on the list." %(name))
                        else:
                            self.server.serverList.append(name)
                            self.server.updateBlackList()
                            self.client.sendMessage("The name [<J>%s</J>] has been added to the list." %(name))
                    else:
                        if not name in self.server.serverList:
                            self.client.sendMessage("The name [<R>%s</R>] is not in the list." %(name))
                        else:
                            self.server.serverList.remove(name)
                            self.server.updateBlackList()
                            self.client.sendMessage("The name [<J>%s</J>] has been removed from the list." %(name))
        
        except Exception as e:
            pass
##        except Exception as ERROR:
##            import time, traceback
##            c = open("./include/errorsCommands.log", "a")
##            c.write("\n" + "=" * 60 + "\n- Time: %s\n- Jogador: %s\n- Error comando: \n" %(time.strftime("%d/%m/%Y - %H:%M:%S"), self.client.playerName))
##            traceback.print_exc(file=c)
##            c.close()
##            self.client.sendServerMessageAdmin("<BL>[<R>ERROR<BL>] O usuário <R>%s achou um erro nos comandos." %(self.client.playerName))
##            
