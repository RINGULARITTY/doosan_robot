from trajectory_lib import Trajectory, Movement, Coordinate

t = Trajectory("piece1")
t.add_movement(Movement(Movement.LINEAR, Movement.PB, 0, [Coordinate(-94.12, 12.78, 1.74, 0, 0)]))
t.add_movement(Movement(Movement.CIRCULAR, Movement.PA, 0, [Coordinate(150.74, 54.47, -52.35, 0, 0), Coordinate(-87.74, 12.78, -24.8, 0, 0)]))
t.add_movement(Movement(Movement.LINEAR, Movement.PB, 0, [Coordinate(-87.74, 12.78, -24.8, 0, 0)]))
t.compile()
t.save("./Trajectoires")