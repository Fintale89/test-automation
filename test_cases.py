import os
import sys

from time import sleep
from datetime import datetime

import framework
import voltmeter

from helpers import *


def testcase_template(dut):
    """ Test case template

    Returns name and result as strings.
    
    """
    name = "Template for a test case"
    results = []  # Result array for sub-tasks

    # begin test content

    # end test content
    result = check_results(results)
    return name, result


def test_read_simple(dut):
    """ Simple reading test.

        Sets few PWM values. Resets DUT in between.

        Returns result "PASS" or "FAIL".

        TODO:
        1. Implement comparison of sent and expected value.
        2. Implement result determining according to specification.

    """
    name = "Simple reading test for few individual values"

    # begin test content
    dut.board.reset()
    my_interface = dut.board.default_interface

    values = [0, 100, 500, 1000, 1500, 2000]
    results = []
    for sent in values:
        write_value(my_interface, sent)
        value = read_value(my_interface)
        # TODO implement missing logic here
        val_string = remove_whitespace(value)
		
        if val_string != str(sent):
            print("incorrect value! Got: " + val_string + ", expected: " + str(sent))
            results.append("FAIL")
        else:
            print("OK! Got: " + val_string + ", expected: " + str(sent))
            results.append("PASS")
			
        sleep(2)
        dut.board.reset()

    result = check_results(results)
    # end test content
    return name, result


def test_read_range(dut):
    """ Simple reading test for value range.
        Sets a range of PWM values.

        Returns result "PASS" or "FAIL".

        TODO:
        1. What goes wrong?
        2. Fix it.

    """
    name = "Simple reading test for value range"
    results = []

    # begin test content
    dut.board.reset()
    for sent in range(0, 2001, 1):
        write_value(dut.board.default_interface, sent)
        value = read_value(dut.board.default_interface)

        val_string = remove_whitespace(value)
        if val_string != str(sent):
            print("incorrect value! Got: " + val_string + ", expected: " + str(sent))
            results.append("FAIL")
        else:
            print("OK! Got: " + val_string + ", expected: " + str(sent))
            results.append("PASS")

    # end test content
    result = check_results(results)
    return name, result


def test_invalid_values(dut):
    """ Test Serial API with invalid values.

        Returns "PASS" or "FAIL"

        TODO:
        1. Implement comparison of sent and expected value.
        2. Implement result determining according to specification.
        3. Simplify test case structure.

    """
    name = "Simple reading test for few invalid values"
    results = []
    # begin test content

    dut.board.reset()
    my_interface = dut.board.default_interface

    # List of commands to send
    command = ["1234", " 1234", "4321", "test", "0est", "tes1", "01234", "012345678", "0", "100", "500", "1000", "2000"]

    # begin test content
    for i in range(0, len(command), 1):
        my_interface.write(command[i] + "\r")	# add cartridge return
        print('Sending command >{}<'.format(command[i]))
        value = read_value(my_interface)
        val_string = remove_whitespace(value)

        # valid command
        if is_valid(val_string):
            # last 4 bytes read back succesful -> PASS
            if val_string == command[i][-4:]:
                results.append("PASS")
                print("Passed")
            # failed to read command back -> FAIL
            else:
                results.append("FAIL")
                print("Failed")
        # invalid command
        else:
            # last 4 bytes read back successful -> PASS
            if val_string == command[i][-4:]:
                results.append("PASS")
                print("Passed")
            # nothing read back -> PASS
            elif val_string == "":
                results.append("PASS")
                print("Passed")
            # failed to read command back -> FAIL
            else:
                results.append("FAIL")
                print("Failed")
        sleep(1)

    # end test content
    result = check_results(results)
    return name, result


