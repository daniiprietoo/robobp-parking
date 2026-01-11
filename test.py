from robobopy.Robobo import Robobo
import time

# Robot IP address - update if needed
ROBOT_IP = "192.168.1.48"

robobo = Robobo(ROBOT_IP)
robobo.connect()


robobo.wait(2)

# robobo.movePanTo(90, 20, True)
# robobo.wait(2)

# robobo.movePanTo(0, 20, True)
# robobo.wait(2)

# robobo.moveWheelsByTime(10, 10, 2, True)

# Test QR reading

robobo.startQrTracking()
robobo.moveTiltTo(80, 50, True)
robobo.movePanTo(90, 50, True)
try:
    while True:
        qr = robobo.readQR()
        if qr:
            print(
                f"QR read: id={qr.id}, distance={qr.distance}, data={qr.p1}, {qr.p2}, {qr.p3}"
            )
        else:
            print("No QR code detected")

        robobo.wait(1)
except KeyboardInterrupt:
    print("KeyboardInterrupt detected, stopping all behaviors...")
finally:
    print("Stopping all behaviors...")
    robobo.movePanTo(0, 20, False)
    robobo.stopMotors()
        


robobo.stopMotors()
robobo.disconnect()


print("Disconnected")
