#!/usr/bin/env python3

import math
import rospy
from geometry_msgs.msg import Twist
from turtlesim.msg import Pose, Color
from turtlesim.srv import SetPen
from maze_definitions import grid_to_world, is_wall

# Module level varibables
_pose = Pose()
_colour = Color()

# Callback methods to update 
def _pose_cb(msg):
    global _pose
    _pose = msg


def _colour_cb(msg):
    global _colour
    _colour = msg


def _green_detected():
    # Return True if turtle is standing on green marker
    return _colour.g > 200 and _colour.r < 80 and _colour.b < 80

# Get shortest angular difference between two angles
def _angle_diff(target, current):
    diff = target - current
    # These conditionals avoid wrong difference. i.e 350 and 10 have a 20 degree difference, not 340
    while diff > math.pi:
        diff -= 2 * math.pi
    while diff < -math.pi:
        diff += 2 * math.pi
    return diff

# Helper method for turning. Tol is acceptable error in radians
def _turn_to(pub, target_theta, tol=0.03):
    rate = rospy.Rate(50)
    twist = Twist()

    while not rospy.is_shutdown():
        # Check for green while turning
        if _green_detected():
            pub.publish(Twist())
            rospy.loginfo("Green detected during turn. Goal reached!")
            return True
        # Difference between the angle the turtle needs and angle it is currently facing
        err = _angle_diff(target_theta, _pose.theta)
        # if err is under acceptable error stop
        if abs(err) < tol:
            twist.angular.z = 0.0
            twist.linear.x = 0.0
            pub.publish(twist)
            return False
	# Cap turtle speed at max 2.5 min -2.5. Spped is proportional to error
        twist.angular.z = max(-2.5, min(2.5, 3.0 * err))
        twist.linear.x = 0.0
	# Publish the speed
        pub.publish(twist)
        rate.sleep()

# Helper method to drive to target points.
def _drive_to(pub, tx, ty, tol=0.06, speed=1.5):
    rate = rospy.Rate(50)
    twist = Twist()
    stop = Twist()

    while not rospy.is_shutdown():
        if _green_detected():
            pub.publish(stop)
            rospy.loginfo("Green detected while driving. Goal reached!")
            return True
	# Get remaining distance in x and y
        dx = tx - _pose.x
        dy = ty - _pose.y
	# Get distance
        dist = math.sqrt(dx * dx + dy * dy)

        if dist < tol:
            pub.publish(stop)
            return False
	# Max and min speed, turtle will slow down as closer to the targer as it is proportional
        twist.linear.x = max(0.25, min(speed, dist * 2.0))
        twist.angular.z = 0.0
        pub.publish(twist)
        rate.sleep()


def _move_to_cell(pub, row, col):
    wx, wy = grid_to_world(row, col, center=True)
    target_theta = math.atan2(wy - _pose.y, wx - _pose.x) # Angle to point directly at cell

    hit_goal = _turn_to(pub, target_theta) # Turn to the target
    if hit_goal:
        return True

    hit_goal = _drive_to(pub, wx, wy) # drive to goal
    return hit_goal


def _get_heading():

    # Convert turtle heading into one of:
    # up, right, down, left

    theta = _pose.theta

    while theta < 0:
        theta += 2 * math.pi
    while theta >= 2 * math.pi:
        theta -= 2 * math.pi
    # If angle greater than 7pi /4 or under pi/4 as comes full circle
    if theta >= 7 * math.pi / 4 or theta < math.pi / 4:
        return "right"
    elif math.pi / 4 <= theta < 3 * math.pi / 4:
        return "up"
    elif 3 * math.pi / 4 <= theta < 5 * math.pi / 4:
        return "left"
    else:
        return "down"


def _left_forward_right_back(row, col, heading):
    """
    Return neighbouring cells in left-hand priority order.
    """
    if heading == "up":
        return [
            (row, col - 1),   # left
            (row - 1, col),   # forward
            (row, col + 1),   # right
            (row + 1, col),   # back
        ]
    elif heading == "right":
        return [
            (row - 1, col),   # left
            (row, col + 1),   # forward
            (row + 1, col),   # right
            (row, col - 1),   # back
        ]
    elif heading == "down":
        return [
            (row, col + 1),   # left
            (row + 1, col),   # forward
            (row, col - 1),   # right
            (row - 1, col),   # back
        ]
    else:  # left
        return [
            (row + 1, col),   # left
            (row, col - 1),   # forward
            (row - 1, col),   # right
            (row, col + 1),   # back
        ]


def navigate(grid, start_cell, pub):
    # Sub to pose and colour for green x
    rospy.Subscriber('/turtle1/pose', Pose, _pose_cb)
    rospy.Subscriber('/turtle1/color_sensor', Color, _colour_cb)

    rospy.sleep(0.5)
    # Wait for services
    rospy.wait_for_service('/turtle1/set_pen')
    rospy.ServiceProxy('/turtle1/set_pen', SetPen)(255, 255, 255, 3, 1)

    rospy.loginfo("Starting autonomous left-hand maze navigation...")

    visited = set() # holds set of cells explored
    stack = [start_cell] # tracks path taken (FIFO)
    current = start_cell # cell turtle is currently in

    while not rospy.is_shutdown():
        row, col = current
        visited.add(current)

        rospy.loginfo("Current cell: %s", current)

        if _green_detected():
            rospy.loginfo("Green detected! Goal reached.")
            pub.publish(Twist())
            return

        heading = _get_heading() # get turtle angle and normalise
        candidates = _left_forward_right_back(row, col, heading) # get neighbours

        next_cell = None

        # Prefer unvisited cells in left-hand order
        for candidate in candidates:
            r, c = candidate
	    # If it is not a wall and not visited - prioritise
            if not is_wall(grid, r, c) and candidate not in visited:
                next_cell = candidate
                break

        # If no unvisited option exists, backtrack
	# Uses stack to backtrack - "pops" stacl
        if next_cell is None:
            if len(stack) > 1:
                stack.pop()
                next_cell = stack[-1]
                rospy.loginfo("Dead end. Backtracking to %s", next_cell)
            else:
                rospy.logwarn("No path found.")
                pub.publish(Twist())
                return
        else:
            stack.append(next_cell)

        rospy.loginfo("Heading: %s | Moving to: %s", heading, next_cell)

        goal_hit = _move_to_cell(pub, next_cell[0], next_cell[1])
        if goal_hit:
            pub.publish(Twist())
            return

        current = next_cell # do again with next cell
