import PulseIdReceiver
import time

# connect to the TDC"
#r = PulseIdReceivereceiver.PulseIdReceiver('sc_ml_xvc_24')
#r = PulseIdReceivereceiver.PulseIdReceiver('10.0.3.100')
# MONA:
receiver = PulseIdReceiver.PulseIdReceiver('192.168.0.150')

# Define custom register addresses (from TimingFrameRx.yaml)
ADDR_RX_DEC_ERR_COUNT = 0x00000090
ADDR_RX_DSP_ERR_COUNT = 0x00000094

# Extend receiver with methods to read those registers
def countRxDecErr(self):
    return self.read(ADDR_RX_DEC_ERR_COUNT)

def countRxDspErr(self):
    return self.read(ADDR_RX_DSP_ERR_COUNT)

# Dynamically bind methods to receiver instance
import types
receiver.countRxDecErr = types.MethodType(countRxDecErr, receiver)
receiver.countRxDspErr = types.MethodType(countRxDspErr, receiver)

# enable the start signal
receiver.enable()

def printCounters():
    receiver.disable()
    receiver.resetCounters()

    receiver.enable()
    time.sleep(1.0)
    receiver.disable()
    print("L0 Counter      : " + str(receiver.countL0()))
    print("Accepted L1     : " + str(receiver.countL1Accepted()))
    print("Rejected L1     : " + str(receiver.countL1Rejected()))
    print("Transition      : " + str(receiver.countTransition()))
    print("Valid           : " + str(receiver.countValid()))
    print("Trigger         : " + str(receiver.countTrigger()))
    print("Partition Addr  : " + str(receiver.partitionAddr()))
    print("Partition Word0 : " + str(receiver.partitionWord0()))
    print("Pause to trig   : " + str(receiver.pauseToTrig()))
    print("notPauseToTrig  : " + str(receiver.notPauseToTrig()))
    print("RxDecErrCount   : " + str(receiver.countRxDecErr()))
    print("RxDspErrCount   : " + str(receiver.countRxDspErr()))

    print("Ratio Valid / Accepted: " + str(receiver.countValid() / receiver.countL1Accepted()))
    receiver.enable()

def monitorCounters(interval_sec=1.0):
    start_date = time.strftime('%Y-%m-%d')
    start_time = time.strftime('%H:%M:%S')
    print(f"\nMonitoring TDC counters — Start Date: {start_date}  Time: {start_time}")
    print(f"{'Time':>8} | {'L0':>10} | {'L1 Accept':>10} | {'L1 Reject':>10} | {'RxDecErr':>10} | {'RxDspErr':>10}")
    print("-" * 70)
    try:
        while True:
            now = time.strftime('%H:%M:%S')
            l0 = receiver.countL0()
            l1a = receiver.countL1Accepted()
            l1r = receiver.countL1Rejected()
            dec_err = receiver.countRxDecErr()
            dsp_err = receiver.countRxDspErr()
            print(f"{now:>8} | {l0:10d} | {l1a:10d} | {l1r:10d} | {dec_err:10d} | {dsp_err:10d}")
            time.sleep(interval_sec)
    except KeyboardInterrupt:
            print("\nMonitoring stopped.")

# Print all counters
printCounters()
monitorCounters(interval_sec=1.0)

# get the limit of the FIFO (in kB, where the pause signal is activated)
receiver.get_fifo_limit()

# Get the max. fifo watermark since the last reset
receiver.get_fifo_max()

