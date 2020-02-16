# Domoticz Home Automation - Plugin Tinkerforge IO-4 Bricklet 2.0
# @author Robert W.B. Linn
# @version 1.0.0 (Build 20200203)
#
# NOTE: after every change run
# sudo chmod +x *.*                      
# sudo systemctl restart domoticz.service OR sudo service domoticz.sh restart
#
# Domoticz Python Plugin Development Documentation:
# https://www.domoticz.com/wiki/Developing_a_Python_plugin
# Tinkerforge IO-4 Bricklet 2.0 Documentation:
# Hardware:
# https://www.tinkerforge.com/en/doc/Hardware/Bricklets/IO4_V2.html#io4-v2-bricklet-description
# API Python Documentation:
# https://www.tinkerforge.com/en/doc/Software/Bricklets/IO4V2_Bricklet_Python.html#io4-v2-bricklet-python-api

"""
<plugin key="tfio4v2" name="Tinkerforge IO-4 Bricklet 2.0" author="rwbL" version="1.0.0">
    <description>
        <h2>Tinkerforge IO-4 Bricklet 2.0</h2><br/>
        This bricklet has 4 I/O pins (channels) which can be configured as digital input or output.<br/>
        For each channel:<br/>
        <ul style="list-style-type:square">
            <li>Domoticz device created is from Type: Light/Switch, SubType: Switch, Switch Type: On/Off.</li>
            <li>Set the direction:
                <ul style="list-style-type:square">
                    <li>Output 'o' (i.e. LED which can be turned on or off) or</li>
                    <li>Input 'i' (i.e. push-button to trigger an action via a dzVents automation script).</li>
                </ul>
            </li>
            <li>Set the default value: 0 (low) or 1 (high).</li>
            <li>Both direction and value are set as comma separated string, i.e. value1,value2,value3,value4.</li>
        </ul>
        In addition, an Alert device is created and used to inform on last action or in case of an error.<br/>
        <br/>
        <h3>Configuration</h3>
        <ul style="list-style-type:square">
            <li>Address: IP address of the host connected to. Default: 127.0.0.1 (for USB connection)</li>
            <li>Port: Port used by the host. Default: 4223</li>
            <li>UID: Unique identifier of IO-4 Bricklet 2.0. Obtain the UID via the Brick Viewer. Default: G4d</li>
            <li>Direction: 'o' (output) or 'i' (input) for each channel. Default: o,i,o,o</li>
            <li>Value: 0 (low) or 1 (high) for each channel. Default: 1,0,0,0</li>
            <li>Important: all 4 channels must be set, even if less are used. For i,o use lower case.</li>
        </ul>
        <h3>Notes</h3>
        <ul style="list-style-type:square">
            <li>If the Master Brick has been disconnected from the Raspberry Pi (i.e. plugged out) and connected again, the hardware must be updated (using Setup > Hardware > select the plugin > Update) or restart Domoticz.</li>
            <li>The callback period for an Input channel is hardcoded set to 250ms. To change, set the new value for constant CALLBACKPERIOD in plugin.py.</li>
        </ul>
    </description>
    <params>
        <param field="Address" label="Host" width="200px" required="true" default="127.0.0.1"/>
        <param field="Port" label="Port" width="75px" required="true" default="4223"/>
        <param field="Mode1" label="UID" width="200px" required="true" default="G4d"/>
        <param field="Mode2" label="Directions" width="100px" required="true" default="o,i,o,o"/>
        <param field="Mode3" label="Values" width="150px" required="true" default="1,0,0,0"/>
        <param field="Mode6" label="Debug" width="75px">
            <options>
                <option label="True" value="Debug" default="true"/>
                <option label="False" value="Normal"/>
            </options>
        </param>
    </params>
</plugin>
""" 

## Imports
import Domoticz
import urllib
import urllib.request

# Amend the import path to enable using the Tinkerforge libraries
# Alternate (ensure to update in case newer Python API bindings):
# create folder tinkerforge and copy the binding content, i.e.
# /home/pi/domoticz/plugins/tfio4v2
from os import path
import sys
sys.path
sys.path.append('/usr/local/lib/python3.7/dist-packages')
                
