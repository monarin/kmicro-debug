# cb_dld_event Module

This module contains debugging files for the `cb_dld_event` callback and pulseId regression detection. It processes DLD (Delay Line Detector) event data and identifies corrupted pulse IDs.

---

## 📚 Files
- `user_callbacks_pipe.cc` – Main C++ file to process pulse IDs and report inconsistencies.
- `Makefile` – Build instructions for the module.
- `config/tdc_gpx2.ini` – Required configuration file for TDC initialization.

---

## 🚀 Build and Run

### 1. Build the Module
```bash
# Navigate to the cb_dld_event directory
cd cb_dld_event

# Build the application
make
```

### 2. Run the Application
```bash
# Run the compiled application
./user_callbacks_pipe
```

### 3. Clean Up Build Files
```bash
# Clean compiled binaries and object files
make clean
```

---

## 🛠️ Dependencies
- `scTDC` library (included in the `lib/` directory).
- Header files in the `include/` directory.

---

## 📊 Expected Output
- Interval event reports printed every 3 seconds.
- Corrupt event details if any pulseID regression is detected.

```
Interval 3s: 125.4321 kHz, Corrupt: 0 events (0.000000%)
Corrupt Event! Last PulseId: 1a2b3c4d, Current PulseId: 1a2b3bff, Difference: -256
Interval 6s: 124.9876 kHz, Corrupt: 1 events (0.000800%)
```

---

⚙️ Required Files in include/
To build user_callbacks_pipe.cc, you need the following header files in the include/ directory:

scTDC_cam.h
scTDC_cam_types.h
scTDC_cmos.h
scTDC_deprecated.h
scTDC_error_codes.h
scTDC.h
scTDC_types.h
These files can be obtained from the vendor, specifically:

tdc_drivers/scTDC1_centos7_lcls2_v1.3023.13

Once obtained, place them in the include/ directory:

kmicro-debug/
├── include/
│   ├── scTDC_cam.h
│   ├── scTDC_cam_types.h
│   ├── scTDC_cmos.h
│   ├── scTDC_deprecated.h
│   ├── scTDC_error_codes.h
│   ├── scTDC.h
│   └── scTDC_types.h

📚 Required Files in lib/
To link the application correctly, the following shared libraries should be placed in the lib/ directory:

libscDeviceClass45.so
libscDeviceClass45.so.0
libscDeviceClass45.so.0.4
libscDeviceClass45.so.0.4.6
libscTDC.so
libscTDC.so.1
libscTDC.so.1.3023
libscTDC.so.1.3023.13
These files can be obtained from:

tdc_drivers/scTDC1_centos7_lcls2_v1.3023.13

tdc_drivers/scTDC1_devclass45_centos7_lcls2_v1.3023.13

Once obtained, place them in the lib/ directory:

kmicro-debug/
├── lib/
│   ├── libscDeviceClass45.so
│   ├── libscDeviceClass45.so.0
│   ├── libscDeviceClass45.so.0.4
│   ├── libscDeviceClass45.so.0.4.6
│   ├── libscTDC.so
│   ├── libscTDC.so.1
│   ├── libscTDC.so.1.3023
│   └── libscTDC.so.1.3023.13

## 📄 Notes
- Ensure that the required `.so` libraries are in the `lib/` directory.
- You may need to set the `LD_LIBRARY_PATH` if using dynamically linked libraries:
```bash
LD_LIBRARY_PATH=../lib ./user_callbacks_pipe
```
- This application should be **run on the data node connected to the TDC unit** for accurate results.


