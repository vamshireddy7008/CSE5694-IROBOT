from irobot_BN import IrobotNetwork as IRN

def main():
    network = IRN()
    print(network.calculate_probability())
    network.add_scanner_value(149)
    network.add_wheel_value(2.4)
    network.add_bumper_value(0)

    network.add_scanner_value(208)
    network.add_wheel_value(1.6)
    network.add_bumper_value(0)

    network.add_scanner_value(229)
    network.add_wheel_value(1.9)
    network.add_bumper_value(0)

    network.add_scanner_value(228)
    network.add_wheel_value(0.4)
    network.add_bumper_value(0)

    network.add_scanner_value(242)
    network.add_wheel_value(2)
    network.add_bumper_value(0)

    print(network.calculate_probability())

if __name__ == "__main__":
    main()
