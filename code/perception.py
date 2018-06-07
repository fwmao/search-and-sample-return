import numpy as np
import cv2

# Identify pixels above the threshold
# Threshold of RGB > 160 does a nice job of identifying ground pixels only
def color_thresh(img, rgb_thresh_low=(160, 160, 160), rgb_thresh_above=(255, 255, 255)):
    # Create an array of zeros same xy size as img, but single channel
    color_select = np.zeros_like(img[:,:,0])
    low_thresh = (img[:,:,0] > rgb_thresh_low[0]) \
                & (img[:,:,1] > rgb_thresh_low[1]) \
                & (img[:,:,2] > rgb_thresh_low[2])

    above_thresh = (img[:,:,0] < rgb_thresh_above[0]) \
                & (img[:,:,1] < rgb_thresh_above[1]) \
                & (img[:,:,2] < rgb_thresh_above[2])

    select = above_thresh & low_thresh

    # Index the array of zeros with the boolean array and set to 1
    color_select[select] = 1
    # Return the binary image
    return color_select

# Define a function to convert from image coords to rover coords
def rover_coords(binary_img):
    # Identify nonzero pixels
    ypos, xpos = binary_img.nonzero()
    # Calculate pixel positions with reference to the rover position being at the 
    # center bottom of the image.  
    x_pixel = -(ypos - binary_img.shape[0]).astype(np.float)
    y_pixel = -(xpos - binary_img.shape[1]/2 ).astype(np.float)
    return x_pixel, y_pixel


# Define a function to convert to radial coords in rover space
def to_polar_coords(x_pixel, y_pixel):
    # Convert (x_pixel, y_pixel) to (distance, angle) 
    # in polar coordinates in rover space
    # Calculate distance to each pixel
    dist = np.sqrt(x_pixel**2 + y_pixel**2)
    # Calculate angle away from vertical for each pixel
    angles = np.arctan2(y_pixel, x_pixel)
    return dist, angles

# Define a function to map rover space pixels to world space
def rotate_pix(xpix, ypix, yaw):
    # Convert yaw to radians
    yaw_rad = yaw * np.pi / 180
    xpix_rotated = (xpix * np.cos(yaw_rad)) - (ypix * np.sin(yaw_rad))
                            
    ypix_rotated = (xpix * np.sin(yaw_rad)) + (ypix * np.cos(yaw_rad))
    # Return the result  
    return xpix_rotated, ypix_rotated

def translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale): 
    # Apply a scaling and a translation
    xpix_translated = (xpix_rot / scale) + xpos
    ypix_translated = (ypix_rot / scale) + ypos
    # Return the result  
    return xpix_translated, ypix_translated


# Define a function to apply rotation and translation (and clipping)
# Once you define the two functions above this function should work
def pix_to_world(xpix, ypix, xpos, ypos, yaw, world_size, scale):
    # Apply rotation
    xpix_rot, ypix_rot = rotate_pix(xpix, ypix, yaw)
    # Apply translation
    xpix_tran, ypix_tran = translate_pix(xpix_rot, ypix_rot, xpos, ypos, scale)
    # Perform rotation, translation and clipping all at once
    x_pix_world = np.clip(np.int_(xpix_tran), 0, world_size - 1)
    y_pix_world = np.clip(np.int_(ypix_tran), 0, world_size - 1)
    # Return the result
    return x_pix_world, y_pix_world

# Define a function to perform a perspective transform
def perspect_transform(img, src, dst):
           
    M = cv2.getPerspectiveTransform(src, dst)
    warped = cv2.warpPerspective(img, M, (img.shape[1], img.shape[0]))# keep same size as input image
    
    return warped


