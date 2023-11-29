import cv2
import numpy as np
import itertools
import math

def evaluate(img_target, img_canvas):
    diff_norm = img_target / 255.0 - img_canvas / 255.0
    return np.sqrt(np.mean(diff_norm ** 2))


# def evaluate(img_target, img_canvas):
#     diff_norm = img_target / 255.0 - img_canvas / 255.0
#     return np.sqrt(np.mean(diff_norm ** 2))    

def draw_thick_thin_line(img_canvas, start, end, spacing, left_thickness, right_thickness):
    start_array = np.asarray(start)
    end_array = np.asarray(end)

    vector = end_array - start_array

    vector_normalized = vector / np.sqrt(np.sum(vector**2)) 

    vector_normalized_orthogonal = np.asarray([vector_normalized[1], -vector_normalized[0]]) #?
    
    start_right = start_array + vector_normalized_orthogonal * spacing / 2
    end_right = end_array + vector_normalized_orthogonal * spacing / 2

    if np.sum(np.isnan(start_right)) == 0 and np.sum(np.isnan(end_right)) == 0:
        cv2.line(img_canvas, (round(start_right[0]), round(start_right[1])), (round(end_right[0]), round(end_right[1])), (0, 0, 0), right_thickness)
    
    
    start_left = start_array - vector_normalized_orthogonal * spacing / 2
    end_left = end_array - vector_normalized_orthogonal * spacing / 2
 
    if np.sum(np.isnan(start_left)) == 0 and np.sum(np.isnan(end_left)) == 0:
        cv2.line(img_canvas, (round(start_left[0]), round(start_left[1])), (round(end_left[0]), round(end_left[1])), (0, 0, 0), left_thickness)
    
    
def draw_single_line(img_canvas, start, end, thickness):
    '''
    draw a solid line based on start, , thickness

    Parameters
    ----------
    img_canvas : TYPE
        DESCRIPTION.
    start : TYPE
        DESCRIPTION.
    end : TYPE
        DESCRIPTION.
    thickness : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    '''
    start_array = np.asarray(start)
    end_array = np.asarray(end)

    if np.sum(np.isnan(start_array)) == 0 and np.sum(np.isnan(end_array)) == 0:
        cv2.line(img_canvas, (round(start_array[0]), round(start_array[1])), (round(end_array[0]), round(end_array[1])), (0, 0, 0), thickness)


def draw_dashed_line_old(img_canvas, start, end, thickness, gap):
    '''
    zanshibuxuyaole
    draw a single dashed line based on start, end, thickness and gap (old version)

    Parameters
    ----------
    img_canvas : TYPE
        DESCRIPTION.
    start : TYPE
        DESCRIPTION.
    end : TYPE
        DESCRIPTION.
    thickness : TYPE
        DESCRIPTION.
    gap : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    '''
    start_array = np.asarray(start)
    end_array = np.asarray(end)
    dist =((start_array[0]-end_array[0])**2+(start_array[1]-end_array[1])**2)**.5
    
    pts= []
    for i in  np.arange(0,dist,gap):###(0,1gap,2gap,3gap,...,dist) (less than dist)
        r=i/dist
        x=int((start_array[0]*(1-r)+end_array[0]*r)+.5)
        y=int((start_array[1]*(1-r)+end_array[1]*r)+.5)
        p = (x,y)
        pts.append(p)
        
    s=pts[0]
    e=pts[0]
    j=0
    for p in pts:
        s=e
        e=p
        if j%2==1:
            cv2.line(img_canvas,s,e,(0, 0, 0),thickness)
        j+=1

