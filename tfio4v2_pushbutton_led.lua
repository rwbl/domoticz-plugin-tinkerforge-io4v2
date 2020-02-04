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