-- Tinkerforge IO4 v2 Bricklet Plugin - Test Script 
-- dzVents Automation Script: tfio4v2_blink_led
--
-- There are two switch devices used:
-- (Idx,Name,Type,SubType - Hardware Connected)
-- Idx=76, TFIO4 - IO4 Channel 0,Light/Switch,Switch,On/Off - LED Blue
-- Idx=77, TFIO4 - IO4 Channel 1,Light/Switch,Switch,On/Off - Push-Button DFRobot
-- Test:
-- Turn every minute the LED Blue ON | OFF triggered by changing the state of the push-button switch
--
-- 20200102 by rwbL

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