import tinkerforge
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_io4_v2 import BrickletIO4V2

# Number of channels = must match number of index defined below
CHANNELS = 4
UNITCHANNEL1 = 1
UNITCHANNEL2 = 2
UNITCHANNEL3 = 3
UNITCHANNEL4 = 4
UNITSTATUS = 5
# Callbackperiod for pull-up = push-button (set to 250ms)
CALLBACKPERIOD = 250
# Device Status Level & Text
STATUSLEVELOK = 1
STATUSLEVELERROR = 5
STATUSTEXTOK = "OK"
STATUSTEXTERROR = "ERROR"

class BasePlugin:
    
    def __init__(self):
        # HTTP Connection
        self.httpConn = None
        self.httpConnected = 0

        # List of channels (#4) direction = i for input and o for output. Example 4 channels: o,i,o,o
        self.ChannelDirections = []
        # List of channels (#4) value = true or false. If true the channel is set to high. Example: true,false,false,false
        self.ChannelValues = []

        # Tinkerforge ipconnection and iodevice
        # Flag to check if connected to the master brick
        self.ipConn = None
        self.ipConnected = 0
        self.ioDev = None

        # NOT USED = PLACEHOLDER
        # The Domoticz heartbeat is set to every 10 seconds. Do not use a higher value than 30 as Domoticz message "Error: hardware (N) thread seems to have ended unexpectedly"
        # The plugin heartbeat is set in Parameter.Mode5 (seconds). This is determined by using a hearbeatcounter which is triggered by:
        # (self.HeartbeatCounter * self.HeartbeatInterval) % int(Parameter.Mode5) = 0
        # Example: trigger action every 60s = (6 * 10) mod 60 = 0
        """
        self.HeartbeatInterval = 10
        self.HeartbeatCounter = 0
        """
        
        return

    def onStart(self):
        Domoticz.Debug("onStart called")
        Domoticz.Debug("Debug Mode:" + Parameters["Mode6"])
        if Parameters["Mode6"] == "Debug":
            self.debug = True
            Domoticz.Debugging(1)
            DumpConfigToLog()
                
        # Get the defaults for direction and value for each of the channels
        # The strings contain 4 entries separated by comma (,).

        ## Directions
        ChannelDirectionsParam = Parameters["Mode2"]
        Domoticz.Debug("ChannelDirections:" + ChannelDirectionsParam)
        ## Split the parameter string into a list of directions
        self.ChannelDirections = ChannelDirectionsParam.strip().split(',')
        # Check the list length against the constant CHANNELS
        if len(self.ChannelDirections) < CHANNELS:
            Domoticz.Error("[ERROR] Directions parameter not correct ("+str(len(self.ChannelDirections))+")! Number of channels should be " + str(CHANNELS) + ".")
            return

        ## Values - convert the values from string to int
        ChannelValuesParam = Parameters["Mode3"]
        Domoticz.Debug("ChannelValues:" + ChannelValuesParam)
        # self.ChannelValues = ChannelValuesParam.strip().split(',')        
        # self.ChannelValues=[int(i.strip()) for i in ChannelValuesParam]
        self.ChannelValues = [int(x.strip()) for x in ChannelValuesParam.split(',')]
        if len(self.ChannelValues) < CHANNELS:
            Domoticz.Error("[ERROR] Values parameter not correct ("+str(len(self.ChannelValues))+")! Number of channels should be " + str(CHANNELS) + ".")
            return

        if (len(Devices) == 0):
            # Create new devices for the Hardware = each channel is a switch
            Domoticz.Debug("Creating new Devices")
            Domoticz.Device(Name="IO4 Channel 0", Unit=UNITCHANNEL1, TypeName="Switch", Used=1).Create()
            Domoticz.Debug("Device created: "+Devices[UNITCHANNEL1].Name)
            Domoticz.Device(Name="IO4 Channel 1", Unit=UNITCHANNEL2, TypeName="Switch", Used=1).Create()
            Domoticz.Debug("Device created: "+Devices[UNITCHANNEL2].Name)
            Domoticz.Device(Name="IO4 Channel 2", Unit=UNITCHANNEL3, TypeName="Switch", Used=1).Create()
            Domoticz.Debug("Device created: "+Devices[UNITCHANNEL3].Name)
            Domoticz.Device(Name="IO4 Channel 3", Unit=UNITCHANNEL4, TypeName="Switch", Used=1).Create()
            Domoticz.Debug("Device created: "+Devices[UNITCHANNEL4].Name)
            Domoticz.Device(Name="IO4 Status", Unit=UNITSTATUS, TypeName="Alert", Used=1).Create()
            Domoticz.Debug("Device created: "+Devices[UNITSTATUS].Name)
            updateStatus(STATUSLEVELOK, STATUSTEXTOK)

        # Get the UID of the IO4
        self.UID = Parameters["Mode1"]
        if len(self.UID) == 0:
            updateStatus(STATUSLEVELERROR, "[ERROR] Device UID not set. Get the UID using the Brick Viewer.")
            return

        # Flag to check if connected to the master brick
        self.ipConnected = 0
        # Create IP connection
        self.ipConn = IPConnection()
        # Create device object
        self.ioDev = BrickletIO4V2(self.UID, self.ipConn)

        # Connect to brickd using Host and Port
        try:
            self.ipConn.connect(Parameters["Address"], int(Parameters["Port"]))
            self.ipConnected = 1
            Domoticz.Debug("IP Connection - OK")
        except:
            updateStatus(STATUSLEVELERROR, "[ERROR] IP Connection failed. Check the parameter.")
            return

        # Don't use device before ipcon is connected
        if self.ipConnected == 0:
            updateStatus(STATUSLEVELERROR, "[ERROR] Can not connect to Master Brick. Check settings, correct and restart Domoticz." )
            return

        Domoticz.Debug("Connected to the Master Brick." )
        Domoticz.Debug("Configure channels." )
        # Configure the channels 0-3 - which is unit 1-4; i=input;o=output
        for channel, direction in enumerate(self.ChannelDirections):
            channelvalue = self.ChannelValues[channel]
            if channelvalue == 0:
                value = False
            else:
                value = True

            # Set the configuation of the io4 bricklet Show error in case ricklet not reachable.
            try:
                # Set the direction and initial value for the chhannel
                self.ioDev.set_configuration(channel, direction, value)
                Domoticz.Debug("Channel=%s, Direction=%s, Value=%s" % (channel, direction, value))

                # Register input value callback to function cb_input_value
                if direction == "i":
                    self.ioDev.register_callback(self.ioDev.CALLBACK_INPUT_VALUE, onInputCallback)
                    # Set period for input value (channel 1) callback to 0.5s (500ms)
                    self.ioDev.set_input_value_callback_configuration(channel, CALLBACKPERIOD, False)
                    Domoticz.Debug("Channel=%s = Callback registered" % (channel))
            except:
                updateStatus(STATUSLEVELERROR, "[ERROR] Set configuration - IO4V2 Bricklet not reachable.")

            # Set the domoticz device value
            if value == True:
                Unit = channel + 1
                Devices[Unit].Update(nValue=1,sValue="")

    def onStop(self):
        Domoticz.Debug("Plugin is stopping.")
        if self.ipConnected == 1:
            self.ipConn.disconnect()

    def onConnect(self, Connection, Status, Description):
        Domoticz.Debug("onConnect called")
        
    def onMessage(self, Connection, Data):
        Domoticz.Debug("onMessage called")

    def onCommand(self, Unit, Command, Level, Hue):
        Domoticz.Debug("onCommand called for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))
        # if command = On then set state on else off
        # The channel is 0-3 but unit 1-4 - ch = u - 1
        Channel = Unit - 1
        try:
            # Trick to test if the IO4 bricklet is reachable
            chiptemperature = self.ioDev.get_chip_temperature()
            
            # Execute command On or Off
            if Command == "On":
                self.ioDev.set_selected_value(Channel, True)
                Devices[Unit].Update(nValue=1,sValue="")
            
            if Command == "Off":
                self.ioDev.set_selected_value(Channel, False)
                Devices[Unit].Update(nValue=0,sValue="")
            
            updateStatus(STATUSLEVELOK, "Command for Unit " + str(Unit) + ": Parameter '" + str(Command) + "', Level: " + str(Level))
        except:
            updateStatus(STATUSLEVELERROR, "[ERROR] IO4V2 Bricklet not reachable.")
            return

    def onNotification(self, Name, Subject, Text, Status, Priority, Sound, ImageFile):
        Domoticz.Debug("Notification: " + Name + "," + Subject + "," + Text + "," + Status + "," + str(Priority) + "," + Sound + "," + ImageFile)

    def onDisconnect(self, Connection):
        Domoticz.Debug("onDisconnect called")
        if self.ipConnected == 1:
            self.ipConn.disconnect()

    def onHeartbeat(self):
        Domoticz.Debug("onHeartbeat called")
        # NOT USED = PLACEHOLDER
        """
        self.HeartbeatCounter = self.HeartbeatCounter + 1
        Domoticz.Debug("onHeartbeat called. Counter=" + str(self.HeartbeatCounter * self.HeartbeatInterval) + " (Heartbeat=" + Parameters["Mode5"] + ")")
        # check the heartbeatcounter against the heartbeatinterval
        if (self.HeartbeatCounter * self.HeartbeatInterval) % int(Parameters["Mode5"]) == 0:
            try:
                #Action
                return
            except:
                #Domoticz.Error("[ERROR] ...")
                return
        """

global _plugin
_plugin = BasePlugin()

def onStart():
    global _plugin
    _plugin.onStart()

def onStop():
    global _plugin
    _plugin.onStop()

def onConnect(Connection, Status, Description):
    global _plugin
    _plugin.onConnect(Connection, Status, Description)

def onMessage(Connection, Data):
    global _plugin
    _plugin.onMessage(Connection, Data)

def onCommand(Unit, Command, Level, Hue):
    global _plugin
    _plugin.onCommand(Unit, Command, Level, Hue)

def onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile):
    global _plugin
    _plugin.onNotification(Name, Subject, Text, Status, Priority, Sound, ImageFile)

