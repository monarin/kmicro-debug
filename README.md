# KMicro Debug

This repository contains debugging tools and utilities for KMicroscope modules. It is designed to analyze pulseID regressions, configure electron event generator devices, and verify the performance of event data processing.

---

## �� Modules and Utilities

### 1. [`cb_dld_event/`](./cb_dld_event/)
- Debugging for the `cb_dld_event` callback and pulseID regression.
- Contains `user_callbacks_pipe.cc` for processing event data and checking for pulseID inconsistencies.
- Includes a `Makefile` to build and run the application.

### 2. [`python/`](./python/)
- Python scripts for analyzing and configuring the KMicroscope system.
- `pulseid_regression_checker.py` reads and checks `bulk.txt` for pulseID regressions.
- `set_generators.py` configures the electron event generator via USB connection.

### 3. [`docs/`](./docs/)
- Documentation related to the architecture and functionality of the system.
- Contains `architecture.md` and module-specific documentation.

### 4. [`data/`](./data/)
- Stores input/output data used in analysis and configuration.
- Contains `bulk.txt` and other data generated by or used in the system.

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/kmicro-debug.git
cd kmicro-debug
```

### 2. Build and Run C++ Module
```bash
cd cb_dld_event
make
./user_callbacks_pipe
```

### 3. Run Python Analysis and Configuration
```bash
cd python
# Analyze pulse ID regressions
python3 pulseid_regression_checker.py ../data/bulk.txt

# Configure electron event generator
python3 set_generators.py --num 5
```

---

## 📄 Directory Structure
```
kmicro-debug/
├── cb_dld_event/            # Debugging files for cb_dld_event callback
├── common/                 # Shared utilities and headers
├── include/                # Header files for external libraries
├── lib/                    # Compiled and external libraries
├── python/                 # Python scripts for analysis and configuration
├── data/                   # Input/output data used for analysis
├── docs/                   # Documentation and architecture overview
├── LICENSE                 # License information
├── CONTRIBUTING.md         # Guidelines for contributing
└── README.md                # Main project documentation
```

---

## 📄 License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🤝 Contributing
We welcome contributions! Please refer to [`CONTRIBUTING.md`](./CONTRIBUTING.md) for guidelines on how to get involved.


