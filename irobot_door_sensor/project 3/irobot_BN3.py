from sre_constants import BRANCH
import numpy as np
import math

LIST_SIZE = 10

class Normal_Distribtion:
    def __init__(self, mean, stdDev, PA):
        self.mean = mean
        self.sd = stdDev
        self.PA = PA

    def get_normal_dist_probability(self, val):
        return  1/(math.sqrt(2 * math.pi)*self.sd) * np.exp(-0.5*((val - self.mean)/self.sd)**2)

class Node:
    def __init__(self, name, event_distribution, nxt, type="normal"):
        self.name = name
        self.normal_dist = event_distribution
        self.next = nxt
        self.type = type
        self.hSize = 0

    # gets the probability using Bayes' Theorem
    def get_probability(self, datalist):
        probEvent = 0.0
        if self.type == "binary":
            probEvent = self.normal_dist.PA
        elif self.type == "normal":
            if datalist == []:
                return 0
            avg = sum(datalist) / len(datalist)
            probEvent = self.normal_dist.get_normal_dist_probability(avg)
        
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
        self.NetworkSet = {
            'Door_Nodes': {
            #Node(       self, name,       event_distribution,                       nxt,                 type="normal"
            'head':      Node('door'   , Normal_Distribtion(0, 0, 0.35)           , ["bump", "no bump"]            , "binary"),
            'no bump':   Node('bump'   , Normal_Distribtion(0, 0, 1)              , ["scanner"]                    , "binary"), # bumps will always be given so return a PA of 1
            'bump':      Node('bump'   , Normal_Distribtion(0, 0, 1)              , ["scanner_b"]                  , "binary"), # bumps will always be given so return a PA of 1
            'scanner':   Node('scanner', Normal_Distribtion(39.368, 21.11, 0.35)  , ["wheel"]                                ),
            'wheel':     Node('wheel'  , Normal_Distribtion(5.905, 3.822, 0.35)   , []                                       ),  
            'scanner_b': Node('scanner', Normal_Distribtion(285, 84.86, 0.35)     , ["wheel_b"]                              ),
            'wheel_b':   Node('wheel'  , Normal_Distribtion(4.533, 3.2, 0.35)     , []                                       ),
            },

            'Wall_Nodes': {
            #Node(       self, name,       event_distribution,                        nxt,                 type="normal"
            'head':      Node('door'   , Normal_Distribtion(0, 0, 0.619)          , ["bump", "no bump"]            , "binary"),
            'no bump':   Node('bump'   , Normal_Distribtion(0, 0, 1)              , ["scanner"]                    , "binary"), # bumps will always be given so return a PA of 1
            'bump':      Node('bump'   , Normal_Distribtion(0, 0, 1)              , ["scanner_b"]                  , "binary"), # bumps will always be given so return a PA of 1
            'scanner':   Node('scanner', Normal_Distribtion(302.283, 85.357, 0.62), ["wheel"]                                ),
            'wheel':     Node('wheel'  , Normal_Distribtion(4.632, 4.172, 0.62)   , []                                       ),  
            'scanner_b': Node('scanner', Normal_Distribtion(730, 430.3, 0.62)     , ["wheel_b"]                              ),
            'wheel_b':   Node('wheel'  , Normal_Distribtion(5.3, 0.174, 0.62)       , []                                       ),
            },

            'Frame_Nodes': {
            #Node(       self, name,       event_distribution,                        nxt,                 type="normal"
            'head':      Node('door'   , Normal_Distribtion(0, 0, 0.031)          , ["bump"]                       , "binary"),
            'no bump':   Node('bump'   , Normal_Distribtion(0, 0, 1)              , ["scanner"]                    , "binary"), # bumps will always be given so return a PA of 1
            'bump':      Node('bump'   , Normal_Distribtion(0, 0, 1)              , ["scanner_b"]                  , "binary"), # bumps will always be given so return a PA of 1
            'scanner':   Node('scanner', Normal_Distribtion(730.09, 534.41, 0.031), ["wheel"]                                ),
            'wheel':     Node('wheel'  , Normal_Distribtion(5.968, 4.734, 0.031)  , []                                       ),  
            'scanner_b': Node('scanner', Normal_Distribtion(1000, 307, 0.031)     , ["wheel_b"]                              ),
            'wheel_b':   Node('wheel'  , Normal_Distribtion(5.9, 3.549, 0.031)  , []                                       ),
            }
        }

        self.Data = {
             'bump': [],
             'wheel': [],
             'scanner': []
        }
    def get_data(self, name, time):
        if name in self.Data and time <= len(self.Data[name]):
            return self.Data[name][:time]
        else:
            return []

    def add_element(self, name, value):
        self.Data[name].insert(0,value)
        if len(self.Data[name]) > LIST_SIZE:
            self.Data[name].pop()

    def add_scanner_value(self, value):
        self.add_element('scanner', value)
        return []
    def add_wheel_value(self, angle):
        self.add_element('wheel', angle)
    
    def add_bumper_value(self, isHit): # 1 true, 0 false
        self.add_element('bump', isHit)

    def remove_bump(self):
        self.Data['bump'] = []

    def remove_scanner(self):
        self.Data['scanner'] = []

    def calculate_probability(self, type= 'door', time=LIST_SIZE):
        if time > LIST_SIZE:
            time = LIST_SIZE

        context = []
        bump = True in self.Data['bump'][:time]
        if bump:
            context.append('bump')
        else:
            context.append('no bump')

        door_prob = self.recursion_tree('Door_Nodes','head', context, time)
        wall_prob = self.recursion_tree('Wall_Nodes','head', context, time)
        frame_prob = self.recursion_tree('Frame_Nodes','head', context, time)

        total_prob = door_prob + wall_prob + frame_prob
        if total_prob== 0:
            return 0
        if type == 'door':
            return door_prob / total_prob
        elif type == 'wall':
            return wall_prob / total_prob
        elif type == 'frame':    
            return frame_prob / total_prob

    def recursion_tree(self, networkName, nodeName, context, time):
        current = self.NetworkSet[networkName][nodeName]
        if not current.has_next():
            return current.get_probability(self.get_data(current.name, time))
        next_list = [i for i in current.go_next() if i in context]
        if len(next_list) == 0:
            next_list = current.go_next()
        total = 0
        for nextNode in next_list:
            total += self.recursion_tree(networkName, nextNode, context, time)
        return total * current.get_probability(self.get_data(current.name, time))
