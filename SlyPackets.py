#coding: utf-8
#İmp - Slyvanas
import re, json, random, urllib, traceback, time as _time, struct

# Game
from utils import Utils
from ByteArray import ByteArray
from Identifiers import Identifiers

# Library
from collections import deque
from twisted.internet import reactor

class Packets:
    def __init__(self, player, server):
        self.client = player
        self.server = player.server
        self.Cursor = player.Cursor

    def parsePacket(self, packetID, C, CC, packet):
        if C == Identifiers.recv.Old_Protocol.C:
            if CC == Identifiers.recv.Old_Protocol.Old_Protocol:
                data = packet.readUTF()
                self.client.Packets.parsePacketUTF(data)
                return

        elif C == Identifiers.recv.Sync.C:
            if CC == Identifiers.recv.Sync.Object_Sync:
                roundCode = packet.readInt()
                if roundCode == self.client.room.lastRoundCode:
                    packet2 = ByteArray()
                    while packet.bytesAvailable():
                        objectID = packet.readShort()
                        objectCode = packet.readShort()
                        if objectCode == -1:
                            packet2.writeShort(objectID)
                            packet2.writeShort(-1)
                        else:
                            posX = packet.readShort()
                            posY = packet.readShort()
                            velX = packet.readShort()
                            velY = packet.readShort()
                            rotation = packet.readShort()
                            rotationSpeed = packet.readShort()
                            ghost = packet.readBoolean()
                            stationary = packet.readBoolean()
                            packet2.writeShort(objectID).writeShort(objectCode).writeShort(posX).writeShort(posY).writeShort(velX).writeShort(velY).writeShort(rotation).writeShort(rotationSpeed).writeBoolean(ghost).writeBoolean(stationary).writeBoolean(self.client.room.getAliveCount() > 1)
                    self.client.room.sendAllOthers(self.client, Identifiers.send.Sync, packet2.toByteArray())
                return

            elif CC == Identifiers.recv.Sync.Mouse_Movement:
                roundCode, droiteEnCours, gaucheEnCours, px, py, vx, vy, jump, jump_img, portal, isAngle = packet.readInt(), packet.readBoolean(), packet.readBoolean(), packet.readUnsignedInt(), packet.readUnsignedInt(), packet.readUnsignedShort(), packet.readUnsignedShort(), packet.readBoolean(), packet.readByte(), packet.readByte(), packet.bytesAvailable(),
                angle = packet.readUnsignedShort() if isAngle else -1
                vel_angle = packet.readUnsignedShort() if isAngle else -1
                loc_1 = packet.readBoolean() if isAngle else False

                if roundCode == self.client.room.lastRoundCode:
                    if droiteEnCours or gaucheEnCours:
                        self.client.isMovingRight = droiteEnCours
                        self.client.isMovingLeft = gaucheEnCours

                        if self.client.isAfk:
                            self.client.isAfk = False

                    self.client.posX = px * 800 / 2700
                    self.client.posY = py * 800 / 2700
                    self.client.velX = vx
                    self.client.velY = vy
                    self.client.isJumping = jump
                
                    packet2 = ByteArray().writeInt(self.client.playerCode).writeInt(roundCode).writeBoolean(droiteEnCours).writeBoolean(gaucheEnCours).writeUnsignedInt(px).writeUnsignedInt(py).writeUnsignedShort(vx).writeUnsignedShort(vy).writeBoolean(jump).writeByte(jump_img).writeByte(portal)
                    if isAngle:
                        packet2.writeUnsignedShort(angle).writeUnsignedShort(vel_angle).writeBoolean(loc_1)
                    self.client.room.sendAllOthers(self.client, Identifiers.send.Player_Movement, packet2.toByteArray())
                return
            
            elif CC == Identifiers.recv.Sync.Mort:
                roundCode, loc_1 = packet.readInt(), packet.readByte()
                if roundCode == self.client.room.lastRoundCode:
                    self.client.isDead = True
                    if not self.client.room.noAutoScore: self.client.playerScore += 1
                    self.client.sendPlayerDied()

                    if self.client.room.getPlayerCountUnique() >= self.server.needToFirst:
                        if self.client.room.isSurvivor:
                            for playerCode, client in self.client.room.clients.items():
                                if client.isShaman:
                                    client.survivorDeath += 1

                                    if client.survivorDeath == 4:
                                        id = 2260
                                        if not id in client.playerConsumables:
                                            client.playerConsumables[id] = 1
                                        else:
                                            count = client.playerConsumables[id] + 1
                                            client.playerConsumables[id] = count
                                        client.sendAnimZeldaInventory(4, id, 1)
                                        client.survivorDeath = 0

                    if not self.client.room.currentShamanName == "":
                        player = self.client.room.clients.get(self.client.room.currentShamanName)

                        if player != None and not self.client.room.noShamanSkills:
                            if player.bubblesCount > 0:
                                if self.client.room.getAliveCount() != 1:
                                    player.bubblesCount -= 1
                                    self.client.sendPlaceObject(self.client.room.objectID + 2, 59, self.client.posX, 450, 0, 0, 0, True, True)

                            if player.desintegration:
                                self.client.Skills.sendSkillObject(6, self.client.posX, 395, 0)
                    self.client.room.checkChangeMap()
                return

            elif CC == Identifiers.recv.Sync.Player_Position:
                direction = packet.readBoolean()
                self.client.room.sendAll(Identifiers.send.Player_Position, ByteArray().writeInt(self.client.playerCode).writeBoolean(direction).toByteArray())
                return

            elif CC == Identifiers.recv.Sync.Shaman_Position:
                direction = packet.readBoolean()
                self.client.room.sendAll(Identifiers.send.Shaman_Position, ByteArray().writeInt(self.client.playerCode).writeBoolean(direction).toByteArray())
                return

            elif CC == Identifiers.recv.Sync.Crouch:
                crouch = packet.readByte()
                self.client.room.sendAll(Identifiers.send.Crouch, ByteArray().writeInt(self.client.playerCode).writeByte(crouch).writeByte(0).toByteArray())
                return

        elif C == Identifiers.recv.Room.C:
            if CC == Identifiers.recv.Room.Map_26:
                if self.client.room.currentMap == 26:
                    posX, posY, width, height = packet.readShort(), packet.readShort(), packet.readShort(), packet.readShort()

                    bodyDef = {}
                    bodyDef["type"] = 12
                    bodyDef["width"] = width
                    bodyDef["height"] = height
                    self.client.room.addPhysicObject(0, posX, posY, bodyDef)
                return

            elif CC == Identifiers.recv.Room.Shaman_Message:
                type, x, y = packet.readByte(), packet.readShort(), packet.readShort()
                self.client.room.sendAll(Identifiers.send.Shaman_Message, ByteArray().writeByte(type).writeShort(x).writeShort(y).toByteArray())
                return

            elif CC == Identifiers.recv.Room.Convert_Skill:
                objectID = packet.readInt()
                self.client.Skills.sendConvertSkill(objectID)
                return

            elif CC == Identifiers.recv.Room.Demolition_Skill:
                objectID = packet.readInt()
                self.client.Skills.sendDemolitionSkill(objectID)
                return

            elif CC == Identifiers.recv.Room.Projection_Skill:
                posX, posY, dir = packet.readShort(), packet.readShort(), packet.readShort()
                self.client.Skills.sendProjectionSkill(posX, posY, dir)
                return

            elif CC == Identifiers.recv.Room.Enter_Hole:
                holeType, roundCode, monde, distance, holeX, holeY = packet.readByte(), packet.readInt(), packet.readInt(), packet.readShort(), packet.readShort(), packet.readShort()
                if roundCode == self.client.room.lastRoundCode and (self.client.room.currentMap == -1 or monde == self.client.room.currentMap or self.client.room.EMapCode != 0):
                    self.client.playerWin(holeType, distance)
                return

            elif CC == Identifiers.recv.Room.Get_Cheese:
                roundCode, cheeseX, cheeseY, distance = packet.readInt(), packet.readShort(), packet.readShort(), packet.readShort()
                if roundCode == self.client.room.lastRoundCode:
                    self.client.sendGiveCheese(distance)
                return

            elif CC == Identifiers.recv.Room.Place_Object:
                if not self.client.isShaman:
                    return

                roundCode, objectID, code, px, py, angle, vx, vy, dur, origin = packet.readByte(), packet.readInt(), packet.readShort(), packet.readShort(), packet.readShort(), packet.readShort(), packet.readByte(), packet.readByte(), packet.readBoolean(), packet.readBoolean()
                if self.client.room.isTotemEditor:
                    if self.client.tempTotem[0] < 20:
                        self.client.tempTotem[0] = int(self.client.tempTotem[0]) + 1
                        self.client.sendTotemItemCount(self.client.tempTotem[0])
                        self.client.tempTotem[1] += "#2#" + chr(1).join(map(str, [code, px, py, angle, vx, vy, dur]))
                else:
                    if code == 44:
                        if not self.client.useTotem:
                            self.client.sendTotem(self.client.totem[1], px, py, self.client.playerCode)
                            self.client.useTotem = True

                    self.client.sendPlaceObject(objectID, code, px, py, angle, vx, vy, dur, False)
                    self.client.Skills.placeSkill(objectID, code, px, py, angle)
                return

            elif CC == Identifiers.recv.Room.Ice_Cube:
                playerCode, px, py = packet.readInt(), packet.readShort(), packet.readShort()
                if self.client.isShaman and not self.client.isDead and not self.client.room.isSurvivor and self.client.room.numCompleted > 1:
                    if self.client.iceCount != 0 and playerCode != self.client.playerCode:
                        for player in self.client.room.clients.values():
                            if player.playerCode == playerCode and not player.isShaman:
                                player.isDead = True
                                if not self.client.room.noAutoScore: self.client.playerScore += 1
                                player.sendPlayerDied()
                                self.client.sendPlaceObject(self.client.room.objectID + 2, 54, px, py, 0, 0, 0, True, True)
                                self.client.iceCount -= 1
                                self.client.room.checkChangeMap()
                return

            elif CC == Identifiers.recv.Room.Bridge_Break:
                if self.client.room.currentMap in [6, 10, 110, 116]:
                    bridgeCode = packet.readShort()
                    self.client.room.sendAllOthers(self.client, Identifiers.send.Bridge_Break, ByteArray().writeShort(bridgeCode).toByteArray())
                return

            elif CC == Identifiers.recv.Room.Defilante_Points:
                self.client.defilantePoints += 1
                return

            elif CC == Identifiers.recv.Room.Restorative_Skill:
                objectID, id = packet.readInt(), packet.readInt()
                self.client.Skills.sendRestorativeSkill(objectID, id)
                return

            elif CC == Identifiers.recv.Room.Recycling_Skill:
                id = packet.readShort()
                self.client.Skills.sendRecyclingSkill(id)
                return

            elif CC == Identifiers.recv.Room.Gravitational_Skill:
                velX, velY = packet.readShort(), packet.readShort()
                self.client.Skills.sendGravitationalSkill(0, velX, velY)
                return

            elif CC == Identifiers.recv.Room.Antigravity_Skill:
                objectID = packet.readInt()
                self.client.Skills.sendAntigravitySkill(objectID)
                return

            elif CC == Identifiers.recv.Room.Handymouse_Skill:
                handyMouseByte, objectID = packet.readByte(), packet.readInt()
                if self.client.room.lastHandymouse[0] == -1:
                    self.client.room.lastHandymouse = [objectID, handyMouseByte]
                else:
                    self.client.Skills.sendHandymouseSkill(handyMouseByte, objectID)
                    self.client.room.sendAll(Identifiers.send.Skill, chr(77) + chr(1))
                    self.client.room.lastHandymouse = [-1, -1]
                return

            elif CC == Identifiers.recv.Room.Enter_Room:
                community, roomName, isSalonAuto = packet.readByte(), packet.readUTF(), packet.readBoolean()
                if isSalonAuto or roomName == "":
                    self.client.startBulle(self.server.recommendRoom(self.client.langue))
                elif not roomName == self.client.roomName or not self.client.room.isEditor or not len(roomName) > 64 or not self.client.roomName == "%s-%s" %(self.client.langue, roomName):
                    if self.client.privLevel < 8: roomName = self.server.checkRoom(roomName, self.client.langue)
                    roomEnter = self.server.rooms.get(roomName if roomName.startswith("*") else ("%s-%s" %(self.client.langue, roomName)))
                    if roomEnter == None or self.client.privLevel >= 7:
                        self.client.startBulle(roomName)
                    else:
                        if not roomEnter.roomPassword == "":
                            self.client.sendPacket(Identifiers.send.Room_Password, ByteArray().writeUTF(roomName).toByteArray())
                        else:
                            self.client.startBulle(roomName)
                return

            elif CC == Identifiers.recv.Room.Room_Password:
                roomPass, roomName = packet.readUTF(), packet.readUTF()
                roomEnter = self.server.rooms.get(roomName if roomName.startswith("*") else ("%s-%s" %(self.client.langue, roomName)))
                if roomEnter == None or self.client.privLevel >= 7:
                    self.client.startBulle(roomName)
                else:
                    if not roomEnter.roomPassword == roomPass:
                        self.client.sendPacket(Identifiers.send.Room_Password, ByteArray().writeUTF(roomName).toByteArray())
                    else:
                        self.client.startBulle(roomName)
                return

            elif CC == Identifiers.recv.Room.Send_Music:
                url = packet.readUTF()
                id = Utils.getYoutubeID(url)
                if (id == None):
                    self.client.sendLangueMessage("", "$ModeMusic_ErreurVideo")
                else:
                    myUrl = urllib.urlopen("https://www.googleapis.com/youtube/v3/videos?id=" + id + "&key=AIzaSyDQ7jD1wcD5A_GeV4NfZqWJswtLplPDr74&part=snippet,contentDetails")
                    data = json.loads(myUrl.read())
                    if data["pageInfo"]["totalResults"] == 0:
                        self.client.sendLangueMessage("", "$ModeMusic_ErreurVideo")
                    else:
                        duration = Utils.Duration(data["items"][0]["contentDetails"]["duration"])
                        duration = 300 if duration > 300 else duration
                        title = data["items"][0]["snippet"]["title"]
                        if (filter(lambda music: music["By"] == (self.client.playerName), self.client.room.musicVideos)):
                            self.client.sendLangueMessage("", "$ModeMusic_VideoEnAttente")
                        elif (filter(lambda music: music["Title"] == (title), self.client.room.musicVideos)):
                            self.client.sendLangueMessage("", "$DejaPlaylist");
                        else:
                            self.client.sendLangueMessage("", "$ModeMusic_AjoutVideo", str(len(self.client.room.musicVideos) + 1))
                            values = {}
                            values["By"] = self.client.playerName
                            values["Title"] = title
                            values["Duration"] = str(duration)
                            values["VideoID"] = id
                            self.client.room.musicVideos.append(values)
                            if (len(self.client.room.musicVideos) == 1):
                                self.client.sendMusicVideo(True)
                                self.client.room.isPlayingMusic = True
                                self.client.room.musicSkipVotes = 0

                    return

            elif CC == Identifiers.recv.Room.Send_PlayList:
                packet = ByteArray().writeShort(len(self.client.room.musicVideos))
                for music in self.client.room.musicVideos:
                    packet.writeUTF(music["Title"]).writeUTF(music["By"])
                self.client.sendPacket(Identifiers.send.Music_PlayList, packet.toByteArray())
                return

            elif CC == Identifiers.recv.Room.Music_Time:
                time = packet.readInt()
                if len(self.client.room.musicVideos) > 0:
                    self.client.room.musicTime = time
                    duration = self.client.room.musicVideos[0]["Duration"]
                    if time >= int(duration) - 5 and self.client.room.canChangeMusic:
                        self.client.room.canChangeMusic = False
                        del self.client.room.musicVideos[0]
                        self.client.room.musicTime = 1
                        if len(self.client.room.musicVideos) >= 1:
                            self.client.sendMusicVideo(True)
                        else:
                            self.client.room.isPlayingMusic = False
                            self.client.room.musicTime = 0
                return
            
        elif C == Identifiers.recv.Others.C:
            if CC == Identifiers.recv.Others.Daily_Quest_Open:
                self.client.DailyQuest.sendDailyQuest()
                return

            elif CC == Identifiers.recv.Others.Daily_Quest_Change:
                missionID = packet.readShort()
                self.client.DailyQuest.changeMission(int(missionID), int(self.client.playerID))
                self.client.DailyQuest.sendDailyQuest()
                return
            

        elif C == Identifiers.recv.Chat.C:
            if CC == Identifiers.recv.Chat.Chat_Message:
                #packet = self.descriptPacket(packetID, packet)
                message = packet.readUTF().replace("&amp;#", "&#").replace("<", "&lt;")
		if self.client.isGuest:
                    self.client.sendLangueMessage("", "$Créer_Compte_Parler")
                elif message == "!lb":
                    self.client.sendLeaderBoard()
                elif message == "!lsrec":
                    self.client.sendTotalRec()
                elif message == "!listrec":
                    self.client.sendListRec()
                elif not message == "" and len(message) < 256:
                    if self.client.isMute:
                        muteInfo = self.server.getModMuteInfo(self.client.playerName)
                        timeCalc = Utils.getHoursDiff(muteInfo[1])          
                        if timeCalc <= 0:
                            self.client.isMute = False
                            self.server.removeModMute(self.client.playerName)
                            self.client.room.sendAllChat(self.client.playerCode, self.client.playerName if self.client.mouseName == "" else self.client.mouseName, message, self.client.langueID, self.server.checkMessage(message))
                        else:
                            self.client.sendModMute(self.client.playerName, timeCalc, muteInfo[0], True)
                            return
                    else:
                        if self.client.room.isUtility == True:
                            self.client.Utility.isCommand = False
                            if message.startswith("!"):
                                self.client.Utility.sentCommand(message)
                            if self.client.Utility.isCommand == True:
                                message = ""
                        if not self.client.chatdisabled:
                            if not message == self.client.lastMessage:
                                self.client.lastMessage = message
                                self.client.room.sendAllChat(self.client.playerCode, self.client.playerName if self.client.mouseName == "" else self.client.mouseName, message, self.client.langueID, self.server.checkMessage(message))
                                reactor.callLater(0.9, self.client.chatEnable)
                                self.client.chatdisabled = True
                            else:
                                self.client.sendLangueMessage("", "$Message_Identique")
                        else:
                            self.client.sendLangueMessage("", "$Doucement")

                    if not self.server.chatMessages.has_key(self.client.playerName):
                        messages = deque([], 60)
                        messages.append([_time.strftime("%Y/%m/%d %H:%M:%S"), message])
                        self.server.chatMessages[self.client.playerName] = messages
                    else:
                        self.server.chatMessages[self.client.playerName].append([_time.strftime("%Y/%m/%d %H:%M:%S"), message])
                return
