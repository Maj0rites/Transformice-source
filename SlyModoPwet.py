from utils import Utils
from ByteArray import ByteArray
from Identifiers import Identifiers
import math

class ModoPwet:

    def __init__(self, player, server):
        self.client = player
        self.server = player.server

    def checkReport(self, array, playerName):
        return playerName in array

    def makeReport(self, playerName, type, comments):
        playerName = Utils.parsePlayerName(playerName)
        repatan = self.client.playerName
        self.client.sendServerMessageAdmin('[REPORT] [<V>%s</V>] <V>%s</V>' % (repatan,playerName))          
        #self.server.sendStaffMessage(8, '[REPORT] [<V>%s</V>] by <V>[%s]</V> reported and reason: <J>%s</J> -> <V>%s</V>' % (repatan,playerName,{0: 'Hack',1: 'Spam / Flood',2: 'Insultos',3: 'Phishing',4: 'Others'}[type],'-' if comments == '' else comments))

        if self.server.players.get(playerName):
            if self.server.reports.has_key(playerName):
                if self.server.reports[playerName]['reporters'].has_key(repatan):
                    r = self.server.reports[playerName]['reporters'][repatan]
                    if r[0] != type:
                        self.server.reports[playerName]['reporters'][repatan]=[type,comments,Utils.getTime()]
                        
                else:
                    self.server.reports[playerName]['reporters'][repatan]=[type,comments,Utils.getTime()]
                self.server.reports[playerName]['durum'] = 'online' if self.server.checkConnectedAccount(playerName) else 'disconnected'
            else:
                self.server.reports[playerName] = {}
                self.server.reports[playerName]['reporters'] = {repatan:[type,comments,Utils.getTime()]}
                self.server.reports[playerName]['durum'] = 'online' if self.server.checkConnectedAccount(playerName) else 'disconnected'
                self.server.reports[playerName]['dil'] = self.getModopwetLangue(playerName)
                self.server.reports[playerName]['isMuted'] = False
            self.updateModoPwet()
            self.client.sendBanConsideration()

    def getModopwetLangue(self, playerName):
        player = self.server.players.get(playerName)
        if player != None:
            return player.langue
        else:
            return 'EN'

    def updateModoPwet(self):
        for player in self.server.players.values():
            if player.isModoPwet and player.privLevel >= 5:
                player.modoPwet.openModoPwet(True)

    def getPlayerRoomName(self, playerName):
        player = self.server.players.get(playerName)
        if player != None:
            return player.roomName
        else:
            return '0'
            
    def getRoomMods(self,room):
        s = []
        i = ""
        for player in self.server.players.values():
            if player.roomName == room and player.privLevel >= 5:
                s.append(player.playerName)
                
        if len(s) == 1:
            return s[0]
        else:
            for isim in s:
                i = i+isim+", "
        return i
        
    def getPlayerKarma(self, playerName):
        player = self.server.players.get(playerName)
        if player:
            return player.playerKarma
        else:
            return 0
    
    def banHack(self, playerName,iban):
        if self.server.banPlayer(playerName, 360, "Hack (last warning before account deletion)", self.client.playerName, iban):
            self.server.sendStaffMessage(5, "<V>%s<BL> baniu <V>%s<BL> por <V>360 <BL>horas. Motivo: <V>Hack (last warning before account deletion)<BL>." %(self.client.playerName, playerName))
        self.updateModoPwet()
        
    def deleteReport(self,playerName,handled):
        if handled == 0:
            self.server.reports[playerName]["durum"] = "deleted"
            self.server.reports[playerName]["deletedby"] = self.client.playerName
        else:
            if self.server.reports.has_key(playerName):
                del self.server.reports[playerName]
                
        self.updateModoPwet()
        
    def sirala(self,verilen):
        for i in verilen[1]["reporters"]:
            return verilen[1]["reporters"][i][2]
            
    def sortReports(self,reports,sort):  
        if sort:
            return sorted(reports.items(), key=self.sirala,reverse=True)
        else:
            return sorted(reports.items(), key=lambda (x): len(x[1]["reporters"]),reverse=True)
    
    def openModoPwet(self,isOpen=False,modopwetOnlyPlayerReports=False,sortBy=False):
        if isOpen:
            if len(self.server.reports) <= 0:
                self.client.sendPacket(Identifiers.send.Modopwet_Open, 0)
            else:
                self.client.sendPacket(Identifiers.send.Modopwet_Open, 0)
                reports,bannedList,deletedList,disconnectList = self.sortReports(self.server.reports,sortBy),{},{},[]
                sayi = 0
                p = ByteArray()  
                for i in reports:
                    isim = i[0]
                    v = self.server.reports[isim]
                    if self.client.modoPwetLangue == 'ALL' or v["dil"] == self.client.modoPwetLangue:
                        oyuncu = self.server.players.get(isim)
                        saat = math.floor(oyuncu.playerTime/3600) if oyuncu else 0
                        odaisim = oyuncu.roomName if oyuncu else "0"
                        sayi += 1
                        self.client.lastReportID += 1
                        if sayi >= 255:
                            break  
                        p.writeByte(sayi)
                        p.writeShort(self.client.lastReportID)
                        p.writeUTF(v["dil"])
                        p.writeUTF(isim)
                        p.writeUTF(odaisim)
                        p.writeByte(1) # alttaki modname uzunlugu ile alakali
                        p.writeUTF(self.getRoomMods(odaisim))
                        p.writeInt(saat) #idk
                        p.writeByte(int(len(v["reporters"])))
                        for name in v["reporters"]:
                            r = v["reporters"][name]
                            p.writeUTF(name)
                            p.writeShort(self.getPlayerKarma(name)) #karma
                            p.writeUTF(r[1])
                            p.writeByte(r[0])
                            p.writeShort(int(Utils.getSecondsDiff(r[2])/60)) #05m felan rep suresi
                                
                        mute = v["isMuted"]
                        p.writeBoolean(mute) #isMute
                        if mute:
                            p.writeUTF(v["mutedBy"])
                            p.writeShort(v["muteHours"])
                            p.writeUTF(v["muteReason"])
                            
                        if v['durum'] == 'banned':
                            x = {}
                            x['banhours'] = v['banhours']
                            x['banreason'] = v['banreason']
                            x['bannedby'] = v['bannedby']
                            bannedList[isim] = x
                        if v['durum'] == 'deleted':
                            x = {}
                            x['deletedby'] = v['deletedby']
                            deletedList[isim] = x
                        if v['durum'] == 'disconnected':
                            disconnectList.append(isim)

                self.client.sendPacket(Identifiers.send.Modopwet_Open, ByteArray().writeByte(int(len(reports))).writeBytes(p.toByteArray()).toByteArray())
                for user in disconnectList:
                    self.changeReportStatusDisconnect(user)

                for user in deletedList.keys():
                    self.changeReportStatusDeleted(user, deletedList[user]['deletedby'])

                for user in bannedList.keys():
                    self.changeReportStatusBanned(user, bannedList[user]['banhours'], bannedList[user]['banreason'], bannedList[user]['bannedby'])

    def changeReportStatusDisconnect(self, playerName):
        self.client.sendPacket(Identifiers.send.Modopwet_Disconnected, ByteArray().writeUTF(playerName).toByteArray())

    def changeReportStatusDeleted(self, playerName, deletedby):
        self.client.sendPacket(Identifiers.send.Modopwet_Deleted, ByteArray().writeUTF(playerName).writeUTF(deletedby).toByteArray())

    def changeReportStatusBanned(self, playerName, banhours, banreason, bannedby):
        self.client.sendPacket(Identifiers.send.Modopwet_Banned, ByteArray().writeUTF(playerName).writeUTF(bannedby).writeInt(int(banhours)).writeUTF(banreason).toByteArray())

    def openChatLog(self, playerName):
        if self.server.chatMessages.has_key(playerName):
            packet = ByteArray().writeUTF(playerName).writeByte(len(self.server.chatMessages[playerName]))
            for message in self.server.chatMessages[playerName]:
                packet.writeUTF(message[1]).writeUTF(message[0])
            self.client.sendPacket(Identifiers.send.Modopwet_Chatlog, packet.toByteArray())
