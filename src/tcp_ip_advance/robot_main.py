# -*- coding: utf-8 -*-
"""
An advance example of TCP/IP communication (main robot part)

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

What does this example: Use the TCPServer class to communicate with an computer
"""
import time

computer = TCPServer()

while True:
    time.sleep(0.05)
    res, msg = computer.read()
    if res <= 0 or msg == "":
        continue

    computer.robot_log("Message from computer: " + str(msg))
    msg = msg.split(",")
    
    if msg[0] == "hi":
        computer.hi()
    elif msg[0] == "display_logs":
        computer.display_logs(msg[1])
    elif msg[0] == "wait_manual_guide":
        computer.wait_manual_guide_robot()
    elif msg[0] == "goto":
        computer.goto(msg[1:7], *msg[7:])
    elif msg[0] == "gotoj":
        computer.gotoj(msg[1:7], *msg[7:])
    elif msg[0] == "gotoc":
        computer.gotoc(msg[1:7], msg[7:13], *msg[13:])
    elif msg[0] == "gotooffset":
        computer.gotooffset(msg[1:7], *msg[7:])
    elif msg[0] == "gotop":
        computer.gotop(msg[1:7], *msg[7:])
    elif msg[0] == "get_current_posj":
        computer.get_posj()
    elif msg[0] == "get_current_rotm":
        computer.get_rotm()
    elif msg[0] == "get_current_posx":
        computer.get_posx()
    elif msg[0] == "get_digital_input":
        computer.get_d_input(int(msg[1]))
    elif msg[0] == "app_weld_enable_digital":
        computer.app_weld_enable_digital_robot()
    elif msg[0] == "app_weld_disable_digital":
        computer.app_weld_disable_digital_robot()
    elif msg[0] == "app_weld_set_weld_cond_digital":
        computer.app_weld_set_weld_cond_digital_robot(*msg[1:32])
    elif msg[0] == "app_weld_adj_welding_cond_digital":
        computer.app_weld_adj_welding_cond_digital_robot(*msg[1:4])
    elif msg[0] == "reset_weld_cond":
        computer.reset_weld_cond_robot(msg[1])