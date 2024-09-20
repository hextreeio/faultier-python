import serial
import serial.tools.list_ports
import platform
import subprocess
import sys
import plotly.graph_objs as go
from IPython.display import display
from .faultier_pb2 import *
import struct
import subprocess
import os

# Get the directory of the current module
MODULE_DIR = os.path.dirname(os.path.realpath(__file__))

def convert_uint8_samples(input: bytes):
    r = []
    for b in input:
        r.append(b/255)
    return r
"""
    This class is used to control the Faultier.

    All functionality that configures the ADC or the glitcher
    require opening the device first, the OpenOCD debug probe
    is always active and does not use the serial interface.
    Because of this the functions using OpenOCD (such as nrf_flash_and_lock)
    are marked as static and can be called without initializing
    the Faultier first.
"""
class Faultier:
    """
    :param path: The path to the serial device. Note that the Faultier exposes
                 two serial devices - the first one is the control channel.
                 
                 On mac this will be /dev/cu.usbmodemfaultier1.
    """

    VID = "2b3e"
    PID = "2343"

    def __init__(self, path = None):
        """
        """
        if path:
            self.device = serial.Serial(path)
        else:
            path = self._find_serial_port()
            if not path:
                raise Exception("No suitable serial port found.")
            self.device = serial.Serial(path)
        self.device.timeout = 5

        # Send hello command to get protocol version from Faultier
        hello = CommandHello()
        cmd = Command()
        cmd.hello.CopyFrom(hello)
        self._send_protobuf(cmd)
        response = self._check_response()
        if response.hello.version != FAULTIER_VERSION:
            self.device.close()
            raise ValueError(f"Invalid Faultier version: Locally: {FAULTIER_VERSION} - Device: {response.hello.version}")
        
        self.default_settings()
    
    def get_serial_path(self):
        """
        The Faultier comes up as two serial ports. The first one is the control channel,
        and the second one is the UART bridge onto the 20-pin connector.
        This function returns the path to the second serial port.
        """
        return self._find_serial_port(index=1)

    def _find_serial_port(self, index = 0):
        system = platform.system()
        if system == "Windows":
            return self._find_serial_port_windows(index)
        elif system == "Darwin":  # macOS
            return self._find_serial_port_macos(index)
        elif system == "Linux":
            return self._find_serial_port_linux(index)
        else:
            raise Exception(f"Unsupported platform: {system}")
    
    def _find_serial_port_windows(self, index = 0):
        i = 0
        for port in serial.tools.list_ports.comports():
            if self.VID.lower() in port.hwid.lower() and self.PID.lower() in port.hwid.lower():
                if(i == index):
                    return port.device
                i += 1
        return None

    def _find_serial_port_macos(self, index = 0):
        i = 0
        ports = serial.tools.list_ports.comports()
        for port in ports:
            if f"USB VID:PID={self.VID.upper()}:{self.PID.upper()}" in port.hwid:
                if(i == index):
                    return port.device
                i += 1
        return None

    def _find_serial_port_linux(self, index = 0):
        if(index == 0):
            return "/dev/serial/by-id/usb-stacksmashing_Faultier_faultier-if00"
        if(index == 1):
            return "/dev/serial/by-id/usb-stacksmashing_Faultier_faultier-if03"
        return None

    def _read_response(self):
        header = self.device.read(4)
        if(header != b"FLTR"):
            print(header)
            raise ValueError(f"Invalid header received: {header}")
        length_data = self.device.read(4)
        length = struct.unpack("<I", length_data)[0]
        return self.device.read(length)

    def _check_response(self):
        response = self._read_response()
        resp = Response()
        resp.ParseFromString(response)
        if resp.WhichOneof('type') == 'error':
            raise ValueError("Error: " + resp.error.message)
        if resp.WhichOneof('type') == 'trigger_timeout':
            raise ValueError("Trigger timeout!")
        return resp

    def _check_ok(self):
        response = self._read_response()
        resp = Response()
        resp.ParseFromString(response)
        if resp.ok:
            return
        if resp.error:
            raise ValueError("Error: " + resp.error.message)
        else:
            raise ValueError("No OK or Error received.", resp)

    # def captureADC(self):
    #     # TODO will be replaced by command structure
    #     self.device.write(b"A")
    #     response = self._read_response()
    #     resp = ResponseADC()
    #     resp.ParseFromString(response)
    #     return convert_uint8_samples(resp.samples)
    
    def _send_protobuf(self, protobufobj):
        serialized = protobufobj.SerializeToString()
        length = len(serialized)
        # Header
        self.device.write(b"FLTR")
        self.device.write(struct.pack("<I", length))
        self.device.write(serialized)
        self.device.flush()

    def _get_default_settings(self):
        return CommandConfigureGlitcher(
                trigger_type = TRIGGER_NONE,
                trigger_source = TRIGGER_IN_NONE,
                glitch_output = OUT_NONE,
                delay = 0,
                pulse = 0,
                power_cycle_output = OUT_NONE,
                power_cycle_length = 0,
                trigger_pull_configuration = TRIGGER_PULL_NONE)

    def default_settings(self):
        """
        Reset the glitcher configuration to the default settings, namely: No trigger,
        no glitch or power-cycle output, delay and pulse to 0, and the pull-configuration
        of the trigger to none.
        """
        self.glitcher_configuration = self._get_default_settings()

    def configure_adc(self, source, sample_count):
        """
        Configures the ADC of the Faultier. The ADC is filled every-time
        that power_cycle() or glitch() is run and starts running after the
        trigger triggered (or immediately if no trigger is configured).

        :param source: The ADC channel to use

            - `ADC_CROWBAR`: Measure on the Crowbar pin (drain-side)
            - `ADC_MUX0`: Measure on the MUX0 pin
            - `ADX_EXT1`: Measure on the EXT1 pin

        :param sample_count: The number of ADC samples to collect. Maximum is 30000.
        """

        if sample_count > 30000:
            raise ValueError(f"Sample count must be under 30000. Provided {sample_count}.")
        configure_adc = CommandConfigureADC(
            source = source,
            sample_count = sample_count
        )
        cmd = Command()
        cmd.configure_adc.CopyFrom(configure_adc)
        self._send_protobuf(cmd)
        self._check_ok()

    def configure_glitcher(self, trigger_type = None, trigger_source = None, glitch_output = None, delay = None, pulse = None, power_cycle_length= None, power_cycle_output = None, trigger_pull_configuration = None):
        """
        Configures the glitcher, i.e. glitch-output, delay, pulse, etc. It does not Arm
        or cause any other change to IOs until glitch() is called.

        :param delay: The delay between Trigger and Glitch.

        :param pulse: The glitch pulse length.

        :param trigger_type: The type of trigger that should be used

            - `TRIGGER_NONE`: No Trigger. The glitch will wait the delay and then glitch.
            - `TRIGGER_LOW`: Waits for the signal to be low. If the signal is low to begin with this will trigger immediately.
            - `TRIGGER_HIGH`: Waits for the signal to be high. If the signal is low to begin with this will trigger immediately.
            - `TRIGGER_RISING_EDGE`: Waits for a rising edge on the trigger input.
            - `TRIGGER_FALLING_EDGE`: Waits for a falling edge on the trigger input.
            - `TRIGGER_PULSE_POSITIVE`: Wait for a positive pulse on the trigger input.
            - `TRIGGER_PULSE_NEGATIVE`: Wait for a negative pulse on the trigger input.
        
        :param trigger_source: The source - as in physical input - of the trigger.

            - `TRIGGER_IN_NONE`: Ignored, use TRIGGER_NONE to disable triggering.
            - `TRIGGER_IN_EXT0`: Configure EXT0 as digital input and use it for triggering.
            - `TRIGGER_IN_EXT1`: Configure EXT1 as digital input and use it for triggering.

        :param trigger_pulls: The pull up/down configuration of the trigger.

            - `TRIGGER_PULL_NONE`: No pulls applied (default)
            - `TRIGGER_PULL_UP`: Pull-up
            - `TRIGGER_PULL_DOWN`: Pull-down

        :param glitch_output: The glitch-output that will be used.

            - `OUT_CROWBAR`: Route the glitch to the gate of the Crowbar MOSFET.
            - `OUT_MUX0`: Route the glitch to control channel 0/X of the analogue switch (the one exposed on the SMA connector).
            - `OUT_MUX1`: Route the glitch to channel 1/Y of the analogue switch (exposed on 20-pin header).
            - `OUT_MUX2`: Route the glitch to channel 2/Z of the analogue switch (exposed on 20-pin header).
            - `OUT_EXT0`: Route the glitch signal to the EXT0 header. Useful to trigger external tools such as a ChipSHOUTER or laser.
            - `OUT_EXT1`: Route the glitch signal to the EXT1 header. Same as above.
            - `OUT_NONE`: Disable glitch generation. Power-cycle, trigger, ADC & co will still run as regular. Good for trigger testing.

        :param power_cycle: Whether a separate output should be toggled before activating the trigger-delay-glitch pipeline. Useful to restart a target.

            - `OUT_CROWBAR`: Route the power-cycle to the gate of the Crowbar MOSFET.
            - `OUT_MUX0`: Route the power-cycle to control channel 0/X of the analogue switch (the one exposed on the SMA connector).
            - `OUT_MUX1`: Route the power-cycle to channel 1/Y of the analogue switch (exposed on 20-pin header).
            - `OUT_MUX2`: Route the power-cycle to channel 2/Z of the analogue switch (exposed on 20-pin header).
            - `OUT_EXT0`: Route the power-cycle signal to the EXT0 header. Useful to trigger external tools such as a ChipSHOUTER or laser.
            - `OUT_EXT1`: Route the power-cycle signal to the EXT1 header. Same as above.
            - `OUT_NONE`: Disable power-cycle generation.

        :param power_cycle_length: The number of clock-cycles for the power cycle.
        """


        if trigger_type is not None:
            self.glitcher_configuration.trigger_type = trigger_type
        
        if trigger_source is not None:
            self.glitcher_configuration.trigger_source = trigger_source
        
        if glitch_output is not None:
            self.glitcher_configuration.glitch_output = glitch_output
        
        if delay is not None:
            self.glitcher_configuration.delay = delay
        
        if pulse is not None:
            self.glitcher_configuration.pulse = pulse
        
        if power_cycle_length is not None:
            self.glitcher_configuration.power_cycle_length = power_cycle_length
        
        if power_cycle_output is not None:
            self.glitcher_configuration.power_cycle_output = power_cycle_output
        
        if trigger_pull_configuration is not None:
            self.glitcher_configuration.trigger_pull_configuration = trigger_pull_configuration

    def _send_configuration(self, config = None):
        cmd = Command()
        if config:
            cmd.configure_glitcher.CopyFrom(config)
        else:    
            cmd.configure_glitcher.CopyFrom(self.glitcher_configuration)
        self._send_protobuf(cmd)
        self._check_ok()

    def glitch(self, delay = None, pulse = None):
        """
        Perform a glitch. Namely power-cycles (if enabled), then waits for a
        trigger (if configured), then waits for delay-cycles, and then enables
        the configured glitch-output (if any) for pulse-cycles.

        :param delay: Delay between trigger and glitch

        :param pulse: Pulse length for the glitch
        """

        if delay != None:
            self.glitcher_configuration.delay = delay
        if pulse != None:
            self.glitcher_configuration.pulse = pulse
        self._glitch()

    def _glitch(self):
        self._send_configuration()

        cmd = Command()
        cmd.glitch.CopyFrom(CommandGlitch())
        self._send_protobuf(cmd)
        self._check_response()

    def glitch_non_blocking(self):
        """
        A non-blocking version of the glitch function. Allows to arm a glitch
        but then still run Python code. Useful for example if your trigger is based
        on another piece of code (i.e. starting a debugger transaction or sending
        something via UART.)

        You MUST call `glitch_check_non_blocking_response` for each glitch_non_blocking
        call, otherwise the communication between the host and the Faultier will desync.
        """
        cmd = Command()
        cmd.configure_glitcher.CopyFrom(self.glitcher_configuration)
        self._send_protobuf(cmd)
        self._check_ok()

        cmd = Command()
        cmd.glitch.CopyFrom(CommandGlitch())
        self._send_protobuf(cmd)
    
    def glitch_check_non_blocking_response(self):
        """
        Reads the response for a non-blocking glitch from the Faultier. This function will
        then cause the error-exceptions such as TriggerTimeout etc.
        """
        self._check_response()

    def swd_check(self):
        """
        Uses the Program header to very quickly check whether an SWD device
        can be found. Useful when for example checking whether a glitch re-enabled
        SWD such as on the STM32 RDP2 to RDP1 glitch.
        """
        cmd = Command()
        cmd.swd_check.CopyFrom(CommandSWDCheck(function = SWD_CHECK_ENABLED))
        self._send_protobuf(cmd)
        response = self._check_response()
        return response.swd_check.enabled

    def nrf52_check(self):
        """
        nRF52 specific check to see whether APPROTECT is disabled/flash can be read.
        """
        cmd = Command()
        cmd.swd_check.CopyFrom(CommandSWDCheck(function = SWD_CHECK_NRF52))
        self._send_protobuf(cmd)
        try:
            response = self._check_response()
        except:
            # TODO check for debug errors only
            return False
            pass
        return response.swd_check.enabled

    def power_cycle(self, power_cycle_length=None, power_cycle_output=None):
        """
        Power-cycles the target.

        Implementation-wise this actually causes a full glitch to be run, but with
        trigger, delay, pulse, and glitch-output disabled. This means that a power-cycle
        will also fill the ADC.

        power_cycle_length and power_cycle_output are taken from the glitcher configuration by default, if not overriden.

        :param power_cycle: Output to toggle the powercycle. If not provided, this will be the value supplied during configure_glitcher().

            - `OUT_CROWBAR`: Route the power-cycle to the gate of the Crowbar MOSFET.
            - `OUT_MUX0`: Route the power-cycle to control channel 0/X of the analogue switch (the one exposed on the SMA connector).
            - `OUT_MUX1`: Route the power-cycle to channel 1/Y of the analogue switch (exposed on 20-pin header).
            - `OUT_MUX2`: Route the power-cycle to channel 2/Z of the analogue switch (exposed on 20-pin header).
            - `OUT_EXT0`: Route the power-cycle signal to the EXT0 header. Useful to trigger external tools such as a ChipSHOUTER or laser.
            - `OUT_EXT1`: Route the power-cycle signal to the EXT1 header. Same as above.
            - `OUT_NONE`: Disable power-cycle generation.

        :param power_cycle_length: The number of clock-cycles for the power cycle. If not provided, this will be the value supplied during configure_glitcher().
        """
        config = self._get_default_settings()
        config.power_cycle_output = self.glitcher_configuration.power_cycle_output if power_cycle_length is None else power_cycle_length
        config.power_cycle_length = self.glitcher_configuration.power_cycle_length if power_cycle_output is None else power_cycle_output
        self._send_configuration(config)

        cmd = Command()
        cmd.glitch.CopyFrom(CommandGlitch())
        self._send_protobuf(cmd)
        self._check_response()

    def read_adc(self):
        """
        Receives the current ADC sample-buffer from the device.
        """
        cmd = Command()
        cmd.read_adc.CopyFrom(CommandReadADC())
        self._send_protobuf(cmd)
        response = self._check_response()
        return convert_uint8_samples(response.adc.samples)

    # @staticmethod
    # def nrf_flash_and_lock():
    #     Faultier.nrf_unlock()
    #     print("Programming softdevice...")
        
    #     subprocess.run([
    #         "openocd", "-s", "/usr/local/share/openocd",
    #         "-f", "interface/tamarin.cfg",
    #         "-f", "target/nrf52.cfg",
    #         "-c", f"program {os.path.join(MODULE_DIR, 'example_firmware', 's132_nrf52_7.2.0_softdevice.hex')}; exit"
    #         ])
    #     print("Programming firmware...")
    #     subprocess.run([
    #         "openocd", "-f", "interface/tamarin.cfg", "-f", "target/nrf52.cfg",
    #         "-c", f"program {os.path.join(MODULE_DIR, 'example_firmware', 'nrf52832_xxaa.hex')}; exit"
    #     ])
    #     print("Locking chip...")
    #     Faultier.nrf_lock()

    @staticmethod
    def flash_nrf(path):
        """
        Flashes a connect nRF52 with the provided firmware. Requires OpenOCD to be in path.
        """
        print("Flashing nRF...")
        if not os.path.isfile(path):
            raise Exception(f"File {path} not found.")
        cmd = [
            "openocd",
            "-f", "interface/tamarin.cfg",
            "-f", "target/nrf52.cfg",
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


    @staticmethod
    def lock_and_flash_nrf(path):
        """
        Flashes and then APPROTECT-locks a connected nRF52 with the provided firmware.
        Requires OpenOCD to be in path.
        """
        print("Flashing nRF...")
        if not os.path.isfile(path):
            raise Exception(f"File {path} not found.")
        cmd = [
            "openocd",
            "-f", "interface/tamarin.cfg",
            "-f", "target/nrf52.cfg",
            "-c", f"init; nrf52_recover; program {path} verify;  flash fillw 0x10001208 0xFFFFFF00 0x01; reset; exit"
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


    @staticmethod
    def check_nrf_lock():
        """
        Checks whether the connected device has APPROTECT enabled using OpenOCD.
        Similar to nrf52_check, but much slower and using OpenOCD.
        """
        cmd = [
            "openocd",
            "-f", "interface/tamarin.cfg",
            "-f", "target/nrf52.cfg",
            "-c", f"init; exit"
            ]
        try:
            result = subprocess.run(cmd, check=True, text=True, capture_output=True)
            nrf_msg = "nRF52 device has AP lock engaged"
            if nrf_msg in result.stdout or nrf_msg in result.stderr:
                return True
            else:
                return False
        except subprocess.CalledProcessError as e:
            raise Exception("Failed to check locking status: " + e.stdout + e.stderr)

    @staticmethod
    def lock_nrf():
        """
        Locks the connect nRF52 using APPROTECT. Requires OpenOCD.
        """
        print("Locking nRF...")
        cmd = [
            "openocd",
            "-f", "interface/tamarin.cfg",
            "-f", "target/nrf52.cfg",
            "-c", f"init; flash fillw 0x10001208 0xFFFFFF00 0x01; reset; exit"
            ]
        try:
            result = subprocess.run(cmd, check=True, text=True, capture_output=True)
            print("Chip locked!")
        except subprocess.CalledProcessError as e:
            print("Error during locking process:", e)
            print("Output:", e.stdout)
            print("Errors:", e.stderr)


    @staticmethod
    def unlock_nrf():
        """
        Unlocks the connect nRF52 by running nrf52_recover in OpenOCD.
        """
        print("Unlocking nRF...")
        cmd = [
            "openocd",
            "-f", "interface/tamarin.cfg",
            "-f", "target/nrf52.cfg",
            "-c", f"init; nrf52_recover; exit"
            ]
        try:
            result = subprocess.run(cmd, check=True, text=True, capture_output=True)
            print("Chip unlocked!")
        except subprocess.CalledProcessError as e:
            print("Error during locking process:", e)
            print("Output:", e.stdout)
            print("Errors:", e.stderr)


    @staticmethod
    def nrf_flash():
        Faultier.nrf_unlock()
        print("Programming softdevice...")
        
        subprocess.run([
            "openocd", "-s", "/usr/local/share/openocd",
            "-f", "interface/tamarin.cfg",
            "-f", "target/nrf52.cfg",
            "-c", f"program {os.path.join(MODULE_DIR, 'example_firmware', 's132_nrf52_7.2.0_softdevice.hex')}; exit"
            ])
        print("Programming firmware...")
        subprocess.run([
            "openocd", "-f", "interface/tamarin.cfg", "-f", "target/nrf52.cfg",
            "-c", f"program {os.path.join(MODULE_DIR, 'example_firmware', 'nrf52832_xxaa.hex')}; exit"
        ])

    @staticmethod
    def nrf_lock():
        subprocess.run(["openocd", "-f", "interface/tamarin.cfg", "-f", "target/nrf52.cfg", "-c", "init; reset; halt; flash fillw 0x10001208 0xFFFFFF00 0x01; reset;exit"])

    @staticmethod
    def nrf_unlock():
        print("Unlocking...")
        subprocess.run(["openocd", "-s", "/usr/local/share/openocd", "-f", "interface/tamarin.cfg", "-f", "target/nrf52.cfg", "-c", "init; nrf52_recover; exit"])
        
    def stm32_lock(self):
        import time
        print("This action is not reversible. Locking in 10 seconds, press stop to interrupt.")
        time.sleep(10)
