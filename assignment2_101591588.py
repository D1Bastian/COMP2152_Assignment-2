"""
Author: John Sebastian Laquis
Assignment: #2
Description: Port Scanner — A tool that scans a target machine for open network ports
"""

# TODO: Import the required modules (Step ii)
# socket, threading, sqlite3, os, platform, datetime
import socket
import threading
import sqlite3
import os
import platform
import datetime



# TODO: Print Python version and OS name (Step iii)
print(f"Pyhton Version: {platform.python_version()}")
print(f"Operating System: {platform.system()} {platform.release()}")



# TODO: Create the common_ports dictionary (Step iv)
# Add a 1-line comment above it explaining what it stores
# Dictionary mapping common port numbers to their typical services
common_ports = {
    20: "FTP Data",
    21: "FTP Control",
    22: "SSH",
    23: "Telnet",
    25: "SMTP",
    53: "DNS",
    80: "HTTP",
    110: "POP3",
    143: "IMAP",
    443: "HTTPS",
    3306: "MySQL",
    3389: "RDP",
    5900: "VNC",
    6379: "Redis",
    8080: "HTTP Proxy",
    8443: "HTTPS Alt"
}


# TODO: Create the NetworkTool parent class (Step v)
# - Constructor: takes target, stores as private self.__target
# - @property getter for target
# - @target.setter with empty string validation
# - Destructor: prints "NetworkTool instance destroyed"
class NetworkTool:
    def __init__(self, target):
        self.__target = target

    @property
    def target(self):
        return self.__target

    @target.setter
    def target(self, value):
        if value == "":
            raise ValueError("Target cannot be empty.")
        self.__target = value

    def __del__(self):
        print("NetworkTool instance destroyed")
        

# Q3: What is the benefit of using @property and @target.setter?
# TODO: Your 2-4 sentence answer here... (Part 2, Q3)
    """Using @property and @target.setter allows for controlled access to the target attribute, 
    ensuring data integrity and providing a clean interface for getting and setting the target value."""

# Q1: How does PortScanner reuse code from NetworkTool?
# TODO: Your 2-4 sentence answer here... (Part 2, Q1)
    """PortScanner inherits from NetworkTool, 
    allowing it to reuse the target management functionality defined in the parent class."""

# TODO: Create the PortScanner child class that inherits from NetworkTool (Step vi)
# - Constructor: call super().__init__(target), initialize self.scan_results = [], self.lock = threading.Lock()
# - Destructor: print "PortScanner instance destroyed", call super().__del__()
class PortScanner(NetworkTool):
    def __init__(self, target):
        super().__init__(target)
        self.scan_results = []
        self.lock = threading.Lock()

    def __del__(self):
        print("PortScanner instance destroyed")
        super().__del__()
#
# - scan_port(self, port):
#     Q4: What would happen without try-except here?
#     TODO: Your 2-4 sentence answer here... (Part 2, Q4)
    """ Without a try-except block, any socket error (like connection refused or timeout)
     would crash the entire program,"""
