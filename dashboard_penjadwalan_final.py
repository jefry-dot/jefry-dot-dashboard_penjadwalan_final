import streamlit as st
import pandas as pd

# Class untuk merepresentasikan Mata Kuliah
class Course:
    def __init__(self, course_name, slots):
        self.course_name = course_name
        self.slots = slots

# Fungsi untuk mengecek bentrok antar slot waktu
def do_slots_overlap(slot1, slot2):
    if not slot1 or not slot2:
        return False

    day1, time1 = slot1.split(" ", 1)
    day2, time2 = slot2.split(" ", 1)
    if day1 != day2:
        return False

    def time_to_minutes(t):
        h, m = map(int, t.split(":"))
        return h * 60 + m

    s1, e1 = map(time_to_minutes, time1.split("-"))
    s2, e2 = map(time_to_minutes, time2.split("-"))

    return max(s1, s2) < min(e1, e2)

# Fungsi utama untuk menghasilkan jadwal optimal
def generate_schedule(selected_courses, all_courses_data):
    courses = [c for c in all_courses_data if c.course_name in selected_courses]
    n = len(courses)
    current = [None] * n
    best = None
    max_ok = 0

    def backtrack(k):
        nonlocal best, max_ok
        if k == n:
            ok = sum(1 for x in current if x)
            if ok > max_ok:
                max_ok = ok
                best = list(current)
            return

        for slot in courses[k].slots:
            if all(not do_slots_overlap(slot, current[i]) for i in range(k)):
                current[k] = slot
                backtrack(k + 1)
                current[k] = None
        backtrack(k + 1)

    backtrack(0)

    hasil = []
    for i in range(n):
        name = courses[i].course_name
        slot = best[i] if best and best[i] else "Tidak tersedia slot tanpa bentrok"
        hasil.append((name, slot))

    all_slots = {(c.course_name, s) for c in all_courses_data for s in c.slots}
    used = {(c, s) for c, s in hasil if s != "Tidak tersedia slot tanpa bentrok"}
    saran = sorted(list(all_slots - used))

    return hasil, saran

# --- Streamlit UI ---
st.set_page_config(layout="wide")
st.title("📅 Aplikasi Penjadwalan Kuliah Otomatis")

if 'courses' not in st.session_state:
    st.session_state.courses = [
        Course("Dasar Digital", ["Senin 10:00-12:00", "Selasa 10:00-12:00", "Rabu 13:00-15:00"]),
        Course("Struktur Data", ["Senin 14:00-16:00", "Selasa 08:00-10:00", "Rabu 10:00-12:00"]),
        Course("Interaksi Manusia dan Komputer", ["Senin 08:00-10:00", "Kamis 14:00-16:00", "Jumat 13:00-15:00"]),
        Course("Sistem Operasi", ["Selasa 07:00-09:00", "Kamis 10:00-12:00", "Jumat 10:00-12:00"]),
        Course("Kecerdasan Buatan", ["Senin 13:00-15:00", "Rabu 14:00-16:00", "Jumat 08:00-10:00"]),
        Course("Grafika Komputer", ["Selasa 13:00-15:00", "Rabu 15:00-17:00", "Jumat 10:00-12:00"]),
        Course("Desain dan Analisis Algoritma", ["Rabu 08:00-10:00", "Kamis 13:00-15:00", "Jumat 14:00-16:00"]),
        Course("Bahasa Indonesia", ["Senin 13:00-15:00", "Selasa 16:00-18:00", "Rabu 08:00-10:00"]),
        Course("Metode Numerik", ["Rabu 10:00-12:00", "Kamis 13:00-15:00", "Jumat 15:00-17:00"]),
        Course("Pemrograman Web", ["Selasa 10:00-12:00", "Kamis 14:00-16:00", "Jumat 08:00-10:00"]),
        Course("Sistem Management Database", ["Senin 15:00-17:00", "Rabu 10:00-12:00", "Kamis 14:00-16:00"]),
        Course("Etika Profesi", ["Senin 08:00-10:00", "Selasa 10:00-12:00", "Rabu 13:00-15:00"]),
        Course("Pemrograman Visual", ["Senin 14:00-16:00", "Selasa 08:00-10:00", "Rabu 10:00-12:00"]),
        Course("Tekno Enterpreneur", ["Senin 13:00-15:00", "Selasa 14:00-16:00", "Jumat 10:00-12:00"]),
        Course("Statistika", ["Rabu 08:00-10:00", "Kamis 13:00-15:00", "Jumat 14:00-16:00"]),
        Course("Organisasi dan Arsitektur Komputer", ["Selasa 10:00-12:00", "Kamis 14:00-16:00", "Jumat 08:00-10:00"]),
    ]

# ======================== Kolom 1: Input Data ========================
col1, col2 = st.columns([1, 2])

with col1:
    st.header("📚 Mata Kuliah yang Tersedia")
    if st.session_state.courses:
        df = pd.DataFrame({
            "Mata Kuliah": [c.course_name for c in st.session_state.courses],
            "Slot Tersedia": [', '.join(c.slots) for c in st.session_state.courses]
        })
        st.dataframe(df, height=300)

# ======================== Kolom 2: Penjadwalan ========================
with col2:
    st.header("2. Pilih Mata Kuliah untuk Dijadwalkan")
    course_names = [c.course_name for c in st.session_state.courses]
    selected = st.multiselect("Pilih mata kuliah:", course_names)

    if st.button("📆 Buat Jadwal Optimal"):
        if len(selected) < 3:
            st.warning("Pilih minimal 3 mata kuliah.")
        else:
            jadwal, saran = generate_schedule(selected, st.session_state.courses)
            data = []
            valid = 0
            for name, slot in jadwal:
                if slot.startswith("Tidak"):
                    data.append({"Mata Kuliah": name, "Slot Jadwal": f"⚠️ {slot}"})
                else:
                    data.append({"Mata Kuliah": name, "Slot Jadwal": slot})
                    valid += 1

            if valid >= 3:
                st.success(f"{valid} mata kuliah berhasil dijadwalkan.")
            else:
                st.error("Jadwal valid kurang dari 3.")

            st.dataframe(pd.DataFrame(data), hide_index=True)
            st.subheader("Saran Slot Lain")
            if saran:
                st.dataframe(pd.DataFrame(saran, columns=["Mata Kuliah", "Slot Waktu"]), hide_index=True)
            else:
                st.info("Tidak ada slot saran tersedia.")