# Apply the above functions in succession and update the Rover state accordingly
def perception_step(Rover):
    # Perform perception steps to update Rover()
    # TODO: 
    # NOTE: camera image is coming to you in Rover.img
    # 1) Define source and destination points for perspective transform
    dst_size = 5
    bottom_offset = 6
    source = np.float32([[23, 144], [284, 128], [190, 96], [114, 97]])
    image = Rover.img
    destination = np.float32([[image.shape[1] / 2 - dst_size, image.shape[0] - bottom_offset],
                              [image.shape[1] / 2 + dst_size, image.shape[0] - bottom_offset],
                              [image.shape[1] / 2 + dst_size, image.shape[0] - 2 * dst_size - bottom_offset],
                              [image.shape[1] / 2 - dst_size, image.shape[0] - 2 * dst_size - bottom_offset],
                              ])
    # 2) Apply perspective transform
    warped = perspect_transform(image,source,destination)
    # 3) Apply color threshold to identify navigable terrain/obstacles/rock samples
    #obstacle = color_thresh(warped, rgb_thresh_low=(0, 0, 0), rgb_thresh_above=(70, 70, 70))
    rock_sample = color_thresh(warped, rgb_thresh_low=(150, 100, 0), rgb_thresh_above=(220, 220, 50))
    nav_terrain = color_thresh(warped)

    # 4) Update Rover.vision_image (this will be displayed on left side of screen)
        # Example: Rover.vision_image[:,:,0] = obstacle color-thresholded binary image
        #          Rover.vision_image[:,:,1] = rock_sample color-thresholded binary image
        #          Rover.vision_image[:,:,2] = navigable terrain color-thresholded binary image
    Rover.vision_image[:, :, 0] = (nav_terrain - 1) * (-1) * 255
    Rover.vision_image[:, :, 1] = rock_sample * 255
    Rover.vision_image[:, :, 2] = nav_terrain * 255

    # 5) Convert map image pixel values to rover-centric coords
    xpix,ypix = rover_coords(nav_terrain)
    xpix_sample, ypix_sample = rover_coords(rock_sample)
    # 6) Convert rover-centric pixel values to world coordinates
    scale = 10
    rover_xpos = Rover.pos[0]
    rover_ypos = Rover.pos[1]
    rover_yaw = Rover.yaw
    x_world, y_world = pix_to_world(xpix, ypix, rover_xpos,
                                    rover_ypos, rover_yaw,
                                    Rover.worldmap.shape[0], scale)
    x_w_sample, y_w_sample = pix_to_world(xpix_sample, ypix_sample, rover_xpos,
                                          rover_ypos, rover_yaw,
                                          Rover.worldmap.shape[0], scale)
    # 7) Update Rover worldmap (to be displayed on right side of screen)
        # Example: Rover.worldmap[obstacle_y_world, obstacle_x_world, 0] += 1
        #          Rover.worldmap[rock_y_world, rock_x_world, 1] += 1
        #          Rover.worldmap[navigable_y_world, navigable_x_world, 2] += 1
    Rover.worldmap[y_w_sample, x_w_sample, 1] += 1
    if Rover.roll < 3 or Rover.roll > 359:
        Rover.worldmap[y_world, x_world, 2] += 1

    # 8) Convert rover-centric pixel positions to polar coordinates
    distances, angles = to_polar_coords(xpix, ypix)
    sample_dis, sample_angles = to_polar_coords(xpix_sample, ypix_sample)

    # Update Rover pixel distances and angles
        # Rover.nav_dists = rover_centric_pixel_distances
        # Rover.nav_angles = rover_centric_angles
    Rover.nav_dists = distances
    Rover.nav_angles = angles
    Rover.nav_angles_rock = sample_angles

    if Rover.samples_collected < 5:
        # use near area to judge navigate angel
        near_judge_area = ypix[np.where(xpix == 35)]

        if len(near_judge_area) >= 5:
            y_right = np.min(near_judge_area)  # drive along right side of road
            y_left = np.max(near_judge_area)
            y_mean = np.clip(y_right + 10, y_right, y_left)
            dist_right, angles_right = to_polar_coords(35, y_mean)
            Rover.nav_angles_right = angles_right
        else:
            Rover.nav_angles_right = None
    else:    # try to find last rock by walking middle of road
        Rover.nav_angles_right = None

    return Rover