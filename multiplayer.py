from ursinanetworking import *
from ursina import *
from car import CarRepresentation, CarUsername
from sys import platform

class Multiplayer(Entity):
    def __init__(self, car):
        self.car = car

        if str(self.car.ip.text) != "IP" and str(self.car.port.text) != "PORT":
            self.client = UrsinaNetworkingClient(self.car.ip.text, int(self.car.port.text))
            self.easy = EasyUrsinaNetworkingClient(self.client)

            if platform != "darwin":
                print("Joining Server: " + "\u0332".join(self.car.ip.text) + " on port " + "\u0332".join(self.car.port.text))

            self.players = {}
            self.players_target_name = {}
            self.players_target_pos = {}
            self.players_target_rot = {}
            self.players_target_tex = {}
            self.players_target_score = {}

            self.selfId = -1

            @self.client.event
            def GetId(id):
                self.selfId = id
                print(f"My ID is : {self.selfId}")

            @self.easy.event
            def onReplicatedVariableCreated(variable):
                variable_name = variable.name
                variable_type = variable.content["type"]

                if variable_type == "player":
                    self.players_target_pos[variable_name] = Vec3(-80, -30, 15)
                    self.players_target_rot[variable_name] = Vec3(0, 90, 0)
                    self.players_target_tex[variable_name] = "./assets/garage/car-red.png"
                    self.players_target_name[variable_name] = "Guest"
                    self.players_target_score[variable_name] = 0.0
                    self.players[variable_name] = CarRepresentation(self.car, (-80, -30, 15), (0, 90, 0))
                    self.players[variable_name].text_object = CarUsername(self.players[variable_name])

                    if self.selfId == int(variable.content["id"]):
                        self.players[variable_name].color = color.red
                        self.players[variable_name].visible = False

            @self.easy.event
            def onReplicatedVariableUpdated(variable):
                self.players_target_pos[variable.name] = variable.content["position"]
                self.players_target_rot[variable.name] = variable.content["rotation"]
                self.players_target_tex[variable.name] = variable.content["texture"]
                self.players_target_name[variable.name] = variable.content["username"]
                self.players_target_score[variable.name] = variable.content["highscore"]

            @self.easy.event
            def onReplicatedVariableRemoved(variable):
                variable_name = variable.name
                variable_type = variable.content["type"]
                
                if variable_type == "player":
                    destroy(self.players[variable_name])
                    del self.players[variable_name]

    def update_multiplayer(self):
        for p in self.players:
            self.players[p].position += (Vec3(self.players_target_pos[p]) - self.players[p].position) / 25
            self.players[p].rotation += (Vec3(self.players_target_rot[p]) - self.players[p].rotation) / 25
            self.players[p].texture = f"{self.players_target_tex[p]}"
            self.players[p].text_object.text = f"{self.players_target_name[p]}"
            self.players[p].highscore = f"{self.players_target_score[p]}"

            if distance(self.players_target_pos[p], self.car.position) > 3:
                self.client.send_message("MyPosition", tuple(self.car.position))
                self.client.send_message("MyRotation", tuple(self.car.rotation))

            if self.car.enabled == False:
                self.players[p].disable()
            elif self.car.enabled == True:
                self.players[p].enable()

        if "player_0" in self.players:
            self.car.leaderboard_01 = str(self.players["player_0"].text_object.text) + " | " + str(self.players["player_0"].highscore)
        else:
            self.car.leaderboard_01 = ""
        if "player_1" in self.players:
            self.car.leaderboard_02 = str(self.players["player_1"].text_object.text) + " | " + str(self.players["player_1"].highscore)
        else:
            self.car.leaderboard_02 = ""
        if "player_2" in self.players:
            self.car.leaderboard_03 = str(self.players["player_2"].text_object.text) + " | " + str(self.players["player_2"].highscore)
        else:
            self.car.leaderboard_03 = ""
        if "player_3" in self.players:
            self.car.leaderboard_04 = str(self.players["player_3"].text_object.text) + " | " + str(self.players["player_3"].highscore)
        else:
            self.car.leaderboard_04 = ""
        if "player_4" in self.players:
            self.car.leaderboard_05 = str(self.players["player_4"].text_object.text) + " | " + str(self.players["player_4"].highscore)
        else:
            self.car.leaderboard_05 = ""

        self.easy.process_net_events()