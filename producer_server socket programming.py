import random
import string
import socket
import xml.etree.ElementTree as ET
import time


# =============================================================
#                       STUDENT CLASS
# =============================================================
class ITStudent:
    def __init__(self):
        self.student_name = self.random_name()
        self.student_id = self.random_id()
        self.programme = random.choice(["Diploma IT", "BSc IT", "Software Engineering"])
        self.courses = self.generate_courses()

    def random_name(self):
        first = random.choice(["John", "Mary", "Alex", "Sarah", "James", "Linda"])
        last = random.choice(["Tan", "Lim", "Singh", "Wong", "Omar", "Kumar"])
        return f"{first} {last}"

    def random_id(self):
        return ''.join(random.choices(string.digits, k=8))

    def generate_courses(self):
        course_list = ["Programming", "Networks", "Databases", "Security", "Web Dev"]
        return {c: random.randint(40,100) for c in random.sample(course_list, k=3)}

    def to_xml(self):
        student = ET.Element("student")
        ET.SubElement(student, "name").text = self.student_name
        ET.SubElement(student, "id").text = self.student_id
        ET.SubElement(student, "programme").text = self.programme

        clist = ET.SubElement(student, "courses")
        for c,m in self.courses.items():
            ce = ET.SubElement(clist, "course")
            ET.SubElement(ce, "course_name").text = c
            ET.SubElement(ce, "mark").text = str(m)

        return student


# =============================================================
#                       PRODUCER
# =============================================================
def producer_main():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect(("127.0.0.1", 5001))

    print("[PRODUCER] Connected to server.")

    for i in range(1, 11):
        student = ITStudent()
        xml_data = ET.tostring(student.to_xml(), encoding='unicode')

        file_name = f"student{i}.xml"
        with open(file_name, "w") as f:
            f.write(xml_data)

        print(f"[PRODUCER] Created {file_name}")

        # send file number through socket
        client_socket.send(str(i).encode())
        print(f"[PRODUCER] Sent file number {i}")

        time.sleep(0.5)

    client_socket.close()
    print("[PRODUCER] Finished sending.")


if __name__ == "__main__":
    producer_main()
