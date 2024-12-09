import psutil
import time
import signal
import sys
import os
import multiprocessing
import traceback

class MemoryStressor:
    def __init__(self, target_memory_increase_gb=1):  # 20% of 2GB is approximately 0.4GB
        self.target_memory_increase = target_memory_increase_gb * 1024 * 1024 * 1024  # Convert to bytes
        self.memory_chunks = multiprocessing.Manager().list()
        self.stop_event = multiprocessing.Event()

    def allocate_memory(self):
        """
        Continuously allocate memory chunks to stress the system
        """
        try:
            while not self.stop_event.is_set():
                try:
                    # Allocate a large chunk of memory
                    chunk = bytearray(int(self.target_memory_increase / 10))  # Split into 10 chunks
                    
                    # Modify the memory to ensure it's not optimized away
                    for i in range(0, len(chunk), 1000):
                        chunk[i] = i % 256
                    
                    self.memory_chunks.append(chunk)
                    
                    # Check current memory usage
                    current_memory = psutil.virtual_memory().used / (1024 * 1024 * 1024)
                    print(f"Current memory usage: {current_memory:.2f} GB")
                    
                    time.sleep(1)  # Small pause between allocations
                except MemoryError:
                    print("Memory allocation limit reached")
                    break
        except Exception as e:
            print(f"Memory allocation error: {e}")
            traceback.print_exc()

    def monitor_memory(self):
        """
        Monitor memory usage and print stats
        """
        try:
            while not self.stop_event.is_set():
                try:
                    mem = psutil.virtual_memory()
                    print(f"Memory Usage: {mem.percent}% | Used: {mem.used/(1024*1024*1024):.2f} GB")
                    time.sleep(2)
                except Exception as e:
                    print(f"Memory monitoring error: {e}")
                    break
        except Exception as e:
            print(f"Unexpected monitoring error: {e}")
            traceback.print_exc()

    def cleanup(self):
        """
        Release all allocated memory
        """
        print("\nCleaning up allocated memory...")
        try:
            # Explicitly delete memory chunks
            while self.memory_chunks:
                chunk = self.memory_chunks.pop()
                del chunk
            
            # Force garbage collection
            import gc
            gc.collect()
            print("Memory cleanup complete.")
        except Exception as e:
            print(f"Error during cleanup: {e}")
            traceback.print_exc()

    def run(self):
        """
        Start memory allocation and monitoring processes
        """
        try:
            # Create processes
            allocation_process = multiprocessing.Process(target=self.allocate_memory)
            monitoring_process = multiprocessing.Process(target=self.monitor_memory)

            # Start processes
            allocation_process.start()
            monitoring_process.start()

            # Wait for keyboard interrupt
            signal.signal(signal.SIGINT, self.handle_interrupt)
            
            # Block main thread
            signal.pause()

        except Exception as e:
            print(f"Error during execution: {e}")
            traceback.print_exc()
        finally:
            # Ensure processes are terminated
            if allocation_process.is_alive():
                allocation_process.terminate()
            if monitoring_process.is_alive():
                monitoring_process.terminate()

    def handle_interrupt(self, signum, frame):
        """
        Handle Ctrl+C interrupt
        """
        print("\nInterrupt received. Stopping memory stress test...")
        
        # Set stop event to signal processes to stop
        self.stop_event.set()
        
        # Cleanup memory
        self.cleanup()
        
        # Exit the program
        sys.exit(0)

def main():
    print("Starting Memory Stress Test")
    print("Press Ctrl+C to stop the test and clean memory")
    
    stressor = MemoryStressor()
    stressor.run()

if __name__ == "__main__":
    # Ensure proper multiprocessing support on macOS
    multiprocessing.set_start_method('spawn')
    main()
