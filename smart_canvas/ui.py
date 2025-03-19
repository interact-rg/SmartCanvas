# Types
UI_State = dict[str, str|float]
from cv2.typing import MatLike
from web.main.common_events import send_ui_state, send_image, send_hand_position



class Progressbar:
    """
    Create a progress bar badly with quads. Simply scale the vertex translation matrix
    to create an illusion of progress bar
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
    def __init__(self, sid: str, is_webapp: bool = False):
        self.keys: dict[str, bool] = {}
        self.progressbar = Progressbar()
        self.sid = sid
        self.is_webapp = is_webapp

    def set_prog(self, value: float):
        self.progressbar.value = value
        if self.is_webapp:
            send_ui_state({"hold_timer": value}, self.sid)
    
    def set_timer(self, value: float):
        if self.is_webapp:
            send_ui_state({"timer": value}, self.sid)
    
    def set_filter(self, value: str):
        if self.is_webapp:
            send_ui_state({"filter": value}, self.sid)

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

    def set_wrist_position(self, position: tuple[float, float]):
        send_hand_position(position, self.sid)

    def get_state(self) -> UI_State:
        state: dict[str, bool|float] = {}

        for k, value in self.keys.items():
            if value:
                state[k] = value
        state["hold_timer"] = self.progressbar.value
        return state