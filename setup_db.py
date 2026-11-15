import sqlite3

def init_db():
    conn = sqlite3.connect("hardware_errors.db")
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS error_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            board TEXT NOT NULL,
            error_code TEXT,
            error_message TEXT NOT NULL,
            meaning TEXT NOT NULL,
            possible_reasons TEXT NOT NULL,
            alternatives TEXT NOT NULL
        )
    ''')
    
    sample_errors = [
        (
            "NVIDIA Jetson Nano", 
            "CUDA_ERROR_OUT_OF_MEMORY", 
            "out of memory / failed to allocate device memory",
            "The GPU memory is saturated during inference or model initialization.",
            "1. SWAP memory not configured or exhausted.\n2. Model batch size too large.\n3. Memory leak in background process.",
            "1. Increase SWAP file size (e.g., 4GB swapfile).\n2. Reduce YOLO image resolution.\n3. Run `sudo jetson_clocks` and clear memory cache."
        ),
        (
            "NVIDIA Jetson Nano", 
            "TEGRA_POWER_DROOP", 
            "System throttle / sudden shutdown under load",
            "Input supply voltage dropped below minimum threshold during GPU/CPU spike.",
            "1. Using a weak 5V/2A Micro-USB adapter instead of 5V/4A DC Barrel jack.\n2. Thin power cables causing high resistance drop.",
            "1. Switch jumper pin to enable 5V/4A DC Barrel Jack power.\n2. Set power mode to 5W mode (`nvpmodel -m 1`)."
        ),
        (
            "Raspberry Pi / Embedded Board", 
            "UNDERVOLTAGE_WARNING", 
            "Under-voltage detected! (Yellow Lightning Bolt icon)",
            "Power rail voltage dropped below 4.63V threshold.",
            "1. Inadequate power supply/charger.\n2. High current draw from connected USB peripherals.\n3. Poor quality USB cable.",
            "1. Use an official 5.1V 3A power supply.\n2. Use a powered USB hub for external peripherals."
        ),
        (
            "Generic PCB / Microcontroller", 
            "ERR_SHORT_CIRCUIT_BROWNOUT", 
            "Brown-out Reset (BOR) triggered / unexpected reset",
            "Microcontroller supply voltage fell below brownout threshold, resetting CPU to prevent memory corruption.",
            "1. Physical trace bridge or short circuit on 3.3V/5V bus.\n2. Excessive current drawn by external components.\n3. Damaged decoupling capacitors.",
            "1. Inspect trace isolation around power regulators.\n2. Check resistance across VCC and GND using a multimeter.\n3. Replace blown smoothing capacitors."
        ),
        (
            "ESP32 / Embedded Wireless", 
            "FLASH_READ_ERR", 
            "rst:0x10 (RTCWDT_RTC_RESET),boot:0x13 (SPI_FAST_FLASH_BOOT)",
            "CPU failing to read instruction headers from external SPI Flash memory during boot.",
            "1. Damaged or cold-solder joint on SPI Flash IC pins.\n2. Corrupted flash partition table.",
            "1. Reflow flash memory IC pins using a hot air station.\n2. Re-flash partition table via esptool."
        )
    ]
    
    cursor.executemany('''
        INSERT INTO error_logs (board, error_code, error_message, meaning, possible_reasons, alternatives)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', sample_errors)
    
    conn.commit()
    conn.close()
    print("Database created successfully! File: hardware_errors.db")

if __name__ == "__main__":
    init_db()