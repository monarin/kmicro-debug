import sys
import serial
from DldSimulator import DldSimulator, DldSimulatorException

# USB device detected with FTDI chip (0403:6010)
COMM_PORT = "/dev/ttyUSB0"  # Update if necessary

def get_current_generators(dld):
    """Get the current number of active spectrum generators."""
    try:
        current_num = dld.getActiveSpectrumGenerators()
        print(f"Current number of active spectrum generators: {current_num}")
        return current_num
    except DldSimulatorException as e:
        print(f"Error reading current number of generators: {e}")
        sys.exit(1)

def set_num_generators(num_of_generators):
    """Set the number of active spectrum generators."""
    try:
        # Create DldSimulator instance and connect to device
        dld = DldSimulator(COMM_PORT)
        print(f"Connected to {COMM_PORT}")

        # Get the current value
        current_num = get_current_generators(dld)

        # Ask the user if they want to update
        if num_of_generators == current_num:
            print(f"No change needed. {num_of_generators} generators are already active.")
        else:
            user_input = input(f"Do you want to update the number of generators to {num_of_generators}? (y/n): ").strip().lower()
            if user_input == "y":
                dld.setActiveSpectrumGenerators(num_of_generators)
                print(f"Successfully updated to {num_of_generators} active spectrum generators.")

                # Verify the update
                updated_num = get_current_generators(dld)
                if updated_num == num_of_generators:
                    print(f"Update verified: {updated_num} generators are active.")
                else:
                    print(f"Warning: The update did not apply correctly. Expected {num_of_generators}, but found {updated_num}.")
            else:
                print("Update aborted. No changes made.")

    except DldSimulatorException as e:
        print(f"Error: {e}")
    except serial.SerialException as e:
        print(f"Unable to connect to {COMM_PORT}. Check if the device is plugged in and accessible.")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        # Clean up and close connection
        try:
            del dld
            print("Connection closed successfully.")
        except:
            pass


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python set_generators.py <num_of_generators>")
        sys.exit(1)

    try:
        num_of_generators = int(sys.argv[1])
        if num_of_generators < 0 or num_of_generators > 32:
            raise ValueError("Number of generators must be between 0 and 32.")
        set_num_generators(num_of_generators)
    except ValueError as e:
        print(f"Invalid input: {e}")
        sys.exit(1)
