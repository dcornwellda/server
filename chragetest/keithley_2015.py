"""
Keithley 2015 Multimeter Control via Serial Port
Supports SCPI commands for the Keithley 2015 DMM
"""

import serial
import time


class Keithley2015:
    """Class to control Keithley 2015 Multimeter via RS-232"""

    def __init__(self, port, baudrate=9600, timeout=2):
        """
        Initialize connection to Keithley 2015

        Args:
            port: Serial port (e.g., 'COM3' on Windows, '/dev/ttyUSB0' on Linux)
            baudrate: Baud rate (default 9600, check instrument settings)
            timeout: Read timeout in seconds
        """
        self.serial = serial.Serial(
            port=port,
            baudrate=baudrate,
            bytesize=serial.EIGHTBITS,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            timeout=timeout
        )
        time.sleep(0.5)  # Give instrument time to initialize

    def write(self, command):
        """Send command to instrument"""
        cmd = command.strip() + '\n'
        self.serial.write(cmd.encode('ascii'))
        time.sleep(0.1)  # Small delay for instrument processing

    def query(self, command):
        """Send command and read response"""
        self.write(command)
        response = self.serial.readline().decode('ascii').strip()
        return response

    def reset(self):
        """Reset instrument to default state"""
        self.write('*RST')
        time.sleep(1)

    def clear(self):
        """Clear status and error queue"""
        self.write('*CLS')

    def get_id(self):
        """Get instrument identification"""
        return self.query('*IDN?')

    def beep(self):
        """Make the instrument beep"""
        self.write('SYST:BEEP')

    # Configuration Methods
    def configure_dc_voltage(self, range_val='AUTO', resolution='DEF'):
        """
        Configure for DC voltage measurement

        Args:
            range_val: Measurement range (e.g., 0.1, 1, 10, 100, 1000, 'AUTO')
            resolution: Resolution (e.g., 0.0001, 'DEF', 'MIN', 'MAX')
        """
        if range_val == 'AUTO':
            self.write(f'CONF:VOLT:DC {resolution}')
            self.write('VOLT:DC:RANG:AUTO ON')
        else:
            self.write(f'CONF:VOLT:DC {range_val},{resolution}')

    def configure_ac_voltage(self, range_val='AUTO', resolution='DEF'):
        """Configure for AC voltage measurement"""
        if range_val == 'AUTO':
            self.write(f'CONF:VOLT:AC {resolution}')
            self.write('VOLT:AC:RANG:AUTO ON')
        else:
            self.write(f'CONF:VOLT:AC {range_val},{resolution}')

    def configure_dc_current(self, range_val='AUTO', resolution='DEF'):
        """Configure for DC current measurement"""
        if range_val == 'AUTO':
            self.write(f'CONF:CURR:DC {resolution}')
            self.write('CURR:DC:RANG:AUTO ON')
        else:
            self.write(f'CONF:CURR:DC {range_val},{resolution}')

    def configure_ac_current(self, range_val='AUTO', resolution='DEF'):
        """Configure for AC current measurement"""
        if range_val == 'AUTO':
            self.write(f'CONF:CURR:AC {resolution}')
            self.write('CURR:AC:RANG:AUTO ON')
        else:
            self.write(f'CONF:CURR:AC {range_val},{resolution}')

    def configure_resistance(self, range_val='AUTO', resolution='DEF'):
        """Configure for 2-wire resistance measurement"""
        if range_val == 'AUTO':
            self.write(f'CONF:RES {resolution}')
            self.write('RES:RANG:AUTO ON')
        else:
            self.write(f'CONF:RES {range_val},{resolution}')

    def configure_fresistance(self, range_val='AUTO', resolution='DEF'):
        """Configure for 4-wire resistance measurement"""
        if range_val == 'AUTO':
            self.write(f'CONF:FRES {resolution}')
            self.write('FRES:RANG:AUTO ON')
        else:
            self.write(f'CONF:FRES {range_val},{resolution}')

    def configure_frequency(self, range_val='AUTO'):
        """Configure for frequency measurement"""
        self.write('CONF:FREQ')

    def configure_period(self, range_val='AUTO'):
        """Configure for period measurement"""
        self.write('CONF:PER')

    # Measurement Methods
    def read(self):
        """
        Read a single measurement
        Returns the measurement as a float
        """
        response = self.query('READ?')
        try:
            return float(response)
        except ValueError:
            return response

    def fetch(self):
        """
        Fetch the last measurement without triggering a new one
        """
        response = self.query('FETC?')
        try:
            return float(response)
        except ValueError:
            return response

    def initiate(self):
        """Initiate a measurement"""
        self.write('INIT')

    # Trigger Methods
    def set_trigger_source(self, source='IMM'):
        """
        Set trigger source
        Args:
            source: 'IMM' (immediate), 'BUS', 'EXT' (external)
        """
        self.write(f'TRIG:SOUR {source}')

    def trigger(self):
        """Send software trigger (when trigger source is BUS)"""
        self.write('*TRG')

    # Display Methods
    def display_on(self):
        """Turn display on"""
        self.write('DISP ON')

    def display_off(self):
        """Turn display off (faster measurements)"""
        self.write('DISP OFF')

    def display_text(self, text):
        """
        Display custom text on instrument
        Args:
            text: Text to display (up to 12 characters)
        """
        self.write(f'DISP:TEXT "{text[:12]}"')

    def display_clear(self):
        """Clear custom text and return to normal display"""
        self.write('DISP:TEXT:CLE')

    # System Methods
    def get_error(self):
        """Get next error from error queue"""
        return self.query('SYST:ERR?')

    def check_errors(self):
        """Check and print all errors in queue"""
        errors = []
        while True:
            error = self.get_error()
            if error.startswith('0,'):
                break
            errors.append(error)
            print(f"Error: {error}")
        return errors

    def local(self):
        """Return instrument to local control"""
        self.write('SYST:LOC')

    def remote(self):
        """Set instrument to remote control"""
        self.write('SYST:REM')

    def close(self):
        """Close serial connection"""
        if self.serial.is_open:
            self.serial.close()

    def __enter__(self):
        """Context manager entry"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.close()


# Example usage
if __name__ == '__main__':
    # Configure your serial port here
    PORT = 'COM3'  # Change to your port (COM1, COM3, etc. on Windows)
    BAUDRATE = 9600  # Check your instrument settings (typical: 9600, 19200, 57600)

    try:
        # Connect to instrument using context manager
        with Keithley2015(PORT, BAUDRATE) as dmm:
            # Get instrument ID
            print("Connected to:", dmm.get_id())

            # Reset and clear
            dmm.reset()
            dmm.clear()

            # Make a beep to confirm connection
            dmm.beep()

            # Configure for DC voltage measurement
            print("\nConfiguring for DC voltage measurement...")
            dmm.configure_dc_voltage(range_val='AUTO')

            # Take 5 measurements
            print("\nTaking 5 DC voltage measurements:")
            for i in range(5):
                voltage = dmm.read()
                print(f"  Measurement {i+1}: {voltage} V")
                time.sleep(0.5)

            # Configure for resistance measurement
            print("\nConfiguring for resistance measurement...")
            dmm.configure_resistance(range_val='AUTO')

            # Take a resistance measurement
            resistance = dmm.read()
            print(f"Resistance: {resistance} Ohms")

            # Check for any errors
            print("\nChecking for errors...")
            errors = dmm.check_errors()
            if not errors:
                print("No errors!")

            # Return to local mode
            dmm.local()

    except serial.SerialException as e:
        print(f"Serial port error: {e}")
        print(f"\nMake sure:")
        print(f"  1. The instrument is connected to {PORT}")
        print(f"  2. The baud rate matches your instrument settings")
        print(f"  3. No other program is using the serial port")
    except Exception as e:
        print(f"Error: {e}")
