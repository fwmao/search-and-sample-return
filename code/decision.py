import numpy as np
import random

# This is where you can build a decision tree for determining throttle, brake and steer 
# commands based on the output of the perception_step() function
def decision_step(Rover):

    # Implement conditionals to decide what to do given perception data
    # Here you're all set up with some basic functionality but you'll need to
    # improve on this decision tree to do a good job of navigating autonomously!

    # Example:
    # Check if we have vision data to make decisions with
    if Rover.stuck_time is not None:
        print('stuck time %f' % Rover.stuck_time)

    if Rover.nav_angles is not None:
        print(Rover.mode)
        # Check for Rover.mode status
        if Rover.mode == 'forward':
            # Check the extent of navigable terrain
            if len(Rover.nav_angles) >= Rover.stop_forward:  
                # If mode is forward, navigable terrain looks good 
                # and velocity is below max, then throttle 
                if Rover.vel < Rover.max_vel:
                    # Set throttle value to throttle setting
                    Rover.throttle = Rover.throttle_set
                else:  # Else coast
                    Rover.throttle = 0
                Rover.brake = 0
                if Rover.nav_angles_right:
                    Rover.steer = np.clip(Rover.nav_angles_right* 180/np.pi + random.randint(-5, 5), -15, 15)
                else:
                    # Set steering to average angle clipped to the range +/- 15
                    Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi) + random.randint(-15,15), -15, 15)
            # If there's a lack of navigable terrain pixels then go to 'stop' mode
            elif len(Rover.nav_angles) < Rover.stop_forward:
                    # Set mode to "stop" and hit the brakes!
                    Rover.throttle = 0
                    # Set brake to stored brake value
                    Rover.brake = Rover.brake_set
                    Rover.steer = 0
                    Rover.mode = 'stop'

            # if rover is stuck, try to adjust steer to get out
            if Rover.throttle == Rover.throttle_set and Rover.vel <= 0.1 and Rover.stuck_time is None:
                Rover.stuck_time = Rover.total_time

            if Rover.throttle == Rover.throttle_set and Rover.vel <= 0.1 and Rover.stuck_time is not None:
                if Rover.total_time - Rover.stuck_time >= 6:
                    Rover.stuck_time = None
                    Rover.mode = 'back'

        # If we're already in "stop" mode then make different decisions
        elif Rover.mode == 'stop':
            Rover.stuck_time = None
            # If we're in stop mode but still moving keep braking
            if Rover.vel > 0.2:
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
                Rover.steer = 0
            # If we're not moving (vel < 0.2) then do something else
            elif Rover.vel <= 0.2:
                # Now we're stopped and we have vision data to see if there's a path forward
                if len(Rover.nav_angles) < Rover.go_forward:
                    Rover.throttle = 0
                    # Release the brake to allow turning
                    Rover.brake = 0
                    # Turn range is +/- 15 degrees, when stopped the next line will induce 4-wheel turning
                    #Rover.steer = -15 if np.clip(np.mean(Rover.nav_angles * 180 / np.pi), -15, 15) < 0 else 15
                    Rover.steer = 5
                    # If we're stopped but see sufficient navigable terrain in front then go!
                if len(Rover.nav_angles) >= Rover.go_forward:
                    # Set throttle back to stored value
                    Rover.throttle = Rover.throttle_set
                    # Release the brake
                    Rover.brake = 0
                    # Set steer to mean angle
                    Rover.steer = np.clip(np.mean(Rover.nav_angles * 180/np.pi), -15, 15)
                    Rover.mode = 'forward'

        elif Rover.mode == 'back':
            Rover.steer = 0
            Rover.brake = 0
            Rover.throttle = - Rover.throttle_set
            if Rover.back_time is None:
                Rover.back_time = Rover.total_time
            else:
                if Rover.total_time - Rover.back_time > 2:
                    Rover.throttle = 0
                    Rover.brake = Rover.brake_set
                    if np.abs(Rover.vel) < 0.1:
                        Rover.back_time = None
                        Rover.mode = 'turn'

        elif Rover.mode == 'turn':
            Rover.steer = 0
            Rover.brake = 0
            Rover.throttle = 0
            if Rover.last_yaw is None:
                Rover.last_yaw = Rover.total_time
                Rover.steer = 10
            else:
                Rover.steer = np.clip(np.abs(Rover.yaw - Rover.last_yaw) + 10, 0, 360)
                if np.abs(Rover.yaw - Rover.last_yaw) >= 10:
                    Rover.last_yaw = Rover.yaw
                    Rover.mode = 'forward'
                    Rover.throttle = Rover.throttle_set


    # Just to make the rover do something 
    # even if no modifications have been made to the code
    else:
        Rover.throttle = Rover.throttle_set
        Rover.steer = 0
        Rover.brake = Rover.brake_set

    if Rover.nav_angles_rock is not None:
        if len(Rover.nav_angles_rock) >= 1:
            Rover.steer = np.clip(np.mean(Rover.nav_angles_rock * 180 / np.pi), -15, 15)
            if Rover.near_sample and not Rover.picking_up:
                Rover.throttle = 0
                Rover.brake = Rover.brake_set
            else:
                Rover.throttle = Rover.throttle_set
                Rover.brake = 0

    # If in a state where want to pickup a rock send pickup command
    if Rover.near_sample and Rover.vel == 0 and not Rover.picking_up:
        Rover.send_pickup = True

    return Rover

