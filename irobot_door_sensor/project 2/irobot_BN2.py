from sre_constants import BRANCH
import numpy as np
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
            'head':      Node('door'   , Normal_Distribtion(0, 0, 0.419)         , ["bump", "no bump"]            , "binary"),
            'no bump':   Node('bump'   , Normal_Distribtion(0, 0, 1)             , ["scanner"]                    , "binary"), # bumps will always be given so return a PA of 1
            'bump':      Node('bump'   , Normal_Distribtion(0, 0, 1)             , ["scanner_b"]                  , "binary"), # bumps will always be given so return a PA of 1
            'scanner':   Node('scanner', Normal_Distribtion(134.58, 54.86, 0.419), ["wheel"]                                ),
            'wheel':     Node('wheel'  , Normal_Distribtion(1.692, 1.378, 0.419) , []                                       ),  
            'scanner_b': Node('scanner', Normal_Distribtion(172.125, 97.2, 0.419), ["wheel_b"]                              ),
            'wheel_b':   Node('wheel'  , Normal_Distribtion(0.475, 0.173, 0.419) , []                                       ),
            },

            'Wall_Nodes': {
            #Node(       self, name,       event_distribution,                        nxt,                 type="normal"
            'head':      Node('door'   , Normal_Distribtion(0, 0, 0.58)           , ["bump", "no bump"]            , "binary"),
            'no bump':   Node('bump'   , Normal_Distribtion(0, 0, 1)              , ["scanner"]                    , "binary"), # bumps will always be given so return a PA of 1
            'bump':      Node('bump'   , Normal_Distribtion(0, 0, 1)              , ["scanner_b"]                  , "binary"), # bumps will always be given so return a PA of 1
            'scanner':   Node('scanner', Normal_Distribtion(299.694, 133.22, 0.58), ["wheel"]                                ),
            'wheel':     Node('wheel'  , Normal_Distribtion(1.65, 1.22, 0.58)     , []                                       ),  
            'scanner_b': Node('scanner', Normal_Distribtion(419, 69.3, 0.58)      , ["wheel_b"]                              ),
            'wheel_b':   Node('wheel'  , Normal_Distribtion(0, 0.174, 0.58)       , []                                       ),
            },

            'Frame_Nodes': {
            #Node(       self, name,       event_distribution,                        nxt,                 type="normal"
            'head':      Node('door'   , Normal_Distribtion(0, 0, 0.042)          , ["bump"]                       , "binary"),
            'no bump':   Node('bump'   , Normal_Distribtion(0, 0, 1)              , ["scanner"]                    , "binary"), # bumps will always be given so return a PA of 1
            'bump':      Node('bump'   , Normal_Distribtion(0, 0, 1)              , ["scanner_b"]                  , "binary"), # bumps will always be given so return a PA of 1
            'scanner':   Node('scanner', Normal_Distribtion(1225, 407, 0.042)     , ["wheel"]                                ),
            'wheel':     Node('wheel'  , Normal_Distribtion(-0.75, 1.549, 0.042)  , []                                       ),  
            'scanner_b': Node('scanner', Normal_Distribtion(1885, 407, 0.042)     , ["wheel_b"]                              ),
            'wheel_b':   Node('wheel'  , Normal_Distribtion(-1.5, 1.549, 0.042)   , []                            ),
            }
        }

        self.Data = {
             'bump': [],
             'wheel': [],
             'scanner': []
        }
    def get_data(self, name, time):
        if name in self.Data:
            return self.Data[name][:time]
        else:
            return []

    def add_element(self, name, value):
        self.Data[name].insert(0,value)
        if len(self.Data[name]) > LIST_SIZE:
            self.history.pop()

    def add_scanner_value(self, value):
        self.add_element('scanner', value)
        return []
    def add_wheel_value(self, angle):
        self.add_element('wheel', angle)
    
    def add_bumper_value(self, isHit): # 1 true, 0 false
        self.add_element('bump', isHit)

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
