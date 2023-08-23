from tcp_ip_advance.computer import TCPClient
from typing import List

class Machine:
    def __init__(self, ip="192.168.137.100", port=20002):
        self.tcp_client = TCPClient(ip, port)
    
    def __del__(self):
        self.tcp_client.close_socket()
    
    def get_digital_input(self, input_number) -> bool:
        cmd = f"get_digital_input,{input_number}"
        self.write(cmd)
        res, response = self.read()
        if res > 0 and response.startswith("digital_input"):
            return response.split(",")[1] == "ON"
        return False

    def get_current_posx(self) -> List[float]:
        cmd = "get_current_posx"
        self.write(cmd)
        res, response = self.read()
        if res > 0 and response.startswith("posx"):
            return response.split(",")[1:-1]
        return None

    def move_to_position(self, x, y, z, rx, ry, rz, vel=30, acc=20) -> bool:
        """ Move the robot to a specified position """
        msg = f"movel({x},{y},{z},{rx},{ry},{rz}),vel={vel},acc={acc},ref=DR_BASE,mod=DR_MV_MOD_ABS"
        self.send(msg)
        response = self.recv()
        if response == "movel,done":
            return True
        return False
    
    def move_circular(self, start_position, end_position, vel=30, acc=20, app_type=DR_MV_APP_NORMAL, ref=DR_BASE):
        """ Move the robot in a circular path between two positions """
        msg = f"movec({start_position},{end_position}),vel={vel},acc={acc},app_type={app_type},ref={ref}"
        self.send(msg)
        response = self.recv()
        if response == "movec,done":
            return True
        return False