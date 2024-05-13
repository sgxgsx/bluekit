import subprocess
import argparse
import re
import logging
import time
import signal

from pathlib import Path
from bluekit.verifyconn import check_availability, check_connectivity

from bluekit.constants import HCITOOL_INFO, SDPTOOL_INFO, BLUING_BR_LMP, BLUING_BR_SDP, OUTPUT_DIRECTORY, REGEX_BT_VERSION, REGEX_BT_VERSION_HCITOOL, VERSION_TABLE, ADDITIONAL_RECON_DATA_FILE
from bluekit.constants import LOG_FILE, REGEX_BT_MANUFACTURER

COMMANDS = [HCITOOL_INFO, SDPTOOL_INFO, BLUING_BR_SDP, BLUING_BR_LMP]
invaisive_commands = [HCITOOL_INFO]

logging.basicConfig(filename=LOG_FILE, level=logging.INFO)

class Recon():
    def check_target(self, target):
        available = check_availability(target)
        if not available:
            print("Device is not available")
        else:
            print("Device is available")
        pairable = check_connectivity(target)
        if not pairable:
            print("Device is not pairable")
        else:
            print("Device is pairable")

    def run_command(self, target, command, filename):
        print("Running command -> {}".format(command))
        try:
            output = subprocess.check_output(command.format(target=target), shell=True).decode()
            f = open(filename, 'w')
            f.write(output)
            f.close()
        except subprocess.CalledProcessError as e:
            print("Error during running command")
            print(e.output)
        return False

    def run_recon(self, target, commands):
        log_dir = OUTPUT_DIRECTORY.format(target=target, exploit='recon')
        Path(log_dir).mkdir(exist_ok=True, parents=True)
        for command, filename in commands:
            self.run_command(target, command, log_dir + filename)
    
    def determine_bluetooth_version(self, target) -> float:
        file_path = Path(OUTPUT_DIRECTORY.format(target=target, exploit='recon') + BLUING_BR_LMP[1])
        if file_path.is_file():
            with file_path.open('r') as f:
                text = f.read()
                mm = re.compile(REGEX_BT_VERSION)
                output = mm.search(text).group()
                return float(output.split(" ")[3])
        else:
            file_path = Path(OUTPUT_DIRECTORY.format(target=target, exploit='recon') + HCITOOL_INFO[1])
            print(file_path)
            if file_path.is_file():
                with file_path.open('r') as f:
                    text = f.read()
                    mm = re.compile(REGEX_BT_VERSION_HCITOOL)
                    output = mm.search(text).group()
                    version = output.split('(')[1].split(')')[0]
                    try:
                        num_version = VERSION_TABLE[version]
                        return num_version
                    except Exception as e:
                        print("Error during retrieving a version")
            else:
                print("Recon files do not exist, please run recon module first, then exploit module for better results")
        return None 

    def start_hcidump(self):
        logging.info("Starting hcidump -X...")
        process = subprocess.Popen(["hcidump", "-X"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return process

    def stop_hcidump(self, process):
        logging.info("Stopping hcidump -X...")
        process.send_signal(subprocess.signal.SIGINT)
        output, _ = process.communicate()
        logging.info("hcidump -> " + str(output.decode()))
        logging.info("hcidump -X stopped.")
        return output

    def get_hcidump(self, target):
        hcidump_process = self.start_hcidump()
        try:
            time.sleep(2)
            
            check_connectivity(target=target)
        finally:
            return self.stop_hcidump(hcidump_process).decode().split("\n")

    def get_capabilities(self, target):
        output = self.get_hcidump(target)
        # Our capability is set as NoInputNoOutput so the other one should be a target device capability
        capabilities = set()
        numb_of_capabilities = 0 
        for line in output:
            if line.strip().startswith("Capability:"):
                capabilities.add(line.strip().split(" ")[1])
                numb_of_capabilities += 1
        logging.info("recon.py -> found the following capabilities " + str(capabilities))
        if len(capabilities) == 0:
            logging.info("recon.py -> most likely legacy pairing")
            return None
        elif numb_of_capabilities == 1:
            logging.info("recon.py -> got only 1 capability " + str(capabilities))
            return capabilities.pop()
        capabilities.remove('NoInputNoOutput')
        capability = None
        if len(capabilities) == 0:
            return "NoInputNoOutput"
        else:
            return capabilities.pop()
    
    def scan_additional_recon_data(self, target):
        # collect additional data - for now it's only capability

        capability = self.get_capabilities(target=target)

        log_dir = OUTPUT_DIRECTORY.format(target=target, exploit='recon')
        Path(log_dir).mkdir(exist_ok=True, parents=True)
        filename = log_dir + ADDITIONAL_RECON_DATA_FILE
        f = open(filename, 'w')
        f.write(capability)
        f.close()




if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-t','--target',required=False, type=str, help="target MAC address")
    parser.add_argument('-a','--availability',required=False, type=bool, help="check availability")
    parser.add_argument('-i','--invaisive',required=False, type=bool, help="do invaisive recon")
    args = parser.parse_args()

    if args.target:
        recon = Recon()
        v = recon.determine_bluetooth_version(args.target)
        print(v)
        #if args.availability:
        #    check_target(args.target)
        recon.scan_additional_recon_data(args.target)
        recon.run_recon(args.target, COMMANDS)
        #if args.invaisive:
            #run_recon(args.target, invaisive_commands)
    else:
        parser.print_help()



