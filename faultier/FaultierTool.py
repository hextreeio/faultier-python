#!/usr/bin/env python
import sys
import os
import time
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

def _import_pyocd():
    try:
        import pyocd
    except:
        print("Please install PyOCD-Faultier by running: pip3 install pyocd-faultier")
        return
    

    
def faultier_nrf52_flash(file_path):
    """
    Flashes a connect nRF52 with the provided firmware.
    """
    _import_pyocd()
    from pyocd.core.helpers import ConnectHelper
    from pyocd.flash.file_programmer import FileProgrammer
    # print("Flashing nRF...")
    
    session = ConnectHelper.session_with_chosen_probe(unique_id="faultier", 
                                                    options=
                                                    {
                                                        "target_override":"nrf52832",
                                                        "auto_unlock": False,
                                                        "connect_mode": "attach"
                                                        })
    try:
        session.open()
    except KeyError as e:
        if "SoCTarget has no selected core" in str(e):
            print("Use 'faultier nrf52 unlock' to unlock the chip (this will erase the chip).")
            return
        raise e
    target = session.target
    FileProgrammer(session).program(file_path)
    target.reset()

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
        "-c", f"init; program {path} verify; reset; exit"
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

def faultier_nrf52_lock(file_path):
    """
    Flashes a connect nRF52 with the provided firmware.
    """
    _import_pyocd()
    from pyocd.core.helpers import ConnectHelper
    from pyocd.flash.file_programmer import FileProgrammer
    from pyocd.flash.loader import MemoryLoader
    print("Locking nRF...")
    session = ConnectHelper.session_with_chosen_probe(unique_id="faultier", 
                                                    options={"target_override":"nrf52832", "auto_unlock": False})
    session.open()
    target = session.target
    loader = MemoryLoader(session)
    loader.add_data(0x10001208, b"\x00\xFF\xFF\xFF")
    loader.commit()
    target.reset()

def faultier_nrf52_unlock(args=None):
    _import_pyocd()
    from pyocd.core.helpers import ConnectHelper
    from pyocd.flash.file_programmer import FileProgrammer
    # print("Flashing nRF...")
    
    session = ConnectHelper.session_with_chosen_probe(unique_id="faultier", 
                                                    options=
                                                    {
                                                        "target_override":"nrf52832",
                                                        "auto_unlock": True
                                                        })
    session.open()
    print("NRF unlocked.")

# def faultier_nrf52_flash(file_path):
#     print(f"Flashing nRF52 with {file_path}")
#     openocd_program("nrf52", file_path)

def faultier_stm32_test(args=None):
    print("Running STM32 test...")

def _stm32_rdp(rdp_value):
    _import_pyocd()
    from pyocd.core.helpers import ConnectHelper
    from pyocd.flash.file_programmer import FileProgrammer
    session = ConnectHelper.session_with_chosen_probe(
        unique_id="faultier", 
        options=
        {
            "target_override":"stm32f401xr"
        })

    session.open()
    target = session.target
    target.init()
    # Unlock flash control
    target.write32(0x40023C08, 0x08192A3B)
    target.write32(0x40023C08, 0x4C5D6E7F)
    target.write8(0x40023C15, rdp_value)
    target.write8(0x40023C14, 0xEE)
    time.sleep(0.2)
    # Lock flash control
    target.write8(0x40023C14, 0xED)

def faultier_stm32_rdp0(args=None):
    print("Unlocking STM32 to RDP0...")
    _stm32_rdp(0xAA)
    time.sleep(3)
    print("Done")

def faultier_stm32_rdp1(args=None):
    print("Locking STM32 to RDP1...")
    _stm32_rdp(0xBB)
    print("Done")

def faultier_stm32_rdp2(really):
    if really:
        print("Locking STM32 to RDP2...")
        _stm32_rdp(0xCC)
        print("Done")
    else:
        print("You must confirm RDP2 with --really flag.")

def faultier_stm32_flash(file_path):
    _import_pyocd()
    from pyocd.core.helpers import ConnectHelper
    from pyocd.flash.file_programmer import FileProgrammer
    # print("Flashing nRF...")
    
    session = ConnectHelper.session_with_chosen_probe(unique_id="faultier", 
                                                    options=
                                                    {
                                                        "target_override":"stm32f401xr",
                                                        })
    session.open()
    target = session.target
    FileProgrammer(session).program(file_path)
    target.reset()