##                else:
##                    self.client.sendMessage("<ROSE>You need 3 cheeses to speak.")

           

            elif CC == Identifiers.recv.Chat.Staff_Chat:
                type, message = packet.readByte(), packet.readUTF() 
                level = self.client.privLevel
                if level >= (5 if type == 5 else 6 if type == 7  else 7 if type == 0 or type == 4 or type == 3 or type == 2 else 8 if type == 1 else 10):
                    self.client.sendAllModerationChat(type, message)
                return
                
                        
        # 2: arbitre,
        # 3: modo,
        # 7: mapcrew,
        # 8: luateam,
        # 9: funcorp,
        # 10: fashionsquad

            
 
                
            

            elif CC == Identifiers.recv.Chat.Commands:
                command = packet.readUTF()
                try:
                    if _time.time() - self.client.CMDTime > 1:
                        self.client.Commands.parseCommand(command)
                        self.client.CMDTime = _time.time()
                except Exception as e:
                    with open("./logs/CommandBugs.log", "a") as f:
                        traceback.print_exc(file=f)
                        f.write("\n")
                return

        elif C == Identifiers.recv.Player.C:
            if CC == Identifiers.recv.Player.Emote:
                emoteID, playerCode = packet.readByte(), packet.readInt()
                flag = packet.readUTF() if emoteID == 10 else ""
                self.client.sendPlayerEmote(emoteID, flag, True, False)
                if playerCode != -1:
                    if emoteID == 14:
                        self.client.sendPlayerEmote(14, flag, False, False)
                        self.client.sendPlayerEmote(15, flag, False, False)
                        player = filter(lambda p: p.playerCode == playerCode, self.server.players.values())[0]
                        if player != None:
                            player.sendPlayerEmote(14, flag, False, False)
                            player.sendPlayerEmote(15, flag, False, False)

                    elif emoteID == 18:
                        self.client.sendPlayerEmote(18, flag, False, False)
                        self.client.sendPlayerEmote(19, flag, False, False)
                        player = filter(lambda p: p.playerCode == playerCode, self.server.players.values())[0]
                        if player != None:
                            player.sendPlayerEmote(17, flag, False, False)
                            player.sendPlayerEmote(19, flag, False, False)

                    elif emoteID == 22:
                        self.client.sendPlayerEmote(22, flag, False, False)
                        self.client.sendPlayerEmote(23, flag, False, False)
                        player = filter(lambda p: p.playerCode == playerCode, self.server.players.values())[0]
                        if player != None:
                            player.sendPlayerEmote(22, flag, False, False)
                            player.sendPlayerEmote(23, flag, False, False)

                    elif emoteID == 26:
                        self.client.sendPlayerEmote(26, flag, False, False)
                        self.client.sendPlayerEmote(27, flag, False, False)
                        player = filter(lambda p: p.playerCode == playerCode, self.server.players.values())[0]
                        if player != None:
                            player.sendPlayerEmote(26, flag, False, False)
                            player.sendPlayerEmote(27, flag, False, False)
                            self.client.room.sendAll(Identifiers.send.Joquempo, ByteArray().writeInt(self.client.playerCode).writeByte(random.randint(0, 2)).writeInt(player.playerCode).writeByte(random.randint(0, 2)).toByteArray())

                if self.client.isShaman:
                    self.client.Skills.parseEmoteSkill(emoteID)
                return
                    
            elif CC == Identifiers.recv.Player.Langue:
                self.client.langueID = packet.readByte()
                langue = Utils.getTFMLangues(self.client.langueID)
                self.client.langue = langue
                return

            elif CC == Identifiers.recv.Player.Emotions:
                emotion = packet.readByte()
                self.client.sendEmotion(emotion)
                return

            elif CC == Identifiers.recv.Player.Shaman_Fly:
                fly = packet.readBoolean()
                self.client.Skills.sendShamanFly(fly)
                return

            elif CC == Identifiers.recv.Player.Shop_List:
                self.client.Shop.sendShopList()
                return

            elif CC == Identifiers.recv.Player.Buy_Skill:
                skill = packet.readByte()
                self.client.Skills.buySkill(skill)
                return

            elif CC == Identifiers.recv.Player.Redistribute:
                self.client.Skills.redistributeSkills()
                return

            elif CC == Identifiers.recv.Player.Report:
                playerName, type, comments = packet.readUTF(), packet.readByte(), packet.readUTF()
                self.client.modoPwet.makeReport(playerName, type, comments)
                return

            elif CC == Identifiers.recv.Player.Ping:
                if (_time.time() - self.client.PInfo[1]) >= 5:
                    self.client.PInfo[1] = _time.time()
                    self.client.sendPacket(Identifiers.send.Ping, self.client.PInfo[0])
                    self.client.PInfo[0] += 1
                    if self.client.PInfo[0] == 31:
                        self.client.PInfo[0] = 0
                return

            
            
            elif CC == Identifiers.recv.Player.Meep:
                posX, posY = packet.readShort(), packet.readShort()
                self.client.room.sendAll(Identifiers.send.Meep_IMG, ByteArray().writeInt(self.client.playerCode).toByteArray())
                self.client.room.sendAll(Identifiers.send.Meep, ByteArray().writeInt(self.client.playerCode).writeShort(posX).writeShort(posY).writeInt(10 if self.client.isShaman else 5).toByteArray())
                return

            elif CC == Identifiers.recv.Player.Bolos:
                #print repr(packet.toByteArray())
                sla, sla2, id, type = packet.readByte(), packet.readByte(), packet.readByte(), packet.readByte()
                #print("ID: "+str(id)+ ", ID da aventura: "+str(sla2)+ ", Sla: "+str(sla))
                #.client.winEventMap()
                if not self.client.hasBolo:
                    p = ByteArray()
                    p.writeByte(52)
                    p.writeByte(1)
                    p.writeByte(2)
                    p.writeUTF(str(self.client.playerCode))
                    p.writeUTF(str(id))
                    self.client.room.sendAll([16, 10], p.toByteArray())
                    self.client.room.sendAll([100, 101], ByteArray().writeByte(2).writeInt(self.client.playerCode).writeUTF("x_Sly/x_aventure/x_recoltables/x_"+str((1 if id == 1 else 0))+".png").writeInt(-1900574).writeByte(0).writeShort(100).writeShort(0).toByteArray())
                    self.client.sendPacket([100, 101], "\x01\x01")
                    #self.client.room.sendAll([5, 53], ByteArray().writeByte(type).writeShort(id).toByteArray())
                    #self.client.room.sendAll([100, 101], ByteArray().writeByte(2).writeInt(self.client.playerCode).writeUTF("x_Sly/x_aventure/x_recoltables/x_"+1 if self.server.adventureID == 52 else 0+".png").writeInt(-1900574).writeByte(0).writeShort(100).writeShort(0).toByteArray())
                    #self.client.sendPacket([100, 101], "\x01\x00")
                    self.client.hasBolo = True
                    if not self.client.isGuest:
                        if id == 1:
                            self.client.selfGet = True
                return

            elif CC == Identifiers.recv.Player.Vampire:
                if self.client.room.isSurvivor:
                    self.client.sendVampireMode(True)
                return

        elif CC == Identifiers.recv.Player.Calendar:
                pass
                return

        elif C == Identifiers.recv.Buy_Fraises.C:
            if CC == Identifiers.recv.Buy_Fraises.Buy_Fraises:
                return

        elif C == Identifiers.recv.Tribe.C:
            if CC == Identifiers.recv.Tribe.Tribe_House:
                if not self.client.tribeName == "":
                    self.client.startBulle("*\x03%s" %(self.client.tribeName))
                return

            elif CC == Identifiers.recv.Tribe.Tribe_Invite:
                playerName = packet.readUTF()
                player = self.server.players.get(playerName)
                if player != None and player.tribeName in self.client.invitedTribeHouses:
                    if self.server.rooms.get("*%s%s" %(chr(3), player.tribeName)) != None:
                        if self.client.room.roomName != "*%s%s" %(chr(3), player.tribeName):
                            self.client.startBulle("*%s%s" %(chr(3), player.tribeName))
                    else:
                        player.sendLangueMessage("", "$InvTribu_MaisonVide")
                return

            elif CC == Identifiers.recv.Tribe.Bot_Bolo:
                pass
                return

        elif C == Identifiers.recv.Shop.C:
            if CC == Identifiers.recv.Shop.Equip_Clothe:
                self.client.Shop.equipClothe(packet)
                return

            elif CC == Identifiers.recv.Shop.Save_Clothe:
                self.client.Shop.saveClothe(packet)
                return
            
            elif CC == Identifiers.recv.Shop.Info:
                self.client.Shop.sendShopInfo()
                return

            elif CC == Identifiers.recv.Shop.Equip_Item:
                self.client.Shop.equipItem(packet)
                return

            elif CC == Identifiers.recv.Shop.Buy_Item:
                self.client.Shop.buyItem(packet)
                return

            elif CC == Identifiers.recv.Shop.Buy_Custom:
                self.client.Shop.customItemBuy(packet)
                return

            elif CC == Identifiers.recv.Shop.Custom_Item:
                self.client.Shop.customItem(packet)
                return

            elif CC == Identifiers.recv.Shop.Buy_Clothe:
                self.client.Shop.buyClothe(packet)
                return

            elif CC == Identifiers.recv.Shop.Buy_Visu_Done:
                p = ByteArray(packet.toByteArray())
                visuID = p.readShort()
                lookBuy = p.readUTF()
                look = self.server.newVisuList[visuID].split(";")
                look[0] = int(look[0])
                count = 0
                if self.client.shopFraises >= self.client.priceDoneVisu:
                    for visual in look[1].split(","):
                        if not visual == "0":
                            item, customID = visual.split("_", 1) if "_" in visual else [visual, ""]
                            item = int(item)
                            itemID = self.client.getFullItemID(count, item)
                            itemInfo = self.client.getItemInfo(count, item)
                            if len(self.client.shopItems) == 1:
                                if not self.client.Shop.checkInShop(itemID):
                                    self.client.shopItems += str(itemID)+"_" if self.client.shopItems == "" else "," + str(itemID)+"_"
                                    if not itemID in self.client.custom:
                                        self.client.custom.append(itemID)
                                    else:
                                        if not str(itemID) in self.client.custom:
                                            self.client.custom.append(str(itemID))
                            else:
                                if not self.client.Shop.checkInShop(str(itemID)):
                                    self.client.shopItems += str(itemID)+"_" if self.client.shopItems == "" else "," + str(itemID)+"_"
                                    if not itemID in self.client.custom:
                                        self.client.custom.append(itemID)
                                    else:
                                        if not str(itemID) in self.client.custom:
                                            self.client.custom.append(str(itemID))
                        count += 1
                        
                    self.client.clothes.append("%02d/%s/%s/%s" %(len(self.client.clothes), lookBuy, "78583a", "fade55" if self.client.shamanSaves >= 1000 else "95d9d6"))
                    furID = self.client.getFullItemID(22, look[0])
                    self.client.shopItems += str(furID) if self.client.shopItems == "" else "," + str(furID)
                    self.client.shopFraises -= self.client.priceDoneVisu
                    self.client.visuDone.append(lookBuy)
                else:
                    self.sendMessage("yarrak")
                self.client.Shop.sendShopList(False)

            elif CC == Identifiers.recv.Shop.Buy_Shaman_Item:
                self.client.Shop.buyShamanItem(packet)
                return

            elif CC == Identifiers.recv.Shop.Equip_Shaman_Item:
                self.client.Shop.equipShamanItem(packet)
                return

            elif CC == Identifiers.recv.Shop.Buy_Shaman_Custom:
                self.client.Shop.customShamanItemBuy(packet)
                return

            elif CC == Identifiers.recv.Shop.Custom_Shaman_Item:
                self.client.Shop.customShamanItem(packet)
                return

            elif CC == Identifiers.recv.Shop.Send_self:
                self.client.Shop.sendself(packet)
                return

            elif CC == Identifiers.recv.Shop.self_Result:
                self.client.Shop.selfResult(packet)
                return

        elif C == Identifiers.recv.Modopwet.C:
            if CC == Identifiers.recv.Modopwet.Modopwet:
                if self.client.privLevel >= 7:
                    isOpen = packet.readBoolean()
                    # if isOpen:
                        # self.client.modoPwet.openModoPwet(True)
                        # change_langue bolumunde acılıyor.
                        
                    self.client.isModoPwet = isOpen    
                return

            elif CC == Identifiers.recv.Modopwet.Delete_Report:
                if self.client.privLevel >= 7:
                    playerName, closeType = packet.readUTF(), packet.readByte()
                    self.client.modoPwet.deleteReport(playerName,int(closeType))
                return

            elif CC == Identifiers.recv.Modopwet.Watch:
                if self.client.privLevel >= 7:
                    playerName = packet.readUTF()
                    if not self.client.playerName == playerName:
                        roomName = self.server.players[playerName].roomName if self.server.players.has_key(playerName) else ""
                        if not roomName == "" and not roomName == self.client.roomName and not "[Editeur]" in roomName and not "[Totem]" in roomName:
                            self.client.startBulle(roomName)
                return

            elif CC == Identifiers.recv.Modopwet.Ban_Hack:
                if self.client.privLevel >= 7:
                    playerName, iban = packet.readUTF(), packet.readBoolean()
                    self.client.modoPwet.banHack(playerName,iban)
                return

            elif CC == Identifiers.recv.Modopwet.Change_Langue:
                if self.client.privLevel >= 7:
                    langue,modopwetOnlyPlayerReports,sortBy = packet.readUTF(),packet.readBoolean(),packet.readBoolean()
                    self.client.modoPwetLangue = langue.upper()
                    self.client.modoPwet.openModoPwet(self.client.isModoPwet,modopwetOnlyPlayerReports,sortBy)
                return
                
            elif CC == Identifiers.recv.Modopwet.Modopwet_Notifications:
                if self.client.privLevel >= 7:
                    isTrue = packet.readBoolean()
                    self.client.isModoPwetNotifications = isTrue  
                return    
                
            elif CC == Identifiers.recv.Modopwet.Chat_Log:
                if self.client.privLevel >= 7:
                    playerName = packet.readUTF()
                    self.client.modoPwet.openChatLog(playerName)
                return


        elif C == Identifiers.recv.Login.C:
            if CC == Identifiers.recv.Login.Create_Account:
                #packet = self.descriptPacket(packetID, packet)
                playerName, password, email, captcha, url, test = Utils.parsePlayerName(packet.readUTF()), packet.readUTF(), packet.readUTF(), packet.readUTF(), packet.readUTF(), packet.readUTF()
            
                if self.client.checkTimeAccount():
                    
                    canLogin = False
                    for urlCheck in self.server.serverURL:
                        if url.startswith(urlCheck):
                            canLogin = True
                            break

                    if not canLogin:
                        self.server.sendStaffMessage(7, "[<V>URL</V>][<J>%s</J>][<V>%s</V>][<R>%s</R>] Invalid login url." %(self.client.ipAddress, playerName, url))
                        self.client.sendPacket(Identifiers.old.send.Player_Ban_Login, [0, "Acesse pelo site: %s" %(self.server.serverURL[0])])
                        self.client.transport.loseConnection()
                        return


                    elif self.server.checkExistingUser(playerName):
                        self.client.sendPacket(Identifiers.send.Login_Result, ByteArray().writeByte(3).writeUTF(playerName).writeUTF("").toByteArray())
                    elif not re.match("^(?=^(?:(?!.*_$).)*$)(?=^(?:(?!_{2,}).)*$)[A-Za-z][A-Za-z0-9_]{2,11}$", playerName):
                        self.client.sendPacket(Identifiers.send.Login_Result, ByteArray().writeByte(5).writeUTF("").writeUTF("").toByteArray())
                    elif not self.client.currentCaptcha == captcha:
                        self.client.sendPacket(Identifiers.send.Login_Result, ByteArray().writeByte(7).writeUTF("").writeUTF("").toByteArray())
                    else:
                        #tag = "0000"
                        #while self.server.checkExistingUser(playerName + "#" + tag):
                            #tag = "".join([str(random.choice(range(9))) for x in range(4)])
                        #playerName += "#" + tag
                        self.client.sendAccountTime()
                        self.server.lastPlayerID += 1
                        self.Cursor.execute("insert into users values (%s, %s, %s, 1, 0, 0, 0, 0, %s, %s, 0, 0, 0, 0, 0, '', '', '', '1;0,0,0,0,0,0,0,0,0,0,0', '0,0,0,0,0,0,0,0,0,0', '78583a', '95d9d6', %s, '{}', '', '', '', '', '', '', '', '', 0, 70, 0, 0, '', 0, '', '', 0, 0, '', 0, 0, 0, '', '', '0,0,0,0', '0,0,0,0', '23:20', '23', 0, 0, '', 0, 0, 0, '', '', '', 0, 0, '2,8,0,0,0,189,133,0,0', 0, %s, '0#0#0#0#0#0', '', '', '', '24:0', 0, 'xx', '0.jpg', 1, '', 0, 0, 0, '', 0, 1, %s, '', 1, '', 0, 0, 'Little Mouse', 0, 0)", [playerName, password, self.server.lastPlayerID, self.server.initialCheeses, self.server.initialFraises, Utils.getTime(), self.client.langue, email])
                        self.Cursor.execute("insert into DailyQuest values (%s, '237129', '0', '20', '0', '20', '1')", [self.server.lastPlayerID])
                        self.client.loginPlayer(playerName, password, "\x03[Tutorial] %s" %(playerName))
                       # self.client.sendNewConsumable(23, 10)
                        #self.client.sendNewConsumable(2252, 5)
                        #self.client.sendNewConsumable(2256, 5)
                        #self.client.sendNewConsumable(2349, 5)
                        #self.client.sendNewConsumable(2379, 5)
                        self.client.sendServerMessageAdmin("[ACCOUNT] [<J>%s</J>] [<J>%s</J>] <V>%s</V> created an account." %(self.client.langue, self.client.ipAddress, playerName))
                        self.server.updateConfig()
                        if "?id=" in url:
                            link = url.split("?id=")
                            self.Cursor.execute("select IP from loginlog where Username = %s", [self.server.getPlayerName(int(link[1]))])
                            ipPlayer = self.Cursor.fetchone()[0]
                            self.Cursor.execute("select Password from users where Password = %s", [password])
                            passProtection = self.Cursor.fetchone()[0]
                            if ipPlayer is None and passProtection is None:
                                player = self.server.players.get(self.server.getPlayerName(int(link[1])))
                                if player != None:
                                    player.cheeseCount += 10
                                    player.firstCount += 10
                                    player.shopCheeses += 2000
                                    player.shopFraises += 2000
                                    player.nowCoins += 15
                                else:
                                    self.Cursor.execute("update users set CheeseCount = CheeseCount + 10, FirstCount = FirstCount + 10, ShopCheeses = ShopCheeses + 2000, ShopFraises = ShopFraises + 2000, Coins = Coins + 15 where Username = %s", [self.server.getPlayerName(int(link[1]))])
                    return
                else:
                    self.client.sendPacket(Identifiers.send.Login_Result, ByteArray().writeByte(5).writeByte(0).writeByte(0).writeUTF(playerName).toByteArray())


            elif CC == Identifiers.recv.Login.Login:
                #packet = self.descriptPacket(packetID, packet)
                playerName, password, url, startRoom, resultKey, byte = Utils.parsePlayerName(packet.readUTF()), packet.readUTF(), packet.readUTF(), packet.readUTF(), packet.readInt(), packet.readByte()
                #authKey = self.client.authKey
                #print(url)

                if not len(self.client.playerName) == 0:
                    self.server.sendStaffMessage(7, "[<V>ANTI-BOT</V>][<J>%s</J>][<V>%s</V>] Attempt to login multiple accounts." %(self.client.ipAddress, self.client.playerName))
                    self.client.sendPacket(Identifiers.old.send.Player_Ban_Login, [0, "Attempt to login multiple accounts."])
                    self.client.transport.loseConnection()
                    return
                elif playerName == "" and not password == "":
                    self.client.sendPacket(Identifiers.send.Login_Result, ByteArray().writeByte(2).writeUTF(playerName).writeUTF("").toByteArray())
                else:
                    self.client.loginPlayer(playerName, password, startRoom)
                #else:
                #self.server.sendStaffMessage(7, "[<V>ANTI-BOT</V>][<J>%s</J>][<V>%s</V>] Invalid login auth key." %(self.client.ipAddress, playerName))
                #self.client.sendPacket(Identifiers.old.send.Player_Ban_Login, [0, "Invalid login auth key."])
                #self.client.transport.loseConnection()
                    return

            elif CC == Identifiers.recv.Login.Player_FPS:
                return

            elif CC == Identifiers.recv.Login.Captcha:
                if _time.time() - self.client.CAPTime > 2:
                    self.client.currentCaptcha, px, ly, lines = self.server.buildCaptchaCode()
                    packet = ByteArray().writeShort(px).writeShort(ly).writeShort((px * ly))
                    for line in lines:
                        packet.writeBytes("\x00" * 4)
                        for value in line.split(","):
                            packet.writeUnsignedByte(value).writeBytes("\x00" * 3)
                        packet.writeBytes("\x00" * 4)
                    packet.writeBytes("\x00" * (((px * ly) - (packet.getLength() - 6) / 4) * 4))
                    self.client.sendPacket(Identifiers.send.Captcha, packet.toByteArray())
                    self.client.CAPTime = _time.time()
                return

            elif CC == Identifiers.recv.Login.Dummy:
                if self.client.awakeTimer.getTime() - _time.time() < 110.0:
                    self.client.awakeTimer.reset(120)
                return

            elif CC == Identifiers.recv.Login.Player_Info:
                return
            elif CC == Identifiers.recv.Login.Player_Info2:
                return

            elif CC == Identifiers.recv.Login.Temps_Client:
                return

            elif CC == Identifiers.recv.Login.Rooms_List:
                mode = packet.readByte()
                self.client.lastGameMode = mode
                self.client.sendGameMode(mode)
                return

            elif CC == Identifiers.recv.Login.Undefined:
                return

        elif C == Identifiers.recv.Transformation.C:
            if CC == Identifiers.recv.Transformation.Transformation_Object:
                objectID = packet.readShort()
                if not self.client.isDead and self.client.room.currentMap in range(200, 211):
                    self.client.room.sendAll(Identifiers.send.Transformation, ByteArray().writeInt(self.client.playerCode).writeShort(objectID).toByteArray())
                return

        elif C == Identifiers.recv.Informations.C:
            if CC == Identifiers.recv.Informations.Game_Log:
                errorC, errorCC, oldC, oldCC, error = packet.readByte(), packet.readByte(), packet.readUnsignedByte(), packet.readUnsignedByte(), packet.readUTF()
                if self.server.isDebug:
                    if errorC == 1 and errorCC == 1:
                        print "[%s] [%s][OLD] GameLog Error - C: %s CC: %s error: %s" %(_time.strftime("%H:%M:%S"), self.client.playerName, oldC, oldCC, error)
                    elif errorC == 60 and errorCC == 1:
                        if oldC == Identifiers.tribulle.send.ET_SignaleDepartMembre or oldC == Identifiers.tribulle.send.ET_SignaleExclusion: return
                        print "[%s] [%s][TRIBULLE] GameLog Error - Code: %s error: %s" %(_time.strftime("%H:%M:%S"), self.client.playerName, oldC, error)
                    else:
                        print "[%s] [%s] GameLog Error - C: %s CC: %s error: %s" %(_time.strftime("%H:%M:%S"), self.client.playerName, errorC, errorCC, error)
                return

            elif CC == Identifiers.recv.Player.Ping:
                if (_time.time() - self.client.PInfo[1]) >= 5:
                    self.client.PInfo[1] = _time.time()
                    self.client.sendPacket(Identifiers.send.Ping, self.client.PInfo[0])
                    self.client.PInfo[0] += 1
                    if self.client.PInfo[0] == 31:
                        self.client.PInfo[0] = 0
                return

            elif CC == Identifiers.recv.Informations.Change_Shaman_Type:
                type = packet.readByte()
                self.client.shamanType = type
                self.client.sendShamanType(type, (self.client.shamanSaves >= 100 and self.client.hardModeSaves >= 150))
                return

            elif CC == Identifiers.recv.Informations.Letter:
                playerName = Utils.parsePlayerName(packet.readUTF())[:-5]
                type = packet.readByte()
                letter = packet.readUTFBytes(packet.getLength())
                idler = {0:29,1:30,2:2241,3:2330,4:2351}
                
                if self.server.checkExistingUser(playerName):
                    id = idler[type]
                    count = self.client.playerConsumables[id]
                    if count > 0:
                        count -= 1
                        self.client.playerConsumables[id] -= 1
                        if count == 0:
                            del self.client.playerConsumables[id]
                            if self.client.equipedConsumables:
                                for id in self.client.equipedConsumables:
                                    if not id:
                                        self.client.equipedConsumables.remove(id)
                                None
                                if id in self.client.equipedConsumables:
                                    self.client.equipedConsumables.remove(id)

                    self.client.updateInventoryConsumable(id, count)
                    self.client.useInventoryConsumable(id)
                    
                    player = self.server.players.get(playerName)
                    if (player != None): 
                        p = ByteArray()
                        p.writeUTF(self.client.playerName)
                        p.writeUTF(self.client.playerLook)
                        p.writeByte(type)
                        p.writeBytes(letter)
                        player.sendPacket(Identifiers.send.Letter, p.toByteArray())
                        self.client.sendLangueMessage("", "$MessageEnvoye")
                    else:
                        self.client.sendLangueMessage("", "$Joueur_Existe_Pas")
                else: 
                    self.client.sendLangueMessage("", "$Joueur_Existe_Pas")
                
                return

            elif CC == Identifiers.recv.Informations.Letter:
                return

            elif CC == Identifiers.recv.Informations.Send_self:
                self.client.sendPacket(Identifiers.send.Send_self, 1)
                return

            elif CC == Identifiers.recv.Informations.Computer_Info:
                return

            elif CC == Identifiers.recv.Informations.Change_Shaman_Color:
                color = packet.readInt()
                self.client.shamanColor = "%06X" %(0xFFFFFF & color)
                return

            elif CC == Identifiers.recv.Informations.Request_Info:
                self.client.sendPacket(Identifiers.send.Request_Info, ByteArray().writeUTF("http://195.154.124.74/outils/info.php").toByteArray())
                return

        elif C == Identifiers.recv.Lua.C:
            if CC == Identifiers.recv.Lua.Lua_Script:
                byte, script = packet.readByte(), packet.readUTF()
                if self.client.privLevel == 11 and self.client.isLuaAdmin:
                    self.client.runLuaAdminScript(script)
                return

            elif CC == Identifiers.recv.Lua.Key_Board:
                key, down, posX, posY = packet.readShort(), packet.readBoolean(), packet.readShort(), packet.readShort()


                if self.client.isFlyMod and key == 32:
                    self.room.bindKeyBoard(self.playerName, 32, False, self.room.isFly)
                
                if self.client.isFFA and key == 40:
                    if self.client.canSpawnCN == True:
                        if self.client.isMovingRight == True and self.client.isMovingLeft == False:
                            reactor.callLater(0.2, self.client.Utility.spawnObj, 17, posX - 10, posY +15, 90)
                        if self.client.isMovingRight == False and self.client.isMovingLeft == True:
                            reactor.callLater(0.2, self.client.Utility.spawnObj, 17, posX + 10, posY +25, 270)
                        reactor.callLater(2.5, self.client.Utility.removeObj)
                        self.client.canSpawnCN = False
                        reactor.callLater(1.3, self.client.enableSpawnCN)

                elif self.client.room.mapCode == 20001:
					if self.client.posX >= 789 and self.client.posX <= 911 and self.client.posY >= 354 and self.client.posY <= 356:
						if self.client.isEvent and key == 32:
							self.client.sendPlayerEmote(11, "", False, False)
							reactor.callLater(5, self.client.sendFishingCount)
					elif self.client.posX >= 962 and self.client.posX <= 1049 and self.client.posY >= 274 and self.client.posY <= 276:
						if self.client.isEvent and key == 32:
							self.client.sendPlayerEmote(11, "", False, False)
							reactor.callLater(5, self.client.sendFishingCount)
					elif self.client.posX >= 1615 and self.client.posX <= 1705 and self.client.posY >= 246 and self.client.posY <= 247:
						if self.client.isEvent and key == 32:
							self.client.sendPlayerEmote(11, "", False, False)
							reactor.callLater(5, self.client.sendFishingCount)
					elif self.client.posX >= 277 and self.client.posX <= 347 and self.client.posY == 193:
						if self.client.isEvent and key == 32:
							self.client.sendPlayerEmote(11, "", False, False)
							reactor.callLater(5, self.client.sendFishingCount)
					elif self.client.posX >= 1752 and self.client.posX <= 2060 and self.client.posY >= 355 and self.client.posY <= 363:
						if self.client.isEvent and key == 32:
							self.client.sendPlayerEmote(11, "", False, False)
							reactor.callLater(8, self.client.sendFishingCount)

		elif self.client.room.mapCode == 20002:
                    if self.client.posX >= 638 and self.client.posX <= 721 and self.client.posY >= 43 and self.client.posY <= 53:
						if self.client.isEvent and key == 32:
							self.client.sendPlayerEmote(11, "", False, False)
							reactor.callLater(5, self.client.sendFishingCount)
                    elif self.client.posX >= 647 and self.client.posX <= 734 and self.client.posY >= 336 and self.client.posY <= 338:
						if self.client.isEvent and key == 32:
							self.client.sendPlayerEmote(11, "", False, False)
							reactor.callLater(5, self.client.sendFishingCount)
                    elif self.client.posX >= 300 and self.client.posX <= 738 and self.client.posY >= 293 and self.client.posY <= 335:
						if self.client.isEvent and key == 32:
							self.client.sendPlayerEmote(11, "", False, False)
							reactor.callLater(5, self.client.sendFishingCount)
                    elif self.client.posX >= 200 and self.client.posX <= 256 and self.client.posY >= 182 and self.client.posY <= 186:
						if self.client.isEvent and key == 32:
							self.client.sendPlayerEmote(11, "", False, False)
							reactor.callLater(5, self.client.sendFishingCount)
                    elif self.client.posX >= 41 and self.client.posX <= 129 and self.client.posY >= 331 and self.client.posY <= 353:
						if self.client.isEvent and key == 32:
							self.client.sendPlayerEmote(11, "", False, False)
							reactor.callLater(8, self.client.sendFishingCount)
                        
                if self.client.isSpeed and key == 32:
                    self.client.room.movePlayer(self.client.playerName, 0, 0, True, 50 if self.client.isMovingRight else -50, 0, True)
                if self.client.room.isFlyMod and key == 32:
                    self.client.room.movePlayer(self.client.playerName, 0, 0, True, 0, -50, True)
                if self.client.isFly and key == 32:
                    self.client.room.movePlayer(self.client.playerName, 0, 0, True, 0, -50, True)

                if self.client.room.isDeathmatch and key == 3:
                    if self.client.room.canCannon:
                        if not self.client.canCN:
                            self.client.room.objectID += 1
                            idCannon = {15: "149aeaa271c.png", 16: "149af112d8f.png", 17: "149af12c2d6.png", 18: "149af130a30.png", 19: "149af0fdbf7.png", 20: "149af0ef041.png", 21: "149af13e210.png", 22: "149af129a4c.png", 23: "149aeaa06d1.png"}
                            #idCannon = "149aeaa271c.png" if self.client.deathStats[4] == 15 else "149af112d8f.png" if self.client.deathStats[4] == 16 else "149af12c2d6.png"
                            if self.client.isMovingRight:
                                x = int(self.client.posX+self.client.deathStats[0]) if self.client.deathStats[0] < 0 else int(self.client.posX+self.client.deathStats[0])
                                y = int(self.client.posY+self.client.deathStats[1]) if self.client.deathStats[1] < 0 else int(self.client.posY+self.client.deathStats[1])
                                self.client.sendPlaceObject(self.client.room.objectID, 17, x, y, 90, 0, 0, True, True)
                                if self.client.deathStats[4] in [15, 16, 17, 18, 19, 20, 21, 22, 23]:
                                    if not self.client.deathStats[3] == 1:
                                        self.client.room.sendAll([29, 19], ByteArray().writeInt(self.client.playerCode).writeUTF(idCannon[self.client.deathStats[4]]).writeByte(1).writeInt(self.client.room.objectID).toByteArray()+"\xff\xf0\xff\xf0")
                            else:
                                x = int(self.client.posX-self.client.deathStats[0]) if self.client.deathStats[0] < 0 else int(self.client.posX-self.client.deathStats[0])
                                y = int(self.client.posY+self.client.deathStats[1]) if self.client.deathStats[1] < 0 else int(self.client.posY+self.client.deathStats[1])
                                self.client.sendPlaceObject(self.client.room.objectID, 17, x, y, -90, 0, 0, True, True)
                                if self.client.deathStats[4] in [15, 16, 17, 18, 19, 20, 21, 22, 23]:
                                    if not self.client.deathStats[3] == 1:
                                        self.client.room.sendAll([29, 19], ByteArray().writeInt(self.client.playerCode).writeUTF(idCannon[self.client.deathStats[4]]).writeByte(1).writeInt(self.client.room.objectID).toByteArray()+"\xff\xf0\xff\xf0")
                            self.client.canCN = True       
                            self.canCCN = reactor.callLater(0.8, self.client.cnTrueOrFalse)        
                if self.client.room.isDeathmatch and key == 79:
                    self.client.sendDeathInventory()
                if self.client.room.isDeathmatch and key == 80:
                    self.client.sendDeathProfile()
                    
                if self.client.room.isFFARace and key == 3:
                    if self.client.canCannon:
                        itemID = random.randint(100, 999)
                        if self.client.isMovingRight:
                            reactor.callLater(0.2, lambda: self.client.room.sendAll(Identifiers.send.Spawn_Object, ByteArray().writeInt(itemID).writeShort(17).writeShort(posX + -5).writeShort(posY + 15).writeShort(90).writeShort(0).writeByte(1).writeByte(0).toByteArray()))
                        else:
                            reactor.callLater(0.2, lambda: self.client.room.sendAll(Identifiers.send.Spawn_Object, ByteArray().writeInt(itemID).writeShort(17).writeShort(posX - -5).writeShort(posY + 15).writeShort(-90).writeShort(0).writeByte(1).writeByte(0).toByteArray()))
                        reactor.callLater(2.5, lambda: self.client.sendPacket(Identifiers.send.Remove_Object, ByteArray().writeInt(itemID).writeBoolean(True).toByteArray()))
                        self.client.canCannon = False
                        reactor.callLater(1.3, setattr, self.client, "canCannon", True)
                return
            
            elif CC == Identifiers.recv.Lua.Mouse_Click:
                posX, posY = packet.readShort(), packet.readShort()
                if self.client.isTeleport:
                    self.client.room.movePlayer(self.client.playerName, posX, posY, False, 0, 0, False)

                elif self.client.isExplosion:
                    self.client.Utility.explosionPlayer(posX, posY)
                return

            elif CC == Identifiers.recv.Lua.Popup_Answer:
                popupID, answer = packet.readInt(), packet.readUTF()
                return

            elif CC == Identifiers.recv.Lua.Text_Area_Callback:
                textAreaID, event = packet.readInt(), packet.readUTF()
                ## Menself Menu System ##
                if event in ["lbileri","lbgeri","lbkapat"]:
                    self.client.lbSayfaDegis(event=="lbileri",event=="lbkapat")
                    return 
                if event == "closed":
                    self.client.sendPacket([29, 22], struct.pack("!l", 7999))
                    self.client.sendPacket([29, 22], struct.pack("!l", 8249))
                    
                    
                if event == "fechar":
                    self.client.sendPacket([29, 22], struct.pack("!l", 10050))
                    self.client.sendPacket([29, 22], struct.pack("!l", 10051))
                    self.client.sendPacket([29, 22], struct.pack("!l", 10052))
                    self.client.sendPacket([29, 22], struct.pack("!l", 10053))


                elif event == "fecharPop":
                    self.client.sendPacket([29, 22], struct.pack("!l", 10056))
                    self.client.sendPacket([29, 22], struct.pack("!l", 10057))
                    self.client.sendPacket([29, 22], struct.pack("!l", 10058))

                        

                
                ## End Duxo Menu System ##
                    
                if event.startswith("fechadin"):
                    for x in range(0, 100):									
                        self.client.sendPacket([29, 22], ByteArray().writeInt(x).toByteArray())
                        
                if textAreaID in [8983, 8984, 8985]:
                    if event.startswith("inventory"):
                        event = event.split("#")
                        if event[1] == "use":
                            self.client.deathStats[4] = int(event[2])
                        else:
                            self.client.deathStats[4] = 0
                        self.client.sendDeathInventory(self.client.page)

                if textAreaID == 123480 or textAreaID == 123479:
                    if event == "next":
                        if not self.client.page >= 3:
                            self.client.page += 1
                            self.client.sendDeathInventory(self.client.page)
                    else:
                        if not self.client.page <= 1:
                            self.client.page -= 1
                            self.client.sendDeathInventory(self.client.page)

                if textAreaID == 9012:
                    if event == "close":
                        ids = 131458, 123479, 130449, 131459, 123480, 6992, 8002, 23, 9012, 9013, 9893, 8983, 9014, 9894, 8984, 9015, 9895, 8985, 504, 505, 506, 507
                        for id in ids:
                            if id <= 507 and not id == 23:
                                self.client.sendPacket([29, 18], ByteArray().writeInt(id).toByteArray())
                            else:
                                self.client.sendPacket([29, 22], ByteArray().writeInt(id).toByteArray())

                if textAreaID == 9009:
                    if event == "close":
                        ids = 39, 40, 41, 7999, 20, 9009, 7239, 8249, 270
                        for id in ids:
                            if id <= 41 and not id == 20:
                                self.client.sendPacket([29, 18], ByteArray().writeInt(id).toByteArray())
                            else:
                                self.client.sendPacket([29, 22], ByteArray().writeInt(id).toByteArray())

                if textAreaID == 20:
                    if event.startswith("offset"):
                        event = event.split("#")
                        if event[1] == "offsetX":
                            if event[2] == "1":
                                if not self.client.deathStats[0] >= 25:
                                    self.client.deathStats[5] += 1
                                    self.client.deathStats[0] += 1
                            else:
                                if not self.client.deathStats[0] <= -25:
                                    self.client.deathStats[5] -= 1
                                    self.client.deathStats[0] -= 1
                        else:
                            if event[2] == "1":
                                if not self.client.deathStats[1] >= 25:
                                    self.client.deathStats[6] += 1
                                    self.client.deathStats[1] += 1
                            else:
                                if not self.client.deathStats[1] <= -25:
                                    self.client.deathStats[6] -= 1
                                    self.client.deathStats[1] -= 1
                    elif event == "show":
                        if self.client.deathStats[3] == 1:
                            self.client.deathStats[3] = 0
                        else:
                            self.client.deathStats[3] = 1
                    self.client.sendDeathProfile()

                    
                if event == "closeRanking":
                        i = 30000
                        while i <= 30010:
                            self.client.room.removeTextArea(i, self.client.playerName)
                            i += 1
                return

            elif CC == Identifiers.recv.Lua.Color_Picked:
                colorPickerId, color = packet.readInt(), packet.readInt()
                try:
                    if colorPickerId == 10000:
                        if color != -1:
                            self.client.nameColor = "%06X" %(0xFFFFFF & color)
                            self.client.room.setNameColor(self.client.playerName, color)
                            self.client.sendMessage("<font color='"+color+"'>" + "İsminizin rengi başarıyla değiştirildi." if self.client.langue.lower() == "tr" else "You've changed color of your nickname successfully." + "</font>")
                    elif colorPickerId == 10001:
                        if color != -1:
                            self.client.mouseColor = "%06X" %(0xFFFFFF & color)
                            self.client.playerLook = "1;%s" %(self.client.playerLook.split(";")[1])
                            self.client.sendMessage("<font color='"+color+"'>" + "Farenizin rengini başarıyla değiştirdiniz. Yeni renk için sonraki turu bekleyin." if self.client.langue.lower() == "tr" else "You've changed color of your mouse successfully.\nWait next round for your new mouse color." + "</font>")
                    elif colorPickerId == 10002:
                        if color != -1:
                            self.client.nickColor = "%06X" %(0xFFFFFF & color)
                            self.client.sendMessage("<font color='"+color+"'>" + "İsminizin rengini başarıyla değiştirdiniz. Yeni renk için sonraki turu bekleyin." if self.client.langue.lower() == "tr" else "You've changed color of your nickname successfully.\nWait next round for your new nickname color." + "</font>")
                except: self.client.sendMessage("<ROSE>" + "Renginizi Başarıyla Değiştiniz." if self.client.langue.lower() == "tr" else "Incorrect color, select other one.")
                return
            
        elif C == Identifiers.recv.Cafe.C:
            if CC == Identifiers.recv.Cafe.Mulodrome_Close:
                self.client.room.sendAll(Identifiers.send.Mulodrome_End)
                return

            elif CC == Identifiers.recv.Cafe.Mulodrome_Join:
                team, position = packet.readByte(), packet.readByte()

                if len(self.client.mulodromePos) != 0:
                    self.client.room.sendAll(Identifiers.send.Mulodrome_Leave, chr(self.client.mulodromePos[0]) + chr(self.client.mulodromePos[1]))

                self.client.mulodromePos = [team, position]
                self.client.room.sendAll(Identifiers.send.Mulodrome_Join, ByteArray().writeByte(team).writeByte(position).writeInt(self.client.playerID).writeUTF(self.client.playerName).writeUTF(self.client.tribeName).toByteArray())
                if self.client.playerName in self.client.room.redTeam: self.client.room.redTeam.remove(self.client.playerName)
                if self.client.playerName in self.client.room.blueTeam: self.client.room.blueTeam.remove(self.client.playerName)
                if team == 1:
                    self.client.room.redTeam.append(self.client.playerName)
                else:
                    self.client.room.blueTeam.append(self.client.playerName)
                return

            elif CC == Identifiers.recv.Cafe.Mulodrome_Leave:
                team, position = packet.readByte(), packet.readByte()
                self.client.room.sendAll(Identifiers.send.Mulodrome_Leave, ByteArray().writeByte(team).writeByte(position).toByteArray())
                if team == 1:
                    for playerName in self.client.room.redTeam:
                        if self.client.room.clients[playerName].mulodromePos[1] == position:
                            self.client.room.redTeam.remove(playerName)
                            break
                else:
                    for playerName in self.client.room.blueTeam:
                        if self.client.room.clients[playerName].mulodromePos[1] == position:
                            self.client.room.blueTeam.remove(playerName)
                            break
                return

            elif CC == Identifiers.recv.Cafe.Mulodrome_Play:
                if not len(self.client.room.redTeam) == 0 or not len(self.client.room.blueTeam) == 0:
                    self.client.room.isMulodrome = True
                    self.client.room.isRacing = True
                    self.client.room.noShaman = True
                    self.client.room.mulodromeRoundCount = 0
                    self.client.room.never20secTimer = True
                    self.client.room.sendAll(Identifiers.send.Mulodrome_End)
                    self.client.room.mapChange()
                return

            elif CC == Identifiers.recv.Cafe.Reload_Cafe:
                if not self.client.isReloadCafe:
                    self.client.cafe.loadCafeMode()
                    self.client.isReloadCafe = True
                    reactor.callLater(3, setattr, self.client, "isReloadCafe", False)
                return

            elif CC == Identifiers.recv.Cafe.Open_Cafe_Topic:
                topicID = packet.readInt()
                self.client.cafe.openCafeTopic(topicID)
                return

            elif CC == Identifiers.recv.Cafe.Create_New_Cafe_Topic:
                if self.client.privLevel >= 1:
                    message, title = packet.readUTF(), packet.readUTF()
                    self.client.cafe.createNewCafeTopic(message, title)
                return

            elif CC == Identifiers.recv.Cafe.Create_New_Cafe_Post:
                if self.client.privLevel >= 1:
                    topicID, message = packet.readInt(), packet.readUTF()
                    self.client.cafe.createNewCafePost(topicID, message)
                return

            elif CC == Identifiers.recv.Cafe.Open_Cafe:
                self.client.isCafe = packet.readBoolean()
                return

            elif CC == Identifiers.recv.Cafe.Vote_Cafe_Post:
                if self.client.privLevel >= 1:
                    topicID, postID, mode = packet.readInt(), packet.readInt(), packet.readBoolean()
                    self.client.cafe.voteCafePost(topicID, postID, mode)
                return

            elif CC == Identifiers.recv.Cafe.Delete_Cafe_Message:
                if self.client.privLevel >= 7:
                    topicID, postID = packet.readInt(), packet.readInt()
                    try: self.client.cafe.deleteCafePost(topicID, postID)
                    except: pass
                else:
                    self.client.sendMessage("Bunu yapmak için izniniz yok.")
                return

            elif CC == Identifiers.recv.Cafe.Delete_All_Cafe_Message:
                if self.client.privLevel >= 7:
                # if 7 in self.client.privLevel:
                    topicID, playerName = packet.readInt(), packet.readUTF()
                    try: self.client.cafe.deleteAllCafePost(topicID, playerName)
                    except: pass
                else:
                    self.client.sendMessage("Bunu yapmak için izniniz yok.")
                return

        elif C == Identifiers.recv.Inventory.C:
            if CC == Identifiers.recv.Inventory.Open_Inventory:
                self.client.sendInventoryConsumables()
                return

            elif CC == Identifiers.recv.Inventory.Use_Consumable:
                id = packet.readShort()
                if self.client.playerConsumables.has_key(id) and not self.client.isDead and not self.client.room.isRacing and not self.client.room.isBootcamp and not self.client.room.isDefilante and not self.client.room.isSpeedRace and not self.client.room.isMeepRace:
                    # if not id in [31, 34, 2240, 2247, 2262, 2332, 2340] or self.client.pet == 0:
                    count = self.client.playerConsumables[id]
                    if count > 0:
                        count -= 1
                        self.client.playerConsumables[id] -= 1
                        if count == 0:
                            del self.client.playerConsumables[id]
                            if self.client.equipedConsumables:
                                for id in self.client.equipedConsumables:
                                    if not id:
                                        self.client.equipedConsumables.remove(id)
                                None
                                if id in self.client.equipedConsumables:
                                    self.client.equipedConsumables.remove(id)

                        if id in [1, 5, 6, 8, 11, 20, 24, 25, 26, 2250]:
                            if id == 11:
                                self.client.room.objectID += 2
                            ids={1:65, 5:6, 6:34, 8:89, 11:90, 20:33, 24:63, 25:80, 26:95, 2250:97}   
                            self.client.sendPlaceObject(self.client.room.objectID if id == 11 else 0, ids[id], self.client.posX + 28 if self.client.isMovingRight else self.client.posX - 28, self.client.posY, 0, 0 if id == 11 or id == 24 else 10 if self.client.isMovingRight else -10, -3, True, True)
                            
