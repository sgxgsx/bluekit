import subprocess
import argparse
import re
import os

from bluekit.constants import COMMAND_CONNECT, COMMAND_INFO, REGEX_COMMAND_CONNECT, NUMBER_OF_DOS_TESTS, MAX_NUMBER_OF_DOS_TEST_TO_FAIL
from bluekit.constants import RETURN_CODE_NOT_VULNERABLE, RETURN_CODE_ERROR, RETURN_CODE_NONE_OF_4_STATE_OBSERVED, RETURN_CODE_UNDEFINED, RETURN_CODE_VULNERABLE



def dos_checker(target):
    try:
        try:
            cont = True
            down_times = 0
            not_pairable = 0
            while cont:
                for i in range(NUMBER_OF_DOS_TESTS):
                    available = check_availability(target)
                    if available:
                        pairable = check_connectivity(target)
                        if not pairable:
                            down_times += 1
                            not_pairable += 1
                        else:
                            break
                    else:
                        down_times += 1
                break
        except Exception as e:
            return RETURN_CODE_ERROR, str(e)
        
        # NEEDS BETTER LOGIC
        
        if down_times > MAX_NUMBER_OF_DOS_TEST_TO_FAIL:
            if not_pairable > MAX_NUMBER_OF_DOS_TEST_TO_FAIL:
                return RETURN_CODE_VULNERABLE, str(down_times)
            elif down_times == NUMBER_OF_DOS_TESTS: 
                return RETURN_CODE_VULNERABLE, str(down_times)
        else:
            return RETURN_CODE_NOT_VULNERABLE, str(down_times)
    except Exception as e:
        return RETURN_CODE_ERROR, str(e)
    
        
        

def check_availability(target):
    try:
        proc_out = subprocess.check_output(COMMAND_INFO.format(target=target), shell=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as e:
        #print("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
        if e.output == b"Can't create connection: Input/output error\nRequesting information ...\n":
            print("Device is down")
        else:
            print("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
        return False
    #print("Availability - True")
    return True


def check_connectivity(target):
    try:
        proc_out = subprocess.check_output(COMMAND_CONNECT.format(target=target), shell=True, stderr=subprocess.STDOUT)
        print("Successful check - Device connectivity is checked")
    except subprocess.CalledProcessError as e:
        #print("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
        text = e.output.decode()
        try:
            mm = re.compile(REGEX_COMMAND_CONNECT.format(target=target))
            output = mm.search(text).group()
            print("Partical check - Device connectivity is checked")
            return True
        except AttributeError as e:
            print("Device is offline")
        return False
    #print("Connectability- True")
    return True


def check_target(self, target):
    cont = True 
    while cont:
        for i in range(10):
            available = check_availability(target)
            if available:
                pairable = check_connectivity(target)
                if not pairable:
                    inp = self.command_input()
                else:
                    return True
        if not available:
            inp = self.command_input()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t','--target',required=False, type=str, help="target MAC address")
    parser.add_argument('-a','--availability',required=False, type=bool, help="check availability")
    parser.add_argument('-c','--connectivity',required=False, type=bool, help="check connectivity")
    args = parser.parse_args()

    if args.target:
        if args.availability:
            check_availability(args.target)
        if args.connectivity:
            check_connectivity(args.target)
        
    else:
        parser.print_help()

