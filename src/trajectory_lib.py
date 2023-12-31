import os
from math import sqrt, atan, pi
from typing import List
import jsonpickle
from tkinter import messagebox
from tcp_ip_advance.computer import TCPClient
from path_changer import resource_path
import json

class Coordinate:
    def __init__(self, x, y, z, a, b, c=0):
        self.x: float = round(x, 2)
        self.y: float = round(y, 2)
        self.z: float = round(z, 2)
        self.a: float = round(a, 2)
        self.b: float = round(b, 2)
        self.c: float = round(c, 2)
    
    def get_as_array(self):
        return [self.x, self.y, self.z, self.a, self.b, self.c]
    
    def get_with_index(self, index):
        return self.get_as_array()[index]

    def to_posx(self):
        return f"posx{self.x, self.y, self.z, self.a, self.b, self.c}"
    
    def str_pos(self):
        return f"{self.x:.2f}, {self.y:.2f}, {self.z:.2f}"
    
    def get_angle(self, c2: "Coordinate"):
        dx, dy, dz = c2.x - self.x, c2.y - self.y, c2.z - self.z
        den = sqrt(dx**2 + dz**2)

        if den == 0:
            return 94

        angle_radians = atan(dy / sqrt(dx**2 + dz**2))
        return 90 - 180 * angle_radians / pi

    def set_c0(self):
        self.c = 0

    def set_p(self, config):
        if config == "P0":
            return

        value = {"PA": 135, "PB": 180}[config]
        if self.b > 0:
            self.b = value
        else:
            self.b = -value


class Movement:
    START_POS = Coordinate(-4.49, 369.3, 65.08, 90, -180, 0)
    
    ORIGIN: str = "ORIGIN"
    APPROACH_POINT: str = "APPROACH_POINT"
    LINEAR: str = "LINEAR"
    CIRCULAR: str = "CIRCULAR"
    PASS: str = "PASS"
    ORIENTATION: str = "ORIENTATION"
    CLEARANCE: str = "CLEARANCE"
    
    TRANSLATIONS = {
        ORIGIN: "Origine",
        APPROACH_POINT: "Point d'approche",
        LINEAR: "Linéaire",
        CIRCULAR: "Circulaire",
        PASS: "Passage",
        ORIENTATION: "Orientation",
        CLEARANCE: "Dégagement"
    }
    
    P0: str = "P0"
    PA: str = "PA"
    PB: str = "PB"

    def __init__(self, nature, config, wield_width, coords, vel=30, acc=20):
        self.nature: str = nature
        self.config: str = config
        self.coords: List[Coordinate] = coords
        self.wield_width = wield_width
        self.vel: float = vel
        self.acc: float = acc
    
    def to_string(self):
        match self.nature:
            case Movement.ORIGIN | Movement.APPROACH_POINT | Movement.PASS | Movement.CLEARANCE:
                return f"{Movement.TRANSLATIONS[self.nature]}, {self.config}, {self.str_coords_pos()}, v={self.vel}, a={self.acc}"
            case _:
                return f"{Movement.TRANSLATIONS[self.nature]}, {self.config}, cordon={self.wield_width}, {self.str_coords_pos()}, v={self.vel}, a={self.acc}"

    def str_coords_pos(self):
        return ", ".join([f"p{i + 1}({c.str_pos()})" for i, c in enumerate(self.coords)])
    
    def set_c0(self):
        for c in self.coords:
            c.c = 0
    
    def set_p(self):
        for c in self.coords:
            c.set_p(self.config)


class Trajectory:
    def __init__(self, name, trajectory=[
        Movement(Movement.APPROACH_POINT, "P0", 0, [Coordinate(0, 0, 0, 0, 0, 0)]),
        Movement(Movement.CLEARANCE, "P0", 0, [Coordinate(0, 0, 0, 0, 0, 0)])
    ]):
        with open(resource_path("config.json")) as f:
            config = json.load(f)
        
        trajectory = [Movement(Movement.ORIGIN, "P0", 0, [Coordinate(
            config["default_coords"]["origin"]["x"],
            config["default_coords"]["origin"]["y"],
            config["default_coords"]["origin"]["z"],
            config["default_coords"]["origin"]["a"],
            config["default_coords"]["origin"]["b"],
            config["default_coords"]["origin"]["c"],
        )])] + trajectory
        
        self.name: str = name
        self.trajectory: List[Movement] = trajectory

    def save(self, directory, override=False) -> bool:
        if not override and os.path.exists(os.path.join(directory, self.name + ".json")):
            messagebox.showerror(
                title="Erreur", 
                icon="error", 
                message=f"Une trajectoire au nom de {self.name} existe déjà"
            )
            return False
        with open(os.path.join(directory, self.name + ".json"), 'w') as f:
            f.write(jsonpickle.encode(self, indent=2))
        return True

    @classmethod
    def load(cls, file_path) -> "Trajectory":
        with open(file_path, 'r') as f:
            return jsonpickle.decode(f.read())

    def add_movement(self, robot: TCPClient, movement: Movement):
        self.trajectory.insert(len(self.trajectory) - 1, movement)
        self.compile(robot)
        
    def re_order(self):
        pass

    def compile(self, robot: TCPClient):       
        for i in range(2, len(self.trajectory) - 1):
            prev_m, m, next_m = self.trajectory[i - 1], self.trajectory[i], self.trajectory[i + 1]

            m.set_c0()
            m.set_p()

            if m.nature == Movement.LINEAR or Movement.PASS:
                if prev_m.nature == Movement.PASS or prev_m.nature == Movement.CIRCULAR:
                    angle = prev_m.coords[-1].get_angle(m.coords[0])
                    prev_m.coords[-1].a = angle
                    m.coords[0].a = angle
                elif next_m.nature == Movement.LINEAR:
                    angle = m.coords[0].get_angle(next_m.coords[0])
                    next_m.coords[0].a = angle
                    m.coords[0].a = angle
            elif m.nature == Movement.CIRCULAR:
                if next_m.nature == Movement.LINEAR or next_m.nature == Movement.PASS:
                    angle = m.coords[0].get_angle(next_m.coords[0])
                    m.coords[1].a = angle
                    next_m.coords[0].a = angle

        with open(resource_path("config.json")) as f:
            config = json.load(f)
        
        self.trajectory[1].config = self.trajectory[2].config
        self.trajectory[1].coords = [Coordinate(*robot.offset(
            self.trajectory[2].coords[0].get_as_array(),
            config["default_coords"]["approach_point"]["x_offset"],
            config["default_coords"]["approach_point"]["y_offset"],
            config["default_coords"]["approach_point"]["z_offset"]
        ))]

        self.trajectory[-1].config = self.trajectory[-2].config
        self.trajectory[-1].coords = [Coordinate(*robot.offset(
            self.trajectory[-2].coords[0].get_as_array(),
            config["default_coords"]["clearance_point"]["x_offset"],
            config["default_coords"]["clearance_point"]["y_offset"],
            config["default_coords"]["clearance_point"]["z_offset"]
        ))]