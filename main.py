#!/usr/bin/env python3

"""
What happens:
  1. A maze is chosen at random from the three predefined layouts
  2. The maze is drawn in turtlesim (walls appear, turtle placed at start)
  3. The turtle explores the maze using local sensing and backtracking
  4. It continues until it reaches the goal
"""

import rospy
from geometry_msgs.msg import Twist
from maze_definitions import get_random_maze
from maze_drawer import draw_maze
from navigator import navigate
from turtlesim.srv import SetPen

def pen_up():
    rospy.wait_for_service('/turtle1/set_pen')
    svc = rospy.ServiceProxy('/turtle1/set_pen', SetPen)
    svc(255, 255, 255, 3, 1)

def main():
    # Register script as node, true gives random no. to avoid conflicts
    rospy.init_node('maze_navigator', anonymous=True)

    # Publisher used by both the drawer and the navigator
    pub = rospy.Publisher('/turtle1/cmd_vel', Twist, queue_size=10)

    # Give turtlesim a moment to connect before we start calling services
    rospy.sleep(1.0)

    # Pick a maze
    maze = get_random_maze()
    rospy.loginfo("Selected maze: '%s'", maze['name'])

    # Draw the maze and place the turtle at the start
    draw_maze(maze, pub)
    pen_up()

    # Small pause so the user can see the completed maze before the turtle moves
    rospy.loginfo("Maze ready. Starting navigation in 3 seconds...")
    rospy.sleep(3.0)

    # Navigate from start to goal
    navigate(
        grid       = maze['grid'],
        start_cell = maze['start'],
        # goal_cell  = maze['goal'],
        pub        = pub,
    )

# Entry point in try except to when user crtl + C will exit smoothly
if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass
