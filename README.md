# PowerMonitor
A web app that is based on Flask for displaying modbus data for Eastron SDM-630 MODBUS energy meter

# Create the python virtual environment in the project folder:
python -m venv myenv

# Activate the virtual environment (make sure to cd in the folder: venv\Scripts):
source myenv/bin/activate  # On Unix/macOS
venv\Scripts\activate.bat  # On Windows

# whatever you do from now on applies to the python virtual environment's installation (and not the machine's)
pip install -r requirements.txt


# Connect meter and Usb to RS485 adapter.
# Check that USB is set to COM6 in Devices/Control Panel

# Run the app (server starts automatically):
python 'app - Integrated Modbus Script.py'

# View the data.json
http://localhost:8000/data.json
