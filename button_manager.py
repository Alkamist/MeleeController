import keyboard

from state import State


base_keys = {
    "!" : "1",
    "@" : "2",
    "#" : "3",
    "$" : "4",
    "%" : "5",
    "^" : "6",
    "&" : "7",
    "*" : "8",
    "(" : "9",
    ")" : "0",
    "_" : "-",
    "+" : "=",
    "{" : "[",
    "}" : "]",
    "|" : "\\",
    ":" : ";",
    "\"" : "'",
    "<" : ",",
    ">" : ".",
    "?" : "/",
    "~" : "`",
}


def get_base_key(key_name):
    if key_name in base_keys:
        return base_keys[key_name]
    else:
        if len(key_name) == 1:
            return key_name.lower()
        else:
            return key_name


class ButtonManager(object):
    def __init__(self, key_binds):
        self.key_binds = key_binds

        self.buttons = {}
        for name in self.key_binds:
            self.buttons[name] = State()

        self.key_binds_reversed = {}
        for bind_name, bind_value in self.key_binds.items():
            if isinstance(bind_value, tuple):
                for i in range(len(bind_value)):
                    self.key_binds_reversed[bind_value[i]] = bind_name
            else:
                self.key_binds_reversed[bind_value] = bind_name

        self.key_is_pressed = {}
        for key_name in self.key_binds_reversed:
            self.key_is_pressed[key_name] = False

        self.parsed_binds = []
        for bind_name, bind_value in self.key_binds.items():
            if isinstance(bind_value, tuple):
                for i in range(len(bind_value)):
                    self.parsed_binds.append(keyboard.parse_hotkey(bind_value[i]))
            else:
                self.parsed_binds.append(keyboard.parse_hotkey(bind_value))

        self.bind_keys()

    def update(self):
        for button in self.buttons.values():
            button.update()

    def bind_keys(self):
        keyboard.unhook_all()
        for key in self.parsed_binds:
            keyboard.on_press_key(key, self._on_press_key, True)
            keyboard.on_release_key(key, self._on_release_key, True)

        keyboard.block_key(".") # Prevent windows emoji menu.
        keyboard.block_key("=") # Prevent windows magnifier.
        keyboard.block_key("e") # Prevent windows explorer.
        keyboard.block_key("q") # Prevent windows search.

    def unbind_keys(self):
        keyboard.unhook_all()
        script_toggle_key = keyboard.parse_hotkey(self.key_binds["toggle_script"])
        keyboard.on_press_key(script_toggle_key, self._on_press_key, True)
        keyboard.on_release_key(script_toggle_key, self._on_release_key, True)

    def _on_press_key(self, key):
        key_name = get_base_key(key.name)

        if key_name in self.key_binds_reversed:
            self.key_is_pressed[key_name] = True
            bind_name = self.key_binds_reversed[key_name]
            self.buttons[bind_name].is_active = True

    def _on_release_key(self, key):
        key_name = get_base_key(key.name)

        if key_name in self.key_binds_reversed:
            bind_name = self.key_binds_reversed[key_name]

            another_same_bind_is_pressed = False
            if isinstance(self.key_binds[bind_name], tuple):
                for physical_key in self.key_binds[bind_name]:
                    if key_name != physical_key and self.key_is_pressed[physical_key]:
                        another_same_bind_is_pressed = True

            if not another_same_bind_is_pressed:
                self.buttons[bind_name].is_active = False

            self.key_is_pressed[key_name] = False