def point_coords_dashed_line(start, end, length):
    x_s = start[0]
    y_s = start[1]
    x_e = end[0]
    y_e = end[1]
    dist =((start[0]-end[0])**2+(start[1]-end[1])**2)**.5
    
    delta_x = 0
    delta_y = 0
    point_x = 0
    point_y = 0
    
    if (x_s<x_e)&(y_s<y_e):
        delta_x = int(abs((x_e - x_s))*length/dist)
        delta_y = int(abs((y_e - y_s))*length/dist)
        point_x = x_s + delta_x
        point_y = y_s + delta_y
    elif (x_s<x_e)&(y_s>y_e):
        delta_x = int(abs((x_e - x_s))*length/dist)
        delta_y = int(abs((y_s - y_e))*length/dist)
        point_x = x_s + delta_x
        point_y = y_s - delta_y
    elif (x_s>x_e)&(y_s>y_e):
        delta_x = int(abs((x_s - x_e))*length/dist)
        delta_y = int(abs((y_s - y_e))*length/dist)
        point_x = x_s - delta_x
        point_y = y_s - delta_y
    elif (x_s>x_e)&(y_s<y_e):
        delta_x = int(abs((x_s - x_e))*length/dist)
        delta_y = int(abs((y_e - y_s))*length/dist)
        point_x = x_s - delta_x
        point_y = y_s + delta_y
    elif (x_s==x_e)&(y_s<y_e):
        delta_y = int(length)
        point_x = x_s 
        point_y = y_s + delta_y
    elif (x_s==x_e)&(y_s>y_e):
        delta_y = int(length)
        point_x = x_s 
        point_y = y_s - delta_y
    elif (x_s>x_e)&(y_s==y_e):
        delta_x = int(length)
        point_x = x_s - delta_x
        point_y = y_s 
    elif (x_s<x_e)&(y_s==y_e):
        delta_x = int(length)
        point_x = x_s + delta_x
        point_y = y_s 
    
    return point_x, point_y
        
        

    

def draw_dashed_line(img_canvas, start, end, thickness,length, gap):
    '''
    draw a single dashed line based on start, end, thickness and gap

    Parameters
    ----------
    img_canvas : TYPE
        DESCRIPTION.
    start : TYPE
        DESCRIPTION.
    end : TYPE
        DESCRIPTION.
    thickness : TYPE
        DESCRIPTION.
    gap : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    '''
    start_array = np.asarray(start)
    end_array = np.asarray(end)
    dist =((start_array[0]-end_array[0])**2+(start_array[1]-end_array[1])**2)**.5
    
    pts= []
    Num =int(dist/(length+gap))*2
    for i in  range(0,Num+1):
        k = int(i/2)
        if i%2==1:
            point_x, point_y = point_coords_dashed_line(start, end, length*(i-k)+gap*k)
            p = (point_x,point_y)
            pts.append(p)
        else:
            point_x, point_y = point_coords_dashed_line(start, end, (length+gap)*k)
            p = (point_x,point_y)
            pts.append(p)
        
    s=pts[0]
    e=pts[0]
    j=0
    for p in pts:
        s=e
        e=p
        if j%2==1:
            cv2.line(img_canvas,s,e,(0, 0, 0),thickness)
        j+=1
    # draw the remaining part
    draw_single_line(img_canvas, pts[-1], end, thickness)

def draw_dashed_single_line(img_canvas, start, end, spacing, left_thickness, right_thickness, length, gap):
    '''
    zanshibuxuyao
    draw two-line symbol, The left is a dashed line, the right is a  single line

    Parameters
    ----------
    img_canvas : TYPE
        DESCRIPTION.
    start : TYPE
        DESCRIPTION.
    end : TYPE
        DESCRIPTION.
    spacing : TYPE
        DESCRIPTION.
    left_thickness : TYPE
        DESCRIPTION.
    right_thickness : TYPE
        DESCRIPTION.
    gap : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    '''
    start_array = np.asarray(start)
    end_array = np.asarray(end)

    vector = end_array - start_array

    vector_normalized = vector / np.sqrt(np.sum(vector**2)) #why is it requeared?

    vector_normalized_orthogonal = np.asarray([vector_normalized[1], -vector_normalized[0]]) #?
    
    start_right = start_array + vector_normalized_orthogonal * spacing / 2
    end_right = end_array + vector_normalized_orthogonal * spacing / 2

    if np.sum(np.isnan(start_right)) == 0 and np.sum(np.isnan(end_right)) == 0:
        # cv2.line(img_canvas, (round(start_right[0]), round(start_right[1])), (round(end_right[0]), round(end_right[1])), (0, 0, 0), right_thickness)
        draw_dashed_line(img_canvas, (round(start_right[0]), round(start_right[1])), (round(end_right[0]), round(end_right[1])), right_thickness, length, gap)

    
    
    start_left = start_array - vector_normalized_orthogonal * spacing / 2
    end_left = end_array - vector_normalized_orthogonal * spacing / 2
 
    if np.sum(np.isnan(start_left)) == 0 and np.sum(np.isnan(end_left)) == 0:
        cv2.line(img_canvas, (round(start_left[0]), round(start_left[1])), (round(end_left[0]), round(end_left[1])), (0, 0, 0), left_thickness)
        # draw_dashed_line(img_canvas, (round(start_left[0]), round(start_left[1])), (round(end_left[0]), round(end_left[1])), left_thickness, gap)
    
    
