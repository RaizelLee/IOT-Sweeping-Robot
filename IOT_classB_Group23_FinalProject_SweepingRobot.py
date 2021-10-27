#Libraries
import RPi.GPIO as GPIO
import time
import readchar

# GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BOARD)

# set GPIO Pins
GPIO_TRIGGER_f = 36
GPIO_ECHO_f = 37

GPIO_TRIGGER_r = 29
GPIO_ECHO_r = 31

GPIO_TRIGGER_l = 16
GPIO_ECHO_l = 18

Motor_R1_Pin = 22
Motor_R2_Pin = 23
Motor_L1_Pin = 11
Motor_L2_Pin = 13
t = 0.38
tr = 0.545
tl = 0.38
times = 0.9

stop_dist = 30.0
#global start_direction
#start_direction = 0 #0:notset yet; 1:left; 2:right

GPIO.setup(Motor_R1_Pin, GPIO.OUT)
GPIO.setup(Motor_R2_Pin, GPIO.OUT)
GPIO.setup(Motor_L1_Pin, GPIO.OUT)
GPIO.setup(Motor_L2_Pin, GPIO.OUT)

# set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER_f, GPIO.OUT)
GPIO.setup(GPIO_ECHO_f, GPIO.IN)
GPIO.setup(GPIO_TRIGGER_r, GPIO.OUT)
GPIO.setup(GPIO_ECHO_r, GPIO.IN)
GPIO.setup(GPIO_TRIGGER_l, GPIO.OUT)
GPIO.setup(GPIO_ECHO_l, GPIO.IN)

class Points_1D:
    def __init__(self, x, y):
        self.x = 0
        self.y = 0
        #bool cantGo = 0 #1:can't go through this point
        #bool alreadySweep = 0 #0: haven't sweep, 1: already sweep
#global maxX
maxX = 0 #x
#global minX
minX = 0 #x

#global maxY
maxY = 0 #y
#global minY
minY = 0 #y

final_width = 0
final_hight = 0

#global nowX
nowX = 0
#global nowY
nowY = 0

#global now_direction
now_direction = 1#1:up 2:right 3:left 4:down
#global start_now
start_now = True
at_start_record_size = False #0: at start and sweeping, 1:running

points_List = [Points_1D(0,0)]

def stop():
    GPIO.output(Motor_R1_Pin, False)
    GPIO.output(Motor_R2_Pin, False)
    GPIO.output(Motor_L1_Pin, False)
    GPIO.output(Motor_L2_Pin, False)


def forward():
    global times
    global maxX
    global minX
    global maxY
    global minY
    global nowX
    global nowY
    global start_now
    GPIO.output(Motor_R1_Pin, True)
    GPIO.output(Motor_R2_Pin, False)
    GPIO.output(Motor_L1_Pin, True)
    GPIO.output(Motor_L2_Pin, False)
    time.sleep(t/2)
    stop()
    GPIO.output(Motor_R1_Pin, True)
    GPIO.output(Motor_R2_Pin, False)
    GPIO.output(Motor_L1_Pin, False)
    GPIO.output(Motor_L2_Pin, True)
    time.sleep(times*t/50)
    stop()
    GPIO.output(Motor_R1_Pin, True)
    GPIO.output(Motor_R2_Pin, False)
    GPIO.output(Motor_L1_Pin, True)
    GPIO.output(Motor_L2_Pin, False)
    time.sleep(t/2)
    stop()
    if at_start_record_size == True:
        if (nowX != 0 or nowY != 0) or (start_now==True):
            if start_now == True:
                start_now = False
            if now_direction == 1:#up y++
                nowY = nowY + 1
                if maxY < nowY:
                    maxY = nowY
            elif now_direction == 2:#left x--
                nowX = nowX -1
                if minX > nowX:
                    minX = nowX
            elif now_direction == 3:#right x++
                nowX = nowX +1
                if maxX < nowX:
                    maxX = nowX
            elif now_direction == 4:#down y--
                nowY = nowY - 1
                if minY > nowY:
                    minY = nowY
            points_List.append(Points_1D(nowX, nowY))
            print(nowX, nowY)
        else:
            at_start_record_size == False
    if times <= 1.0:
       times = times + 0.02

