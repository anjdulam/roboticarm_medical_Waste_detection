import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout
from PyQt5.QtCore import Qt, QThread, QTimer
import time
import smbus


# PCA9685 Registers
MODE1 = 0x00
PRESCALE = 0xFE
LED0_ON_L = 0x06

# PCA9685 Constants
I2C_BUS = 1  # I2C bus number
PCA9685_ADDRESS = 0x40  # I2C address of PCA9685
FREQUENCY = 50  # PWM frequency (Hz)
SERVO_MIN = 500  # Min pulse length for servos (0 degrees)
SERVO_MAX = 2500  # Max pulse length for servos (180 degrees)
SERVO_RANGE = SERVO_MAX - SERVO_MIN  # Pulse length range for servos

class ServoControlThread(QThread):
    u_angle = 40
    d_angle = 135
    l_angle = 80
    r_angle = 80
    o_angle = 60

    def __init__(self):
        super().__init__()
        self.bus = smbus.SMBus(I2C_BUS)
        self.set_pwm_frequency(self.bus, PCA9685_ADDRESS, FREQUENCY)
        self.moving_up = False
        self.moving_down = False
        self.moving_left = False
        self.moving_right = False
        self.moving_default = False
        self.open_grip = False
        self.close_grip = False

    def set_pwm_frequency(self, bus, address, frequency):
        prescale_val = int((25000000 / (4096 * frequency)) - 1)
        bus.write_byte_data(address, MODE1, 0x10)  # Sleep mode
        bus.write_byte_data(address, PRESCALE, prescale_val)
        bus.write_byte_data(address, MODE1, 0x00)  # Wake up

    def set_servo_angle(self, bus, address, channel, angle):
        pulse_width = SERVO_MIN + (float(angle) / 180.0) * SERVO_RANGE
        pulse_width_value = int(pulse_width * 4096 / 20000)  # Convert to 12-bit value
        # Set the PWM pulse for the servo motor
        bus.write_byte_data(address, LED0_ON_L + 4 * channel, 0x00)
        bus.write_byte_data(address, LED0_ON_L + 4 * channel + 1, 0x00)
        bus.write_byte_data(address, LED0_ON_L + 4 * channel + 2, pulse_width_value & 0xFF)
        bus.write_byte_data(address, LED0_ON_L + 4 * channel + 3, pulse_width_value >> 8)

    def default_pos(self):
        self.set_servo_angle(self.bus, PCA9685_ADDRESS, 0, 60)
        self.set_servo_angle(self.bus, PCA9685_ADDRESS, 5, 80)
        self.set_servo_angle(self.bus, PCA9685_ADDRESS, 4, 40)
        self.set_servo_angle(self.bus, PCA9685_ADDRESS, 3, 120)
        self.set_servo_angle(self.bus, PCA9685_ADDRESS, 2, 40)
        self.set_servo_angle(self.bus, PCA9685_ADDRESS, 1, 90)

    def move_Up(self):
        self.u_angle += 1
        self.set_servo_angle(self.bus, PCA9685_ADDRESS, 4, self.u_angle)  # Move up

    def move_Down(self):
        self.u_angle -= 1
        self.set_servo_angle(self.bus, PCA9685_ADDRESS, 4, self.u_angle)  # Move down

    def move_Left(self):
        self.l_angle += 1
        self.set_servo_angle(self.bus, PCA9685_ADDRESS, 5, self.l_angle)  # Move left

    def move_Right(self):
        self.l_angle -= 1
        self.set_servo_angle(self.bus, PCA9685_ADDRESS, 5, self.l_angle)  # Move right

    def gripper_Open(self):
        self.set_servo_angle(self.bus, PCA9685_ADDRESS, 0, 60)
        self.o_angle = 60  # Open gripper

    def gripper_Close(self):
        if self.o_angle < 115:
            self.o_angle += 5
            self.set_servo_angle(self.bus, PCA9685_ADDRESS, 0, self.o_angle)  # Close gripper

    def run(self):
        while True:
            if self.moving_up:
                self.move_Up()
            if self.moving_down:
                self.move_Down()
            if self.moving_left:
                self.move_Left()
            if self.moving_right:
                self.move_Right()
            if self.moving_default:
                self.default_pos()
            if self.open_grip:
                self.gripper_Open()
            if self.close_grip:
                self.gripper_Close()

            time.sleep(0.01)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.servo_thread = ServoControlThread()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Servo Control")
        self.setGeometry(100, 100, 300, 200)

        # Set layout
        layout = QVBoxLayout()
        self.setLayout(layout)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_W:
            self.servo_thread.moving_up = True
        elif event.key() == Qt.Key_S:
            self.servo_thread.moving_down = True
        elif event.key() == Qt.Key_A:
            self.servo_thread.moving_left = True
        elif event.key() == Qt.Key_D:
            self.servo_thread.moving_right = True
        elif event.key() == Qt.Key_P:
            self.servo_thread.moving_default = True
        elif event.key() == Qt.Key_O:
            self.servo_thread.open_grip = True
        elif event.key() == Qt.Key_C:
            self.servo_thread.close_grip = True

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_W:
            self.servo_thread.moving_up = False
        elif event.key() == Qt.Key_S:
            self.servo_thread.moving_down = False
        elif event.key() == Qt.Key_A:
            self.servo_thread.moving_left = False
        elif event.key() == Qt.Key_D:
            self.servo_thread.moving_right = False
        elif event.key() == Qt.Key_P:
            self.servo_thread.moving_default = False
        elif event.key() == Qt.Key_O:
            self.servo_thread.open_grip = False
        elif event.key() == Qt.Key_C:
            self.servo_thread.close_grip = False

    def closeEvent(self, event):
        self.servo_thread.quit()
        self.servo_thread.wait()
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.servo_thread.start()
    sys.exit(app.exec_())
