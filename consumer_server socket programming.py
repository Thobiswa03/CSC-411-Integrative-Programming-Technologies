import socket
import threading
import xml.etree.ElementTree as ET
import os
import time


# =============================================================
#                 BUFFER USING SEMAPHORES
# =============================================================
class Buffer:
    def __init__(self, size=10):
        self.size = size
        self.buffer = []

        self.empty = threading.Semaphore(size)  # buffer has SIZE empty slots
        self.full = threading.Semaphore(0)      # starts empty
        self.mutex = threading.Semaphore(1)     # exclusive access

    def insert(self, item):
        self.empty.acquire()
        self.mutex.acquire()

        self.buffer.append(item)
        print(f"[BUFFER] Inserted {item}. Size = {len(self.buffer)}")

        self.mutex.release()
        self.full.release()

    def remove(self):
        self.full.acquire()
        self.mutex.acquire()

        item = self.buffer.pop(0)
        print(f"[BUFFER] Removed {item}. Size = {len(self.buffer)}")

        self.mutex.release()
        self.empty.release()
        return item


# =============================================================
#                 CONSUMER THREAD
# =============================================================
class Consumer(threading.Thread):
    def __init__(self, buffer, directory="."):
        super().__init__()
        self.buffer = buffer
        self.directory = directory

    def run(self):
        while True:
            file_num = self.buffer.remove()

            file_name = f"{self.directory}/student{file_num}.xml"
            if not os.path.exists(file_name):
                print(f"[Consumer] ERROR: {file_name} missing.")
                continue

            print(f"[Consumer] Processing {file_name}")

            tree = ET.parse(file_name)
            root = tree.getroot()

            print("   Name:", root.find("name").text)
            print("   ID:", root.find("id").text)
            print("   Programme:", root.find("programme").text)
            print("   Courses:")
            for course in root.find("courses"):
                cname = course.find("course_name").text
                mark = course.find("mark").text
                print(f"      {cname}: {mark}")

            time.sleep(0.3)


# =============================================================
#                 SERVER SOCKET (Accepts Producer)
# =============================================================
def server_main():
    shared_buffer = Buffer(10)
    consumer = Consumer(shared_buffer)
    consumer.start()

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 5001))
    server_socket.listen(1)

    print("\n[SERVER] Waiting for producer to connect...")
    conn, addr = server_socket.accept()
    print(f"[SERVER] Producer connected from: {addr}\n")

    while True:
        data = conn.recv(1024).decode()
        if not data:
            break

        file_num = int(data.strip())
        print(f"[SERVER] Received file number: {file_num}")

        shared_buffer.insert(file_num)

    conn.close()
    print("[SERVER] Producer disconnected.")


if __name__ == "__main__":
    server_main()
