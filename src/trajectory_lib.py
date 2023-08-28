import os
from math import sqrt, atan, pi
from typing import List, Dict
import jsonpickle
from tkinter import messagebox


class Coordinate:
    def __init__(self, x, y, z, a, b, c=0):
        self.x: float = x
        self.y: float = y
        self.z: float = z
        self.a: float = a
        self.b: float = b
        self.c: float = c
    
    def get_as_array(self):
        return [self.x, self.y, self.z, self.a, self.b, self.c]
    
    def get_with_index(self, index):
        return self.get_as_array()[index]
    
    def to_posx(self):
        return f"posx{self.x, self.y, self.z, self.a, self.b, self.c}"
    
    def str_pos(self):
        return f"{self.x, self.y, self.z}"
    
    def get_angle(self, c2):
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
    START_POS = Coordinate(-6.25, 368, 500, 90, -180, 0)
    
    START: str = "START"
    LINEAR: str = "LINEAR"
    CIRCULAR: str = "CIRCULAR"
    PASS: str = "PASS"
    
    P0: str = "P0"
    PA: str = "PA"
    PB: str = "PB"

    # app_type pas sur premier movement ni passage
    # premier move doit être movel ou movec

    def __init__(self, nature, config, wield_width, coords, vel=30, acc=20):
        self.nature: str = nature
        self.config: str = config
        self.coords: List[Coordinate] = coords
        self.wield_width = wield_width
        self.vel: float = 30
        self.acc: float = 20
    
    def str_coords_pos(self):
        return ", ".join([c.str_pos() for c in self.coords])
    
    def set_c0(self):
        for c in self.coords:
            c.c = 0
    
    def set_p(self):
        for c in self.coords:
            c.set_p(self.config)


class Trajectory:
    def __init__(self, name, trajectory=[
        Movement(Movement.START, "P0", 0, [Movement.START_POS])
    ]):
        self.name: str = name
        self.trajectory: List[Movement] = trajectory

    def save(self, directory) -> bool:
        if os.path.exists(os.path.join(directory, self.name + ".json")):
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
    def load(cls, file_path):
        with open(file_path, 'r') as f:
            return jsonpickle.decode(f.read())

    def add_movement(self, movement: Movement):
        self.trajectory.append(movement)
        
    def re_order(self):
        pass

    def compile(self):
        for i in range(1, len(self.trajectory) - 1):
            prev_m, m, next_m = self.trajectory[i - 1], self.trajectory[i], self.trajectory[i + 1]

            m.set_c0()
            m.set_p()

            if m.nature == Movement.LINEAR:
                if prev_m.nature == Movement.PASS or prev_m.nature == Movement.CIRCULAR:
                    angle = prev_m.coords[-1].get_angle(m.coords)
                    prev_m.coords[-1].a = angle
                    m.coords[0].a = angle
                elif next_m.nature == Movement.LINEAR:
                    angle = m.coords[-1].get_angle(next_m.coords)
                    next_m.coords[0].a = angle
                    m.coords[0].a = angle