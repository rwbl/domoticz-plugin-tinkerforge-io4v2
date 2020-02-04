# domoticz-plugin-tinkerforge-io4v2
Domoticz plugin to interact with the Tinkerforge IO-4 Bricklet 2.0.

# Objectives
* To control the 4 I/O pins of the [Tinkerforge IO-4 Bricklet 2.0](https://www.tinkerforge.com/en/doc/Hardware/Bricklets/IO4_V2.html#io4-v2-bricklet-description).
* To configure each of the 4 I/O pins as digital input or output.
* To learn how to write generic Python plugin(s) for the Domoticz Home Automation system communicating with [Tinkerforge](http://www.tinkerforge.com) Building Blocks. This plugin espcially focus on handling callbacks.

_Abbreviations_: TF=Tinkerforge, IO4=Tinkerforge IO-4 Bricklet 2.0, GUI=Domoticz Web UI.

## Solution
A Domoticz Python plugin named "Tinkerforge IO-4 Bricklet 2.0" with 4 devices type Light/Switch, subtype Switch, Switch Type On/Off.
The Tinkerforge IO-4 Bricklet 2.0 is connected to a Tinkerforge Master Brick direct connected via USB with the Domoticz Home Automation system.
The Domoticz Home Automation system is running on a Raspberry Pi.

ADD PICTURE TEST SETUP

![](.png)

Additional info **domoticz-plugin-tinkerforge-io4v2.pdf**.

## Hardware Parts
* Raspberry Pi 3B+ [(Info)](https://www.raspberrypi.org)
* Tinkerforge Master Brick 2.1 FW 2.4.10 [(Info)](https://www.tinkerforge.com/en/doc/Hardware/Bricks/Master_Brick.html#master-brick)
* Tinkerforge IO-4 Bricklet 2.0 FW 2.0.4 [(Info)](https://www.tinkerforge.com/en/doc/Hardware/Bricklets/IO4_V2.html#)
* LED Blue
* Push-button (DFRobot Digital Push Button Green)

## Software
* Raspberry Pi Raspian Debian Linux Buster 4.19.93-v7+ #1290
* Domoticz Home Automation System V4.11666 (beta)
* Tinkerforge Brick Daemon 2.4.1, Brick Viewer 2.4.11
* Tinkerforge Python API-Binding 2.1.24
* Python 3.7.3, GCC 8.2.0
* The versions for developing this plugin are subject to change.

## Quick Steps
For implementing the Plugin on the Domoticz Server running on the Raspberry Pi.
See also Appendix Python Plugin Code (well documented).

## Test Setup
For testing this plugin, the test setup has a Master Brick with IO-4 Bricklet 2.0 connected to port B.
The IO-4 Bricklet 2.0 has two channels (out of the four) in use and configured as:
* Channel 0 = Output: LED
* Channel 1 = Input: Push-button

On the Raspberry Pi, it is mandatory to install the Tinkerforge Brick Daemon and Brick Viewer following [these](https://www.tinkerforge.com/en/doc/Embedded/Raspberry_Pi.html) installation instructions (Raspian armhf).

Build the test setup by connecting the Tinkerforge Building Blocks:
* IO-4 Bricklet 2.0 > LED to Channel 0 > Push-button to Channel 1
* IO-4 Bricklet 2.0 > Master Brick using bricklet cable 7p-10p (because using a Master Brick with 10p connectors and the IO-4 Bricklet 2.0 has the newer 7p connector).
* Master Brick > USB cable to Raspberry Pi

Start the Brick Viewer and action:
* Update the devices firmware
* Obtain the UID of the IO-4 Bricklet 2.0 as required by the Python plugin (i.e. G4d).

## Domoticz Web GUI
Open windows GUI Setup > Hardware, GUI Setup > Log, GUI Setup > Devices
This is required to add the new hardware with its device and monitor if the plugin code is running without errors.

## Create folder
```
cd /home/pi/domoticz/plugins/TFIO4V2
```

## Create the plugin
The plugin has a mandatory filename plugin.py located in the newly created plugin folder
Domoticz Python Plugin Source Code: see file **plugin.py**.

## Install the Tinkerforge Python API
There are two options:

### 1) sudo pip3 install tinkerforge
Advantage: in case of binding updates, only a single folder must be updated.
Check if a subfolder tinkerforge is created in folder /usr/lib/python3/dist-packages.
_Note_: Check the version of "python3" in the folder path. This could also be python 3.7 or other = see below.

**If not the case**, unzip the Tinkerforge Python Binding into the folder /usr/lib/python3/dist-packages.
_Example_
  Create subfolder Tinkerforge holding the Tinkerforge Python Library
```
  cd /home/pi/tinkerforge
```
  Unpack the latest python bindings into folder /home/pi/tinkerforge
  Copy /home/pi/tinkerforge to the Python3 dist-packges
```
  sudo cp -r /home/pi/tinkerforge /usr/lib/python3/dist-packages/
```

In the Python Plugin code amend the import path to enable using the Tinkerforge libraries
```
from os import path
import sys
sys.path
sys.path.append('/usr/local/lib/python3.7/dist-packages')
```

### 2) Install the Tinkerforge Python Bindings in a subfolder of the plugin and copy the binding content.
Disadvantage: Every Python plugin using the Tinkerforge bindings must have a subfolder tinkerforge.
In case of binding updates,each of the tinkerforge plugin folders must be updated.
/home/pi/domoticz/plugins/soilmoisturemonitor/tinkerforge

There is no need to amend the path as for option 1.

For either ways, the bindings are used like:
```
import tinkerforge
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_io4_v2 import BrickletIO4V2
```
add more depending Tinkerforge brick/bricklet used.

Ensure to update the files in case of newer Tinkerforge Python Bindings.

## Make plugin.py executable
```
cd /home/pi/domoticz/plugins/TFIO4V2
chmod +x plugin.py
```

## Restart Domoticz
Restart Domoticz to find the plugin:
```
sudo systemctl restart domoticz.service
```

**Note**
When making changes to the Python plugin code, ensure to restart Domoticz and refresh any of the Domoticz Web GUI's.

## Domoticz Add Hardware Tinkerforge IO-4 Bricklet 2.0
**IMPORTANT**
Prior adding, set GUI Stup > Settings > Hardware the option to allow new hardware.
If this option is not enabled, no new devices are created assigned to this hardware.
Check in the Domoticz log as error message Python script at the line where the new device is used
(i.e. Domoticz.Debug("Device created: "+Devices[1].Name))

In the GUI Setup > Hardware add the new hardware "Tinkerforge IO-4 Bricklet 2.0".

## Add Hardware - Check the Domoticz Log
After adding,ensure to check the Domoticz Log (GUI Setup > Log)

ADD DOMOTICZ ADD HARDWARE PIC
![...-h](.png)

_Example:_
```
```
## Domoticz Log Entry Adding Hardware with Debug=True
```
2020-02-02 10:43:52.694 Status: (TFIO4V2) Started. 
2020-02-02 10:43:53.174 (TFIO4V2) Debug logging mask set to: PYTHON PLUGIN QUEUE IMAGE DEVICE CONNECTION MESSAGE ALL 
2020-02-02 10:43:53.174 (TFIO4V2) 'HardwareID':'7' 
2020-02-02 10:43:53.174 (TFIO4V2) 'HomeFolder':'/home/pi/domoticz/plugins/TFIO4V2/' 
2020-02-02 10:43:53.174 (TFIO4V2) 'StartupFolder':'/home/pi/domoticz/' 
2020-02-02 10:43:53.174 (TFIO4V2) 'UserDataFolder':'/home/pi/domoticz/' 
2020-02-02 10:43:53.174 (TFIO4V2) 'Database':'/home/pi/domoticz/domoticz.db' 
2020-02-02 10:43:53.174 (TFIO4V2) 'Language':'en' 
2020-02-02 10:43:53.174 (TFIO4V2) 'Version':'1.0.0' 
2020-02-02 10:43:53.174 (TFIO4V2) 'Author':'rwbL' 
2020-02-02 10:43:53.174 (TFIO4V2) 'Name':'TFIO4V2' 
2020-02-02 10:43:53.174 (TFIO4V2) 'Address':'127.0.0.1' 
2020-02-02 10:43:53.174 (TFIO4V2) 'Port':'4223' 
2020-02-02 10:43:53.174 (TFIO4V2) 'Key':'TFIO4V2' 
2020-02-02 10:43:53.174 (TFIO4V2) 'Mode1':'G4d' 
2020-02-02 10:43:53.174 (TFIO4V2) 'Mode2':'o,i,o,o' 
2020-02-02 10:43:53.174 (TFIO4V2) 'Mode3':'1,0,0,0' 
2020-02-02 10:43:53.174 (TFIO4V2) 'Mode6':'Debug' 
2020-02-02 10:43:53.174 (TFIO4V2) 'DomoticzVersion':'4.11666' 
2020-02-02 10:43:53.174 (TFIO4V2) 'DomoticzHash':'3630122d7' 
2020-02-02 10:43:53.174 (TFIO4V2) 'DomoticzBuildTime':'2020-01-31 08:45:14' 
2020-02-02 10:43:53.174 (TFIO4V2) Device count: 0 
2020-02-02 10:43:53.174 (TFIO4V2) ChannelDirections:o,i,o,o 
2020-02-02 10:43:53.174 (TFIO4V2) ChannelValues:1,0,0,0 
2020-02-02 10:43:53.174 (TFIO4V2) Creating new Devices 
2020-02-02 10:43:53.175 (TFIO4V2) Creating device 'IO4 Channel 0'. 
2020-02-02 10:43:53.176 (TFIO4V2) Device created: TFIO4V2 - IO4 Channel 0 
2020-02-02 10:43:53.176 (TFIO4V2) Creating device 'IO4 Channel 1'. 
2020-02-02 10:43:53.177 (TFIO4V2) Device created: TFIO4V2 - IO4 Channel 1 
2020-02-02 10:43:53.177 (TFIO4V2) Creating device 'IO4 Channel 2'. 
2020-02-02 10:43:53.178 (TFIO4V2) Device created: TFIO4V2 - IO4 Channel 2 
2020-02-02 10:43:53.178 (TFIO4V2) Creating device 'IO4 Channel 3'. 
2020-02-02 10:43:53.179 (TFIO4V2) Device created: TFIO4V2 - IO4 Channel 3 
2020-02-02 10:43:53.183 (TFIO4V2) IP Connection - OK 
2020-02-02 10:43:53.183 (TFIO4V2) Connected to the Master Brick. 
2020-02-02 10:43:53.183 (TFIO4V2) Configure channels. 
2020-02-02 10:43:53.184 (TFIO4V2) Channel=0, Direction=o, Value=True 
2020-02-02 10:43:53.184 (TFIO4V2 - IO4 Channel 0) Updating device from 0:'' to have values 1:''. 
2020-02-02 10:43:53.203 (TFIO4V2) Channel=1, Direction=i, Value=False 
2020-02-02 10:43:53.206 (TFIO4V2) Channel=1 = Callback registered 
2020-02-02 10:43:53.207 (TFIO4V2) Channel=2, Direction=o, Value=False 
2020-02-02 10:43:53.207 (TFIO4V2) Channel=3, Direction=o, Value=False 
2020-02-02 10:43:53.170 Status: (TFIO4V2) Initialized version 1.0.0, author 'rwbL' 
2020-02-02 10:43:53.170 Status: (TFIO4V2) Entering work loop. 
```

## Notes

### Master Brick Disconnected & Re-connected
If the Master Brick has been disconnected from the Raspberry Pi (i.e. plugged out) and re-connected again, the hardware must be updated (using Setup > Hardware > select the plugin > Update) or restart Domoticz.

### Callback Period Input Channel
The callback period for an Input channel is hardcoded set to 250ms. To change, set the new value for constant CALLBACKPERIOD.

### Domoticz Status Device
If do not want to use the status device to display messages after any action, comment the device with _UNITSTATUS_ out.

## dzVents Lua Automation Script Examples

### Handle Push-button (Channel 1)
```
-- Tinkerforge IO4 v2 Bricklet Plugin - Test Script 
-- dzVents Automation Script: tfio4v2_pushbutton_led
--
-- There are two switch devices used:
-- (Idx,Name,Type,SubType - Hardware Connected)
-- Idx=76, TFIO4 - IO4 Channel 0,Light/Switch,Switch,On/Off - LED Blue
-- Idx=77, TFIO4 - IO4 Channel 1,Light/Switch,Switch,On/Off - Push-Button DFRobot
-- Test:
-- Turn the LED Blue on, when pressing the push-button down and off again when released.
--
-- 20200102 by rwbL

IDXLEDBLUE = 76
IDXPUSHBUTTON = 77

return {
	on = {
		devices = {
			IDXPUSHBUTTON
		}
	},
	execute = function(domoticz, device)
		domoticz.log('Device ' .. device.name .. ' was changed to ' .. device.state, domoticz.LOG_INFO)
		if (device.state == 'On') then
            domoticz.devices(IDXLEDBLUE).switchOn()
        else
            domoticz.devices(IDXLEDBLUE).switchOff()
		end
	end
}
```

### LED Blick (Channel 0)
```
--- Let the LED (at channel 0, output) blink every minute by triggering the push button (at channel 1, input).
--- The trigger is handled by previous script - BUT could also be set direct in the script below.
IDXPUSHBUTTON = 77

return {
	on = {
		timer = {
			'every minute',              
	   },
    },
	execute = function(domoticz, timer)
		domoticz.log('Timer event was triggered by ' .. timer.trigger, domoticz.LOG_INFO)
        if (domoticz.devices(IDXPUSHBUTTON).state == 'On') then
            domoticz.devices(IDXPUSHBUTTON).switchOff()
        else
            domoticz.devices(IDXPUSHBUTTON).switchOn()
		end
	end
}
```