def backward():
    GPIO.output(Motor_R1_Pin, False)
    GPIO.output(Motor_R2_Pin, True)
    GPIO.output(Motor_L1_Pin, False)
    GPIO.output(Motor_L2_Pin, True)
    time.sleep(t)
    stop()

def turnRight():
    global times
    times = 0.9
    stop()
    time.sleep(tr/2)
    global now_direction
    GPIO.output(Motor_R1_Pin, False)
    GPIO.output(Motor_R2_Pin, True)
    GPIO.output(Motor_L1_Pin, True)
    GPIO.output(Motor_L2_Pin, False)
    if now_direction == 1:
        now_direction = 2
    elif now_direction == 2:
        now_direction = 4
    elif now_direction == 3:
        now_direction = 1
    elif now_direction == 4:
        now_direction = 3
    time.sleep(tr)
    stop()


def turnLeft():
    global times
    times = 0.9
    stop()
    time.sleep(tl/2)
    global now_direction
    GPIO.output(Motor_R1_Pin, True)
    GPIO.output(Motor_R2_Pin, False)
    GPIO.output(Motor_L1_Pin, False)
    GPIO.output(Motor_L2_Pin, True)
    if now_direction == 1:
        now_direction = 3
    elif now_direction == 2:
        now_direction = 1
    elif now_direction == 3:
        now_direction = 4
    elif now_direction == 4:
        now_direction = 2
    time.sleep(tl)
    stop()

def action_truth_table(wall_f, wall_r, wall_l, start_direction):
    #global start_direction
    if not wall_f and not wall_r and not wall_l: #000 #can be any direction
        if at_start_record_size == True: #at running
            if start_direction == 2:
                forward()
                turnRight()
                forward()
                forward()
                #forward()
                
            elif start_direction == 1:
                forward()
                turnLeft()
                forward()
                forward()
                #forward()
        else: #at start
            while not wall_f and not wall_r and not wall_l:
                forward()
                wall_f = against_the_wall(GPIO_TRIGGER_f,GPIO_ECHO_f)
                wall_r = against_the_wall(GPIO_TRIGGER_r,GPIO_ECHO_r)
                wall_l = against_the_wall(GPIO_TRIGGER_l,GPIO_ECHO_l)
        print("001")

    elif not wall_f and not wall_r and wall_l: #001 #Left
        if start_direction == 2:
            turnRight()
        elif start_direction == 1:
            while not wall_f and not wall_r and wall_l :
                forward()
                wall_f = against_the_wall(GPIO_TRIGGER_f,GPIO_ECHO_f)
                wall_r = against_the_wall(GPIO_TRIGGER_r,GPIO_ECHO_r)
                wall_l = against_the_wall(GPIO_TRIGGER_l,GPIO_ECHO_l)
                print("002")
            

    elif not wall_f and wall_r and not wall_l: #010 #Right
        if at_start_record_size == True: #at running
            if start_direction == 1:            
                turnLeft()
            elif start_direction == 2:
                while not wall_f and wall_r and not wall_l:
                    forward()
                    wall_f = against_the_wall(GPIO_TRIGGER_f,GPIO_ECHO_f)
                    wall_r = against_the_wall(GPIO_TRIGGER_r,GPIO_ECHO_r)
                    wall_l = against_the_wall(GPIO_TRIGGER_l,GPIO_ECHO_l)
                    print("003")
        else: #at start
            #if start_direction == 2:
            while not wall_f and wall_r and not wall_l:
                    forward()
                    wall_f = against_the_wall(GPIO_TRIGGER_f,GPIO_ECHO_f)
                    wall_r = against_the_wall(GPIO_TRIGGER_r,GPIO_ECHO_r)
                    wall_l = against_the_wall(GPIO_TRIGGER_l,GPIO_ECHO_l)
                    print("004")
            #elif start_direction == 1:  << no this case
                #while not wall_f and not wall_r and wall_l :
                    #forward()

    elif not wall_f and wall_r and wall_l: #011 #Left
        while not wall_f and wall_r and wall_l:
            forward()
            wall_f = against_the_wall(GPIO_TRIGGER_f,GPIO_ECHO_f)
            wall_r = against_the_wall(GPIO_TRIGGER_r,GPIO_ECHO_r)
            wall_l = against_the_wall(GPIO_TRIGGER_l,GPIO_ECHO_l)
            print("005")
    
    elif wall_f and not wall_r and not wall_l: #100 #Left
        if at_start_record_size == True: #at running
            if start_direction == 2:
                turnRight()
            elif start_direction == 1:
                turnLeft()
        else: # at start
            # if start_direction == 2:  << no this case
                # turnLeft()
            #elif start_direction == 1:
            turnRight()
    
    elif wall_f and not wall_r and wall_l: #101 #Left
        turnRight()
    
    elif wall_f and wall_r and not wall_l: #110 #Left
        if at_start_record_size == True: #at running
            turnLeft()
        else:
            turnRight()
            turnRight()
    
    elif wall_f and wall_r and wall_l: #111
        while wall_f and wall_r and wall_l:
            backward()
            wall_f = against_the_wall(GPIO_TRIGGER_f,GPIO_ECHO_f)
            wall_r = against_the_wall(GPIO_TRIGGER_r,GPIO_ECHO_r)
            wall_l = against_the_wall(GPIO_TRIGGER_l,GPIO_ECHO_l)

