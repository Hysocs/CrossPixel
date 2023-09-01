from Components.Settings.Config import save_keybinds_to_file, load_keybinds_from_file
import keyboard
from PyQt5.QtCore import QTimer

class Keybinds:
    _instance = None  # Singleton instance
    
    def __new__(cls):
        # If an instance already exists, return that, else create a new one
        if not isinstance(cls._instance, cls):
            cls._instance = super(Keybinds, cls).__new__(cls)
            
            # Move the initialization code here
            cls._instance.keybinds = load_keybinds_from_file()
            cls._instance.action_map = {}
            cls._instance._hotkeys = {}
            
            # Register the keybinds as global hotkeys
            cls._instance._register_global_hotkeys()
        return cls._instance

    def set_keybind(self, action, key_sequence):
        """Set a keybind for a specific action."""
        self.keybinds[action] = key_sequence

    def get_keybind(self, action):
        """Get the keybind for a specific action."""
        return self.keybinds.get(action)

    def matches(self, action, key_sequence):
        return self.keybinds.get(action) == key_sequence

    def register_action(self, action, func):
        """Register an action with its corresponding function."""
        self.action_map[action] = func

    def execute_action(self, key_sequence):
        """Execute the function corresponding to the given key sequence."""
        for action, bind in self.keybinds.items():
            if bind == key_sequence:
                func = self.action_map.get(action)
                if func:
                    QTimer.singleShot(0, func)
                break

    def _register_global_hotkeys(self):
        """Registers the keybinds as global hotkeys."""
        for action, key_sequence in self.keybinds.items():
            if key_sequence not in self._hotkeys:
                # Add the key_sequence as a global hotkey that triggers execute_action
                self._hotkeys[key_sequence] = keyboard.add_hotkey(key_sequence, lambda ks=key_sequence: self.execute_action(ks))

    def _unregister_global_hotkeys(self):
        """Unregisters the global hotkeys."""
        for key_sequence, hotkey in self._hotkeys.items():
            keyboard.remove_hotkey(hotkey)
        self._hotkeys.clear()

    def update_keybinds(self, new_keybinds):
        """Update keybinds using provided dictionary."""
        # Unregister old hotkeys
        self._unregister_global_hotkeys()
        
        # Update the keybinds
        for action, key_sequence in new_keybinds.items():
            self.set_keybind(action, key_sequence)
        
        # Register new hotkeys
        self._register_global_hotkeys()
        
        # Save updated keybinds to file
        save_keybinds_to_file(self.keybinds)