##                        if id == 1 or id == 5 or id == 6 or id == 8 or id == 11 or id == 20 or id == 24 or id == 25 or id == 26 or id == 2250:
##                                if id == 11:
##                                    self.client.room.objectID += 2
##                                self.client.sendPlaceObject(self.client.room.objectID if id == 11 else 0, 65 if id == 1 else 6 if id == 5 else 34 if id == 6 else 89 if id == 8 else 90 if id == 11 else 33 if id == 20 else 63 if id == 24 else 80 if id == 25 else 95 if id == 26 else 114 if id == 2250 else 0, self.client.posX + 28 if self.client.isMovingRight else self.client.posX - 28, self.client.posY, 0, 0 if id == 11 or id == 24 else 10 if self.client.isMovingRight else -10, -3, True, True)
                        if id == 10:
                            x = 0
                            for player in self.client.room.clients.values():
                                if x < 5 and player != self.client:
                                    if player.posX >= self.client.posX - 400 and player.posX <= self.client.posX + 400:
                                        if player.posY >= self.client.posY - 300 and player.posY <= self.client.posY + 300:
                                            player.sendPlayerEmote(3, "", False, False)
                                            x += 1

                        if id == 11:
                            self.client.room.newConsumableTimer(self.client.room.objectID)
                            self.client.isDead = True
                            if not self.client.room.noAutoScore: self.client.playerScore += 1
                            self.client.sendPlayerDied()
                            self.client.room.checkChangeMap()
                    
                        if id == 28:
                            self.client.Skills.sendBonfireSkill(self.client.posX, self.client.posY, 15)

                        if id in [31, 34, 2240, 2247, 2262, 2332, 2340,2437]:
                            self.client.pet = {31:2, 34:3, 2240:4, 2247:5, 2262:6, 2332:7, 2340:8,2437:9}[id]
                            self.client.petEnd = Utils.getTime() + (1200 if self.client.pet == 8 else 3600)
                            self.client.room.sendAll(Identifiers.send.Pet, ByteArray().writeInt(self.client.playerCode).writeUnsignedByte(self.client.pet).toByteArray())

                        if id == 33:
                            self.client.sendPlayerEmote(16, "", False, False)
                        
                        if id == 21:
                            self.client.sendPlayerEmote(12, "", False, False)        

                        if id == 35:
                            if len(self.client.shopBadges) > 0:
                                self.client.room.sendAll(Identifiers.send.Balloon_Badge, ByteArray().writeInt(self.client.playerCode).writeShort(random.choice(self.client.shopBadges.keys())).toByteArray())

                        if id == 800:
                            self.client.shopCheeses += 5
                            self.client.sendAnimZelda(2, 0)
                            self.client.sendGiveCurrency(0, 5)

                        if id == 801:
                            self.client.shopFraises += 5
                            self.client.sendAnimZelda(2, 2)

                        if id == 2234:
                            x = 0
                            self.client.sendPlayerEmote(20, "", False, False)
                            for player in self.client.room.clients.values():
                                if x < 5 and player != self.client:
                                    if player.posX >= self.client.posX - 400 and player.posX <= self.client.posX + 400:
                                        if player.posY >= self.client.posY - 300 and player.posY <= self.client.posY + 300:
                                            player.sendPlayerEmote(6, "", False, False)
                                            x += 1

                        if id == 2239:
                            self.client.room.sendAll(Identifiers.send.Crazzy_Packet, ByteArray().writeByte(4).writeInt(self.client.playerCode).writeInt(self.client.shopCheeses).toByteArray())
                        
                        if id in [2252,2256,2349,2379]:
                            renkler = {2252:"56C93E",2256:"C93E4A",2349:"52BBFB",2379:"FF8400"}
                            renk = int(renkler[id],16)
                            self.client.drawingColor = renk
                            self.client.sendPacket(Identifiers.send.Crazzy_Packet, ByteArray().writeUnsignedByte(1).writeUnsignedShort(650).writeInt(renk).toByteArray())

                        if id in [9,12,13,17,18,19,22,27,407,2251,2258,2308,2439]: # kurkler
                            ids={9:"10",12:"33",13:"35",17:"37",18:"16",19:"42",22:"45",27:"51",407:"7",2251:"61",2258:"66",2308:"75",2439:"118"}[id]
                            look = self.client.playerLook
                            index = look.index(";")
                            self.client.fur = ids + look[index:]
                            
                        if id == 2246:
                            self.client.sendPlayerEmote(24, "", False, False)

                        if id == 2100:
                            idlist = ["1", "5", "6", "8", "11", "20", "24", "25", "26", "31", "34", "2240", "2247", "2262", "2332", "2340", "33", "35", "800", "801", "2234", "2239", "2255", "10", "28"]
                            ids = int(random.choice(idlist))
                            if not ids in self.client.playerConsumables:
                                self.client.playerConsumables[ids] = 1
                            else:
                               counts = self.client.playerConsumables[ids] + 1
                               self.client.playerConsumables[ids] = counts
                            self.client.sendAnimZeldaInventory(4, ids, 1)

                        if id == 2255:
                            self.client.sendAnimZelda2(7, case="$De6", id=random.randint(0, 6))
                            
                        if id == 2259:
                            self.client.room.sendAll(Identifiers.send.Crazzy_Packet, self.client.getCrazzyPacket(5, [self.client.playerCode, (self.client.playerTime / 86400),(self.client.playerTime / 3600) % 24]));
                                
                        self.client.updateInventoryConsumable(id, count)
                        self.client.useInventoryConsumable(id)
                return

            elif CC == Identifiers.recv.Inventory.Equip_Consumable:
                id, equip = packet.readShort(), packet.readBoolean()
                try:
                    if equip:
                        self.client.equipedConsumables.append(id)
                    else:
                        self.client.equipedConsumables.remove(str(id))
                except: pass
                return
                
            elif CC == Identifiers.recv.Inventory.Trade_Invite:
                playerName = packet.readUTF()
                self.client.tradeInvite(playerName)
                return
                
            elif CC == Identifiers.recv.Inventory.Cancel_Trade:
                playerName = packet.readUTF()
                self.client.cancelTrade(playerName)
                return
                
            elif CC == Identifiers.recv.Inventory.Trade_Add_Consusmable:
                id, isAdd = packet.readShort(), packet.readBoolean()
                try:
                    self.client.tradeAddConsumable(id, isAdd)
                except: pass
                return
                
            elif CC == Identifiers.recv.Inventory.Trade_Result:
                isAccept = packet.readBoolean()
                self.client.tradeResult(isAccept)
                return

        elif C == Identifiers.recv.Tribulle.C:
            if CC == Identifiers.recv.Tribulle.Tribulle:
                if not self.client.isGuest:
                    code = packet.readShort()
                    self.client.tribulle.parseTribulleCode(code, packet)
                return

        elif C == Identifiers.recv.Sly.C:
            if CC == Identifiers.recv.Sly.Invocation:
                objectCode, posX, posY, rotation, position, invocation = packet.readShort(), packet.readShort(), packet.readShort(), packet.readShort(), packet.readUTF(), packet.readBoolean()
                if self.client.isShaman:
                    showInvocation = True
                    if self.client.room.isSurvivor:
                        showInvocation = invocation
                    pass
                    if showInvocation:
                        self.client.room.sendAllOthers(self.client, Identifiers.send.Invocation, ByteArray().writeInt(self.client.playerCode).writeShort(objectCode).writeShort(posX).writeShort(posY).writeShort(rotation).writeUTF(position).writeBoolean(invocation).toByteArray())
                return

            elif CC == Identifiers.recv.Sly.Remove_Invocation:
                if self.client.isShaman:
                    self.client.room.sendAllOthers(self.client, Identifiers.send.Remove_Invocation, ByteArray().writeInt(self.client.playerCode).toByteArray())
                return

            elif CC == Identifiers.recv.Sly.Change_Shaman_Badge:
                badge = packet.readByte()
                if str(badge) or badge == 0 in self.client.shamanBadges:
                    self.client.equipedShamanBadge = str(badge)
                    self.client.sendProfile(self.client.playerName)
                return
                
            elif CC == Identifiers.recv.Sly.Crazzy_Packet:
                type = packet.readByte()
                if type == 2:
                    posX = int(packet.readShort())
                    posY = int(packet.readShort())
                    lineX = int(packet.readShort())
                    lineY = int(packet.readShort())
                    self.client.room.sendAllOthers(self.client, Identifiers.send.Crazzy_Packet, self.client.getCrazzyPacket(2,[self.client.playerCode, self.client.drawingColor, posX, posY, lineX, lineY]))
                       

            elif CC == Identifiers.recv.Sly.NPC_Functions:
                id = packet.readByte()
                if id == 4:
                    self.client.openNpcShop(packet.readUTF())
                else:
                    self.client.buyNPCItem(packet.readByte())
                return

            
            elif CC == Identifiers.recv.Sly.Full_Look:
                p = ByteArray(packet.toByteArray())
                visuID = p.readShort()

                shopItems = [] if self.client.shopItems == "" else self.client.shopItems.split(",")
                look = self.server.newVisuList[visuID].split(";")
                look[0] = int(look[0])
                lengthCloth = len(self.client.clothes)
                buyCloth = 5 if (lengthCloth == 0) else (50 if lengthCloth == 1 else 100)

                self.client.visuItems = {-1: {"ID": -1, "Buy": buyCloth, "Bonus": True, "Customizable": False, "HasCustom": False, "CustomBuy": 0, "Custom": "", "CustomBonus": False}, 22: {"ID": self.client.getFullItemID(22, look[0]), "Buy": self.client.getItemInfo(22, look[0])[6], "Bonus": False, "Customizable": False, "HasCustom": False, "CustomBuy": 0, "Custom": "", "CustomBonus": False}}

                count = 0
                for visual in look[1].split(","):
                    if not visual == "0":
                        item, customID = visual.split("_", 1) if "_" in visual else [visual, ""]
                        item = int(item)
                        itemID = self.client.getFullItemID(count, item)
                        itemInfo = self.client.getItemInfo(count, item)
                        self.client.visuItems[count] = {"ID": itemID, "Buy": itemInfo[6], "Bonus": False, "Customizable": bool(itemInfo[2]), "HasCustom": customID != "", "CustomBuy": itemInfo[7], "Custom": customID, "CustomBonus": False}
                        if self.client.Shop.checkInShop(self.client.visuItems[count]["ID"]):
                            self.client.visuItems[count]["Buy"] -= itemInfo[6]
                        if len(self.client.custom) == 1:
                            if itemID in self.client.custom:
                                self.client.visuItems[count]["HasCustom"] = True
                            else:
                                self.client.visuItems[count]["HasCustom"] = False
                        else:
                            if str(itemID) in self.client.custom:
                                self.client.visuItems[count]["HasCustom"] = True
                            else:
                                self.client.visuItems[count]["HasCustom"] = False
                    count += 1
                hasVisu = map(lambda y: 0 if y in shopItems else 1, map(lambda x: x["ID"], self.client.visuItems.values()))
                visuLength = reduce(lambda x, y: x + y, hasVisu)
                allPriceBefore = 0
                allPriceAfter = 0
                promotion = 70.0 / 100

                p.writeUnsignedShort(visuID)
                p.writeUnsignedByte(20)
                p.writeUTF(self.server.newVisuList[visuID])
                p.writeUnsignedByte(visuLength)

                for category in self.client.visuItems.keys():
                    if len(self.client.visuItems.keys()) == category:
                        category = 22
                    itemID = self.client.getSimpleItemID(category, self.client.visuItems[category]["ID"])

                    buy = [self.client.visuItems[category]["Buy"], int(self.client.visuItems[category]["Buy"] * promotion)]
                    customBuy = [self.client.visuItems[category]["CustomBuy"], int(self.client.visuItems[category]["CustomBuy"] * promotion)]

                    p.writeShort(self.client.visuItems[category]["ID"])
                    p.writeUnsignedByte(2 if self.client.visuItems[category]["Bonus"] else (1 if not self.client.Shop.checkInShop(self.client.visuItems[category]["ID"]) else 0))
                    p.writeUnsignedShort(buy[0])
                    p.writeUnsignedShort(buy[1])
                    p.writeUnsignedByte(3 if not self.client.visuItems[category]["Customizable"] else (2 if self.client.visuItems[category]["CustomBonus"] else (1 if self.client.visuItems[category]["HasCustom"] == False else 0)))
                    p.writeUnsignedShort(customBuy[0])
                    p.writeUnsignedShort(customBuy[1])
                    
                    allPriceBefore += buy[0] + customBuy[0]
                    allPriceAfter += (0 if (self.client.visuItems[category]["Bonus"]) else (0 if self.client.Shop.checkInShop(itemID) else buy[1])) + (0 if (not self.client.visuItems[category]["Customizable"]) else (0 if self.client.visuItems[category]["CustomBonus"] else (0 if self.client.visuItems[category]["HasCustom"] else (customBuy[1]))))
                    
                p.writeShort(allPriceBefore)
                p.writeShort(allPriceAfter)
                self.client.priceDoneVisu = allPriceAfter

                self.client.sendPacket(Identifiers.send.Buy_Full_Look, p.toByteArray())

            elif CC == Identifiers.recv.Sly.Map_Info:
                self.client.room.cheesesList = []
                cheesesCount = packet.readByte()
                i = 0
                while i < cheesesCount / 2:
                    cheeseX, cheeseY = packet.readShort(), packet.readShort()
                    self.client.room.cheesesList.append([cheeseX, cheeseY])
                    i += 1
                
                self.client.room.holesList = []
                holesCount = packet.readByte()
                i = 0
                while i < holesCount / 3:
                    holeType, holeX, holeY = packet.readShort(), packet.readShort(), packet.readShort()
                    self.client.room.holesList.append([holeType, holeX, holeY])
                    i += 1
                return

        if self.server.isDebug:
            print "[%s] Packet not implemented - C: %s - CC: %s - packet: %s" %(self.client.playerName, C, CC, repr(packet.toByteArray()))

    def parsePacketUTF(self, packet):
        values = packet.split(chr(1))
        C = ord(values[0][0])
        CC = ord(values[0][1])
        values = values[1:]

        if C == Identifiers.old.recv.Player.C:
            if CC == Identifiers.old.recv.Player.Conjure_Start:
                self.client.room.sendAll(Identifiers.old.send.Conjure_Start, values)
                return

            elif CC == Identifiers.old.recv.Player.Conjure_End:
                self.client.room.sendAll(Identifiers.old.send.Conjure_End, values)
                return

            elif CC == Identifiers.old.recv.Player.Conjuration:
                reactor.callLater(10, self.client.sendConjurationDestroy, int(values[0]), int(values[1]))
                self.client.room.sendAll(Identifiers.old.send.Add_Conjuration, values)
                return

            elif CC == Identifiers.old.recv.Player.Snow_Ball:
                self.client.sendPlaceObject(0, 34, int(values[0]), int(values[1]), 0, 0, 0, False, True)
                return

            elif CC == Identifiers.old.recv.Player.Bomb_Explode:
                self.client.room.sendAll(Identifiers.old.send.Bomb_Explode, values)
                return

        elif C == Identifiers.old.recv.Room.C:
            if CC == Identifiers.old.recv.Room.Anchors:
                self.client.room.sendAll(Identifiers.old.send.Anchors, values)
                self.client.room.anchors.extend(values)
                return

            elif CC == Identifiers.old.recv.Room.Begin_Spawn:
                if not self.client.isDead:
                    self.client.room.sendAll(Identifiers.old.send.Begin_Spawn, [self.client.playerCode] + values)
                return

            elif CC == Identifiers.old.recv.Room.Spawn_Cancel:
                self.client.room.sendAll(Identifiers.old.send.Spawn_Cancel, [self.client.playerCode])
                return

            elif CC == Identifiers.old.recv.Room.Totem_Anchors:
                if self.client.room.isTotemEditor:
                    if self.client.tempTotem[0] < 20:
                        self.client.tempTotem[0] = int(self.client.tempTotem[0]) + 1
                        self.client.sendTotemItemCount(self.client.tempTotem[0])
                        self.client.tempTotem[1] += "#3#" + chr(1).join(map(str, [values[0], values[1], values[2]]))
                return

            elif CC == Identifiers.old.recv.Room.Move_Cheese:
                self.client.room.sendAll(Identifiers.old.send.Move_Cheese, values)
                return

            elif CC == Identifiers.old.recv.Room.Bombs:
                self.client.room.sendAll(Identifiers.old.send.Bombs, values)
                return

        elif C == Identifiers.old.recv.Balloons.C:
            if CC == Identifiers.old.recv.Balloons.Place_Balloon:
                self.client.room.sendAll(Identifiers.old.send.Balloon, values)
                return

            elif CC == Identifiers.old.recv.Balloons.Remove_Balloon:
                self.client.room.sendAllOthers(self.client, Identifiers.old.send.Balloon, [self.client.playerCode, "0"])
                return

        elif C == Identifiers.old.recv.Map.C:
            if CC == Identifiers.old.recv.Map.Vote_Map:
                if len(values) == 0:
                    self.client.room.receivedNo += 1
                else:
                    self.client.room.receivedYes += 1
                return

            elif CC == Identifiers.old.recv.Map.Load_Map:
                values[0] = values[0].replace("@", "")
                if values[0].isdigit():
                    code = int(values[0])
                    self.client.room.CursorMaps.execute("select * from Maps where Code = ?", [code])
                    rs = self.client.room.CursorMaps.fetchone()
                    if rs:
                        if self.client.playerName == rs["Name"] or self.client.privLevel >= 6:
                            self.client.sendPacket(Identifiers.old.send.Load_Map, [rs["XML"], rs["YesVotes"], rs["NoVotes"], rs["Perma"]])
                            self.client.room.EMapXML = rs["XML"]
                            self.client.room.EMapLoaded = code
                            self.client.room.EMapValidated = False
                        else:
                            self.client.sendPacket(Identifiers.old.send.Load_Map_Result, [])
                    else:
                        self.client.sendPacket(Identifiers.old.send.Load_Map_Result, [])
                else:
                    self.client.sendPacket(Identifiers.old.send.Load_Map_Result, [])
                return

            elif CC == Identifiers.old.recv.Map.Validate_Map:
                mapXML = values[0]
                if self.client.room.isEditor:
                    self.client.sendPacket(Identifiers.old.send.Map_Editor, [""])
                    self.client.room.EMapValidated = False
                    self.client.room.EMapCode = 1
                    self.client.room.EMapXML = mapXML
                    self.client.room.mapChange()
                return

            elif CC == Identifiers.old.recv.Map.Map_Xml:
                self.client.room.EMapXML = values[0]
                return

            elif CC == Identifiers.old.recv.Map.Return_To_Editor:
                self.client.room.EMapCode = 0
                self.client.sendPacket(Identifiers.old.send.Map_Editor, ["", ""])
                return

            elif CC == Identifiers.old.recv.Map.Export_Map:
                isTribeHouse = len(values) != 0
                if self.client.cheeseCount < 40 and self.client.privLevel < 6 and not isTribeHouse:
                    self.client.sendMessage("<ROSE>Haritayı Aktarabilmek İçin 40 Peynire İhtiyacınız Var.", False)
                elif self.client.shopCheeses < (5 if isTribeHouse else 40) and self.client.privLevel < 6:
                    self.client.sendPacket(Identifiers.old.send.Editor_Message, ["", ""])
                elif self.client.room.EMapValidated or isTribeHouse:
                    if self.client.privLevel < 6:
                        self.client.shopCheeses -= 5 if isTribeHouse else 40

                    code = 0
                    if self.client.room.EMapLoaded != 0:
                        code = self.client.room.EMapLoaded
                        self.client.room.CursorMaps.execute("update Maps set XML = ?, Updated = ? where Code = ?", [self.client.room.EMapXML, Utils.getTime(), code])
                    else:
                        self.server.lastMapEditeurCode += 1
                        self.server.configs("game.lastMapCodeId", str(self.server.lastMapEditeurCode))
                        self.server.updateConfig()
                        code = self.server.lastMapEditeurCode
                        
                    self.client.room.CursorMaps.execute("insert into Maps (Code, Name, XML, YesVotes, NoVotes, Perma, Del) values (?, ?, ?, ?, ?, ?, ?)", [code, self.client.playerName, self.client.room.EMapXML, 0, 0, 22 if isTribeHouse else 0, 0])
                    self.client.sendPacket(Identifiers.old.send.Map_Editor, ["0"])
                    self.client.enterRoom(self.server.recommendRoom(self.client.langue))
                    self.client.sendPacket(Identifiers.old.send.Map_Exported, [code])
                return

            elif CC == Identifiers.old.recv.Map.Reset_Map:
                self.client.room.EMapLoaded = 0
                return

            elif CC == Identifiers.old.recv.Map.Exit_Editor:
                self.client.sendPacket(Identifiers.old.send.Map_Editor, ["0"])
                self.client.enterRoom(self.server.recommendRoom(self.client.langue))
                return

            elif C == Identifiers.old.recv.Draw.C:
                if CC == Identifiers.old.recv.Draw.Drawing:
                    if self.client.privLevel >= 10:
                        self.client.room.sendAllOthers(self.client, Identifiers.old.send.Drawing, values)
                    return

            elif CC == Identifiers.old.recv.Draw.Point:
                if self.client.privLevel >= 10:
                    self.client.room.sendAllOthers(self.client, Identifiers.old.send.Drawing_Point, values)
                return

            elif CC == Identifiers.old.recv.Draw.Clear:
                if self.client.privLevel >= 10:
                    self.client.room.sendAll(Identifiers.old.send.Drawing_Clear, values)
                return


        if self.server.isDebug:
            print "[%s][OLD] Packet not implemented - C: %s - CC: %s - values: %s" %(self.client.playerName, C, CC, repr(values))

    def descriptPacket(self, packetID, packet):
        data = ByteArray()
        while packet.bytesAvailable():
            packetID = (packetID + 1) % len(self.server.packetKeys)
            data.writeByte(packet.readByte() ^ self.server.packetKeys[packetID])
        return data