def distance(GPIO_TRIGGER,GPIO_ECHO):
    # set Trigger to HIGH
    d_tmp = [0,0,0]
    for i in range(0,3,1):
        GPIO.output(GPIO_TRIGGER, True)

        # set Trigger after 0.01ms to LOW
        time.sleep(0.00001)
        GPIO.output(GPIO_TRIGGER, False) 
        StartTime = time.time()
        StopTime = time.time()
     
        # save StartTime
        while GPIO.input(GPIO_ECHO) == 0:
            StartTime = time.time()
     
        # save time of arrival
        while GPIO.input(GPIO_ECHO) == 1:
            StopTime = time.time()

        # time difference between start and arrival
        TimeElapsed = StopTime - StartTime
        # multiply with the sonic speed (34300 cm/s)
        # and divide by 2, because there and back
        d_tmp[i] = (TimeElapsed * 34300) / 2
    
    find = False
    for i in range(0,3,1):
        for j in range(0,3,1):
            if(i!=j):
                if d_tmp[i]-d_tmp[j] <= 20 or d_tmp[i]-d_tmp[j]>=-20:
                    distance = d_tmp[i]
                    find = True
                    break
    if find == False:
        return d[1]
    else:
        return distance

def against_the_wall(GPIO_TRIGGER,GPIO_ECHO):
# set Trigger to HIGH
    d_tmp = [0,0,0]
    for i in range(0,3,1):
        GPIO.output(GPIO_TRIGGER, True)

        # set Trigger after 0.01ms to LOW
        time.sleep(0.00001)
        GPIO.output(GPIO_TRIGGER, False) 
        StartTime = time.time()
        StopTime = time.time()
     
        # save StartTime
        while GPIO.input(GPIO_ECHO) == 0:
            StartTime = time.time()
     
        # save time of arrival
        while GPIO.input(GPIO_ECHO) == 1:
            StopTime = time.time()

        # time difference between start and arrival
        TimeElapsed = StopTime - StartTime
        # multiply with the sonic speed (34300 cm/s)
        # and divide by 2, because there and back
        d_tmp[i] = (TimeElapsed * 34300) / 2
    
    find = False
    for i in range(0,3,1):
        for j in range(0,3,1):
            if(i!=j):
                if d_tmp[i]-d_tmp[j] <= 20 or d_tmp[i]-d_tmp[j]>=-20:
                    distance = d_tmp[i]
                    find = True
                    break
    if find == False:
        distance = d[1]
    
    print(distance)
    result = distance <= stop_dist
    return result

