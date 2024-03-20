# !/usr/bin/env python3

from flask import Flask, render_template, send_from_directory
from waitress import serve

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# imports from modbus script
import argparse
import collections
import datetime
import json
import platform
import sys
import time
import minimalmodbus
# import serial  # enable if needed

app = Flask(__name__)
# app = Flask(__name__, static_url_path='/static')

# Set rate limiting to the Flask application (Server side limiting)
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["60 per minute"], # ["200 per day", "50 per hour"],
    storage_uri="memory://",
)

def getModbusData():
    # Parse command line arguments
    argparser = argparse.ArgumentParser(description='Read Modbus data from the Energy Meter and output them as JSON')
    argparser.add_argument('--metername', default='EASTRON_SDM630V2', help='Meter name in the JSON output attribute "meterName" (default EASTRON_SDM630V2)')
    argparser.add_argument('-b', dest='baud', type=int, default=9600, help='Baudrate for RS-485 communication (default 9600)')
    argparser.add_argument('-s', dest='serialport', default='COM6', help='Serial device name (default /dev/ttyAMA0)')
    argparser.add_argument('-a', dest='address', type=int, default=1, help='Address (RS-485 Node Address) of meter (default=1)')
    argparser.add_argument('-t', dest='metertype', default="EASTRON_SDM630V2", help='Type of Energy meter (default=EASTRON_SDM630V2)')
    # The store_true option has a default value of False, whereas store_false has a default of True.
    argparser.add_argument('-d', dest='debug', action='store_true', help="Debug connection")
    args = argparser.parse_args()

    # instrument = minimalmodbus.Instrument("COM6", 1, "rtu", True, True)
    instrument = minimalmodbus.Instrument(args.serialport, args.address, debug=args.debug)
    instrument.serial.baudrate = args.baud  # 9600 Baud default
    instrument.mode = minimalmodbus.MODE_RTU  # RTU or ASCII mode

    # Defaults - see documentation https://minimalmodbus.readthedocs.io/en/stable/usage.html:
    # instrument.serial.bytesize = 8
    # instrument.parity = serial.PARITY_NONE
    # instrument.serial.stopbits = 1
    # instrument.serial.timeout = 0.05  # seconds
    # instrument.address = args.address # this is the slave address number
    # instrument.clear_buffers_before_each_transaction = True
    # instrument.serial.parity = serial.PARITY_NONE  # PARITY_NONE, PARITY_EVEN, PARITY_ODD
    # alternatively to avoid the import of serial you can use:
    # instrument.serial.parity = minimalmodbus.serial.PARITY_NONE

    # in some cases (mostly on Windows) the serial port must be closed after each call. This will slow down the port considerably
    #instrument.close_port_after_each_call = False  # Default is False

    # To see which settings you are actually using: print(instrument)
    #print("\n" + str(instrument) + "\n")

    meter_database = {
        'EASTRON_SDM630V2': {
            'name': 'Eastron SDM630V2',
            'data_points': [
                # Modbus address is mapped to the 'Modbus Protocol Start Address Hex' column (Hi and Lo Bytes) per parameter
                {'modbus_addr': 0x00, 'name': 'L1_V', 'description': "L1 Line to Neutral (V)", 'type': 'float'},
                {'modbus_addr': 0x02, 'name': 'L2_V', 'description': "L2 Line to Neutral (V)", 'type': 'float'},
                {'modbus_addr': 0x04, 'name': 'L3_V', 'description': "L3 Line to Neutral (V)", 'type': 'float'},

                {'modbus_addr': 0x06, 'name': 'L1_A', 'description': "L1 Current (A)", 'type': 'float'},
                {'modbus_addr': 0x08, 'name': 'L2_A', 'description': "L2 Current (A)", 'type': 'float'},
                {'modbus_addr': 0x0A, 'name': 'L3_A', 'description': "L3 Current (A)", 'type': 'float'},
                # {'modbus_addr': 0xE0, 'name': 'N_A', 'description': "Neutral Current (A)", 'type': 'float'},

                {'modbus_addr': 0x0C, 'name': 'L1_W', 'description': "L1 Power (W)", 'type': 'float'},
                {'modbus_addr': 0x0E, 'name': 'L2_W', 'description': "L2 Power (W)", 'type': 'float'},
                {'modbus_addr': 0x10, 'name': 'L3_W', 'description': "L3 Power (W)", 'type': 'float'},
                {'modbus_addr': 0x34, 'name': 'Total_Sys_Power', 'description': "Total System Power (W)",
                 'type': 'float'},

                {'modbus_addr': 0x12, 'name': 'L1_VA', 'description': "L1 Volt Amps (VA)", 'type': 'float'},
                {'modbus_addr': 0x14, 'name': 'L2_VA', 'description': "L2 Volt Amps (VA)", 'type': 'float'},
                {'modbus_addr': 0x16, 'name': 'L3_VA', 'description': "L3 Volt Amps (VA)", 'type': 'float'},

                {'modbus_addr': 0x18, 'name': 'L1_VAr', 'description': "L1 Volt Amps Reactive (VAr)", 'type': 'float'},
                {'modbus_addr': 0x1A, 'name': 'L2_VAr', 'description': "L2 Volt Amps Reactive (VAr)", 'type': 'float'},
                {'modbus_addr': 0x1C, 'name': 'L3_VAr', 'description': "L3 Volt Amps Reactive (VAr)", 'type': 'float'},
                {'modbus_addr': 0x3C, 'name': 'Total_Sys_VAr', 'description': "Total System VAr (VAr)",
                 'type': 'float'},

                {'modbus_addr': 0x1E, 'name': 'L1_Power_Factor', 'description': "L1 Power Factor (-)", 'type': 'float'},
                {'modbus_addr': 0x20, 'name': 'L2_Power_Factor', 'description': "L2 Power Factor (-)", 'type': 'float'},
                {'modbus_addr': 0x22, 'name': 'L3_Power_Factor', 'description': "L3 Power Factor (-)", 'type': 'float'},
                {'modbus_addr': 0x3E, 'name': 'Total_System_Power_Factor',
                 'description': "Total System Power Factor (-)", 'type': 'float'},

                # \u00B0 is the unicode character for the degrees sign. We can also reference it by the charater's name which is easier to remember
                # {'modbus_addr': 0x24, 'name': 'L1_Phase_Angle', 'description': "L1 Phase Angle (\N{DEGREE SIGN})", 'type': 'float'},
                # {'modbus_addr': 0x26, 'name': 'L2_Phase_Angle', 'description': "L2 Phase Angle (\N{DEGREE SIGN})", 'type': 'float'},
                # {'modbus_addr': 0x28, 'name': 'L3_Phase_Angle', 'description': "L3 Phase Angle (\N{DEGREE SIGN})", 'type': 'float'},
                # {'modbus_addr': 0x42, 'name': 'Total_System_Phase_Angle', 'description': "Total System Phase Angle (\N{DEGREE SIGN})", 'type': 'float'},

                {'modbus_addr': 0x2A, 'name': 'Avg_L_N_Volts', 'description': "Average Line to Neutral Volts (V)", 'type': 'float'},
                {'modbus_addr': 0x3E, 'name': 'Avg_L_Current', 'description': "Average Line Current (A)", 'type': 'float'},
                {'modbus_addr': 0x30, 'name': 'Sum_L1L2L3_A', 'description': "Sum of Line currents (A)", 'type': 'float'},
                # modbus_addr:  0x34 implemented above
                {'modbus_addr': 0x38, 'name': 'Total_Sys_VA', 'description': "Total System Volt Amps (VA)", 'type': 'float'},

                {'modbus_addr': 0x46, 'name': 'LineFrequency_Hz', 'description': "Line frequency (Hz)", 'type': 'float'},

                {'modbus_addr': 0x48, 'name': 'EnergyImported_kWh', 'description': "Imported Energy since last reset (kWh)", 'type': 'float'},
                {'modbus_addr': 0x4A, 'name': 'EnergyExported_kWh', 'description': "Exported Energy since last reset (kWh)", 'type': 'float'},

                # {'modbus_addr': 0x4C, 'name': 'Import_VArh', 'description': "Import VArh since last reset (kVArh)", 'type': 'float'},
                # {'modbus_addr': 0x4E, 'name': 'Export_VArh', 'description': "Export VArh since last reset (kVArh)", 'type': 'float'},
                {'modbus_addr': 0x50, 'name': 'Export_VArh', 'description': "Export VArh since last reset (kVArh)", 'type': 'float'},
                {'modbus_addr': 0x52, 'name': 'Export_VArh', 'description': "Export VArh since last reset (kVArh)", 'type': 'float'},

                {'modbus_addr': 0x56, 'name': 'Max_Total_Sys_Power_Demand', 'description': "Maximum Total System Power Demand (VA)", 'type': 'float'},
                {'modbus_addr': 0x64, 'name': 'Total_System_VA_Demand', 'description': "Total System VA Demand (VA)", 'type': 'float'},
                {'modbus_addr': 0x66, 'name': 'Max_Total_Sys_VA_Demand', 'description': "Maximum Total System VA Demand (VA)", 'type': 'float'},
                {'modbus_addr': 0x68, 'name': 'Neutral_Current_Demand', 'description': "Neutral Current Demand (A)", 'type': 'float'},
                {'modbus_addr': 0x6A, 'name': 'Max_Neutral_Current', 'description': "Maximum Neutral Current (A)", 'type': 'float'},

                {'modbus_addr': 0xC8, 'name': 'L1L2_V', 'description': "L1 Line to L2 (V)", 'type': 'float'},
                {'modbus_addr': 0xCA, 'name': 'L2L3_V', 'description': "L2 Line to L3 (V)", 'type': 'float'},
                {'modbus_addr': 0xCC, 'name': 'L3L1_V', 'description': "L3 Line to L1 (V)", 'type': 'float'},

                {'modbus_addr': 0xCE, 'name': 'Avg_Line_Line_V', 'description': "Average Line to Line Volts (V)", 'type': 'float'},
                # modbus_addr:  0xE0 implemented above
                {'modbus_addr': 0xEA, 'name': 'L1_N_Volts_THD', 'description': "L1-N Volts THD (%)", 'type': 'float'},
                {'modbus_addr': 0xEC, 'name': 'L2_N_Volts_THD', 'description': "L2-N Volts THD (%)", 'type': 'float'},
                {'modbus_addr': 0xEE, 'name': 'L3_N_Volts_THD', 'description': "L3-N Volts THD (%)", 'type': 'float'},

                {'modbus_addr': 0xF0, 'name': 'L1_Current_THD', 'description': "Phase 1 Current THD (%)", 'type': 'float'},
                {'modbus_addr': 0xF2, 'name': 'L2_Current_THD', 'description': "Phase 2 Current THD (%)", 'type': 'float'},
                {'modbus_addr': 0xF4, 'name': 'L3_Current_THD', 'description': "Phase 3 Current THD (%)", 'type': 'float'},

                {'modbus_addr': 0xF8, 'name': 'Avg_L_N_Volts_THD', 'description': "Average L to N Volts THD (%)", 'type': 'float'},
                {'modbus_addr': 0xFA, 'name': 'Avg_L_Current_THD', 'description': "Average L Current THD (%)", 'type': 'float'},

                {'modbus_addr': 0x0108, 'name': 'L1_MAX_A', 'description': "L1 Maximum Current Demand (A)", 'type': 'float'},
                {'modbus_addr': 0x010A, 'name': 'L2_MAX_A', 'description': "L2 Maximum Current Demand (A)", 'type': 'float'},
                {'modbus_addr': 0x010C, 'name': 'L3_MAX_A', 'description': "L3 Maximum Current Demand (A)", 'type': 'float'},

                {'modbus_addr': 0x0156, 'name': 'Total_kWh', 'description': "Total Energy (kWh)", 'type': 'float'},
                {'modbus_addr': 0x0158, 'name': 'Total_kVARh', 'description': "Total KVARh (kVArh)", 'type': 'float'},
                {'modbus_addr': 0x015A, 'name': 'L1_import_kWh', 'description': "L1 import kWh (kWh)", 'type': 'float'},
                {'modbus_addr': 0x015C, 'name': 'L2_import_kWh', 'description': "L2 import kWh (kWh)", 'type': 'float'},
                {'modbus_addr': 0x015E, 'name': 'L3_import_kWh', 'description': "L3 import kWh (kWh)", 'type': 'float'},
                {'modbus_addr': 0x0160, 'name': 'L1_export_kWh', 'description': "L1 export kWh (kWh)", 'type': 'float'},
                {'modbus_addr': 0x0162, 'name': 'L2_export_kWh', 'description': "L2 export kWh (kWh)", 'type': 'float'},
                {'modbus_addr': 0x0164, 'name': 'L3_export_kWh', 'description': "L3 export kWh (kWh)", 'type': 'float'},

                {'modbus_addr': 0x0166, 'name': 'L1_Total_kWh', 'description': "L1 Total kWh (kWh)", 'type': 'float'},
                {'modbus_addr': 0x0168, 'name': 'L2_Total_kWh', 'description': "L2 Total kWh (kWh)", 'type': 'float'},
                {'modbus_addr': 0x016A, 'name': 'L3_Total_kWh', 'description': "L3 Total kWh (kWh)", 'type': 'float'},

                {'modbus_addr': 0x016C, 'name': 'L1_Import_kVArh', 'description': "L1 Import KVARh (KVARh)", 'type': 'float'},
                {'modbus_addr': 0x016E, 'name': 'L2_Import_kVArh', 'description': "L2 Import KVARh (KVARh)", 'type': 'float'},
                {'modbus_addr': 0x0170, 'name': 'L3_Import_kVArh', 'description': "L3 Import KVARh (KVARh)", 'type': 'float'},
                {'modbus_addr': 0x0172, 'name': 'L1_Export_kVArh', 'description': "L1 Export KVARh (KVARh)", 'type': 'float'},
                {'modbus_addr': 0x0174, 'name': 'L2_Export_kVArh', 'description': "L2 Export KVARh (KVARh)", 'type': 'float'},
                {'modbus_addr': 0x0176, 'name': 'L3_Export_kVArh', 'description': "L3 Export KVARh (KVARh)", 'type': 'float'},
                # {'modbus_addr': 0x0178, 'name': 'L1_Total_kVArh', 'description': "L1 Total KVARh (KVARh)", 'type': 'float'},
                # {'modbus_addr': 0x017A, 'name': 'L2_Total_kVArh', 'description': "L2 Total KVARh (KVARh)", 'type': 'float'},
                # {'modbus_addr': 0x017C, 'name': 'L3_Total_kVArh', 'description': "L3 Total KVARh (KVARh)", 'type': 'float'}

            ]
        }
    }

    if not args.metertype in meter_database:
        print("ERROR: Unknown meter type '" + args.metertype + "', exiting", file=sys.stderr)
        sys.exit(-1)
    meter = meter_database[args.metertype]

    result = collections.OrderedDict()

    # Add Metername and type
    result['meterName'] = args.metername
    result['meterType'] = meter['name']
    result['collector'] = sys.argv[0] + ", hostname=" + platform.node() + ", serialport=" + args.serialport + ", RS485_addr=" + str(args.address)

    # Add Timestamp
    result['ts'] = datetime.datetime.utcnow().isoformat() + "Z"
    utc_offset_sec = time.altzone if time.localtime().tm_isdst else time.timezone
    utc_offset = datetime.timedelta(seconds=-utc_offset_sec)
    result['ts_local'] = datetime.datetime.now().replace(tzinfo=datetime.timezone(offset=utc_offset)).isoformat()

    # print("\nΤάση: " + str(round(instrument.read_float(0x00, functioncode=4, number_of_registers=2, byteorder=0), 2)) + " Volts.\n")
    # (registeraddress: int, functioncode: int = 3, number_of_registers: int = 2, byteorder: int = 0minimalmodbus.BYTEORDER_BIG= 0

    # Read all datapoints
    for dp in meter['data_points']:
        if dp['type'] == "float":
            # exception handling for communication problems that might happen
            try:
                value = instrument.read_float(dp['modbus_addr'], functioncode=4, number_of_registers=2)
                # Compare the value with its integer representation. If the number is not an 'integer',
                #  then round the number to 2 decimal digits (this way nums 0 and 1 won't appear as 0.0 or 1.0, etc.)
                if value != int(value):
                    value = str(round(value, 2))
            except IOError:
                value = "Failed to read from instrument"
                #print(value)
        else:
            value = "UNSUPPORTED_DATA_TYPE"
        # result.append({})
        result[dp['name']] = value
        ######################## print each row datapoint ##################
        #print(str(value) + " " + dp['description'])

    # close the serial port
    #instrument.serial.close()

    # Dump result to STDOUT
    # print('\n' + json.dumps(result)) # json.dumps converts Python dictionary to JSON-formatted string

    # Write the data to JSON file
    with open('static/data.json', 'w') as f:
        json.dump(result, f)

    # return the json
    return json.dumps(result)

