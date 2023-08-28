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
from typing import List, Tuple, Union

class TCPClient():
    # Machine works with degrees and mm 
    
    ANSWER_WAIT_TIME = 0.25
    
    def __init__(self, ip: str="192.168.137.100", port: int=20002):
        self.ip = ip
        self.port = port
        self._socket = None
        self.display_log = False

        self.log(f"Connecting to robot at {self.ip}:{self.port}")
        self.log("Waiting the server...")
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.connect((self.ip, self.port))
        except Exception as e:
            self.log(f"Socket connection failed. Error: {e}")
            raise e

        self._socket.settimeout(30)

        self.log(f"Connection on {port}")

    def log(self, msg):
        if self.display_log:
            print(msg)

    def close_socket(self):
        self._socket.close()
        self.log("Close robot socket")
        
    def __del__(self):
        self.close_socket()

    def recv(self, bufsize: int=255) -> Union[str, None]:
        response = b""
        while True:
            data = None
            try:
                data = self._socket.recv(bufsize)
            except socket.timeout as e:
                self.log(e)
            except Exception as e:
                self.log(f"Socket connection failed. Error: {e}")
                raise e
            if data:
                self.log(f"data {data}")
                response += data
                if b"\r" in data:
                    response = response[:-1]
                    break
        
        return response.decode()

    def send(self, cmd) -> bool:
        cmd += "\r"
        bytes_sent = self._socket.send((cmd).encode())
        if len(cmd) != bytes_sent:
            self.log(f"Error during sending commande {cmd}, bytes_sent = {bytes_sent}")
            return False
        return True

    def send_and_receive(self, msg, log=True) -> str:
        if log:
            self.log(f"Send '{msg}' to the robot")
        self.send(msg)

        time.sleep(TCPClient.ANSWER_WAIT_TIME)

        response = self.recv()
        if log:
            self.log(f"Received '{response}' from the robot")

        return response

    def hi(self):
        response = self.send_and_receive("hi")
        return response == "hi,done"
    
    def set_machine_display_log(self, status):
        response = self.send_and_receive(f"display_logs,{status}")
        return response == "display_logs,done"

    def wait_manual_guide(self):
        response = self.send_and_receive("wait_manual_guide")
        return response == "wait_manual_guide,done"

    def goto(self, x, y, z, rx, ry, rz, vel, acc, app_type, ref, mod) -> bool:
        response = self.send_and_receive(f"goto,{x},{y},{z},{rx},{ry},{rz},{vel},{acc},{app_type},{ref},{mod}")
        return response == "goto,done"

    def gotoc(self, pos1, pos2, vel, acc, app_type, ref, mod) -> bool:
        pos1, pos2 = [str(p) for p in pos1], [str(p) for p in pos2]
        response = self.send_and_receive(f"gotoc,{','.join(pos1)},{','.join(pos2)},{vel},{acc},{app_type},{ref},{mod}")
        return response == "gotoc,done"

    def offset(self, pos, z) -> Union[None, List[float]]:  
        pos = [str(p) for p in pos]     
        response = self.send_and_receive(f"offset,{','.join(pos)},z")
        if not "offset,done" in response:
            return None
        return [float(p) for p in response.split(",")[2:]]

    def gotop(self, x, y, z, rx, ry, rz, vel, acc, ref, mod) -> bool:       
        response = self.send_and_receive(f"gotop,{x},{y},{z},{rx},{ry},{rz},{vel},{acc},DR_MV_APP_NONE,{ref},{mod}")
        return response == "gotop,done"
    
    def approachpoint(self, pos) -> bool:
        pos = [str(p) for p in pos]
        response = self.send_and_receive(f"approachpoint,{','.join(pos)}")
        return response == "approachpoint,done"
    
    def gotoj(self, j1, j2, j3, j4, j5, j6) -> bool:
        response = self.send_and_receive(f"gotoj,{j1},{j2},{j3},{j4},{j5},{j6}")
        return response == "gotoj,done"

    def get_current_posj(self) -> Union[None, List[float]]:
        response = self.send_and_receive("get_current_posj")

        if response != None:
            response = response.split(",")
            self.log(f"response split: {response}")
            if response[0] == "posj": 
                return response[1:]

            self.log("response don't start with 'posj'")

        return None

    def get_current_posx(self) -> Tuple[Union[None, List[float]], Union[None, float]]:
        response = self.send_and_receive("get_current_posx")

        if response != None:
            response = response.split(",")
            self.log(f"response split:{response}")
            if response[0] == "posx": 
                return [float(r) for r in response[1:-1]], response[-1]
            self.log("response don't start with 'posx'")
        return None, None
    
    def get_digital_input(self, input_id: int) -> bool:
        response = self.send_and_receive(f"get_digital_input,{input_id}")

        if response != None:
            response = response.split(",")
            if response[0] == "input":
                return bool(int(response[1]))
        return False

    def app_weld_enable_digital(self) -> bool:
        response = self.send_and_receive("app_weld_enable_digital")
        return response == "app_weld_enable_digital,done"
    
    def app_weld_disable_digital(self):
        response = self.send_and_receive("app_weld_disable_digital")
        return response == "app_weld_disable_digital,done"
    
    def app_weld_set_weld_cond_digital(self, flag_dry_run, vel_target, vel_min, vel_max, simulation, job_num, synergic_id, r_wire_feed_speed):
        response = self.send_and_receive(f"app_weld_set_weld_cond_digital,{flag_dry_run},{vel_target},{vel_min},{vel_max},0,0,0,0,{simulation},0,0,{job_num},{synergic_id},{r_wire_feed_speed},0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
        return response == "app_weld_set_weld_cond_digital,done"
    
    def app_weld_adj_welding_cond_digital(self, vel_target, job_number, synergic_id):
        response = self.send_and_receive(f"app_weld_adj_welding_cond_digital,{vel_target},{job_number},{synergic_id}")
        return response == "app_weld_adj_welding_cond_digital,done"
    
    def reset_weld_cond(self, flag_reset):
        response = self.send_and_receive(f"reset_weld_cond,{flag_reset}")
        return response == "reset_weld_cond,done"
    
    def send_mission(self, mission_name) -> bool:
        response = self.send_and_receive(mission_name)
        return response == f"{mission_name},done"