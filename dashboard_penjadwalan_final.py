import streamlit as st

st.set_page_config(page_title="Dashboard Jadwal Otomatis", layout="wide")

# Data slot
days = ['senin', 'selasa', 'rabu', 'kamis', 'jumat']
times = ['08:00-10:00', '10:00-12:00', '13:00-15:00', '15:00-17:00']
all_slots = [f"{day} {time}" for day in days for time in times]

# Kelas & Fungsi
class Course:
    def __init__(self, course_name):
        self.course_name = course_name
        self.slots = []

def do_slots_overlap(slot1, slot2):
    if slot1 and slot2:
        day1, time1 = slot1.split(" ")
        day2, time2 = slot2.split(" ")
        if day1 != day2:
            return False
        start1, end1 = map(lambda x: int(x.split(":")[0]) * 60 + int(x.split(":")[1]), time1.split("-"))
        start2, end2 = map(lambda x: int(x.split(":")[0]) * 60 + int(x.split(":")[1]), time2.split("-"))
        return start1 < end2 and start2 < end1
    return False

def generate_schedule_from_choices(courses):
    n = len(courses)
    schedule = [None] * n
    for i in range(n):
        best_slot = None
        for slot in courses[i].slots:
            if all(not do_slots_overlap(slot, schedule[j]) for j in range(i)):
                best_slot = slot
                break
        schedule[i] = best_slot
    return [(courses[i].course_name, schedule[i] if schedule[i] else "Tidak tersedia jadwal") for i in range(n)]

# UI Input
st.title("📅 Dashboard Jadwal Otomatis (4 Matkul)")

with st.form("jadwal_form"):
    course_inputs = []
    for i in range(4):
        st.markdown(f"### Mata Kuliah {i+1}")
        course_name = st.text_input(f"Nama Mata Kuliah {i+1}", key=f"name_{i}")
        selected_slots = st.multiselect(
            f"Pilih 3 slot waktu untuk matkul {i+1}:", all_slots, max_selections=3, key=f"slots_{i}"
        )
        course_inputs.append((course_name, selected_slots))

    submitted = st.form_submit_button("🔍 Cari Jadwal")

# Proses
if submitted:
    courses = []
    valid = True

    for name, slots in course_inputs:
        if not name or len(slots) != 3:
            valid = False
            break
        course = Course(name)
        course.slots = slots
        courses.append(course)

    if not valid:
        st.warning("Pastikan setiap mata kuliah memiliki nama dan tepat 3 slot dipilih.")
    else:
        result = generate_schedule_from_choices(courses)
        st.subheader("📆 Jadwal Terbaik (Tanpa Tabrakan):")
        for course, slot in result:
            st.markdown(f"- **{course}** → `{slot}`")