#
#     - try-except with socket operations
#     - Create socket, set timeout, connect_ex
#     - Determine Open/Closed status
#     - Look up service name from common_ports (use "Unknown" if not found)
#     - Acquire lock, append (port, status, service_name) tuple, release lock
#     - Close socket in finally block
#     - Catch socket.error, print error message
    def scan_port(self, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((self.target, port))
            status = "Open" if result == 0 else "Closed"
            service_name = common_ports.get(port, "Unknown")
            with self.lock:
                self.scan_results.append((port, status, service_name))
        except socket.error as e:
            print(f"Socket error on port {port}: {e}")
        finally:
            sock.close()
            
#
#
    def get_open_ports(self):
        return [result for result in self.scan_results if result[1] == "Open"]
#  - get_open_ports(self):
#     - Use list comprehension to return only "Open" results
#
#     Q2: Why do we use threading instead of scanning one port at a time?
#     TODO: Your 2-4 sentence answer here... (Part 2, Q2)
    """Threading allows us to scan multiple ports simultaneously, 
    significantly reducing the total scan time compared to scanning each port sequentially."""
#
# - scan_range(self, start_port, end_port):
#     - Create threads list
#     - Create Thread for each port targeting scan_port
#     - Start all threads (one loop)
#     - Join all threads (separate loop)
    def scan_range(self, start_port, end_port):
        threads = []
        for port in range(start_port, end_port + 1):
            thread = threading.Thread(target=self.scan_port, args=(port,))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()


# TODO: Create save_results(target, results) function (Step vii)
# - Connect to scan_history.db
# - CREATE TABLE IF NOT EXISTS scans (id, target, port, status, service, scan_date)
# - INSERT each result with datetime.datetime.now()
# - Commit, close
# - Wrap in try-except for sqlite3.Error
def save_results(target, results):
    try:
        conn = sqlite3.connect("scan_history.db")
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scans (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target TEXT,
                port INTEGER,
                status TEXT,
                service TEXT,
                scan_date TEXT
            )
        """)
        for port, status, service in results:
            cursor.execute("""
                INSERT INTO scans (target, port, status, service, scan_date)
                VALUES (?, ?, ?, ?, ?)
            """, (target, port, status, service, datetime.datetime.now().isoformat()))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error: {e}")
    finally:
        conn.close()


# TODO: Create load_past_scans() function (Step viii)
# - Connect to scan_history.db
# - SELECT all from scans
# - Print each row in readable format
# - Handle missing table/db: print "No past scans found."
# - Close connection
def load_past_scans():
    try:
        conn = sqlite3.connect("scan_history.db")
        cursor = conn.cursor()
        cursor.execute("SELECT target, port, status, service, scan_date FROM scans")
        rows = cursor.fetchall()
        if not rows:
            print("No past scans found.")
            return
        for target, port, status, service, scan_date in rows:
            print(f"Target: {target}, Port: {port}, Status: {status}, Service: {service}, Date: {scan_date}")
    except sqlite3.Error:
        print("No past scans found.")
    finally:
        conn.close()


# Q5: New Feature Proposal
# TODO: Your 2-3 sentence description here... (Part 2, Q5)
# Diagram: See diagram_studentID.png in the repository root
"""A useful new feature would be to export the scan results to a CSV file. This would allow users to easily analyze and 
share their scan results using spreadsheet software. It would involve a nested if statement after the scan completes, asking the user if they want to export. If yes,
 The export_to_csv function would take the scan results and write them to a file in a structured format."""
def export_to_csv(results, filename="scan_results.csv"):
    try:
        with open(filename, "w") as f:
            f.write("Port,Status,Service\n")
            for port, status, service in results:
                f.write(f"{port},{status},{service}\n")
        print(f"Results exported to {filename}")
    except Exception as e:
        print("Error exporting to CSV:", e)


# ============================================================
# MAIN PROGRAM
# ============================================================
if __name__ == "__main__":
    
    # TODO: Get user input with try-except (Step ix)
    try:
        target = input("Enter target IP address (default 127.0.0.1): ").strip()
        if not target:
            target = "127.0.0.1"
        start_port = int(input("Enter start port (1-1024): "))
        end_port = int(input("Enter end port (1-1024): "))
        if not (1 <= start_port <= 1024) or not (1 <= end_port <= 1024):
            print("Port must be between 1 and 1024.")
            exit(1)
        if start_port > end_port:
            print("Start port must be less than or equal to end port.")
            exit(1)
    except ValueError:
        print("Invalid input. Please enter a valid integer.")
        exit(1)


    # TODO: After valid input (Step x)
    scanner = PortScanner(target)
    print(f"Scanning {target} from port {start_port} to {end_port}...")
    scanner.scan_range(start_port, end_port)
    open_ports = scanner.get_open_ports()
    for port, status, service in open_ports:
        print(f"Port {port} is {status} ({service})")
    print(f"Total open ports found: {len(open_ports)}")

    save_results(target, scanner.scan_results)

    choice = input("Export results to CSV? (yes/no): ").strip().lower()
    if choice == "yes":
        export_to_csv(scanner.scan_results)

    if input("Would you like to see past scan history? (yes/no): ").strip().lower() == "yes":
        load_past_scans()