import psutil
import time
import signal
import sys
import os
import threading
import numpy as np

class MemoryStressor:
    def __init__(self, target_memory_increase_gb=1):  # 20% of 2GB is approximately 0.4GB
        self.stop_event = threading.Event()
        self.target_memory_increase = target_memory_increase_gb
        self.memory_chunks = []

    def allocate_memory(self):
        """
        Continuously allocate memory chunks to stress the system
        """
        try:
            while not self.stop_event.is_set():
                # Create a large numpy array to consume memory
                chunk = np.zeros((100000, 100000), dtype=np.float32)
                self.memory_chunks.append(chunk)
                
                # Check current memory usage
                current_memory = psutil.virtual_memory().used / (1024 * 1024 * 1024)
                print(f"Current memory usage: {current_memory:.2f} GB")
                
                time.sleep(0.5)  # Small pause to prevent overwhelming the system
        except Exception as e:
            print(f"Memory allocation error: {e}")

    def monitor_memory(self):
        """
        Monitor memory usage and print stats
        """
        try:
            while not self.stop_event.is_set():
                mem = psutil.virtual_memory()
                print(f"Memory Usage: {mem.percent}% | Used: {mem.used/(1024*1024*1024):.2f} GB")
                time.sleep(2)
        except Exception as e:
            print(f"Memory monitoring error: {e}")

    def cleanup(self):
        """
        Release all allocated memory
        """
        print("\nCleaning up allocated memory...")
        for chunk in self.memory_chunks:
            del chunk
        self.memory_chunks.clear()
        print("Memory cleanup complete.")

    def run(self):
        """
        Start memory allocation and monitoring threads
        """
        allocation_thread = threading.Thread(target=self.allocate_memory)
        monitoring_thread = threading.Thread(target=self.monitor_memory)

        allocation_thread.start()
        monitoring_thread.start()

        # Wait for keyboard interrupt
        signal.signal(signal.SIGINT, self.handle_interrupt)
        signal.pause()

    def handle_interrupt(self, signum, frame):
        """
        Handle Ctrl+C interrupt
        """
        print("\nInterrupt received. Stopping memory stress test...")
        self.stop_event.set()
        self.cleanup()
        sys.exit(0)

def main():
    print("Starting Memory Stress Test")
    print("Press Ctrl+C to stop the test and clean memory")
    
    stressor = MemoryStressor()
    stressor.run()

if __name__ == "__main__":
    main()
