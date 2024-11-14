from sre_constants import BRANCH
import numpy as np
import scipy.stats as stats
import math

LIST_SIZE = 5


class Normal_Distribtion:
    def __init__(self, mean, stdDev, PA):
        self.mean = mean
        self.sd = stdDev
        self.PA = PA

    def get_normal_dist_probability(self, val):
        return  1/(math.sqrt(2 * math.pi)*self.sd) * np.exp(-0.5*((val - self.mean)/self.sd)**2)

class Node:
    def __init__(self, name, event_distribution, not_event_dist, nxt, type="normal"):
        self.name = name
        self.normal_dist = event_distribution
        self.not_normal_dist = not_event_dist
        self.next = nxt
        self.history = []
        self.type = type
        self.hSize = 0

    def add_element(self, value):
        self.history.insert(0, value)
        if self.hSize == LIST_SIZE:
            self.history.pop()
        else:
            self.hSize += 1

    # gets the probability using Bayes' Theorem
    def get_probability(self,door=True):
        probEvent = 0.0
        if self.type == "binary":
            if door:
                probEvent = self.normal_dist.PA
            else:
                probEvent = self.not_normal_dist.PA
        elif self.type == "normal":
            if self.history == []:
                return 0
            avg = sum(self.history) / self.hSize
            if door:
                probEvent = self.normal_dist.get_normal_dist_probability(avg)
            else:
                probEvent = self.not_normal_dist.get_normal_dist_probability(avg)
        
        if probEvent == 0:
            print(self.name + " has 0 probability")
        return probEvent
    
    def has_next(self):
        if self.next == []:
            return False
        else:
            return True

    def go_next(self):
        return self.next

class IrobotNetwork:  
    def __init__(self):
        self.nodes = {
                    # self, name, event_distribution, not_event_dist, nxt, type="normal"
        'scanner':   Node('scanner', Normal_Distribtion(134.58, 54.86, 0.413),  Normal_Distribtion(324.7, 200.99, 0.587), ["door"]),
        'wheel':     Node('wheel', Normal_Distribtion(1.692, 1.378, 0.413),  Normal_Distribtion(1.608, 1.227, 0.587), ["scanner"]),
        'scanner_b': Node('scanner_b', Normal_Distribtion(172.125, 97.2, 0.4),  Normal_Distribtion(405.41, 391.14, 0.6), ["door"]),
        'wheel_b':   Node('wheel_b', Normal_Distribtion(0.475, 0.173, 0.4),  Normal_Distribtion(-0.75, 0.225, 0.6), ["scanner_b"]),
        'bump':      Node('bump', Normal_Distribtion(0, 0, 1), Normal_Distribtion(0, 0, 1), ["wheel_b","wheel"], "binary"),
        'door':      Node('door', Normal_Distribtion(0, 0, 0.438), Normal_Distribtion(0, 0, 0.562), [], "binary")
        }
        self.head = 'bump'
    
    def add_scanner_value(self, value):
        self.nodes['scanner'].add_element(value)
        self.nodes['scanner_b'].add_element(value)
    
    def add_wheel_value(self, angle):
        self.nodes['wheel'].add_element(angle)
        self.nodes['wheel_b'].add_element(angle)
    
    def add_bumper_value(self, value): # 1 true, 0 false
        self.nodes['bump'].add_element(value)

    def calculate_probability(self):
        prob = self.recursion_tree(self.head, True)
        prob_not = self.recursion_tree(self.head, False)
        denominator = (prob + prob_not)
        if denominator == 0:
            return 0
        alpha =  1 / denominator
        return prob * alpha

    def recursion_tree(self,nodeName, door):
        current = self.nodes[nodeName]
        if not current.has_next():
            return current.get_probability(door)

        if nodeName == "bump":
            if 1 in current.history:
                return current.get_probability(door) * self.recursion_tree(current.go_next()[0], door)
            else:
                return current.get_probability(door) * self.recursion_tree(current.go_next()[1], door)

        lst = current.go_next()
        total = 0
        for nextNode in current.go_next():
            total += self.recursion_tree(nextNode, door)
        return total * current.get_probability(door)