# Route for serving the JSON data to the frontend without saving them to a file
@app.route("/data", methods=["GET"])
@limiter.limit("1/second")  # Adjust the limit as needed eg. '30 per minute'
# (ex1. 60 requests/min = 60sec/ 60req = every 1 sec.)
# (ex2. 10 requests/min = 60sec/ 10req = every 6 sec.)
def get_data():
    # Get data from your function (e.g., getmodbusdata())
    data = getModbusData()
    return data

# Route for getting the data.json as file
@app.route('/data.json')
@limiter.limit('30 per minute')  # Adjust the limit as needed
def get_data_file():
    getModbusData()
    return send_from_directory('static', 'data.json')

# default route for index.html
@app.route('/')
@limiter.exempt # exempt this route from any limiting
def index():
    with open("static/data.json", "r") as f:
       data = f.read()
       # print("JSON data " +data)
    return render_template("index.html")
    # return render_template("index.html", data=data)
    #return render_template("index.html", headings=headings, data=data)


mode = "prod" # Values: "dev" or "prod"

if __name__ == '__main__':


    print("running in " + mode + " mode. You can stop the server using CTRL+C in the terminal.")
    if mode == "dev":
        # default Flask server
        app.run(host='0.0.0.0', debug=True, port=8000)
    else:
        # using waitress server (1, or 2 or ...4 parallel threads)
        # serve(app, host='0.0.0.0', port=8000, threads=2)
        # submounting the application on a url_prefix. Just add the url_prefix parameter and set it to the url needed (make sure that the prefix starts with '/').
        # this means that the application will work even if I use the URL: localhost:8000/my-app
        serve(app, host='0.0.0.0', port=8000, threads=4, url_prefix="/my-app")