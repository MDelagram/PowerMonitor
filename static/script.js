$(document).ready(function() {
    console.log("script.js loaded and ready.");

    function fetchData() {
        // Logic for fetching the JSON data from the Flask route '/data'
        $.ajax({
            url: '/data',  // Update the URL to the Flask route
            dataType: 'json',
            success: function(data) {
                updateTable(data);
            },
            error: function(xhr, status, error) {
                console.error("Error fetching data:", error);
            }
        });
    }

    // currently not used
    function fetchDataFromFile() {
        // Logic for reading from the data.json file
        $.ajax({
            url: 'data.json',
            dataType: 'json',
            success: function(data) {
                updateTable(data);
            }
        });
    }

    // Function to extract serial port from collector field
    function getSerialPort(collector) {
        // Split the collector string based on comma delimiter
        var parts = collector.split(',');

        // Loop through each part to find the one containing "serialport="
        for (var i = 0; i < parts.length; i++) {
            var keyValue = parts[i].trim().split('=');
            if (keyValue[0] === 'serialport') {
                // Return the value corresponding to "serialport"
                return keyValue[1];
            }
        }
        // Return null if "serialport" is not found
        return null;
    }

    // Call the function with the "collector" value from the data object
    /*var serialPort = getSerialPort(data.collector);
    console.log("Serial Port:", serialPort); // Output the serial port value to console
    */

    // Function to extract the RS485_addr from collector field
    function getRS485Addr(collector) {
        // Split the collector string based on comma delimiter
        var parts = collector.split(',');

        // Loop through each part to find the one containing "RS485_addr="
        for (var i = 0; i < parts.length; i++) {
            var keyValue = parts[i].trim().split('=');
            if (keyValue[0] === 'RS485_addr') {
                // Return the value corresponding to "RS485_addr"
                return keyValue[1];
            }
        }
        // Return null if "RS485_addr" is not found
        return null;
    }

    // Converts the timestamp to dd/MM/yyyy hh/mm/ss (24-hour format)
    function formatTimestamp(timestamp) {
        // Parse the timestamp string into a Date object
        var date = new Date(timestamp);

        // Format the timestamp using toLocaleString()
        var formattedTimestamp = date.toLocaleString('en-GB', {
            day: '2-digit',
            month: '2-digit',
            year: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            hour12: false // Use 12-hour format
        });

        return formattedTimestamp;
    }

    // Example usage:
    //var timestamp = "2024-02-07T21:35:58.286748+02:00";
    //var formattedTimestamp = formatTimestamp(timestamp);
    //console.log("Formatted Timestamp:", formattedTimestamp);


    // 'data' is the object that contains the parsed JSON data obtained from the server using AJAX.
    // when you make the AJAX request to fetch the JSON file, JavaScript automatically parses the JSON response
    // into a JavaScript object, making it easy to work with in your code.
    function updateTable(data) {
        //removes the entire table and the script below should recreate it every time the data is updated
        //$('#data-table').empty();
        // Update specific table cells with data from JSON

        // JQuery expressions to set text to the table elements by their ids:
        $('#serial_port').text(getSerialPort(data.collector));
        $('#data_local_timestamp').text(formatTimestamp(data.ts_local));
        $('#rs485_address').text(getRS485Addr(data.collector));
        $('#meter_name').text(data.meterName);
        //console.log("...Typing L1_V: " + (data.L1_V));

        // Volts
        $('#L1-N_Volts').text(data.L1_V);
        $('#L2-N_Volts').text(data.L2_V);
        $('#L3-N_Volts').text(data.L3_V);
        // Amps
        $('#L1_Amps').text(data.L1_A);
        $('#L2_Amps').text(data.L2_A);
        $('#L3_Amps').text(data.L3_A);
        $('#Sum_Line_Currents').text(data.Sum_L1L2L3_A);
        // Power
        $('#L1_Pwr').text(data.L1_W);
        $('#L2_Pwr').text(data.L2_W);
        $('#L3_Pwr').text(data.L3_W);
        $('#Total_Watts').text(data.Total_Sys_Power);
        // Line Frequency
        $('#Line_Frequency').text(data.LineFrequency_Hz);
        // Power Factor
        $('#L1_Pwr_Factor').text(data.L1_Power_Factor);
        $('#L2_Pwr_Factor').text(data.L2_Power_Factor);
        $('#L3_Pwr_Factor').text(data.L3_Power_Factor);
        $('#Total_Pwr_Factor').text(data.Total_System_Power_Factor);
        // THD Voltage
        $('#L1_N_Volts_THD').text(data.L1_N_Volts_THD);
        $('#L2_N_Volts_THD').text(data.L2_N_Volts_THD);
        $('#L3_N_Volts_THD').text(data.L3_N_Volts_THD);
        $('#Average_L_N_Volts_THD').text(data.Avg_L_N_Volts_THD);
        // THD Current
        $('#L1_Current_THD').text(data.L1_Current_THD);
        $('#L2_Current_THD').text(data.L2_Current_THD);
        $('#L3_Current_THD').text(data.L3_Current_THD);
        $('#Average_L_Current_THD').text(data.Avg_L_Current_THD);
        // Import Energy
        $('#L1_Import_kwh').text(data.L1_import_kWh);
        $('#L2_Import_kwh').text(data.L2_import_kWh);
        $('#L3_Import_kwh').text(data.L3_import_kWh);
        $('#Import_Wh_Since_Last_Reset').text(data.EnergyImported_kWh);
        // Export Energy
        $('#L1_Export_kwh').text(data.L1_export_kWh);
        $('#L2_Export_kwh').text(data.L2_export_kWh);
        $('#L3_Export_kwh').text(data.L3_export_kWh);
        $('#Export_Wh_Since_Last_Reset').text(data.EnergyExported_kWh);
        // Volt Amps
        $('#Phase1_VA').text(data.L1_VA);
        $('#Phase2_VA').text(data.L2_VA);
        $('#Phase3_VA').text(data.L3_VA);
        $('#Total_System_VA').text(data.Total_Sys_VA);
        // Volt Amps Reactive
        $('#Phase1_VAr').text(data.L1_VAr);
        $('#Phase2_VAr').text(data.L2_VAr);
        $('#Phase3_VAr').text(data.L3_VAr);
        $('#Total_System_VAr').text(data.Total_Sys_VAr);
        // Line - Line Volts
        $('#L1-L2_Volts').text(data.L1L2_V);
        $('#L2-L3_Volts').text(data.L2L3_V);
        $('#L3-L1_Volts').text(data.L3L1_V);
        // Average values
        $('#Average_Line_Neutral_Volts_Value').text(data.Avg_L_N_Volts);
        $('#Average_Line_Line_Volts_Value').text(data.Avg_Line_Line_V);
        $('#Average_Line_Current_Value').text(data.Avg_L_Current);
        $('#Sum_of_Line_Currents_Value').text(data.Sum_L1L2L3_A);
        // Maximum values
        $('#Max_Phase1_Current_Demand_value').text(data.L1_MAX_A);
        $('#Max_Phase2_Current_Demand_value').text(data.L2_MAX_A);
        $('#Max_Phase3_Current_Demand_value').text(data.L3_MAX_A);
        $('#Max_Neutral_Current_value').text(data.Max_Neutral_Current);
        console.log("The entire JSON object is:");
        console.log(data);
        // Loop through data and generate table rows dynamically (based on the JSON file order)
        /*
        #...the table should match the order of the JSON
        $.each(data, function(key, value) {
        // Create a new table row
        var newRow = $('<tr>');
        // Add table cells with unique IDs for each field
        newRow.append('<td id="' + key + '">' + value + '</td>');
        // Append the new row to the table
        $('#data-table').append(newRow);
        */
    /*});*/
    }

    // Fetch data every 3 seconds
    setInterval(fetchData, 3000);
    // setInterval(fetchDataFromFile, 2000);
});
