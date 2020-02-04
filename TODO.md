# Changelog domoticz-plugin-tinkerforge-io4v2
 
### NEW: Parameter to set input channel callback period
The callback period for channels configured as input pull-up, is hardcoded set by 250ms.
Define a new parameter "Mode4" for setting the callbacl period in ms. Default: 500ms.

**Workaround**
Change the variable:
```
# Callbackperiod for pull-up = push-button (set to 250ms)
CALLBACKPERIOD = 250
```

_Status_
Not started.
 
### NEW: Recognise disconnecting the Master brick
If the master brick is disconnected from the USB port, the plugin does not recognize that.
This is because, the ip connection from Domoticz to the Master Brick is made during the function onStart.
A solution could to use the function onHeartbeat and check every 60s (or higher) if the Master Brick is reachable.

**Workaround**
In the function onCommand, the IO4 bricklet chip temperature is checked.
If the bricklet is not reachable, an error is set.

_Status_
Not started.
