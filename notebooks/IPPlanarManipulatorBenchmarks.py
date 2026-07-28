from IPEnvironmentKin import KinChainCollisionChecker
from IPPlanarManipulator import PlanarRobot
from shapely.geometry import LineString

def create_planar_benchmarks():
    """Create two reusable planar manipulator benchmarks for Task 9."""
    obstacles_2dof = {
        "obs1": LineString([(-2.2, 0.0), (-0.8, 0.0)]).buffer(0.45),
        "obs2": LineString([(1.4, 0.0), (1.4, 1.2)]).buffer(0.18),
        "obs3": LineString([(-1.0, 1.6), (1.1, 1.6)]).buffer(0.12),
    }

    # Redesigned 4-DoF obstacles to guarantee safe start/goal states.
    # Two vertical pillars on the left and right, leaving the Y-axis completely free.
    obstacles_4dof = {
        "obs1": LineString([(1.8, -2.5), (1.8, 2.5)]).buffer(0.3),
        "obs2": LineString([(-1.8, -2.5), (-1.8, 2.5)]).buffer(0.3),
    }

    return [
        {
            "name": "Planar 2-DoF corridor",
            "dof": 2,
            "obstacles": obstacles_2dof,
            # The direct interpolation intersects an obstacle; the planner
            # must route around it in configuration space.
            "start": [-0.5825, -2.4636],
            "goal": [-0.6016, 3.0480],
            "limits": [[-3.14, 3.14], [-3.14, 3.14]],
            "fk_resolution": 0.2,
            "description": "A 2-DoF narrow-passage problem; start and goal are free but their direct joint-space edge is in collision.",
        },
        {
            "name": "Planar 4-DoF sweep",
            "dof": 4,
            "obstacles": obstacles_4dof,
            # Arm points straight DOWN along the Y-axis. Completely clear of obstacles.
            "start": [-1.57, 0.0, 0.0, 0.0],
            # Arm points straight UP along the Y-axis. Completely clear of obstacles.
            "goal": [1.57, 0.0, 0.0, 0.0], 
            "limits": [[-3.14, 3.14], [-3.14, 3.14], [-3.14, 3.14], [-3.14, 3.14]],
            "fk_resolution": 0.2,
            "description": "A 4-DoF sweep: the direct upright-to-inverted motion hits both pillars, so the arm has to fold before rotating.",
        },
    ]

def build_planar_environment(benchmark):
    """Create a KinChainCollisionChecker for a benchmark definition."""
    robot = PlanarRobot(n_joints=benchmark["dof"])
    limits = benchmark.get("limits")
    environment = KinChainCollisionChecker(
        robot,
        benchmark["obstacles"],
        limits=limits,
        fk_resolution=benchmark.get("fk_resolution", 0.2),
    )
    return environment
