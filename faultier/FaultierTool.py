#!/usr/bin/env python
import sys
import os
try:
    import faultier
except:
    print("Can't import faultier - make sure you install the latest faultier version with pip3 install -U faultier")
    sys.exit(1)
import argparse
import subprocess

# Define your functions, all accepting 'args' even if they don't use it
def faultier_nrf52_test(args=None):
    print("Running NRF test...")

    
def faultier_nrf52_flash(file_path):
    """
    Flashes a connect nRF52 with the provided firmware. Requires OpenOCD to be in path.
    """
    print("Flashing nRF...")
    if not os.path.isfile(file_path):
        raise Exception(f"File {file_path} not found.")
    cmd = [
        "openocd",
        "-f", "interface/tamarin.cfg",
        "-f", "target/nrf52.cfg",
        "-c", f"init; nrf52_recover; program {file_path} verify; reset; exit"
        ]
    try:
        result = subprocess.run(cmd, check=True, text=True, capture_output=True)

        if "Verified OK" in result.stdout or "Verified OK" in result.stderr:
            print("Flashing successful: Verified OK")
        else:
            print("Error: 'Verified OK' not found in OpenOCD output")
            print("Output:", result.stdout)
            print("Errors:", result.stderr)
    except subprocess.CalledProcessError as e:
        print("Error during flashing process:", e)
        print("Output:", e.stdout)
        print("Errors:", e.stderr)

def openocd_program(config, path):
    if not os.path.isfile(path):
        raise Exception(f"File {path} not found.")
    if " " in path:
        raise Exception(f"Path contains spaces - unsupported.")
    if ";" in path:
        raise Exception(f"Path contains semicolon - unsupported.")
    cmd = [
        "openocd",
        "-f", "interface/tamarin.cfg",
        "-f", f"target/{config}.cfg",
        "-c", f"init; nrf52_recover; program {path} verify; reset; exit"
    ]
    try:
        result = subprocess.run(cmd, check=True, text=True, capture_output=True)

        if "Verified OK" in result.stdout or "Verified OK" in result.stderr:
            print("Flashing successful: Verified OK")
        else:
            print("Error: 'Verified OK' not found in OpenOCD output")
            print("Output:", result.stdout)
            print("Errors:", result.stderr)
    except subprocess.CalledProcessError as e:
        print("Error during flashing process:", e)
        print("Output:", e.stdout)
        print("Errors:", e.stderr)


    pass

def faultier_nrf52_lock(args=None):
    print("Locking nRF...")
    cmd = [
    "openocd",
    "-f", "interface/tamarin.cfg",
    "-f", "target/nrf52.cfg",
    "-c", f"init; reset halt; flash fillw 0x10001208 0xFFFFFF00 0x01; reset; exit"
    ]
    try:
        result = subprocess.run(cmd, check=True, text=True, capture_output=True)
        print("Chip locked!")
    except subprocess.CalledProcessError as e:
        print("Error during locking process:", e)
        print("Output:", e.stdout)
        print("Errors:", e.stderr)

    # faultier.Faultier.lock_nrf()

def faultier_nrf52_unlock(args=None):
    print("NRF unlocked.")
    faultier.Faultier.unlock_nrf()

def faultier_nrf52_flash(file_path):
    print(f"Flashing nRF52 with {file_path}")
    openocd_program("nrf52", file_path)

def faultier_stm32_test(args=None):
    print("Running STM32 test...")

def faultier_stm32_rdp1(args=None):
    print("STM32 RDP1 enabled.")

def faultier_stm32_rdp2(really):
    if really:
        print("STM32 RDP2 enabled.")
    else:
        print("You must confirm RDP2 with --really flag.")

def faultier_stm32_rdp0(args=None):
    print("STM32 RDP0 enabled.")

def faultier_stm32_flash(file_path):
    print(f"Flashing STM32 with {file_path}")
    openocd_program("stm32f4x", file_path)

def faultier_test(args=None):
    print("Running test...")

def main():
    # Set up argparse
    parser = argparse.ArgumentParser(description="Faultier tool")

    # Create subparsers for the different modes
    subparsers = parser.add_subparsers(dest="mode", help="")

    # NRF mode
    nrf_parser = subparsers.add_parser("nrf52", help="nRF52 commands")
    nrf_subparsers = nrf_parser.add_subparsers(dest="command", help="NRF commands")

    nrf_subparsers.add_parser("lock", help="Lock NRF").set_defaults(func=faultier_nrf52_lock)
    nrf_subparsers.add_parser("unlock", help="Unlock NRF").set_defaults(func=faultier_nrf52_unlock)

    flash_nrf_parser = nrf_subparsers.add_parser("flash", help="Flash NRF with a file")
    flash_nrf_parser.add_argument("file", help="File path for flashing NRF")
    flash_nrf_parser.set_defaults(func=lambda args: faultier_nrf52_flash(args.file))

    # STM32 mode
    stm32_parser = subparsers.add_parser("stm32", help="STM32 commands")
    stm32_subparsers = stm32_parser.add_subparsers(dest="command", help="STM32 commands")

    stm32_subparsers.add_parser("rdp1", help="Enable RDP1").set_defaults(func=faultier_stm32_rdp1)
    rdp2_parser = stm32_subparsers.add_parser("rdp2", help="Enable RDP2")
    rdp2_parser.add_argument("--really", action="store_true", help="Confirm enabling RDP2")
    rdp2_parser.set_defaults(func=lambda args: faultier_stm32_rdp2(args.really))

    stm32_subparsers.add_parser("rdp0", help="Enable RDP0").set_defaults(func=faultier_stm32_rdp0)

    flash_stm32_parser = stm32_subparsers.add_parser("flash", help="Flash STM32 with a file")
    flash_stm32_parser.add_argument("file", help="File path for flashing STM32")
    flash_stm32_parser.set_defaults(func=lambda args: faultier_stm32_flash(args.file))

    # Parse arguments and check for subcommand
    args = parser.parse_args()

    # Show help if no subcommand was provided
    if args.mode == "nrf52" and args.command is None:
        nrf_parser.print_help()
        sys.exit(1)
    elif args.mode == "stm32" and args.command is None:
        stm32_parser.print_help()
        sys.exit(1)

    # Call the function assigned to the subcommand
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()