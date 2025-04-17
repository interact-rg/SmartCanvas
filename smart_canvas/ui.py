# Types
UI_State = dict[str, str|float]
from typing import Dict, List
from cv2.typing import MatLike
from web.main.common_events import send_ui_state, send_filter, send_image, send_hand_position, send_qr, send_acknowledge, send_fingertip_position

class Progressbar:
    """
    Representation of the progress bar in the UI.
    """

    def __init__(self):
        self.visible: bool = True
        self._value = 0.0


    @property
    def value(self) -> float:
        return self._value

    @value.setter
    def value(self, value: float):
        if value < 0.0:
            self._value = 0.0
        else:
            self._value = value

class TextElement:
    def __init__(self):
        self.visible: bool = False
        self.text = ""
        self.scale = 0.0

    def draw(self):
        pass


class UI:
    """
    Class for managing UI elements
    """
    def __init__(self, sid: str, is_webapp: bool = False, base_url: str | None = None):
        self.progressbar = Progressbar()
        self.sid = sid
        self.is_webapp = is_webapp
        self.base_url: str | None = base_url  # <-- Actually assign a default value
        self.keys: dict[str, bool] = {}

    def set_prog(self, value: float, max: float = 1.0):
        self.progressbar.value = value / max
        if self.is_webapp:
            send_ui_state({"hold_timer": self.progressbar.value}, self.sid)
    
    def set_fingertip_position(self, position: tuple[float, float]):
        """Sends index fingertip position data using the common_events helper."""
        if self.is_webapp:
            send_fingertip_position(position, self.sid)

    def set_timer(self, value: float):
        if self.is_webapp:
            send_ui_state({"timer": value}, self.sid)
    
    def set_filter(self, name: str, performance: float):
        if self.is_webapp:
            send_filter(name, performance, self.sid)

    def show(self, *names: str):
        for name in names:
            self.keys[name] = True
        if self.is_webapp:
            send_ui_state({key: True for key in names}, self.sid)

    def hide(self, *names: str):
        for name in names:
            self.keys[name] = False
        if self.is_webapp:
            send_ui_state({key: False for key in names}, self.sid)

    def show_image(self, image: MatLike):
        send_image(image, self.sid)

    def show_qr(self, image_id: str):
        """Generate and send a QR code to the client."""
        if not self.base_url:
            print(f"[ERROR] Base URL is not set for UI instance (sid: {self.sid}). Cannot generate QR code.")
            return  # Exit early if base_url is not set

        # Call send_qr with the valid base_url
        send_qr(image_id, self.sid, self.base_url)

    def set_wrist_position(self, position: tuple[float, float]):
        send_hand_position(position, self.sid)

    def ready(self):
        if self.is_webapp:
            send_acknowledge(self.sid)

    def get_state(self) -> UI_State:
        state: dict[str, bool|float] = {}

        for k, value in self.keys.items():
            if value:
                state[k] = value
        state["hold_timer"] = self.progressbar.value
        return state
    
