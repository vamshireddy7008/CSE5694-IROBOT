from irobot_BN import IrobotNetwork as IRN
from irobot_BN2 import IrobotNetwork as IRN2

network = IRN()
network2 = IRN2()
    
def main():

    print_output()
    
    add_scanner(149)
    add_wheel(2.2)
    add_bumper(0)

    print_output()
    
    add_scanner(84)
    add_wheel(2)
    add_bumper(0)

    print_output()
    
    add_scanner(83)
    add_wheel(2.4)
    add_bumper(0)

    print_output()
    
    add_scanner(82)
    add_wheel(3.2)
    add_bumper(0)
    
    print_output()
    
    add_scanner(74)
    add_wheel(3.5)
    add_bumper(0)
    
    print_output()

def add_scanner(value):
    network.add_scanner_value(value)
    network2.add_scanner_value(value)

def add_wheel(value):
    network.add_wheel_value(value)
    network2.add_wheel_value(value)

def add_bumper(value):
    network.add_bumper_value(value)
    network2.add_bumper_value(value)

def print_output():
    print('1:')
    print(network.calculate_probability())
    print('2:')
    print(network2.calculate_probability())

if __name__ == "__main__":
    main()
