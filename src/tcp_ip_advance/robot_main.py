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
from robot import TCPServer

computer = TCPServer()

while True:
    res, msg = computer.read()
    if res <= 0 or msg == "":
        continue

    tp_log("Message from computer: " + str(msg))
    msg = msg.split(",")
    
    match msg[0]:
        case "hi":
            computer.hi()
        case "goto":
            computer.goto(msg[1:])
        case "gotoj":
            computer.gotoj(msg[1:])
        case "gotoc":
            computer.gotoc(msg[1:7], msg[7:13], 30,20,"DR_MV_APP_NONE","DR_BASE","DR_MV_MOD_ABS")
        case "gotooffset":
            computer.gotooffset(msg[1:7],30,20,"DR_TOOL","DR_MV_MOD_REL")
        case "gotop":
            computer.gotop(msg[1:7],30,20,"DR_MV_APP_NONE","DR_BASE","DR_MV_MOD_ABS")
        case "get_current_posj":
            computer.get_posj()
        case "get_current_rotm":
            computer.get_rotm()
        case "get_current_posx":
            computer.get_posx()
        case "get_digital_input":
            input_number = int(msg[1])
            computer.get_d_input(input_number)
        case "app_weld_enable_digital":
            computer.app_weld_enable_digital_robot()
        case "app_weld_disable_digital":
            computer.app_weld_disable_digital_robot()
        case "app_weld_set_weld_cond_digital":
            computer.app_weld_set_weld_cond_digital_robot(*msg[1:32])
        case "app_weld_adj_welding_cond_digital":
            computer.app_weld_adj_welding_cond_digital_robot(*msg[1:4])
        case "reset_weld_cond":
            computer.reset_weld_cond_robot(msg[1])