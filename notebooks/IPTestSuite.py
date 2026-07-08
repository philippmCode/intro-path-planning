# coding: utf-8

"""
This code is part of the course "Introduction to robot path planning" (Author: Bjoern Hein).
It gathers all visualizations of the investigated and explained planning algorithms.
License is based on Creative Commons: Attribution-NonCommercial 4.0 International (CC BY-NC 4.0) (pls. check: http://creativecommons.org/licenses/by-nc/4.0/)
"""

from IPBenchmark import Benchmark 
from IPEnvironment import CollisionChecker
from shapely.geometry import Point, Polygon, LineString
import shapely.affinity
import math
import numpy as np


benchList = list()

# -----------------------------------------
trapField = dict()
trapField["obs1"] =   LineString([(6, 18), (6, 8), (16, 8), (16,18)]).buffer(1.0)
description = "Following the direct connection from goal to start would lead the algorithm into a trap."
benchList.append(Benchmark("Trap", CollisionChecker(trapField), [[10,15]], [[10,1]], description, 2))

# -----------------------------------------
bottleNeckField = dict()
bottleNeckField["obs1"] = LineString([(0, 13), (11, 13)]).buffer(.5)
bottleNeckField["obs2"] = LineString([(13, 13), (23,13)]).buffer(.5)
description = "Planer has to find a narrow passage."
benchList.append(Benchmark("Bottleneck", CollisionChecker(bottleNeckField), [[4,15]], [[18,1]], description, 2))

# -----------------------------------------
fatBottleNeckField = dict()
fatBottleNeckField["obs1"] = Polygon([(0, 8), (11, 8),(11, 15), (0, 15)]).buffer(.5)
fatBottleNeckField["obs2"] = Polygon([(13, 8), (24, 8),(24, 15), (13, 15)]).buffer(.5)
description = "Planer has to find a narrow passage with a significant extend."
benchList.append(Benchmark("Fat bottleneck", CollisionChecker(fatBottleNeckField), [[4,21]], [[18,1]], description, 2))

# -----------------------------------------

myField = dict()
myField["L"] = Polygon([(10, 16), (10, 11), (13, 11), (13,12), (11,12), (11,16)])
myField["T"] = Polygon([(14,16), (14, 15), (15, 15),(15,11), (16,11), (16,15), (17, 15), (17, 16)])
myField["C"] = Polygon([(19, 16), (19, 11), (22, 11), (22, 12), (20, 12), (20, 15), (22, 15), (22, 16)])

myField["Antenna_L"] = Polygon([(3, 12), (1, 16), (2, 16), (4, 12)])
myField["Antenna_Head_L"] = Point(1.5, 16).buffer(1)

myField["Antenna_R"] = Polygon([(7, 12), (9, 16), (8, 16), (6, 12)])
myField["Antenna_Head_R"] = Point(8.5, 16).buffer(1)

myField["Rob_Head"] = Polygon([(2, 13), (2, 8), (8, 8), (8, 13)])
description = "Planer has to find a passage past a robot head and the print of the LTC."
benchList.append(Benchmark("MyField", CollisionChecker(myField), [[4,21]], [[18,1]], description, 2))

# ---------------------------------------------------------
zigzagField = dict()
zigzagField["obs1"] = Polygon([
    # downwards (inner side)
    (0, 17), (14, 15), (4, 13), (14, 11), (4, 9), (14, 7), (0, 5),
    # upwards (outer tips, slightly offset for wall thickness)
    (0, 4), (16, 7), (6, 9), (16, 11), (6, 13), (16, 15), (0, 18)
]).buffer(.5)
description_zigzag = "Tests if the planner falls into local minima (zigzags) or finds the global path around them."
# start on the top left and goal on the bottom left
benchList.append(Benchmark(
    "Zigzag Traps", 
    CollisionChecker(zigzagField), 
    [[4, 21]], 
    [[4, 3]], 
    description_zigzag, 
    2
))


# ---------------------------------------------------------

emptyField = dict() 
# no obstacles
description_empty = "Tests the path optimality and smoothing. The planner should find a perfectly straight line."
# Start on the top center [12, 21], goal on the bottom center [12, 3]
benchList.append(Benchmark(
    "Empty Field", 
    CollisionChecker(emptyField), 
    [[12, 21]], 
    [[12, 3]], 
    description_empty, 
    2
))


# ---------------------------------------------------------
# Clutter / Forest Field
clutterField = dict()

# Define a deterministic set of coordinates for small obstacles
positions = [(5, 5), (8, 12), (12, 18), (15, 6), (18, 14), (6, 15), (10, 8), (14, 12), (20, 4)]
for i, (x, y) in enumerate(positions):
    # Create a small circular obstacle for each position
    clutterField[f"tree_{i}"] = Point(x, y).buffer(1.2)
    
description_clutter = "Tests sampling algorithms and the ability to navigate through multiple unstructured small obstacles."
# Start bottom-left, goal top-right
benchList.append(Benchmark("Clutter Forest", CollisionChecker(clutterField), [[2, 2]], [[22, 20]], description_clutter, 2))

# ---------------------------------------------------------
# Dual Path Field
dualPathField = dict()

# Large central block forcing the planner to choose between a top or bottom route
dualPathField["center_block"] = Polygon([(4, 10), (20, 10), (20, 16), (4, 16)])

# Bottom block creating a very narrow but direct lower passage (y=8.5 to y=10)
dualPathField["bottom_block"] = Polygon([(4, 0), (20, 0), (20, 8.5), (4, 8.5)])

description_dual = "Tests if the planner prefers a short, extremely narrow path or a longer, wider, and safer path."
# Start on the left, goal on the right
benchList.append(Benchmark("Dual Path", CollisionChecker(dualPathField), [[2, 9]], [[22, 9]], description_dual, 2))

# ---------------------------------------------------------
# Nested Bug Trap
nestedTrapField = dict()

# Outer C-Shape opening to the bottom
nestedTrapField["outer_C"] = LineString([(18, 20), (4, 20), (4, 4), (18, 4)]).buffer(1.0)

# Inner C-Shape opening to the right
nestedTrapField["inner_C"] = LineString([(8, 16), (14, 16), (14, 8), (8, 8)]).buffer(1.0)

description_nested = "A complex trap setup forcing massive backtracking. Especially hard for potential fields and bug algorithms."
# Start inside the inner trap, goal completely outside on the bottom right
benchList.append(Benchmark("Nested Trap", CollisionChecker(nestedTrapField), [[11, 12]], [[22, 2]], description_nested, 2))