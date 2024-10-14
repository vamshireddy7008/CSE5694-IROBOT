import numpy as np
import scipy.stats as stats
import math

LIST_SIZE = 10

class Node:
    def __init__(self, name, mean, stdDev):
        self.name = name
        self.mean = mean
        self.sd = stdDev
        self.normalDistribution = stats.norm(0,stdDev)
        self.history = []
        self.hSize = 0
    
    def add_element(self, value):
        self.history.insert(0, value)
        if self.hSize == LIST_SIZE:
            self.history.pop()
        else:
            self.hSize += 1

    def get_probability(self):
        if not self.history:
            return 0
        total = sum(self.history)
        avg = total / self.hSize
        #print(self.history)
        #print(self.name + ' avg: ' + str(avg))
        return np.exp(-0.5*((avg- self.mean)/self.sd)**2) # uses the highes point of a normal distribution curve as 1

class IrobotNetwork:
    def __init__(self, rightScanner, wheel, bumper):
        self.Scanner = rightScanner
        self.wheel = wheel
        self.bump = bumper
    
    def __init__(self):
        self.Scanner = Node('scanner', -100, 20)
        self.wheel = Node('wheel', 90, 20)
        self.bump = Node('bump', 1, 0.1)
    
    def add_scanner_value(self, value):
        self.Scanner.add_element(value)
    
    def add_wheel_value(self, angle):
        self.wheel.add_element(angle)
    
    def add_bumper_value(self, value): # 1 true, 0 false
        self.bump.add_element(value)
    
    def calculate_probability(self):
        scannerProb = self.Scanner.get_probability()
        wheelProb = self.wheel.get_probability()
        bump = False
        if 1 in self.bump.history:
            bump = True
        #print("scanner: " + str(scannerProb))
        #print("wheel: " + str(wheelProb))
        prob = scannerProb * wheelProb
        if bump:
            prob = math.sqrt(prob)
        return prob