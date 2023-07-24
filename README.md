# epson_print_conf
Epson Printer Configuration accessed via SNMP (TCP/IP)

## Installation

```
git clone https://github.com/Ircama/epson_print_conf
pip3 install easysnmp
cd epson_print_conf
```

## Usage

```
usage: epson_print_conf.py [-h] -m MODEL -a HOSTNAME [-i] [--reset_waste_ink] [--brute-force-read-key] [-d]
                           [--dry-run] [--write-first-ti-received-time FTRT FTRT FTRT]

optional arguments:
  -h, --help            show this help message and exit
  -m MODEL, --model MODEL
                        Printer model. Example: -m XP-205 (use ? to print all supported models)
  -a HOSTNAME, --address HOSTNAME
                        Printer host name or IP address. Example: -m 192.168.1.87
  -i, --info            Print information and statistics
  --reset_waste_ink     Reset all waste ink levels to 0
  --brute-force-read-key
                        Detect the read_key via brute force
  -d, --debug           Print debug information
  --dry-run             Dry-run change operations
  --write-first-ti-received-time FTRT FTRT FTRT
                        Change the first TI received time (year, month, day)

Epson Printer Configuration accessed via SNMP (TCP/IP)
```

Examples:

```
# Print informations
python3 epson_print_conf.py -m XP-205 -a 192.168.1.87 -i

# Reset all waste ink levels to 0
python3 epson_print_conf.py -m XP-205 -a 192.168.1.87 --reset_waste_ink

# Change the first TI received time to 25 December 2012
python3 epson_print_conf.py -m XP-205 -a 192.168.1.87 -d --write-first-ti-received-time 2012 12 25

# Detect the read_key via brute force
python3 epson_print_conf.py -m XP-205 -a 192.168.1.87 --brute-force-read-key
```

## API Interface

```python
import epson_print_conf
printer = epson_print_conf.EpsonPrinter("XP-205", "192.168.1.87")

stats = printer.stats
print("stats:", stats)

ret = printer.session.get_sys_info()
print("get_sys_info:", ret)
ret = printer.session.get_serial_number()
print("get_serial_number:", ret)
ret = printer.session.get_firmware_version()
print("get_firmware_version:", ret)
ret = printer.session.get_printer_head_id()
print("get_printer_head_id:", ret)
ret = printer.session.get_cartridges()
print("get_cartridges:", ret)
ret = printer.session.get_printer_status()
print("get_printer_status:", ret)
ret = printer.session.get_ink_replacement_counters()
print("get_ink_replacement_counters:", ret)
ret = printer.session.get_waste_ink_levels()
print("get_waste_ink_levels:", ret)
ret = printer.session.get_last_printer_fatal_errors()
print("get_last_printer_fatal_errors:", ret)
ret = printer.session.get_stats()
print("get_stats:", ret)

printer.session.reset_waste_ink_levels()
printer.session.brute_force_read_key()
printer.session.write_first_ti_received_time(2000, 1, 2)
```

### Exceptions

```
TimeoutError
ValueError
```

## Resources

### snmpget

Installation:

```
sudo apt-get install snmp
```

Usage:

```
# Read address 173.0
snmpget -v1 -d -c public 192.168.1.87 1.3.6.1.4.1.1248.1.2.2.44.1.1.2.1.124.124.7.0.25.7.65.190.160.173.0

# Read address 172.0
snmpget -v1 -d -c public 192.168.1.87 1.3.6.1.4.1.1248.1.2.2.44.1.1.2.1.124.124.7.0.25.7.65.190.160.172.0

# Write 25 to address 173.0
snmpget -v1 -d -c public 192.168.1.87 1.3.6.1.4.1.1248.1.2.2.44.1.1.2.1.124.124.16.0.25.7.66.189.33.173.0.25.88.98.108.98.117.112.99.106

# Write 153 to address 172.0
snmpget -v1 -d -c public 192.168.1.87 1.3.6.1.4.1.1248.1.2.2.44.1.1.2.1.124.124.16.0.25.7.66.189.33.172.0.153.88.98.108.98.117.112.99.106
```

### Other resources

epson-printer-snmp: https://github.com/Zedeldi/epson-printer-snmp

ReInkPy: https://codeberg.org/atufi/reinkpy/

ReInk: https://github.com/lion-simba/reink (especially https://github.com/lion-simba/reink/issues/1)

reink-net: https://github.com/gentu/reink-net

epson-l4160-ink-waste-resetter: https://github.com/nicootto/epson-l4160-ink-waste-resetter

emanage x900: https://github.com/abrasive/x900-otsakupuhastajat/

### Not used resources

Use at your risk.

WICreset: https://wic-reset.com / https://www.2manuals.com / https://resetters.com

The key, trial, can be used to reset your counters to 80%. After packet sniffing with wireshark, the correct OIDs can be found
This application also stores a log containing SNMP information at ~/.wicreset/application.log

Printhelp: https://printhelp.info/
