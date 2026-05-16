# ROS-Turtlesim-Maze-Navigator
This project is made using ROS and the turtlesim package. The application randomly chooses one of the three randomly defined maps, and the turtle navigates its surroundings using a Left hand First algorithm along with the use of a stack for backtracking. A catkin workspace was used to organise the environment. 

## Tech Stacl
### Operating System
- Ubunut 20.04 via WSL
### Middleware
- Ros Noetic to handle node communication via topics
### Simulation
- Turtlesim package for a 2D environment
### Language
- Python 3
### Build System
- Catkin

## Getting Started
This project was run using Ubunutu 20.04 on WSL and ROS Noetic. It is only based on ROS, not ROS2.  

To install turtlesim with ROS Noetic, you can use the following commands:
-  sudo apt update
-  sudo apt install ros-noetic-turtlesim

When running this project, at least three terminals will need to be running.
### Terminal 1 - ROS Master
roscore
### Termianl 2 - Turtlesim 
rosrun turtlesim turtlesim_node
### Terminal 3 - 
python3 main.py  
** Ensure to naviagte to the source of the file in the Linux workspace before running this

Ensure to source the workspace either automatically or manually using 'source /opt/ros/noetic/setup.bash' in every new termianl. 
I used a catkin workspace and sourced after a 'catkin_make' using 'source devel/setup.bash'

## When Running
The third termianl will inform the user which maze was randomly chosen, inform when maze is drawn, inform the user of the start and end goal, print the current location and print the moving to location along with the turn required.  

<img width="800" height="200" alt="image" src="https://github.com/user-attachments/assets/ae07d02d-e92f-4c2f-b1d3-dd8a05dbb6d6" />  

If the turtle reaches a dead end, it will inform the user and show the appropriate coordinates. It is a## ble to backtrack using its most recent movements as it is saved onto a stack. Each coordinate of thw stack is moved to and popped until the turtle has more options again. Once green is detected, it will inform the user and stop.  

<img width="800" height="200" alt="image" src="https://github.com/user-attachments/assets/473e9968-be34-4d68-99a7-290bcf74a122" />  

## The Maze
The maze can be one of three mazes designed by the user with an array of 1s and 0s. To customise the maze/make your own, this can be done by editing the maze_defintions.py. The starting point and end goal can also be changed.  
The maze below is called Trapped Corridor, FalseTrap would be the hardest for the turtle due to the Left Hand bias.  

<img width="400" height="400" alt="image" src="https://github.com/user-attachments/assets/312b10e4-0bf9-4755-89c5-9d21c5dbc816" />

To edit the maze to your liking to test this poor turtle!, it can be done with the following commands: 
'nano filename.py' or 'code filename.py' in your relevent file path.

The code below shows a dictionary with a list inside holding the maze defintion. This list can be edited to customise the maze. This also is where the start and goal coordinates are edited, make sure the start and goal are within the constraints of the map

<img width="600" height="400" alt="image" src="https://github.com/user-attachments/assets/99c9a63b-a7a8-4edc-afdd-7d2ecb2b8eac" />


