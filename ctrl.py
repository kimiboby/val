import hid

BTN_LEFT = 1
BTN_RIGHT = 2
BTN_MIDDLE = 4
BTN_ALL = BTN_LEFT | BTN_RIGHT | BTN_MIDDLE

class HIDMouseController:
    def __init__(self, device):
        self._button_state = 0
        self._device = device
        self.move(0, 0)

    @classmethod
    def initialize(cls, code=0xaa):
        device = locate_device(code)
        return cls(device)

    def _update_button_state(self, new_state):
        if new_state != self._button_state:
            self._button_state = new_state
            self.move(0, 0)

    def trigger(self, button=BTN_LEFT):
        self._button_state = button
        self.move(0, 0)
        self._button_state = 0
        self.move(0, 0)

    def hold(self, button=BTN_LEFT):
        self._update_button_state(self._button_state | button)

    def let_go(self, button=BTN_LEFT):
        self._update_button_state(self._button_state & ~button)

    def is_holding(self, button=BTN_LEFT):
        return (button & self._button_state) > 0

    def move(self, dx, dy):
        x, y = self._constrain(dx), self._constrain(dy)
        report = self._prepare_report(x, y)
        self._device.write(report)

    def _prepare_report(self, dx, dy):
        return [
            0x01,
            self._button_state,
            dx & 0xFF, (dx >> 8) & 0xFF,
            dy & 0xFF, (dy >> 8) & 0xFF
        ]

    def _constrain(self, value):
        return max(min(value, 32767), -32767)

class MissingDeviceError(Exception):
    pass

def ping_device(device, code):
    device.write([0, code])
    try:
        response = device.read(max_length=1, timeout_ms=10)
        return response and response[0] == code
    except OSError:
        return False

def locate_device(code):
    mouse_device = hid.device()
    for info in hid.enumerate():
        mouse_device.open_path(info['path'])
        if ping_device(mouse_device, code):
            return mouse_device
        mouse_device.close()
    raise MissingDeviceError
