from irobot_BN import IrobotNetwork as IRN

def main():
    network = IRN()
    print(network.calculate_probability())
    network.add_scanner_value(257)
    network.add_wheel_value(2.2)
    network.add_bumper_value(0)

    network.add_scanner_value(307)
    network.add_wheel_value(2)
    network.add_bumper_value(0)

    network.add_scanner_value(328)
    network.add_wheel_value(2.4)
    network.add_bumper_value(0)

    network.add_scanner_value(347)
    network.add_wheel_value(3.2)
    network.add_bumper_value(0)

    network.add_scanner_value(252)
    network.add_wheel_value(3.5)
    network.add_bumper_value(1)

    print(network.calculate_probability())

if __name__ == "__main__":
    main()