def test_measure(dut):
    """ Simple voltage measurement test.

    Sets valid PWM values 0...2000. Reads voltage.
    Expects voltage to follow the changes of the PWM value.

    TODO:
    1. Implement voltmeter API re-using voltmeter.py functions. Add it to framework as a read-only interface.
    2. Re-use logic of other tests to make the functionality

    """
    name = "Voltage Measurement task"
    results = []
    # begin test content

    dut.board.reset()
    my_interface = dut.board.default_interface
    my_interface2 = dut.board.default_voltmeter

    # set PWM and measure voltage
    values = [0, 100, 500, 1000, 1500, 2000]
    results = []

    # set tolerance for voltage measurement (+-)
    tolerance = 0.05
#    for sent in values:
    for i in range(0, len(values), 1):
        write_value(my_interface, values[i])
        sleep(0.1)
        volts = read_value(my_interface2)
        print("Measured DC: "+ str(round(float(volts),4))+"V")
        expectedVoltage = round(((values[i] / 2000) * 3.3),4)
        print("Expecting " + str(round(((values[i] / 2000) * 3.3),4)))
        if ((float(volts) - expectedVoltage < tolerance) or (expectedVoltage - float(volts) < tolerance)):
            print("Passed")
            results.append("PASS")
        else:
            print("Failed")
            results.append("FAIL")
			
        sleep(1)
        dut.board.reset()

    # end test content

    result = check_results(results)
    return name, result


def test_sequence(dut, test_cases, firmware_file):
    """ Sequences tests and keeps a simple scoreboard for results.
    
    """
    results = {}

    print("*" * 78)
    for test in test_cases:
        print("BEGIN TEST: " + str(datetime.now()))
        name, result = test(dut)
        results[name] = result
        print("END TEST: " + str(datetime.now()))
        print((name + ": ").ljust(50) + "[" + result.upper() + "]")
        print("*" * 78)

    print("Tests completed.\nSummary:")

    # write test results to log file
    file_name = firmware_file[len(firmware_file)-10:-4] + ".log"
    log_file = open(file_name, "w")

    for r in results:
        print((r + ": ").ljust(50) + "[" + results[r].upper() + "]")
        log_file.write((r + ": ").ljust(50) + "[" + results[r].upper() + "]\r\n")
    log_file.close()

def main():
    """ Brings up the board and starts the test sequence.
    
    """
    # ENVIRONMENT CONFIGURATION -------------------------------------------------

    serial_port = "COM7"     # serial_port = "/dev/ttyUSB0"
    firmware_file = "firmware\\tamk_1.bin" # optionally overridden with command line argument
    board_name = "MyBoard"
    dut_name = "MyIndividualDut"

    # BOARD CONFIGURATION -------------------------------------------------------

    # Overrides the default firmware_file
    if len(sys.argv) > 1:
        firmware_file = sys.argv[1]

    myboard = framework.Board(board_name)

    # Interfaces
    myserial = framework.Serial(serial_port)
    myboard.add_interface("Serial", myserial)


    # TODO Voltmeter yet unfinished!
    myvoltmeter = framework.VoltMeter()
    myboard.add_interface("VoltMeter", myvoltmeter)

    myboard.set_default_interface("Serial")
    myboard.set_default_voltmeter("VoltMeter")

    sleep(1)

    # FIRMWARE CONFIGURATION ----------------------------------------------------
    myfirmware = framework.Firmware(firmware_file)
    myfirmware.write_to_dut()

    # DUT CONFIGURATION ---------------------------------------------------------
    mydut = framework.Dut(myfirmware, myboard, dut_name)

    print("Set-up: DUT: {dut} FW {firmware} on HW {board} connected with {interface}".
        format(
            dut=mydut.name,
            firmware=mydut.firmware.name,
            board=mydut.board.name,
            interface=mydut.board.default_interface.name
        )
    )

    # TEST CASES ----------------------------------------------------------------
    test_cases = [
        test_read_simple,
        test_read_range,
        test_invalid_values,
        test_measure
    ]

    # added firmware_file to parameters to write log file
    test_sequence(mydut, test_cases, firmware_file)


if __name__ == "__main__":
    main()
