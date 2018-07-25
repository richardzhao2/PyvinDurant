import numpy
import cv2
import pywinauto
import PIL
import time
import math

basket_color= ([90, 191, 210], [106, 225, 247])
ball_color = ([37, 45, 71], [98, 106, 135])

ball_coords = (959, 860)

vel_fac = 6.70
arc_fac = 0.4

last_pos = (0, 0)

middle_range = 100

sample_interval = 0.1

last_velocity = 0

last_time = 0

shot_interval = 2.75
shot_timer = shot_interval

def id_basket(image):
    lower_color = numpy.array(basket_color[0], dtype='uint8')
    upper_color = numpy.array(basket_color[1], dtype='uint8')
    mask = cv2.inRange(image, lower_color, upper_color)
    masked = cv2.bitwise_and(image, image, mask = mask)
    (_, binary) = cv2.threshold(cv2.cvtColor(masked, cv2.COLOR_BGR2GRAY), 127, 255, cv2.THRESH_BINARY)
    _, contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    largest_contour = max(contours, key=lambda c: cv2.contourArea(c))
    if largest_contour is None:
        raise Exception
    M = cv2.moments(largest_contour)
    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])
    return cX, cY

def adjust_x(x):
    diff = ball_coords[0] - x
    return x + int(arc_fac * diff)

def get_basket_loc():
    pil_grab = PIL.ImageGrab.grab()
    cv_grab = cv2.cvtColor(numpy.array(pil_grab), cv2.COLOR_RGB2BGR)
    basket_x, basket_y = id_basket(cv_grab)
    return basket_x, basket_y

def fire(position):
    pywinauto.mouse.press(coords=ball_coords)
    adjusted = (adjust_x(position[0]), position[1])
    pywinauto.mouse.release(coords=adjusted)

def is_constant_velocity(last_velocity, velocity):
    dv = (velocity[0] - last_velocity[0], velocity[1] - last_velocity[1])
    dv_mag = math.sqrt(math.pow(dv[0], 2) + math.pow(dv[0], 2))
    print(dv_mag)
    return dv_mag < max_dv

def get_velocity_mag(velocity):
    return math.sqrt(math.pow(velocity[0], 2) + math.pow(velocity[0], 2))

def is_in_middle(position):
    return abs(position[0] - ball_coords[0]) < middle_range

firefox = pywinauto.Application()
firefox.connect(path=r'C:\Program Files (x86)\Mozilla Firefox\firefox.exe')

print('Starting in five seconds.')
time.sleep(5)

last_position = get_basket_loc()
last_time = time.time()

while True:
    cur_time = time.time()
    dt = cur_time - last_time
    #fix first frame issues
    if dt == 0:
        continue
    try:
        position = get_basket_loc()
    except Exception as e:
        print('Basket not found. Exiting...')
        break
    velocity = (position[0] - last_position[0], position[1] - last_position[1])
    velocity = (velocity[0] / dt, velocity[1] / dt)
    if shot_timer < 0:
        if (get_velocity_mag(velocity) == 0 and get_velocity_mag(last_velocity) == 0) or is_in_middle(position):
            fire((position[0] + int(vel_fac * velocity[0] * dt), position[1] + int(vel_fac * velocity[1] * dt)))
            shot_timer = shot_interval
    shot_timer -= dt
    last_position = position
    last_velocity = velocity
    last_time = cur_time
    time.sleep(sample_interval)