import math

def is_constraint_zone(x, y,WIDTH):
    def is_in_square(x,y):
        CELL_SIZE = WIDTH // 8
        row = y // CELL_SIZE
        col = x // CELL_SIZE
        constraint_lines_one = [ 5,7]
        if row in constraint_lines_one and 3 <= col <= 4:
            return True
        if row == 4 and 2 <= col <=5 :
            return True
        if row ==2 and col == 2 :
            return True 
    def is_in_circles(x,y,):
        circles_center=[[3,3],[5,3],[5,8],[3,5],[5,5],[3,8]]
        for center in circles_center:
            center_x, center_y = center
            center_x, center_y = center_x * WIDTH//8, center_y * WIDTH//8
            distance = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
            if distance <= WIDTH/8:
                return True
    if is_in_circles(x,y)==True or is_in_square(x,y)==True:
        return True
    return False




def which_constraint_zone(x, y,WIDTH):
    CELL_SIZE = WIDTH // 8
    row = y // CELL_SIZE
    col = x // CELL_SIZE
    def is_in_zone1(x,y):
        def check1():
            if row ==2 and col == 2 :
                return True
        def check2():
            center_x, center_y = [3,3]
            center_x, center_y = center_x * WIDTH//8, center_y * WIDTH//8
            distance = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
            if distance <= WIDTH/8:
                return True
            else:
                return False
        if check1() is True or check2() is True :
            return True 

    def is_in_zone2(x,y):
        center_x, center_y = [5,3]
        center_x, center_y = center_x * WIDTH//8, center_y * WIDTH//8
        distance = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
        if distance <= WIDTH/8:
            return True
        else:
            return False
    def is_in_zone3(x,y):
        def check1():
            centers=[[3,5],[5,5]]
            for center in centers : 
                center_x, center_y = center
                center_x, center_y = center_x * WIDTH//8, center_y * WIDTH//8
                distance = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
                if distance <= WIDTH/8:
                    return True
                else:
                    return False
        def check2():
            if row == 4 and 2 <= col <=5 :
                return True
        def check3():
            constraint_lines_one = [ 5]
            if row in constraint_lines_one and 3 <= col <= 4:
                return True
        if check1() is True or check2() is True or check3() is True :
            return True 
        
    def is_in_zone4(x,y):
        def check1():
            constraint_lines_one = [7]
            if row in constraint_lines_one and 3 <= col <= 4:
                return True
        def check2():
            centers=[[5,8],[3,8]]
            for center in centers : 
                center_x, center_y = center
                center_x, center_y = center_x * WIDTH//8, center_y * WIDTH//8
                distance = math.sqrt((x - center_x) ** 2 + (y - center_y) ** 2)
                if distance <= WIDTH/8:
                    return True
        if check1() is True or check2() is True :
            return True
        else :
            return False
    if is_in_zone1(x,y) is True : 
        return 1
    if is_in_zone2(x,y) is True : 
        return 2
    if is_in_zone3(x,y) is True : 
        return 3
    if is_in_zone4(x,y) is True : 
        return 4
    else :
        return None
    