def avg(values):
    total = 0.0
    for v in values:
        total += v
    return total/len(values)

def collect_adc(ft, adc, glitch_output):
    ft.configure_glitcher(
        trigger_type=faultier.TRIGGER_NONE,
        trigger_source=faultier.TRIGGER_IN_NONE,
        glitch_output=glitch_output,
        power_cycle_output=faultier.OUT_NONE,
        power_cycle_length=0,
        delay = 0,
        pulse = 2000*100
    )

    ft.configure_adc(
        source=adc,
        sample_count=1000
    )

    ft.glitch()
    return avg(ft.read_adc())

def faultier_test(args=None):
    print("Running test...")
    ft = faultier.Faultier()
    ft.configure_glitcher(
        trigger_type=faultier.TRIGGER_NONE,
        trigger_source=faultier.TRIGGER_IN_NONE,
        glitch_output=faultier.OUT_CROWBAR,
        power_cycle_output=faultier.OUT_MUX0,
        power_cycle_length=30000000,
        delay = 0,
        pulse = 30000000
    )
    ft.glitch()

    okay = True

    avg_cb_open = collect_adc(ft, faultier.ADC_CROWBAR, faultier.OUT_NONE)
    if avg_cb_open > 0.15 and avg_cb_open < 0.3:
        print(f"\tCrowbar open   OKAY")
    else:
        print(f"\tCrowbar open   NOT OKAY {avg_cb_open}")
        okay = False

    avg_cb_closed = collect_adc(ft, faultier.ADC_CROWBAR, faultier.OUT_CROWBAR)
    if avg_cb_closed < 0.05:
        print(f"\tCrowbar closed OKAY")
    else:
        print(f"\tCrowbar closed NOT OKAY {avg_cb_closed}")
        okay = False

    avg_mux_open = collect_adc(ft, faultier.ADC_MUX0, faultier.OUT_NONE)
    if avg_mux_open > 0.9:
        print(f"\tMUX0 open      OKAY")
    else:
        print(f"\tMUX0 open      NOT  OKAY {avg_mux_open} - Check if jumpers are connected")
        okay = False

    avg_mux_closed = collect_adc(ft, faultier.ADC_CROWBAR, faultier.OUT_CROWBAR)
    if avg_mux_closed < 0.05:
        print(f"\tMUX0 closed    OKAY")
    else:
        print(f"\tMUX0 closed    NOT OKAY {avg_mux_closed} - Check if jumpers are connected")
        okay = False
    
    if not okay:
        print("###############################")
        print("# Faultier self-check failed. #")
        print("###############################")


def faultier_visualize(args):
    print(f"Visualizing {args.file}")
    try:
        from .DashApp import visualize
    except:
        print("Please run: pip3 install 'dash>=2.14.0' 'plotly>=5.17.0' 'pandas>=2.0.0' 'dash-bootstrap-components>=1.5.0' 'numpy>=1.24.0'")
    visualize(args.file, debug=False)


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

    stm32_subparsers.add_parser("rdp0", help="Enable RDP0 (Will erase the chip)").set_defaults(func=faultier_stm32_rdp0)
    stm32_subparsers.add_parser("rdp1", help="Enable RDP1").set_defaults(func=faultier_stm32_rdp1)
    rdp2_parser = stm32_subparsers.add_parser("rdp2", help="Enable RDP2")
    rdp2_parser.add_argument("--really", action="store_true", help="Confirm enabling RDP2")
    rdp2_parser.set_defaults(func=lambda args: faultier_stm32_rdp2(args.really))

    flash_stm32_parser = stm32_subparsers.add_parser("flash", help="Flash STM32 with a file")
    flash_stm32_parser.add_argument("file", help="File path for flashing STM32")
    flash_stm32_parser.set_defaults(func=lambda args: faultier_stm32_flash(args.file))

    # Parse arguments and check for subcommand
    subparsers.add_parser("selfcheck", help="Run self test").set_defaults(func=faultier_test)

    visualize_parser = subparsers.add_parser("visualize", help="Visualize a glitching database")
    visualize_parser.set_defaults(func=faultier_visualize)
    visualize_parser.add_argument("file", help="File to visualize")

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