def start():
    global start_direction
    global at_start_record_size
    wall_f = against_the_wall(GPIO_TRIGGER_f,GPIO_ECHO_f)
    wall_r = against_the_wall(GPIO_TRIGGER_r,GPIO_ECHO_r)
    wall_l = against_the_wall(GPIO_TRIGGER_l,GPIO_ECHO_l)
    dist_f = distance(GPIO_TRIGGER_f,GPIO_ECHO_f)
    dist_r = distance(GPIO_TRIGGER_r,GPIO_ECHO_r)
    dist_l = distance(GPIO_TRIGGER_l,GPIO_ECHO_l)
    print("Measured Distance = %.1f cm" % dist_f)
    print("Measured Distance = %.1f cm" % dist_r)
    print("Measured Distance = %.1f cm" % dist_l)
    # !r and !l and !f
    if not wall_f and not wall_r and not wall_l: # all directions are empty
        dict_f = distance(GPIO_TRIGGER_f,GPIO_ECHO_f)
        dict_r = distance(GPIO_TRIGGER_r,GPIO_ECHO_r)
        dict_l = distance(GPIO_TRIGGER_l,GPIO_ECHO_l)
        start_direction = 1 #set left
        if dict_f < dict_l and dict_f < dict_r: #if near front wall
            while True:
                dict_f = distance(GPIO_TRIGGER_f,GPIO_ECHO_f)
                if dict_f > stop_dist:
                    print("006")
                    forward()
                else:
                    stop()
                    turnRight()
                    break
        elif dict_l < dict_f and dict_l < dict_r: #near the left wall
            turnLeft()
            while True:
                dict_f = distance(GPIO_TRIGGER_f,GPIO_ECHO_f)
                if dict_f > stop_dist:
                    print("007")
                    forward()
                else:
                    stop()
                    print("")
                    turnLeft()
                    break
        elif dict_r < dict_l and dict_r < dict_f: #near the right wall
            turnRight()
            while True:
                dict_f = distance(GPIO_TRIGGER_f,GPIO_ECHO_f)
                if dict_f > stop_dist:
                    print("008")
                    forward()
                else:
                    stop()
                    turnRight()
                    break
    else:
        if wall_l:
            start_direction = 1
            #at_start_record_size = True
        elif wall_f:
            start_direction = 1
            action_truth_table(wall_f, wall_r, wall_l, start_direction)
        elif wall_r:
            start_direction = 2
            #at_start_record_size = True

        


