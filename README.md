[//]: # (Image References)
[image_0]: ./misc/rover_image.jpg
[![Udacity - Robotics NanoDegree Program](https://s3-us-west-1.amazonaws.com/udacity-robotics/Extra+Images/RoboND_flag.png)](https://www.udacity.com/robotics)
# Search and Sample Return Project


![alt text][image_0] 

This project is modeled after the [NASA sample return challenge](https://www.nasa.gov/directorates/spacetech/centennial_challenges/sample_return_robot/index.html) and it will give you first hand experience with the three essential elements of robotics, which are perception, decision making and actuation.  You will carry out this project in a simulator environment built with the Unity game engine.  

## The Simulator
The first step is to download the simulator build that's appropriate for your operating system.  Here are the links for [Linux](https://s3-us-west-1.amazonaws.com/udacity-robotics/Rover+Unity+Sims/Linux_Roversim.zip), [Mac](	https://s3-us-west-1.amazonaws.com/udacity-robotics/Rover+Unity+Sims/Mac_Roversim.zip), or [Windows](https://s3-us-west-1.amazonaws.com/udacity-robotics/Rover+Unity+Sims/Windows_Roversim.zip).  

You can test out the simulator by opening it up and choosing "Training Mode".  Use the mouse or keyboard to navigate around the environment and see how it looks.

## Dependencies
You'll need Python 3 and Jupyter Notebooks installed to do this project.  The best way to get setup with these if you are not already is to use Anaconda following along with the [RoboND-Python-Starterkit](https://github.com/ryan-keenan/RoboND-Python-Starterkit). 


Here is a great link for learning more about [Anaconda and Jupyter Notebooks](https://classroom.udacity.com/courses/ud1111)

## Recording Data
I've saved some test data for you in the folder called `test_dataset`.  In that folder you'll find a csv file with the output data for steering, throttle position etc. and the pathnames to the images recorded in each run.  I've also saved a few images in the folder called `calibration_images` to do some of the initial calibration steps with.  

The first step of this project is to record data on your own.  To do this, you should first create a new folder to store the image data in.  Then launch the simulator and choose "Training Mode" then hit "r".  Navigate to the directory you want to store data in, select it, and then drive around collecting data.  Hit "r" again to stop data collection.

## Data Analysis
Included in the IPython notebook called `Rover_Project_Test_Notebook.ipynb` are the functions from the lesson for performing the various steps of this project.  The notebook should function as is without need for modification at this point.  To see what's in the notebook and execute the code there, start the jupyter notebook server at the command line like this:

```sh
jupyter notebook
```

This command will bring up a browser window in the current directory where you can navigate to wherever `Rover_Project_Test_Notebook.ipynb` is and select it.  Run the cells in the notebook from top to bottom to see the various data analysis steps.  

The last two cells in the notebook are for running the analysis on a folder of test images to create a map of the simulator environment and write the output to a video.  These cells should run as-is and save a video called `test_mapping.mp4` to the `output` folder.  This should give you an idea of how to go about modifying the `process_image()` function to perform mapping on your data.  

## Navigating Autonomously
### excution environment: 
resolution is 800*600, graphics quality is good 
### perception_step
First I record pictures to locate 4 grid corner and threshold of sample rock
![image](https://github.com/fwmao/search-and-sample-return/tree/master/calibration_images/1.jpg)
![image](https://github.com/fwmao/search-and-sample-return/blob/master/calibration_images/2.jpg)

then I modified color_thresh, add a upper threashold parameter,  
use rock_sample = color_thresh(warped, rgb_thresh=(150, 100, 0), rgb_thresh_max=(220, 220, 50)), i get the rock_sample image, and obstacle is logical not (nav_image and rock_sample),and i judge roll and pitch degree to increase fidelity.  
    if (Rover.roll < 0.5 or Rover.roll > 359.5) and (Rover.pitch < 0.5 or Rover.pitch > 359.5):  
        Rover.worldmap[y_world, x_world, 2] += 1  
before collecting last sample rock, i used a strategy, drive along right side of road,  use nav_right. when collecting 5th sample rock, i record the time, if spending over 1000S to get the last sample, i will use nav_angle.
and i add a sample_angles to drive to sample rock, when find a sample in camera.
### decision_step
if nav_right exist, rover will use nav_right, if not, rover will use nav_angles instead, but add a random angle limited (-15,15) to avoid drive into repeat route.  
to avoid being stuck, i add a juage condition and two mode to get off from stuck.  
if mode is "forward" and steer is 0.2 annd vel < 0.2, rover is being thought as stuck, then will turn into "back" mode, pull back for 2S, then turn into "turn" mode, rover will turn >10 degree than befor yaw angle. under "back" and "turn" mode, nav_right and nav_angle are ignored, until rover vel > 0.2, then will turn back to "forward" mode.

### more need to do
1 sometimes sample rock is at the right behind a obstacle, but rover is stuck by the obstacle, the decision tell rover to turn left to avoid stuck, and sample_angle tell rover to steer to sample rock, rover will turn right and left repeatly.  
2 return to start:  a challenge that I did not implement.