def onDisconnect(Connection):
    global _plugin
    _plugin.onDisconnect(Connection)

def onHeartbeat():
    global _plugin
    _plugin.onHeartbeat()

# Generic helper functions
def DumpConfigToLog():
    for x in Parameters:
        if Parameters[x] != "":
            Domoticz.Debug( "'" + x + "':'" + str(Parameters[x]) + "'")
    Domoticz.Debug("Device count: " + str(len(Devices)))
    for x in Devices:
        Domoticz.Debug("Device:           " + str(x) + " - " + str(Devices[x]))
        Domoticz.Debug("Device ID:       '" + str(Devices[x].ID) + "'")
        Domoticz.Debug("Device Name:     '" + Devices[x].Name + "'")
        Domoticz.Debug("Device nValue:    " + str(Devices[x].nValue))
        Domoticz.Debug("Device sValue:   '" + Devices[x].sValue + "'")
        Domoticz.Debug("Device LastLevel: " + str(Devices[x].LastLevel))
    return

# Callback function for input value callback
def onInputCallback(channel, changed, value):
    #
    if changed == True:
        Domoticz.Debug("Channel:" + str(channel) + ",Changed:" + str(changed) + ",Value:" + str(value))
        Unit = channel + 1
        try:
            if value == True:
                Devices[Unit].Update(nValue=1,sValue="")
            else:
                Devices[Unit].Update(nValue=0,sValue="")
            # onCommand(self, Unit, Command, Level, Hue):
        except:
            updateStatus(STATUSLEVELERROR, "[ERROR] IO4V2 Bricklet not reachable.")

# Update the device status with last action
# Alert Level (0=gray, 1=green, 2=yellow, 3=orange, 4=red)
def updateStatus(level,text):
    Devices[UNITSTATUS].Update(nValue=level,sValue=text)
    if level == STATUSLEVELERROR:
        Domoticz.Error(text)
