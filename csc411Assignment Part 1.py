import random
import string
import threading
import xml.etree.ElementTree as ET
import time
import os

# =============================================================
#                 ITStudent CLASS (unchanged)
# =============================================================
class ITStudent:
    def __init__(self):
        self.student_name = self.random_name()
        self.student_id = self.random_id()
        self.programme = random.choice(["Diploma IT", "BSc IT", "Software Engineering"])
        self.courses = self.generate_courses()

    def random_name(self):
        first = random.choice(["John", "Mary", "Alex", "Sarah", "James", "Linda"])
        last = random.choice(["Tan", "Lim", "Omar", "Singh", "Wong", "Kumar"])
        return f"{first} {last}"

    def random_id(self):
        return ''.join(random.choices(string.digits, k=8))

    def generate_courses(self):
        course_list = ["Programming", "Networks", "Databases", "Web Dev", "Security"]
        courses = {}
        for course in random.sample(course_list, k=3):
            courses[course] = random.randint(40, 100)
        return courses

    def to_xml(self):
        student = ET.Element("student")

        name = ET.SubElement(student, "name")
        name.text = self.student_name

        sid = ET.SubElement(student, "id")
        sid.text = self.student_id

        prog = ET.SubElement(student, "programme")
        prog.text = self.programme

        course_list = ET.SubElement(student, "courses")
        for c, m in self.courses.items():
            course_el = ET.SubElement(course_list, "course")

            cname = ET.SubElement(course_el, "course_name")
            cname.text = c

            mark = ET.SubElement(course_el, "mark")
            mark.text = str(m)

        return student


# =============================================================
#                 BUFFER USING SEMAPHORES
# =============================================================
class Buffer:
    def __init__(self, size=10):
        self.size = size
        self.buffer = []

        # Semaphores
        self.empty = threading.Semaphore(size)  # Start with all empty slots
        self.full = threading.Semaphore(0)      # Initially buffer is empty
        self.mutex = threading.Semaphore(1)     # Mutex for mutual exclusion

    def insert(self, item):
        self.empty.acquire()       # Wait if buffer is full
        self.mutex.acquire()       # Exclusive access

        self.buffer.append(item)
        print(f"[BUFFER] Inserted {item}. Buffer size: {len(self.buffer)}")

        self.mutex.release()
        self.full.release()        # Signal that buffer now has one more full slot

    def remove(self):
        self.full.acquire()        # Wait if buffer is empty
        self.mutex.acquire()       # Exclusive access

        item = self.buffer.pop(0)
        print(f"[BUFFER] Removed {item}. Buffer size: {len(self.buffer)}")

        self.mutex.release()
        self.empty.release()       # Signal that buffer now has one more empty slot

        return item


# =============================================================
#                 PRODUCER THREAD
# =============================================================
class Producer(threading.Thread):
    def __init__(self, buffer, directory=".", num_files=10):
        super().__init__()
        self.buffer = buffer
        self.directory = directory
        self.num_files = num_files

    def run(self):
        for i in range(1, self.num_files + 1):
            student = ITStudent()
            xml_element = student.to_xml()
            xml_data = ET.tostring(xml_element, encoding="unicode")

            file_name = f"{self.directory}/student{i}.xml"
            with open(file_name, "w") as f:
                f.write(xml_data)

            print(f"[Producer] Created {file_name}")

            self.buffer.insert(i)  # Insert file number into buffer

            time.sleep(0.5)


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
            try:
                file_num = self.buffer.remove()
            except:
                print("[Consumer] Error reading from buffer")
                continue

            file_name = f"{self.directory}/student{file_num}.xml"
            if not os.path.exists(file_name):
                print(f"[Consumer] ERROR: {file_name} does not exist")
                continue

            print(f"[Consumer] Processing {file_name}")

            tree = ET.parse(file_name)
            root = tree.getroot()

            print(f"   Name: {root.find('name').text}")
            print(f"   ID: {root.find('id').text}")
            print(f"   Programme: {root.find('programme').text}")
            print("   Courses:")

            for course in root.find("courses"):
                c_name = course.find("course_name").text
                mark = course.find("mark").text
                print(f"      {c_name}: {mark}")

            time.sleep(0.5)


# =============================================================
#                 MAIN PROGRAM
# =============================================================
if __name__ == "__main__":
    shared_buffer = Buffer(size=10)

    producer = Producer(shared_buffer)
    consumer = Consumer(shared_buffer)

    producer.start()
    consumer.start()

    producer.join()
    # Consumer runs indefinitely unless stopped manually
