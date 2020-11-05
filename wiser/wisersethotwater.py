from wiserHeatingAPI import wiserHub
#from .util import convert_to_wiser_schedule, convert_from_wiser_schedule

import logging
import json
import time

_LOGGER = logging.getLogger(__name__)
_LOGGER.setLevel(logging.DEBUG)

wiserHub._LOGGER.setLevel(logging.DEBUG)

# Get Wiser Parameters from keyfile
with open("wiserkeys.params", "r") as f:
    data = f.read().split("\n")
wiserkey = ""
wiserip = ""
schedulefile = "./hotwaterschedule-off.json"
schedulebackup = "./backupschedule.json"

# Get wiserkey/hubIp from wiserkeys.params file
# This file is not source controlled as it contains the testers secret etc

for lines in data:
    line = lines.split("=")
    if line[0] == "wiserkey":
        wiserkey = line[1]
    if line[0] == "wiserhubip":
        wiserip = line[1]

print(" Wiser Hub IP= {} , WiserKey= {}".format(wiserip, wiserkey))


try:
    wh = wiserHub.wiserHub(wiserip, wiserkey)

    print("display all data")
    print(json.dumps(wh.getHubData(), indent=2))
          
    print("-------------------------------")
    print("Running tests")
    print("-------------------------------")
    print ("Model # {}".format(wh.getWiserHubName()))
    # Display some states
    # Heating State
    print("Hot water status: {} ".format(wh.getHotwaterRelayStatus()))
    data = wh.getHotwater()
    print("Hotwater {} ".format(json.dumps(data,indent=2)))
    print("Hotwater schedule: {} ".format(data["ScheduleId"]))

    print("--------------------------------")
    print("List of Devices")
    print("--------------------------------")

    for device in wh.getDevices():
        print(
            "Device : Id {} Name {} Type {} , SignalStrength {}  ".format(
                device.get("id"),
                device.get("Name"),
                device.get("ProductType"),
                device.get("DisplayedSignalStrength"),
            )
        )

    print("--------------------------------")
    print("Saving Hotwater schedule to file")
    with open(schedulebackup, "w") as f:
        data = wh.getHotwaterSchedule()
        json.dump(data, f)
        f.close()
        print("File {} created ".format(schedulebackup))
    print("--------------------------------")
    print("Set room schedule for Hotwater")
    with open(schedulebackup, "r") as f:
        data = json.load(f)
        wh.setHotwaterSchedule(data)

        print(
            "Schedule for hotwater loaded indirectly from file {}".format(schedulebackup)
        )
    # Load schedule and set direct from file
    print("--------------------------------")
    print("Set hotwater schedule from file")
    wh.setHotwaterScheduleFromFile(schedulefile)
    print("Schedule for hotwater loaded directly from file {}".format(schedulefile))
    print("--------------------------------")

    #  List all Rooms
    findValve = 0
    roomName = None

    print("--------------------------------")
    print("Listing all Rooms")
    print("--------------------------------")
    for room in wh.getRooms():
        smartValves = room.get("SmartValveIds")
        roomStat = room.get("RoomStatId")
        if smartValves is None and roomStat is None:
            print(
                "Room {} has no roomStats or smartValves".format(
                    room.get("Name")
                )
            )
        else:
            print(
                "Room {}, setpoint={}C, current temp={}C".format(
                    room.get("Name"),
                    room.get("CurrentSetPoint") / 10,
                    room.get("CalculatedTemperature") / 10,
                )
            )

    print("--------------------------------")
    print("Listing all smartplugs")
    print("--------------------------------")

    # Find and set smartPlug on off
    if wh.getSmartPlugs() is not None:
        for smartPlug in wh.getSmartPlugs():
            smartPlugId = smartPlug.get("id")
            print(
                "Smartplug ID {} Name {} OutputState is {} Mode is {}".format(
                    smartPlug.get("id"),
                    smartPlug.get("Name"),
                    wh.getSmartPlugState(smartPlugId),
                    wh.getSmartPlugMode(smartPlugId),
                )
            )
            print("Bouncing Plug {} ".format(smartPlugId))
            originalPlugState = wh.getSmartPlugState(smartPlugId)
            if originalPlugState == "On":
                wh.setSmartPlugState(smartPlug.get("id"), "Off")
                time.sleep(1)
            else:
                wh.setSmartPlugState(smartPlug.get("id"), "On")
                time.sleep(1)
            # Set back to original state
            wh.setSmartPlugState(smartPlugId, originalPlugState)


# Other Examples
# Setting HOME Mode , change to AWAY for away mode
#    wh.setHomeAwayMode("HOME")
#    wh.setHomeAwayMode("AWAY",10)
# Set room 4 TRVs to off, which is -200
#    print( wh.getRoom(4).get("Name"))
#    wh.setRoomMode(4,"off")
# Set room 4 TRVs to manual, setting normal scheduled temp
#    wh.setRoomMode(4,"manual")
# Set temperature of room 4 to 13C
#    wh.setRoomTemperature(4,10)
# Set TRV off in room 4 to Off
#    wh.setRoomTemperature(4,-20)

except json.decoder.JSONDecodeError as ex:
    print("JSON Exception")
