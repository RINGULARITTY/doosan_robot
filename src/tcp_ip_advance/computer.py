# -*- coding: utf-8 -*-
"""
An advance example of TCP/IP communication (TCPServer class part)
Copyright (C) 2021 HumaRobotics

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import socket
import time
import math

class TCPClient():
    """Class of the client TCP connection"""

    def __init__(self, ip="192.168.137.100", port=20002):
        """
        Initialize robot connection

        Params:\n
            - 'ip': ip of the robot
            - 'port': port of the TCP connection
        """

        self.ip = ip
        self.port = port
        self._socket = None

        print("Connecting to robot at %s:%d"%(self.ip, self.port))
        print("Waiting the server...")
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.connect((self.ip, self.port))
        except Exception as e:
            print("Socket connection failed. Error: {0}".format(
            str(e)))
            raise e

        self._socket.settimeout(30)

        print("Connection on {}".format(port))

    def close_socket(self):
        """ Close the robot network socket"""
        self._socket.close()
        print("Close robot socket")
        
    def __del__(self):
        """ Destructor: close the robot socket before close the program"""
        print("call __del__ function")
        self.close_socket()

    def recv(self, bufsize=255):
        """
        Read the socket

        Params:\n
            - 'bufsize': number of bytes to read (default = 255)

        Return:\n
            - 'response': data if data is received, None otherwise
        """
        response = b""
        while True:
            data = None
            try:
                data = self._socket.recv(bufsize)
            except socket.timeout as e:
                print(e)
            except Exception as e:
                print("Socket connection failed. Error: {0}".format(
                str(e)))
                raise e
            if data:
                print("data", data)
                response += data
                if b"\r" in data:
                    response = response[:-1]
                    break
        
        return response.decode()

    def send(self, cmd):
        """
        Write 'cmd' in the socket

        Params:\n
            - 'cmd': command send to the robot
        """
        cmd += "\r"
        bytes_sent = self._socket.send((cmd).encode())
        if len(cmd) != bytes_sent:
            print("Error during sending commande {0}, bytes_sent = {1}".format(cmd, bytes_sent))
            return -1
        return 0

    def goto(self,x,y,z,rx,ry,rz):
        """
        Tell the robot to reach x,y,z,rx,ry,rz position expressed in meters and radians
        Return:\n
            - 'done': True if the position is reached, None otherwise
        """
        x = x * 1000
        y = y * 1000
        z = z * 1000
        rx = math.degrees(rx)
        ry = math.degrees(ry)
        rz = math.degrees(rz)
        msg = "goto," + str(x) + "," + str(y) + "," + str(z) + "," + str(rx) + "," + str(ry) + "," + str(rz)
        print("Send '{0}' to the robot".format(msg))
        self.send(msg)
        time.sleep(0.1)
        response = self.recv()
        print("response", response)
        if response == "goto,done":
            return True

    def gotoc(self, pos1, pos2, vel, acc, app_type, ref, mod):
        """
        Tell the robot to move from pos1 to pos2 with movec, both positions expressed in meters and radians
        Return:\n
            - 'done': True if the movement is completed, None otherwise
        """
        pos1_x, pos1_y, pos1_z, pos1_rx, pos1_ry, pos1_rz = pos1
        pos2_x, pos2_y, pos2_z, pos2_rx, pos2_ry, pos2_rz = pos2
        
        pos1_x = pos1_x * 1000
        pos1_y = pos1_y * 1000
        pos1_z = pos1_z * 1000
        pos1_rx = math.degrees(pos1_rx)
        pos1_ry = math.degrees(pos1_ry)
        pos1_rz = math.degrees(pos1_rz)
        
        pos2_x = pos2_x * 1000
        pos2_y = pos2_y * 1000
        pos2_z = pos2_z * 1000
        pos2_rx = math.degrees(pos2_rx)
        pos2_ry = math.degrees(pos2_ry)
        pos2_rz = math.degrees(pos2_rz)
        
        vel = str(vel)
        acc = str(acc)
        app_type = str(app_type)
        ref = str(ref)
        mod = str(mod)
        
        msg = f"gotoc,{pos1_x},{pos1_y},{pos1_z},{pos1_rx},{pos1_ry},{pos1_rz},{pos2_x},{pos2_y},{pos2_z},{pos2_rx},{pos2_ry},{pos2_rz},{vel},{acc},{app_type},{ref},{mod}"
        print("Send '{0}' to the robot".format(msg))
        self.send(msg)
        time.sleep(0.1)
        response = self.recv()
        print("response", response)
        if response == "gotoc,done":
            return True
        return None   

    def gotooffset(self,z, vel, acc, ref, mod):
        """
        Tell the robot to go to the current position to the offset position in z in reference to the tool and the mode relative
        """
        x = 0
        y = 0
        z = z * 1000
        rx = 0
        ry = 0
        rz = 0
        vel = str(vel)
        acc = str(acc)
        ref = "DR_TOOL"
        mod = "DR_MV_MOD_REL"
        
        msg = f"gotooffset,{x},{y},{z},{rx},{ry},{rz},{vel},{acc},{ref},{mod}"
        print("Send '{0}' to the robot".format(msg))
        self.send(msg)
        time.sleep(0.1)
        response = self.recv()
        print("response", response)
        if response == "gotooffset,done":
            return True
        return None
        
    def gotop(self,x,y,z,rx,ry,rz, vel, acc, app_type, ref, mod):
        x *= 1000
        y *= 1000
        z *= 1000
        rx = math.degrees(rx)
        ry = math.degrees(ry)
        rz = math.degrees(rz)
        
        self.gotooffset(-0.050, 30, 20, "DR_TOOL", "DR_MV_MOD_REL")
        msg = f"gotop,{x},{y},{z},{rx},{ry},{rz},{vel},{acc},{app_type},{ref},{mod}"
        print("Send '{0}' to the robot".format(msg))
        self.send(msg)
        time.sleep(0.1)
        response = self.recv()
        print("response", response)
        if response == "coord_transform,done":
            return True
        return None
    
    def gotoj(self,j1,j2,j3,j4,j5,j6):
        """
        Tell the robot to reach j1,j2,j3,j4,j5,j6 position expressed in radians
        Return:\n
            - 'done': True if the position is reached, None otherwise
        """
        j1 = math.degrees(j1)
        j2 = math.degrees(j2)
        j3 = math.degrees(j3)
        j4 = math.degrees(j4)
        j5 = math.degrees(j5)
        j6 = math.degrees(j6)
        msg = "gotoj," + str(j1) + "," + str(j2) + "," + str(j3) + "," + str(j4) + "," + str(j5) + "," + str(j6)
        print("Send '{0}' to the robot".format(msg))
        self.send(msg)
        time.sleep(0.1)
        response = self.recv()
        print("response", response)
        if response == "gotoj,done":
            return True

        return None

    def get_current_posj(self):
        """
        Ask the robot his current joints state

        Return:\n
            - 'posj': joints 1 values in radians
        """
        msg = "get_current_posj"
        print("Send '{0}' to the robot".format(msg))
        self.send(msg)
        time.sleep(0.1)
        response = self.recv()
        if response != None:
            response = response.split(",")
            print("response split:", response)
            if response[0] == "posj": 
                j1, j2, j3, j4, j5, j6 = response[1:]
                j1 = math.radians(float(j1))
                j2 = math.radians(float(j2))
                j3 = math.radians(float(j3))
                j4 = math.radians(float(j4))
                j5 = math.radians(float(j5))
                j6 = math.radians(float(j6))
                return [j1,j2,j3,j4,j5,j6]
            else:
                print("response don't start with 'posj'")

        return None

    def get_current_posx(self):
        """
        Ask the robot his current posx

        Return:\n
            - 'posx: current coordinate of the tool
            - 'sol_space': current solution space of the robot
        """
        msg = "get_current_posx"
        print("Send '{0}' to the robot".format(msg))
        self.send(msg)
        time.sleep(0.1)
        response = self.recv()
        if response != None:
            response = response.split(",")
            print("response split:", response)
            if response[0] == "posx": 
                posx = [0,0,0,0,0,0]
                for i, elem in enumerate(response[1:-1]):
                    posx[i] = float(elem)
                    if i <= 2:
                        posx[i] = posx[i] / 1000 # mm to m
                    elif i>2:
                        posx[i] = math.radians(posx[i])
                sol_space = response[-1]
                return posx, sol_space
            else:
                print("response don't start with 'posx'")
        return None, None
    
    def get_digital_input(self, input_number):
        msg = "get_digital_input," + str(input_number)
        print("Send '{0}' to the robot".format(msg))
        self.send(msg)
        time.sleep(0.1)
        response = self.recv()
        if response != None:
            response = response.split(",")
            if response[0] == "input":
                input_status = response[1]
                return input_status
        return None

    
    def send_mission(self, mission_name):
        """
        Tell the robot to start the mission: mission_name
        Return:\n
            - 'done': True if the mission is a success, None otherwise
        """
        msg = mission_name
        print("Send '{0}' to the robot".format(msg))
        self.send(msg)
        time.sleep(0.1)
        response = self.recv()
        print("response", response)
        if response == mission_name+",done":
            return True

        return None

if __name__ == "__main__":
    # Example:
    robot = TCPClient(ip="192.168.127.100", port=20002)
    print("Send 'Hello' to the robot")
    robot.send("Hello")
    response = robot.recv()
    print("Response to 'Hello': ", response)

    """done = robot.goto(0.500,0.500,0.500,0,math.radians(90),0)
    print("Response to goto: ", str(done))

    posj = robot.get_current_posj()
    print("Response to get_current_posj:", str(posj))
    
    input_status = robot.get_digital_input(1)
    if input_status == "ON":
        print("L'entrée numérique 1 est activée")

    
    posx = robot.get_current_posx()
    print("Response to get_current_posx:", str(posx))
    
    pos_init = robot.gotoj(90,0,90,0,90,0)
    print("Response to goto: ", str(pos_init))
    
    while True:
        print(robot.get_digital_input(1))"""
    
    move = robot.gotop(0.063,0.403,0.035,math.radians(97.82),math.radians(180),math.radians(0),30,20,"DR_MV_APP_NONE","DR_BASE","DR_MV_MOD_ABS")
    
    robot.close_socket()