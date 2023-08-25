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

import time
import sys
import os
import socket

class TCPServer:
    """Class of the TCP connection"""

    def __init__(self, port=20002):
        """
        Initialize server

        Params:\n
            - 'port': port of the TCP connection
        """

        self.thread_id = -1

        try:
            self.socket = server_socket_open(port)
            tp_log("Connection ok!")
        except Exception as e:
            tp_popup("Socket connection failed. Error {0}".format(str(e)), DR_PM_ALARM)
            raise e

    def close_socket(self):
        """ Close the network socket"""
        try:
            server_socket_close(self.socket)
            tp_log("Close the socket")
        except Exception as e:
            tp_log("Socket connection was not closed. Error: {0}".format(str(e)))
            raise e

    def read(self, length=-1, timeout=-1):
        """
        Read the socket

        Params:\n
            - 'length': number of bytes to read (default = -1)
            - 'timeout': Waiting time (default = -1)

        Return:\n
            - 'res': result of the reading
            - 'rx_data': data received
        """
        res, rx_data = server_socket_read(self.socket, length, timeout)

        # Check res value
        if res == -1:
            tp_log("error " + 
                "Error during a socket read: Server not connected")
        elif res == -2:
            tp_log("error " + "Error during a socket read: Socket error")
        elif res == -3:
            tp_log("error " + 
                "Error during a socket read: Waiting time has expired")
        elif res > 0:
            if rx_data != "":
                tp_log("info" + 
                    "Read res = {0} and rx_data = {1}".format(res, rx_data))
                rx_data = rx_data[:-1]
                rx_data = rx_data.decode()

        return res, rx_data

    def write(self, msg):
        """
        Write 'msg' in the socket

        Params:\n
            - 'msg': a message

        Return:\n
            - 'res': result of the writing

        Exemple:\n
            write("posj(100,100,100,100,100,100)")
        """
        msg = msg + "\r"
        # Convert msg in ascii before sending
        msg = bytes(msg, encoding="ascii")

        res = server_socket_write(self.socket, msg)

        # Check res value
        if res == -1:
            tp_log("error " + 
                "Error during a socket write: Server not connected")
        elif res == -2:
            tp_log("error " + "Error during a socket write: Socket error")
        elif res == 0:
            tp_log("info" + "Sending {0} command ok".format(msg))
        return res

    def hi(self):
        tp_log("debug " + "hi")
        self.write("hi,done")

    def wait_manual_guide_robot(self):
        try:
            wait_manual_guide()
        except Exception as ex:
            self.write("wait_manual_guide,{}".format(ex))
        self.write("wait_manual_guide,done")

    def goto(self, msg_pos, vel, acc, app_type, ref, mod):
        tp_log("debug " + "goto")
        p = [float(elem) for elem in msg_pos]
        try:
            movel(p,vel=vel,acc=acc,app_type=app_type,ref=ref,mod=mod)
        except Exception as ex:
            self.write("goto,{}".format(ex))
        self.write("goto,done")
        
    def gotoc(self, msg_pos1, msg_pos2, vel, acc, app_type, ref, mod):
        tp_log("debug " + "gotoc")
        p1 = [float(elem) for elem in msg_pos1]
        p2 = [float(elem) for elem in msg_pos2]
        try:
            movec(p1,p2,vel=vel,acc=acc,app_type=eval(app_type),ref=eval(ref),mod=eval(mod))
        except Exception as ex:
            self.write("gotoc,{}".format(ex))
        self.write("gotoc,done")
        
    def gotooffset(self, msg_pos, vel, acc, ref, mod):
        tp_log("debug " + "gotooffset")
        p = [float(elem) for elem in msg_pos]
        try:
            movel(p,vel=vel,acc=acc,ref=eval(ref),mod=eval(mod))
        except Exception as ex:
            self.write("gotooffset,{}".format(ex))
        self.write("gotooffset,done")
        
    def gotop(self, msg_posx,vel, acc, app_type, ref, mod):
        tp_log("debug " + "gotop")
        p = [float(elem) for elem in msg_posx]
        
        try:
            offset = coord_transform(p, DR_BASE, DR_TOOL)
        except Exception as ex:
            self.write("gotop,{}".format(ex))

        tp_log("debug " + "offset: " + str(offset))
        offset[2] -= 50
        tp_log("debug " + "offset: " + str(offset))

        try:
            p2 = coord_transform(offset, DR_TOOL, DR_BASE)
        except Exception as ex:
            self.write("gotop,{}".format(ex))

        try:
            movel(p2, vel=vel,acc=acc,app_type=eval(app_type),ref=eval(ref),mod=eval(mod))
            movel(p, vel=vel,acc=acc,app_type=eval(app_type),ref=eval(ref),mod=eval(mod))
        except Exception as ex:
            self.write("gotop,{}".format(ex))
        self.write("gotop,done")

    def gotoj(self, msg_posj, vel, acc, mod):
        tp_log("debug " + "gotoj")
        p = [float(elem) for elem in msg_posj]
        
        try:
            movej(p, vel=vel, acc=acc, mod=mod)
        except Exception as ex:
            self.write("gotoj,{}".format(ex))
        self.write("gotoj,done")

    def get_posj(self):
        tp_log("debug " + "get_posj")
        
        try:
            current_posj = get_current_posj()
        except Exception as ex:
            self.write("get_posj,{}".format(ex))

        msg = "posj," + str(current_posj).replace(']','').replace('[','')
        self.write(msg)

    def get_posx(self):
        tp_log("debug " + "get_posx")
        
        try:
            posx, sol_space = get_current_posx()
        except Exception as ex:
            self.write("get_current_posx,{}".format(ex))

        msg = "posx," + str(posx).replace(']','').replace('[','') + ',' + str(sol_space)
        self.write(msg)
        
    def get_d_input(self, msg_input_number):
        tp_log("debug " + "get_digital_input")
        
        try:
            input_status = get_digital_input(msg_input_number)
        except Exception as ex:
            self.write("get_digital_input,{}".format(ex))
        msg = "input," + str(input_status)
        self.write(msg)
    
    def app_weld_enable_digital_robot(self):
        tp_log("debug " + "app_weld_enable_digital")
        
        try:
            app_weld_enable_digital()
        except Exception as ex:
            self.write("app_weld_enable_digital,{}".format(ex))

        msg = "app_weld_enable_digital,done"
        self.write(msg)
    
    def app_weld_set_weld_cond_digital_robot(self, flag_dry_run, vel_target, vel_min, vel_max, welding_mode, s_2t, pulse_mode, wm_opt1, simulation, ts_opt1, ts_opt2, job_num, synergic_id, r_wire_feed_speed, voltage_correct, dynamic_correct, r_opt1, r_opt2, r_opt3, r_opt4, r_opt5, r_opt6, r_opt7, r_opt8, r_opt9, r_opt10, r_opt11, r_opt12, r_opt13, r_opt14, r_opt15):
        tp_log("debug " + "app_weld_set_weld_cond_digital")
        try:
            app_weld_set_weld_cond_digital(flag_dry_run, vel_target, vel_min,
                vel_max, welding_mode, s_2t, pulse_mode, wm_opt1,
                simulation, ts_opt1, ts_opt2, job_num, synergic_id,
                r_wire_feed_speed, voltage_correct, dynamic_correct, r_opt1,
                r_opt2, r_opt3, r_opt4, r_opt5, r_opt6, r_opt7, r_opt8,
                r_opt9, r_opt10, r_opt11, r_opt12, r_opt13, r_opt14, r_opt15)
        except Exception as ex:
            self.write("app_weld_set_weld_cond_digital,{}".format(ex))
        msg = "app_weld_set_weld_cond_digital,done"
        self.write(msg)
    
    def app_weld_adj_welding_cond_digital_robot(self, vel_target, job_number, synergic_id):
        tp_log("debug " + "app_weld_adj_welding_cond_digital")
        try:
            app_weld_adj_welding_cond_digital(vel_target=vel_target, job_number=job_number, synergic_id=synergic_id)
        except Exception as ex:
            self.write("app_weld_adj_welding_cond_digital,{}".format(ex))

        msg = "app_weld_adj_welding_cond_digital,done"
        self.write(msg)
    
    def reset_weld_cond_robot(self, flag_reset):
        tp_log("debug " + "reset_weld_cond")
        try:
            reset_weld_cond(flag_reset=flag_reset)
        except Exception as ex:
            self.write("reset_weld_cond,{}".format(ex))
        msg = "reset_weld_cond,done"
        self.write(msg)
    
    def app_weld_disable_digital_robot(self):
        tp_log("debug " + "app_weld_disable_digital")
        try:
            app_weld_disable_digital()
        except Exception as ex:
            self.write("app_weld_disable_digital,{}".format(ex))
        msg = "app_weld_disable_digital,done"
        self.write(msg)