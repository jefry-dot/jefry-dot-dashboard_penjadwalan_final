import streamlit as st
from collections import defaultdict

# Data waktu yang tersedia
WEEKDAYS = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat"]
TIME_SLOTS = ["08:00-10:00", "10:00-12:00", "13:00-15:00", "15:00-17:00"]

# Daftar mata kuliah
COURSES = [
    "Dasar Digital", "Struktur Data", "Interaksi Manusia dan Komputer", "Sistem Operasi",
    "Kecerdasan Buatan", "Grafika Komputer", "Desain dan Analisis Algoritma", "Bahasa Indonesia",
    "Metode Numerik", "Pemrograman Web", "Sistem Management Database", "Etika Profesi",
    "Pemrograman Visual", "Tekno Enterpreneur", "Statistika", "Organisasi dan Arsitektur Komputer"
]

st.set_page_config(page_title="Penjadwalan Kuliah", layout="wide")
st.title("📘 Penjadwalan Mata Kuliah Mahasiswa")

st.markdown("""
Silakan pilih **minimal 3 mata kuliah** dan preferensi jam kuliah untuk masing-masing hari. Sistem akan menyusun jadwal tanpa tabrakan waktu.
""")

# Sidebar untuk input
st.sidebar.header("📚 Pilih Mata Kuliah")
selected_courses = st.sidebar.multiselect("Pilih mata kuliah (min 3)", COURSES)

# Validasi jumlah mata kuliah
if len(selected_courses) < 3:
    st.warning("Pilih minimal 3 mata kuliah untuk melanjutkan penjadwalan.")
    st.stop()

st.sidebar.header("🕒 Pilih Jam Kuliah")
user_preferences = defaultdict(list)

for day in WEEKDAYS:
    selected_times = st.sidebar.multiselect(f"{day}", TIME_SLOTS, key=day)
    if len(selected_times) > 0:
        user_preferences[day] = selected_times

# Generate semua kombinasi slot dari preferensi user
def get_available_slots(preferences):
    slots = []
    for day, times in preferences.items():
        for time in times:
            slots.append(f"{day} {time}")
    return slots

def do_slots_overlap(slot1, slot2):
    if slot1 and slot2:
        day1, time1 = slot1.split(" ")
        day2, time2 = slot2.split(" ")
        if day1 != day2:
            return False
        s1, e1 = map(lambda t: int(t.split(":" )[0])*60 + int(t.split(":" )[1]), time1.split("-"))
        s2, e2 = map(lambda t: int(t.split(":" )[0])*60 + int(t.split(":" )[1]), time2.split("-"))
        return s1 < e2 and s2 < e1
    return False

def generate_schedule(courses, available_slots):
    schedule = {}
    used_slots = []

    for course in courses:
        for slot in available_slots:
            # Cek apakah slot ini sudah dipakai atau tabrakan dengan yang lain
            if all(not do_slots_overlap(slot, us) for us in used_slots):
                schedule[course] = slot
                used_slots.append(slot)
                break
        if course not in schedule:
            schedule[course] = "❌ Tidak tersedia slot sesuai preferensi"

    return schedule

# Proses generate
available_slots = get_available_slots(user_preferences)
schedule = generate_schedule(selected_courses, available_slots)

# Tampilkan hasil
st.subheader("📅 Jadwal Kuliah yang Direkomendasikan")

if schedule:
    for course, slot in schedule.items():
        st.markdown(f"**{course}**: {slot}")
else:
    st.error("Tidak ditemukan jadwal yang sesuai.")
