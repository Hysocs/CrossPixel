import os
import gc
import psutil
import threading

class MemoryManager:
    def __init__(self):
        self.buffer = None
        self.print_lock = threading.Lock()

        # Start a thread to monitor memory usage
        self.monitor_thread = threading.Thread(target=self._monitor_memory_usage)
        self.monitor_thread.daemon = True  # Set as a daemon so it exits when the main program exits
        self.monitor_thread.start()

    def _get_current_memory_usage(self):
        """Return the current memory usage details of the process."""
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()

        rss = mem_info.rss / (1024 * 1024)  # Convert to MB
        vms = mem_info.vms / (1024 * 1024)  # Convert to MB
        
        return {
            "RSS": rss,
            "VMS": vms
        }

    def _get_system_usage(self):
        """Return the current CPU usage percentage."""
        cpu_usage = psutil.cpu_percent(interval=1)
        gpu_usage = 0  # Set GPU usage to 0, skipping GPU monitoring

        return cpu_usage, gpu_usage

    def allocate_memory(self, size: int, data=None):
        """Allocate or resize memory to the given size and prevent buffer overflow."""
        with self.print_lock:
            if not isinstance(size, int) or size <= 0:
                print("Invalid memory size. It must be a positive integer.")
                return

            if data and len(data) > size:
                print("Data size exceeds the buffer size. Avoiding buffer overflow.")
                return

            if self.buffer:
                current_size = len(self.buffer)
                if size > current_size:
                    self.buffer.extend(bytearray(size - current_size))
                    print(f"Resized buffer to {size / (1024 * 1024):.2f} MB (increased).")
                elif size < current_size:
                    del self.buffer[size:]
                    print(f"Resized buffer to {size / (1024 * 1024):.2f} MB (decreased).")
            else:
                self.buffer = bytearray(size)
                print(f"Allocated memory of size {size / (1024 * 1024):.2f} MB.")

            if data:
                self.buffer[:len(data)] = data

    def allocate_based_on_current_usage(self):
        """Allocate memory based on 10% of the current memory usage."""
        current_usage = self._get_current_memory_usage()
        size_to_allocate = int(current_usage * 0.10 * 1024 * 1024)  # Convert MB to bytes for allocation
        self.allocate_memory(size_to_allocate)

    def release_memory(self):
        """Release the allocated memory."""
        with self.print_lock:
            if self.buffer:
                self.buffer.clear()  # Clear the contents of the bytearray
                self.buffer = None   # De-reference the buffer
                print("Memory has been released.")
            gc.collect()  # Run garbage collector to free up memory

    def _monitor_memory_usage(self):
        """Monitor memory usage, CPU and GPU usage, and adjust allocation dynamically."""
        previous_usage = {"RSS": 0, "VMS": 0}
        while True:
            current_usage = self._get_current_memory_usage()
            cpu_usage, gpu_usage = self._get_system_usage()

            #print(f"Current CPU Usage: {cpu_usage:.2f}%")

            # Compare the RSS for memory usage adjustments
            if cpu_usage > 50 and current_usage["RSS"] > 1.1 * previous_usage["RSS"]:
                # If CPU usage exceeds 80% and memory usage increased by more than 10%
                # we trim down the memory to the bare minimum (for demonstration, using 0.01 times current usage)
                size_to_allocate = int(current_usage["RSS"] * 0.01 * 1024 * 1024)
                self.allocate_memory(size_to_allocate)
                print("Reducing memory due to high CPU usage.")
            elif current_usage["RSS"] > 1.1 * previous_usage["RSS"]:
                # If only memory usage increased by more than 10%
                size_to_allocate = int(current_usage["RSS"] * 0.10 * 1024 * 1024)
                self.allocate_memory(size_to_allocate)
            elif current_usage["RSS"] < 0.9 * previous_usage["RSS"]:
                self.release_memory()

            previous_usage = current_usage  # Update the previous usage to the current usage
            threading.Event().wait(8)  # Check roughly every 8 seconds


    def __del__(self):
        self.release_memory()

class MemoryHandler:
    def __init__(self, main_window, save_modules=None):
        """Initialize the MemoryHandler."""
        self.main_window = main_window
        self.memory_manager = MemoryManager()
        self.memory_manager.allocate_based_on_current_usage()
        self.save_modules = save_modules or []

    def handle_module(self, module_name, action):
        """Handle specific modules for saving/loading to/from disk."""
        with self.memory_manager.print_lock:
            if module_name in self.save_modules:
                if action == 'save':
                    print(f"(Placeholder) Saving {module_name} to disk...")
                    # Implement logic for saving the module data to disk.
                elif action == 'load':
                    print(f"(Placeholder) Loading {module_name} from disk...")
                    # Implement logic for loading the module data from disk.

    def closeEvent(self, event):
        """This method is called when the window is closed."""
        self.memory_manager.release_memory()  # Release the memory