def draw_single_dashed_line(img_canvas, start, end, spacing, left_thickness, right_thickness, length, gap):
    '''
    draw two-line symbol, The left is a dashed line, the right is a  single line

    Parameters
    ----------
    img_canvas : TYPE
        DESCRIPTION.
    start : TYPE
        DESCRIPTION.
    end : TYPE
        DESCRIPTION.
    spacing : TYPE
        DESCRIPTION.
    left_thickness : TYPE
        DESCRIPTION.
    right_thickness : TYPE
        DESCRIPTION.
    gap : TYPE
        DESCRIPTION.

    Returns
    -------
    None.

    '''
    start_array = np.asarray(start)
    end_array = np.asarray(end)

    vector = end_array - start_array

    vector_normalized = vector / np.sqrt(np.sum(vector**2)) #why is it requeared?

    vector_normalized_orthogonal = np.asarray([vector_normalized[1], -vector_normalized[0]]) #?
    
    start_right = start_array + vector_normalized_orthogonal * spacing / 2
    end_right = end_array + vector_normalized_orthogonal * spacing / 2

    if np.sum(np.isnan(start_right)) == 0 and np.sum(np.isnan(end_right)) == 0:
        cv2.line(img_canvas, (round(start_right[0]), round(start_right[1])), (round(end_right[0]), round(end_right[1])), (0, 0, 0), right_thickness)
    
    
    start_left = start_array - vector_normalized_orthogonal * spacing / 2
    end_left = end_array - vector_normalized_orthogonal * spacing / 2
 
    if np.sum(np.isnan(start_left)) == 0 and np.sum(np.isnan(end_left)) == 0:
        # cv2.line(img_canvas, (round(start_left[0]), round(start_left[1])), (round(end_left[0]), round(end_left[1])), (0, 0, 0), left_thickness)
        draw_dashed_line(img_canvas, (round(start_left[0]), round(start_left[1])), (round(end_left[0]), round(end_left[1])), left_thickness, length, gap)
    

