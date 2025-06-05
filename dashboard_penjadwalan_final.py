import streamlit as st

# Setup
st.set_page_config(page_title="Dashboard Jadwal Kuliah", layout="wide")

# Hari dan Jam
days = ['senin', 'selasa', 'rabu', 'kamis', 'jumat']
times = ['08:00-10:00', '10:00-12:00', '13:00-15:00', '15:00-17:00']
all_slots = [f"{day} {time}" for day in days for time in times]

# Kelas dan Fungsi
class Course:
    def __init__(self, course_name, slots):
        self.course_name = course_name
        self.slots = slots

def do_slots_overlap(slot1, slot2):
    if slot1 and slot2:
        day1, time1 = slot1.split(" ")
        day2, time2 = slot2.split(" ")
        if day1 != day2:
            return False
        start1, end1 = time1.split("-")
        start2, end2 = time2.split("-")
        start1 = int(start1.split(":")[0]) * 60 + int(start1.split(":")[1])
        end1 = int(end1.split(":")[0]) * 60 + int(end1.split(":")[1])
        start2 = int(start2.split(":")[0]) * 60 + int(start2.split(":")[1])
        end2 = int(end2.split(":")[0]) * 60 + int(end2.split(":")[1])
        return start1 < end2 and start2 < end1
    return False

def generate_schedule(course_list, selected_courses, preferred_slots):
    selected = [c for c in course_list if c.course_name in selected_courses]
    n = len(selected)
    schedule = [None] * n

    for i in range(n):
        best_slot = None
        for slot in selected[i].slots:
            if slot not in preferred_slots:
                continue
            is_valid_slot = True
            for j in range(i):
                if do_slots_overlap(slot, schedule[j]):
                    is_valid_slot = False
                    break
            if is_valid_slot:
                best_slot = slot
                break
        schedule[i] = best_slot

    return [(selected[i].course_name, schedule[i] if schedule[i] else "Tidak tersedia jadwal") for i in range(n)]

# Data Mata Kuliah
course_list = [
    Course("Dasar digital", ["senin 10:00-12:00", "selasa 10:00-12:00", "rabu 13:00-15:00"]),
    Course("Struktur data", ["senin 14:00-16:00", "selasa 08:00-10:00", "rabu 10:00-12:00"]),
    Course("Interaksi manusia dan komputer", ["senin 08:00-10:00", "kamis 14:00-16:00", "jumat 13:00-15:00"]),
    Course("Sistem operasi", ["selasa 07:00-09:00", "kamis 10:00-12:00", "jumat 10:00-12:00"]),
    Course("Kecerdasan buatan", ["senin 13:00-15:00", "rabu 14:00-16:00", "jumat 08:00-10:00"]),
    Course("Grafika komputer", ["selasa 13:00-15:00", "rabu 15:00-17:00", "jumat 10:00-12:00"]),
    Course("Desain dan analisis algoritma", ["rabu 08:00-10:00", "kamis 13:00-15:00", "jumat 14:00-16:00"]),
    Course("Bahasa Indonesia", ["senin 13:00-15:00", "selasa 16:00-18:00", "rabu 08:00-10:00"]),
    Course("Metode numerik", ["rabu 10:00-12:00", "kamis 13:00-15:00", "jumat 15:00-17:00"]),
    Course("Pemrograman web", ["selasa 10:00-12:00", "kamis 14:00-16:00", "jumat 08:00-10:00"]),
    Course("Sistem management database", ["senin 15:00-17:00", "rabu 10:00-12:00", "kamis 14:00-16:00"]),
    Course("Etika profesi", ["senin 08:00-10:00", "selasa 10:00-12:00", "rabu 13:00-15:00"]),
    Course("Pemrograman visual", ["senin 14:00-16:00", "selasa 08:00-10:00", "rabu 10:00-12:00"]),
    Course("Tekno enterpreneur", ["senin 13:00-15:00", "selasa 14:00-16:00", "jumat 10:00-12:00"]),
    Course("Statistika", ["rabu 08:00-10:00", "kamis 13:00-15:00", "jumat 14:00-16:00"]),
    Course("Organisasi dan arsitektur komputer", ["selasa 10:00-12:00", "kamis 14:00-16:00", "jumat 08:00-10:00"]),
]

# UI
st.title("📚 Dashboard Jadwal Kuliah")

selected_courses = st.multiselect("Pilih mata kuliah:", [c.course_name for c in course_list])
preferred_slots = st.multiselect("Pilih slot waktu yang kamu sukai (minimal 3):", all_slots)

if st.button("🔍 Buat Jadwal"):
    if len(selected_courses) < 1:
        st.warning("Pilih minimal 1 mata kuliah.")
    elif len(preferred_slots) < 3:
        st.warning("Pilih minimal 3 slot waktu.")
    else:
        result = generate_schedule(course_list, selected_courses, preferred_slots)
        st.subheader("📅 Jadwal Direkomendasikan:")
        for course, slot in result:
            st.markdown(f"- **{course}** → `{slot}`")
