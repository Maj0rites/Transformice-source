#coding: utf-8
# Modules
from utils import Utils
from ByteArray import ByteArray
from Identifiers import Identifiers
class Cafe:
    def __init__(self, player, server):
        self.client = player
        self.server = player.server
        # self.CursorCafe = player.server.CursorCafe
    
    def loadCafeMode(self):
        can = not self.client.isGuest
        
        if not can:
            self.client.sendLangueMessage("", "<ROSE>$PasAutoriseParlerSurServeur")
            
        self.client.sendPacket(Identifiers.send.Open_Cafe, ByteArray().writeBoolean(can).toByteArray())

        packet = ByteArray()
        konular = self.server.cafeTopics
        if len(konular) > 0:
            # for i,v in self.server.cafeTopics.items():
            for i,v in sorted(konular.items(), key=lambda x: x[1]["Tarih"],reverse=True):
                if v["Dil"] == self.client.langue:
                    konuid,baslik,sahip,yorumlar,sonyazan,tarih = v["KonuID"],v["Baslik"],v["Sahip"],v["Yorumlar"],v["SonYazan"],v["Tarih"]
                    packet.writeInt(konuid).writeUTF(baslik).writeInt(self.server.getPlayerID(sahip)).writeInt(yorumlar).writeUTF(sonyazan).writeInt(Utils.getSecondsDiff(tarih))
        
        self.client.sendPacket(Identifiers.send.Cafe_Topics_List, packet.toByteArray())
            

    def openCafeTopic(self, topicID):
        if self.server.cafeTopics.has_key(topicID):
            packet = ByteArray().writeBoolean(True).writeInt(topicID)
            for id,v in self.server.cafePosts[topicID].items():
                yorumid,yorumyazan,yorumtarih,mesaj,puan,verenler = v["YorumID"],v["YorumYazan"],v["YorumTarih"],v["YorumMesaj"],v["Puan"],v["OyVerenler"]
                packet.writeInt(yorumid).writeInt(self.server.getPlayerID(yorumyazan)).writeInt(Utils.getSecondsDiff(yorumtarih)).writeUTF(yorumyazan).writeUTF(mesaj).writeBoolean(str(self.client.playerID) not in verenler).writeShort(puan)
            self.client.sendPacket(Identifiers.send.Open_Cafe_Topic, packet.toByteArray())
        
    def createNewCafeTopic(self, title, message):
        id = len(self.server.cafeTopics)+1
        self.server.cafeTopics[id] = {}
        self.server.cafeTopics[id]["KonuID"] = id
        self.server.cafeTopics[id]["Baslik"] = "CENSORED" if self.server.checkMessage(title) else title
        self.server.cafeTopics[id]["Sahip"] = self.client.playerName
        self.server.cafeTopics[id]["Yorumlar"] = 0
        self.server.cafeTopics[id]["SonYazan"] = self.client.playerName
        self.server.cafeTopics[id]["Tarih"] = Utils.getTime()
        self.server.cafeTopics[id]["Dil"] = self.client.langue
        self.createNewCafePost(id, "CENSORED" if self.server.checkMessage(message) else message)
        self.loadCafeMode()

    def createNewCafePost(self, topicID, message):
        commentsCount = 0
        if not self.server.cafeTopics.has_key(topicID): return
        
        if not self.server.cafePosts.has_key(topicID):
            self.server.cafePosts[topicID] = {}
            
        id = len(self.server.cafePosts[topicID])+1 #yorum id
        self.server.cafePosts[topicID][id] = {}
        self.server.cafePosts[topicID][id]["KonuID"] = topicID
        self.server.cafePosts[topicID][id]["YorumID"] = id
        self.server.cafePosts[topicID][id]["YorumYazan"] = self.client.playerName
        self.server.cafePosts[topicID][id]["YorumMesaj"] = "CENSORED" if self.server.checkMessage(message) else message
        self.server.cafePosts[topicID][id]["YorumTarih"] = Utils.getTime()
        self.server.cafePosts[topicID][id]["Puan"] = 0
        self.server.cafePosts[topicID][id]["OyVerenler"] = []
            
        self.server.cafeTopics[topicID]["Yorumlar"] += 1
        self.server.cafeTopics[topicID]["SonYazan"] = self.client.playerName
        self.server.cafeTopics[topicID]["Tarih"] = Utils.getTime()

        commentsCount = self.server.cafeTopics[topicID]["Yorumlar"]
        self.openCafeTopic(topicID)
        for player in self.server.players.values():
            if player.isCafe:
                player.sendPacket(Identifiers.send.Cafe_New_Post, ByteArray().writeInt(topicID).writeUTF(self.client.playerName).writeInt(commentsCount).toByteArray())
       
    def voteCafePost(self, topicID, postID, mode):
        try:
            if not self.client.playerID in self.server.cafePosts[topicID][postID]["OyVerenler"]:
                puan = self.server.cafePosts[topicID][postID]["Puan"]
                playerid = str(self.client.playerID)

                self.server.cafePosts[topicID][postID]["OyVerenler"].append(playerid) 
                if mode:
                    self.server.cafePosts[topicID][postID]["Puan"] += 1
                else:
                    self.server.cafePosts[topicID][postID]["Puan"] -= 1

                self.openCafeTopic(topicID)
        except: pass

    def deleteCafePost(self, topicID, postID):   
        del self.server.cafePosts[topicID][postID]
        
        self.server.cafeTopics[topicID]["Yorumlar"] -= 1
        
        if len(self.server.cafePosts[topicID]) < 1:
            del self.server.cafeTopics[topicID]
            
        for player in self.server.players.values():
            if player.isCafe:
                player.sendPacket(Identifiers.send.Delete_Cafe_Message, ByteArray().writeInt(topicID).writeInt(postID).toByteArray())
        
        self.openCafeTopic(topicID)

    def deleteAllCafePost(self, topicID, playerName):
        if self.server.cafeTopics[topicID]["Sahip"] == playerName:
            del self.server.cafePosts[topicID]
            del self.server.cafeTopics[topicID]
        else:
            for id,v in self.server.cafePosts[topicID].items():
                if v["YorumYazan"] == playerName:
                    del self.server.cafePosts[topicID][id]
                    
        self.loadCafeMode()
        self.openCafeTopic(topicID)
