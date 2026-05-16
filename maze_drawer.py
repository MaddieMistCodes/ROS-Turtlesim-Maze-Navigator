#!/usr/bin/env python3

# Draws a maze in turtlesim. Call draw_maze(maze_dict, cmd_vel_pub) once at
# startup and the walls will appear before the navigator takes over.

import math
import rospy
from geometry_msgs.msg import Twist
from turtlesim.srv import TeleportAbsolute, SetPen
from turtlesim.msg import Pose
from std_srvs.srv import Empty

from maze_definitions import grid_to_world, CELL_SIZE, GRID_ROWS, GRID_COLS

## Module-level pose cache — updated by subscriber
_pose = Pose()

def _pose_cb(msg):
    global _pose
    _pose = msg

def _teleport(x, y, theta):
    # Teleport turtle to (x, y, theta) with no trail.
    svc = rospy.ServiceProxy('/turtle1/teleport_absolute', TeleportAbsolute)
    svc(float(x), float(y), float(theta))

def _set_pen(r, g, b, width, off):
    # Call the SetPen service.
    # off=1 → pen up (no drawing), off=0 → pen down (drawing).
    svc = rospy.ServiceProxy('/turtle1/set_pen', SetPen)
    svc(r, g, b, width, off)

def _pen_up():
    _set_pen(255, 255, 255, 3, 1)

def _pen_down():
    # White walls on the turtlesim canvas
    _set_pen(255, 255, 255, 3, 0)

def _clear_canvas():
    # Clear all drawings from the turtlesim canvas.
    try:
        rospy.wait_for_service('/clear', timeout=3.0)
        rospy.ServiceProxy('/clear', Empty)()
    except rospy.ROSException:
        rospy.logwarn("Could not call /clear service — skipping canvas clear.")

# Line drawing

def _draw_line(pub, x1, y1, x2, y2, speed=8.0):
    """
    Draw a straight line from (x1, y1) to (x2, y2).

    Steps:
      • Pen up, teleport to (x1, y1) facing (x2, y2)
      • Pen down, drive forward until we arrive
      • Pen up
    """
    theta = math.atan2(y2 - y1, x2 - x1)

    _pen_up()
    _teleport(x1, y1, theta)
    rospy.sleep(0.05)   # let the teleport settle before moving
    _pen_down()

    rate     = rospy.Rate(50)
    twist    = Twist()
    stop_msg = Twist()

    while not rospy.is_shutdown():
        dx   = x2 - _pose.x
        dy   = y2 - _pose.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < 0.03:
            pub.publish(stop_msg)
            break

        twist.linear.x = min(speed, dist * 6.0)   # slow down near the end
        pub.publish(twist) # Publish the movement
        rate.sleep()

    _pen_up()

# Segment extraction

def _get_wall_segments(grid):
    """
    Walk every wall cell and collect the edges that border open space
    (or the area outside the grid).  Each such edge is added to a set
    so duplicates are automatically removed.

    Returns a list of (x1, y1, x2, y2) tuples in world coordinates.
    Essentially takes the four sides of a square, and splits into segments
    Identifies which segment to be drawn in maze
    """
    segments = set()

    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            if grid[r][c] != 1:
                continue

            # Bottom-left corner of this wall cell in world space
            bx, by = grid_to_world(r, c, center=False)

            # top edge: between (r,c) and (r-1,c) ---
            if r == 0 or grid[r - 1][c] == 0:
                seg = _round_seg(bx, by + CELL_SIZE,
                                 bx + CELL_SIZE, by + CELL_SIZE)
                segments.add(seg)

            # bottom edge: between (r,c) and (r+1,c)
	    # grid_rows - 1 = bottom (9-1)
            if r == GRID_ROWS - 1 or grid[r + 1][c] == 0:
                seg = _round_seg(bx, by,
                                 bx + CELL_SIZE, by)
                segments.add(seg)

            # left edge: between (r,c) and (r,c-1) ---
            if c == 0 or grid[r][c - 1] == 0:
                seg = _round_seg(bx, by,
                                 bx, by + CELL_SIZE)
                segments.add(seg)

            # right edge: between (r,c) and (r,c+1) ---
            if c == GRID_COLS - 1 or grid[r][c + 1] == 0:
                seg = _round_seg(bx + CELL_SIZE, by,
                                 bx + CELL_SIZE, by + CELL_SIZE)
                segments.add(seg)

    return list(segments)

def _round_seg(x1, y1, x2, y2, digits=4):
    """Round segment coordinates to avoid floating-point duplicates."""
    return (round(x1, digits), round(y1, digits),
            round(x2, digits), round(y2, digits))

# Public entry point

def draw_maze(maze_dict, pub):
    """
    Draw a maze and place the turtle at its start position.

    Args:
        maze_dict : one of MAZE_1 / MAZE_2 / MAZE_3 from maze_definitions
        pub       : rospy.Publisher for /turtle1/cmd_vel
    """
    # Subscribe to pose so _draw_line can do pose-based stopping
    rospy.Subscriber('/turtle1/pose', Pose, _pose_cb)
    rospy.sleep(0.3)

    # Wait for the services we need
    for svc in ['/turtle1/teleport_absolute',
                '/turtle1/set_pen']:
        rospy.wait_for_service(svc)

    # Fresh canvas
    _clear_canvas()

    grid     = maze_dict['grid']
    # Gather the segments to draw based on grid in maze_definitions
    segments = _get_wall_segments(grid)

    rospy.loginfo("Drawing maze '%s' (%d wall segments)...",
                  maze_dict.get('name', '?'), len(segments))
    # for loop to draw maze
    for seg in segments:
        x1, y1, x2, y2 = seg
        _draw_line(pub, x1, y1, x2, y2)

    rospy.loginfo("Maze drawn.")

    # Place turtle at the start cell, facing right
    start_row, start_col = maze_dict['start']
    sx, sy = grid_to_world(start_row, start_col, center=True)
    _pen_up()
    _teleport(sx, sy, 0.0)

    # Mark the goal with a visible green X
    goal_row, goal_col = maze_dict['goal']
    gx, gy = grid_to_world(goal_row, goal_col, center=True)

    marker = 0.18  # size of the X

    # First diagonal \
    _draw_marker_line(pub, gx - marker, gy - marker, gx + marker, gy + marker)

    # Second diagonal /
    _draw_marker_line(pub, gx - marker, gy + marker, gx + marker, gy - marker)

    # Return turtle to start
    _pen_up()
    _teleport(sx, sy, 0.0)

    rospy.loginfo("Turtle at start (%.1f, %.1f). Goal at (%.1f, %.1f).",
              sx, sy, gx, gy)

def _draw_marker_line(pub, x1, y1, x2, y2):
    """
    Draw a small green marker line (used for goal marking).
    """
    theta = math.atan2(y2 - y1, x2 - x1)

    _pen_up()
    _teleport(x1, y1, theta)
    rospy.sleep(0.02)

    _set_pen(0, 255, 0, 5, 0)   # green pen down

    rate = rospy.Rate(50)
    twist = Twist()
    stop_msg = Twist()

    while not rospy.is_shutdown():
        dx = x2 - _pose.x
        dy = y2 - _pose.y
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < 0.02:
            pub.publish(stop_msg)
            break

        twist.linear.x = min(2.0, dist * 8.0)
        twist.angular.z = 0.0
        pub.publish(twist)
        rate.sleep()

    _pen_up()
