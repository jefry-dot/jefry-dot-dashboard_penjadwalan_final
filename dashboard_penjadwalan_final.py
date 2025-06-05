import streamlit as st
import pandas as pd
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
Silakan pilih satu mata kuliah dan waktu kuliah yang kamu inginkan, lalu klik "Buat Jadwal". Mata kuliah yang sudah dijadwalkan akan hilang dari daftar.
""")

# Inisialisasi session state
if "selected_courses" not in st.session_state:
    st.session_state.selected_courses = COURSES.copy()
if "schedule" not in st.session_state:
    st.session_state.schedule = []

# Sidebar
st.sidebar.header("📚 Pilih Mata Kuliah")
selected_course = st.sidebar.selectbox("Pilih satu mata kuliah", st.session_state.selected_courses)

st.sidebar.header("🕒 Pilih Jam Kuliah")
user_preferences = {}
for day in WEEKDAYS:
    selected_times = st.sidebar.selectbox(f"{day}", ["-"] + TIME_SLOTS, key=day)
    if selected_times != "-":
        user_preferences[day] = selected_times

# Fungsi bantu

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

# Buat slot gabungan
def get_user_slots(preferences):
    return [f"{day} {time}" for day, time in preferences.items()]

# Tombol eksekusi
if st.sidebar.button("📅 Buat Jadwal"):
    chosen_slots = get_user_slots(user_preferences)

    if not chosen_slots:
        st.warning("Pilih minimal satu slot waktu terlebih dahulu.")
    else:
        # Cek apakah slot bentrok dengan yang sudah dijadwalkan
        is_conflict = False
        for _, s in st.session_state.schedule:
            for new_slot in chosen_slots:
                if do_slots_overlap(s, new_slot):
                    is_conflict = True
                    break

        if is_conflict:
            st.error("Jadwal bentrok dengan mata kuliah yang sudah dipilih.")
        else:
            # Tambahkan jadwal
            st.session_state.schedule.append((selected_course, chosen_slots[0]))
            st.session_state.selected_courses.remove(selected_course)
            st.success(f"Jadwal untuk '{selected_course}' berhasil ditambahkan!")

# Tampilkan jadwal yang sudah dibuat
st.subheader("📊 Jadwal Kuliah Anda")
if st.session_state.schedule:
    df = pd.DataFrame(st.session_state.schedule, columns=["Mata Kuliah", "Slot Waktu"])
    st.dataframe(df, hide_index=True, use_container_width=True)
else:
    st.info("Belum ada jadwal yang dibuat.")
