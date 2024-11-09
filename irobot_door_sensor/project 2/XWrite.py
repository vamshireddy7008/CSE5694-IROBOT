import xlwt;
import os.path

DEFAULT_NAME = 'TRIAL'

class writer:
    def __init__(self):
        self.fname=DEFAULT_NAME + '.xls'
        cnt = 0
        while os.path.isfile(self.fname):
            cnt += 1
            self.fname= DEFAULT_NAME + '_' +str(cnt) + '.xls'
        self.book = xlwt.Workbook(encoding="utf-8")
        self.sheet1 = self.book.add_sheet("Sheet 1")
        
        self.wall = 0
        self.door = 1
        self.frame = 2
        self.angle = 3
        self.bump = 4

        self.sheet1.write(0, self.wall, "wall")
        self.sheet1.write(0, self.door, "Door")
        self.sheet1.write(0, self.frame, "Frame")
        self.sheet1.write(0, self.angle, "Angle")
        self.sheet1.write(0, self.bump, "Bump")

        self.row = 1
        
    def add_wall(self, value):
        self.sheet1.write(self.row, self.wall, value)
    def add_door(self, value):
        self.sheet1.write(self.row, self.door, value)
    def add_frame(self, value):
        self.sheet1.write(self.row, self.frame, value)
    def add_Bump(self):
        self.sheet1.write(self.row, self.bump, 'Y')
    def add_angle(self, value):
        self.sheet1.write(self.row, self.angle, value)
    
    def go_next(self):
        self.row += 1
    def save(self):
        self.book.save(self.fname)

if __name__ == '__main__':
    xcel = writer()
    xcel.add_wall(1)
    xcel.add_door(1)
    xcel.add_frame(1)
    xcel.add_angle(1)
    xcel.add_Bump()
    xcel.go_next()
    xcel.add_wall(2)
    xcel.add_door(2)
    xcel.add_frame(2)
    xcel.add_angle(2)
    xcel.go_next()
    xcel.save()
    