if __name__ == '__main__':
    #global now_direction
    try:
        # dist_1 = distance()
        # time.sleep(0.0001)
        now_direction = 0
        start()
        #nowX = 0
        #nowY = 0
        now_direction = 1
        at_start_record_size = True
        while at_start_record_size == True:
            # dist_2 = distance()
            # if dist_1 - dist_2<=15.0 and dist_1 - dist_2 >=-15.0:
            # dist = dist_2
            # else:
            # dist = dist_1
            # dist_1 = dist_2
            #dist = distance()
            #print("Measured Distance = %.1f cm" % dist)
            #time.sleep(0.01)
            print("F:")
            wall_f = against_the_wall(GPIO_TRIGGER_f,GPIO_ECHO_f)
            print("R:")
            #time.sleep(0.01) 
            wall_r = against_the_wall(GPIO_TRIGGER_r,GPIO_ECHO_r)
            print("L:")
            #time.sleep(0.01)
            wall_l = against_the_wall(GPIO_TRIGGER_l,GPIO_ECHO_l)
            time.sleep(0.01)

            action_truth_table(wall_f, wall_r, wall_l, start_direction)

            """ch = readchar.readkey()
            if ch != 'q':
                wall_f = against_the_wall(GPIO_TRIGGER_f,GPIO_ECHO_f)
                wall_r = against_the_wall(GPIO_TRIGGER_r,GPIO_ECHO_r)
                wall_l = against_the_wall(GPIO_TRIGGER_l,GPIO_ECHO_l)
                action_truth_table(wall_f, wall_r, wall_l, start_direction)

            #elif ch == 's':
                #backward()

            #elif ch == 'd':
                #turnRight()

            #elif ch == 'a':
                #turnLeft()

            elif ch == 'q':
                print("\nQuit")
                GPIO.cleanup()"""
                
        print("Finish")
        GPIO.cleanup()
        exit()
        
        #Hey~ Zhou Hao, this block down below was missing, so I re-write it, please check:
        #from here
        final_height = maxY - minY
        final_width = maxX - minX
        minDistanceForConponentPoint = 0
        minIndex = 0
        points_array_2D[final_height][final_width]
        
        for i in range(len(points_List)):
            points_array_2D[points_List[i].y-minY][points_List[i].x-minX] = 1 #beause the x and y could be negative, so need to plus back to >=0
        
        for i in range(len(points_array_2D)): #the no.y column
            judge = False
            for j in range(len(points_array_2D[i])): #the no.y colum if no.x
                if points_array_2D[i][j] == 1:
                    judge = not judge
                elif judge == True:
                    oints_array_2D[i][j] = 0
                else:
                    oints_array_2D[i][j] = 4
        #to here
                    
        #and the code below is new
        
              #while at_start_record_size == False:
                    
        #this block below is to create components
        components_array = []
        new_component = []
        for i in range(len(points_array_2D)): #the no.y column
            #new_component.clear()
            if i%2 == 0:
                for j in range(len(points_array_2D[i])): #running from left to right
                    if points_array_2D[i][j] == 0:
                        tmp = Points_1D(j, i)
                        if len(new_component) != 0:
                            if new_component[len(new_component)-1].y == i and new_component[len(new_component)-1].x+1 == j:
                                new_component.append(tmp)
                            elif new_component[len(new_component)-1].y+1 == i and new_component[len(new_component)-1].x == j:
                                new_component.append(tmp)
                            else:
                                if len(components_array) == 0:
                                    components_array.append(new_component)
                                else:
                                    for k in range(len(components_array)):
                                        if components_array[k][len(components_array[k])-1].y + 1 ==  new_component[0].y \
                                        and components_array[k][len(components_array[k])-1].x ==  new_component[0].x:
                                            components_array[k].append(new_component)
                                            break
                                new_component.clear()
                        else:
                            new_component.append(tmp)
            else:
                for j in range(len(points_array_2D[i])-1, -1, -1): #running from right to left
                    if points_array_2D[i][j] == 0:
                        tmp = Points_1D(j,i)
                        if len(new_component) != 0:
                            if new_component[len(new_component)-1].y == i and new_component[len(new_component)-1].x-1 == j:
                                new_component.append(tmp)
                            elif new_component[len(new_component)-1].y+1 == i and new_component[len(new_component)-1].x == j:
                                new_component.append(tmp)
                            else:
                                if len(components_array) == 0:
                                    components_array.append(new_component)
                                else:
                                    for k in range(len(components_array)):
                                        if components_array[k][len(components_array[k])-1].y + 1 ==  new_component[0].y \
                                        and components_array[k][len(components_array[k])-1].x ==  new_component[0].x:
                                            components_array[k].append(new_component)
                                            break
                                new_component.clear()
                        else:
                            new_component.append(tmp)
        
        
        #this block below is for the car to sweep all the components
        
        #step 1: move to the first component's first point
                            
                 #step 1-1: find the first column's first point's x,y
        the_first_point_of_first_component = Points_1D(0,0)
        for i in range(len(points_array_2D[0])):
            if points_array_2D[0][i]==1:
                the_first_point_of_first_component.y = 0
                the_first_point_of_first_component.x = i
                break
                   
                #step 1-2: culculate witch way is more short to arrive << this step can is dispensable
        #way_negative = False
        the_first_point_index = 0
        for i in range(len(points_List)):
            if points_List[i].x - minX == the_first_point_of_first_component.x and points_List[i].y - minY == the_first_point_of_first_component.y:
                the_first_point_index = i
                break
                   
                #step 1-3: move to the first component's first point
        if the_first_point_index <= (len(points_List)/2): #move by the positive way
            
            for i in range(0, the_first_point_index):
                if now_direction == 1: #up
                    #if points_List[i].x == nowX and points_List[i].y > nowY:#up
                        #foward()
                    if points_List[i].x == nowX and points_List[i].y < nowY:#down
                        turnRight()
                        turnRight()
                        now_direction = 4
                    elif points_List[i].y == nowY and points_List[i].x > nowX:#right
                        turnRight()
                        now_direction = 2
                        #forward()
                    elif points_List[i].y == nowY and points_List[i].x < nowX:#left
                        turnLeft()
                        now_direction = 3
                        #forward()
                elif now_direction == 2: #right
                    if points_List[i].x == nowX and points_List[i].y > nowY:#up
                        turnLeft()
                        now_direction = 1
                        #forward()
                    elif points_List[i].x == nowX and points_List[i].y < nowY:#down
                        turnRight()
                        now_direction = 4
                        #forward()
                    #elif points_List[i].y == nowY and points_List[i].x > nowX:#right
                        #forward()
                    elif points_List[i].y == nowY and points_List[i].x < nowX:#left
                        turnRight()
                        turnRight()
                        now_direction = 3
                        #forward()
                elif now_direction == 3: #left
                    if points_List[i].x == nowX and points_List[i].y > nowY:#up
                        turnRight()
                        now_direction = 1
                        #forward()
                    elif points_List[i].x == nowX and points_List[i].y < nowY:#down
                        turnLeft()
                        now_direction = 4
                        #forward()
                    elif points_List[i].y == nowY and points_List[i].x > nowX:#right
                        turnRight()
                        turnRight()
                        now_direction = 2
                        #forward()
                    #elif points_List[i].y == nowY and points_List[i].x < nowX:#left
                        #forward()
                elif now_direction == 4: #down
                    if points_List[i].x == nowX and points_List[i].y > nowY:#up
                        turnRight()
                        turnRight()
                        now_direction = 1
                        #forward() 
                    #elif points_List[i].x == nowX and points_List[i].y < nowY:#down
                       
                    elif points_List[i].y == nowY and points_List[i].x > nowX:#right
                        turnLeft()
                        now_direction = 2
                    elif points_List[i].y == nowY and points_List[i].x < nowX:#left
                        turnRight()
                        now_direction = 3
                forward()
                
        else: #move by the negative way
            for i in range((len(points_List)-1), the_first_point_index-1, -1):
                if now_direction == 1: #up
                    #if points_List[i].x == nowX and points_List[i].y > nowY:#up
                        #foward()
                    if points_List[i].x == nowX and points_List[i].y < nowY:#down
                        turnRight()
                        turnRight()
                        now_direction = 4
                    elif points_List[i].y == nowY and points_List[i].x > nowX:#right
                        turnRight()
                        now_direction = 2
                        #forward()
                    elif points_List[i].y == nowY and points_List[i].x < nowX:#left
                        turnLeft()
                        now_direction = 3
                        #forward()
                elif now_direction == 2: #right
                    if points_List[i].x == nowX and points_List[i].y > nowY:#up
                        turnLeft()
                        now_direction = 1
                        #forward()
                    elif points_List[i].x == nowX and points_List[i].y < nowY:#down
                        turnRight()
                        now_direction = 4
                        #forward()
                    #elif points_List[i].y == nowY and points_List[i].x > nowX:#right
                        #forward()
                    elif points_List[i].y == nowY and points_List[i].x < nowX:#left
                        turnRight()
                        turnRight()
                        now_direction = 3
                        #forward()
                elif now_direction == 3: #left
                    if points_List[i].x == nowX and points_List[i].y > nowY:#up
                        turnRight()
                        now_direction = 1
                        #forward()
                    elif points_List[i].x == nowX and points_List[i].y < nowY:#down
                        turnLeft()
                        now_direction = 4
                        #forward()
                    elif points_List[i].y == nowY and points_List[i].x > nowX:#right
                        turnRight()
                        turnRight()
                        now_direction = 2
                        #forward()
                    #elif points_List[i].y == nowY and points_List[i].x < nowX:#left
                        #forward()
                elif now_direction == 4: #down
                    if points_List[i].x == nowX and points_List[i].y > nowY:#up
                        turnRight()
                        turnRight()
                        now_direction = 1
                        #forward() 
                    #elif points_List[i].x == nowX and points_List[i].y < nowY:#down
                       
                    elif points_List[i].y == nowY and points_List[i].x > nowX:#right
                        turnLeft()
                        now_direction = 2
                    elif points_List[i].y == nowY and points_List[i].x < nowX:#left
                        turnRight()
                        now_direction = 3
                forward()

        #step 2: sweep every component #in the case of there has no obstacle
        #for i in range(len(components_array)):
            #if pow(pow((components_array[i][0].x - nowX - minX),2)+pow((compoments_array[i][0].y - newY -miny),2),1/2) < minDistanceForConponentPoint:            
                #minIndex = i
                #minDistanceForConponentPoint = pow(pow((components_array[i][0].x - nowX - minX),2)+pow((compoments_array[i][0].y - newY -miny),2),1/2)
                
    # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()