def draw_tramway(img_canvas, start, end, spacing, left_thickness, right_thickness, bar_thickness, gap):
    '''
    

    Parameters
    ----------
    img_canvas : TYPE
        canvas.
    start : TYPE
        DESCRIPTION.
    end : TYPE
        DESCRIPTION.
    spacing : TYPE
        the distance between left line and right line.
    left_thickness : TYPE
        the thickness of left line.
    right_thickness : TYPE
        the thickness of right line.
    bar_thickness : TYPE
        the thickness of stroke/bar.
    gap : TYPE
        the distance between two strokes.

    Returns
    -------
    None.

    '''
    
    # The first step is to draw the left and right lines
    start_array = np.asarray(start)
    end_array = np.asarray(end)

    vector = end_array - start_array

    vector_normalized = vector / np.sqrt(np.sum(vector**2)) #why is it requeared?

    vector_normalized_orthogonal = np.asarray([vector_normalized[1], -vector_normalized[0]]) #?
    
    start_right = start_array + vector_normalized_orthogonal * spacing / 2
    end_right = end_array + vector_normalized_orthogonal * spacing / 2

    if np.sum(np.isnan(start_right)) == 0 and np.sum(np.isnan(end_right)) == 0:
        cv2.line(img_canvas, (round(start_right[0]), round(start_right[1])), (round(end_right[0]), round(end_right[1])), (0, 0, 0), right_thickness)
    
    
    start_left = start_array - vector_normalized_orthogonal * spacing / 2
    end_left = end_array - vector_normalized_orthogonal * spacing / 2
 
    if np.sum(np.isnan(start_left)) == 0 and np.sum(np.isnan(end_left)) == 0:
        cv2.line(img_canvas, (round(start_left[0]), round(start_left[1])), (round(end_left[0]), round(end_left[1])), (0, 0, 0), left_thickness)
      
    #The second step is to draw strokes between left and right lines
    x_l = None
    y_l = None
    x_r = None
    y_r = None


    dist =((start_array[0]-end_array[0])**2+(start_array[1]-end_array[1])**2)**.5
    Num =int(dist/gap)
    for i in range(0,Num+1):
        temp = gap*i # the temporary distance between start and the point being searched
        if start_array[0]==end_array[0]: # the line between start and end is a horizonal line
            if start_array[0]>end_array[0]:
                x_l = start_left[0]
                y_l = start_left[1] - temp
                x_r = start_right[0]
                y_r = start_right[1] - temp
                cv2.line(img_canvas, (round(x_l), round(y_l)), (round(x_r), round(y_r)), (0, 0, 0), bar_thickness)
            else:
                x_l = start_left[0]
                y_l = start_left[1] + temp
                x_r = start_right[0]
                y_r = start_right[1] + temp
                cv2.line(img_canvas, (round(x_l), round(y_l)), (round(x_r), round(y_r)), (0, 0, 0), bar_thickness)

                
        else:
            slope = (start_array[1]-end_array[1])/(start_array[0]-end_array[0])
            if start_array[0]>end_array[0]:
                x_l = start_left[0] - math.sqrt((temp**2)/(slope**2 + 1))
                y_l = start_left[1] - math.sqrt((temp**2)/(slope**2 + 1))*slope
                x_r = start_right[0] - math.sqrt((temp**2)/(slope**2 + 1))
                y_r = start_right[1] - math.sqrt((temp**2)/(slope**2 + 1))*slope
                cv2.line(img_canvas, (round(x_l), round(y_l)), (round(x_r), round(y_r)), (0, 0, 0), bar_thickness)

            else:
                x_l = start_left[0] + math.sqrt((temp**2)/(slope**2 + 1))
                y_l = start_left[1] + math.sqrt((temp**2)/(slope**2 + 1))*slope
                x_r = start_right[0] + math.sqrt((temp**2)/(slope**2 + 1))
                y_r = start_right[1] + math.sqrt((temp**2)/(slope**2 + 1))*slope
                cv2.line(img_canvas, (round(x_l), round(y_l)), (round(x_r), round(y_r)), (0, 0, 0), bar_thickness)

                
        
        
    



if __name__ == '__main__':
    img_target = cv2.imread("0001.jpg")
    
    img_canvas = img_target.copy()
    
    
    # img_canvas[:,:,:] = 255
    # draw_thick_thin_line(img_canvas, (50, 100), (100, 50), spacing=10, left_thickness=5, right_thickness=5)
    # cv2.imwrite("drawing_thick_thin_line_test.png", img_canvas)
    
    
    # # img_canvas[:,:,:] = 255
    # # draw_single_line(img_canvas, (50, 100), (100, 50), thickness=3)
    # # cv2.imwrite("drawing_single_line_test.png", img_canvas)
    
    
    # img_canvas[:,:,:] = 255
    # draw_dashed_line(img_canvas, (50, 100), (100, 50), thickness=3, length=8, gap=7)
    # cv2.imwrite("drawing_one_dashed_line_8_7.png", img_canvas)
    
    # img_canvas[:,:,:] = 255
    # draw_dashed_single_line(img_canvas, (50, 100), (100, 50), spacing=10, left_thickness=5, right_thickness=5, length=10, gap=10)
    # cv2.imwrite("drawing_dashed_single_line10271.png", img_canvas)
    
    
    img_canvas[:,:,:] = 255
    draw_tramway(img_canvas, (0, 50), (50, 100), spacing=10, left_thickness=3, right_thickness=3, bar_thickness=3, gap=10)
    cv2.imwrite("drawing_tramway_test4.png", img_canvas)





