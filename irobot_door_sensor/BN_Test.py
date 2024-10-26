from irobot_BN import IrobotNetwork as IRN

def main():
    network = IRN()
    network.add_scanner_value(149)
    network.add_wheel_value(2.4)
    network.add_bumper_value(0)

    network.add_scanner_value(84)
    network.add_wheel_value(1.6)
    network.add_bumper_value(0)

    network.add_scanner_value(83)
    network.add_wheel_value(1.9)
    network.add_bumper_value(0)

    network.add_scanner_value(82)
    network.add_wheel_value(0.4)
    network.add_bumper_value(0)

    network.add_scanner_value(74)
    network.add_wheel_value(2)
    network.add_bumper_value(0)

    print(network.calculate_probability())

if __name__ == "__main__":
    main()