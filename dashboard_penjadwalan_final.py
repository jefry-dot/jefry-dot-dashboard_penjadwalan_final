import streamlit as st
from collections import defaultdict
import pandas as pd

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

# --- Sidebar untuk Input ---
st.sidebar.header("📚 Pilih Mata Kuliah")
selected_courses = st.sidebar.multiselect("Pilih mata kuliah (min 3)", COURSES)

st.sidebar.header("🕒 Pilih Jam Kuliah")
user_preferences = defaultdict(list)

for day in WEEKDAYS:
    # Bold hari dalam multiselect
    selected_times = st.sidebar.multiselect(f"**{day}**", TIME_SLOTS, key=day)
    if selected_times: # Hanya tambahkan jika ada waktu yang dipilih untuk hari itu
        user_preferences[day] = selected_times

# --- Fungsi Logika Penjadwalan ---

def get_available_slots(preferences):
    """
    Menghasilkan daftar semua slot waktu yang tersedia berdasarkan preferensi pengguna.
    """
    slots = []
    for day, times in preferences.items():
        for time in times:
            slots.append(f"{day} {time}")
    return slots

def parse_time_to_minutes(time_str):
    """
    Mengkonversi string waktu (HH:MM) menjadi menit sejak tengah malam.
    """
    try:
        h, m = map(int, time_str.split(":"))
        return h * 60 + m
    except ValueError:
        st.error(f"Format waktu tidak valid: {time_str}. Harap gunakan format HH:MM.")
        st.stop()

def do_slots_overlap(slot1, slot2):
    """
    Memeriksa apakah dua slot yang diberikan bertabrakan.
    """
    if not slot1 or not slot2:
        return False

    day1, time_range1 = slot1.split(" ", 1)
    day2, time_range2 = slot2.split(" ", 1)

    if day1 != day2:
        return False # Slot pada hari yang berbeda tidak bertabrakan

    start1_str, end1_str = time_range1.split("-")
    start2_str, end2_str = time_range2.split("-")

    start1_min = parse_time_to_minutes(start1_str)
    end1_min = parse_time_to_minutes(end1_str)
    start2_min = parse_time_to_minutes(start2_str)
    end2_min = parse_time_to_minutes(end2_str)

    # Overlap terjadi jika satu interval dimulai sebelum interval lain berakhir, dan sebaliknya.
    return start1_min < end2_min and start2_min < end1_min

def generate_schedule(courses, available_slots):
    """
    Mencoba menghasilkan jadwal untuk mata kuliah yang diberikan menggunakan slot yang tersedia.
    Versi ini mencoba menugaskan slot non-konflik pertama.
    Untuk penjadwalan yang lebih kompleks/optimal, algoritma backtracking akan lebih baik.
    """
    schedule = {}
    used_slots = []

    for course in courses:
        assigned = False
        for slot in available_slots:
            # Periksa apakah slot ini bertabrakan dengan slot yang sudah digunakan
            if all(not do_slots_overlap(slot, us) for us in used_slots):
                schedule[course] = slot
                used_slots.append(slot)
                assigned = True
                break
        if not assigned:
            schedule[course] = "❌ Tidak tersedia slot yang cocok"

    return schedule

# --- Proses Penjadwalan Utama dan Tampilan ---

# Tambahkan tombol untuk memicu penjadwalan
if st.sidebar.button("Buat Jadwal"):
    if len(selected_courses) < 3:
        st.warning("Pilih minimal 3 mata kuliah untuk melanjutkan penjadwalan.")
    elif not user_preferences:
        st.warning("Mohon pilih setidaknya satu jam kuliah di sidebar untuk hari yang Anda inginkan.")
    else:
        with st.spinner('Membuat jadwal Anda...'):
            available_slots = get_available_slots(user_preferences)
            if not available_slots:
                st.error("Tidak ada slot waktu yang tersedia berdasarkan preferensi Anda.")
                st.stop()

            schedule = generate_schedule(selected_courses, available_slots)

        st.subheader("📅 Jadwal Kuliah yang Direkomendasikan")
        
        if schedule:
            schedule_data = []
            all_assigned = True
            for course, slot in schedule.items():
                if "❌" in slot:
                    # Hapus simbol silang untuk tampilan yang lebih bersih di tabel
                    schedule_data.append({"Mata Kuliah": course, "Hari": "Tidak Dijadwalkan", "Jam": slot.replace("❌ ", "")})
                    all_assigned = False
                else:
                    day, time_range = slot.split(" ", 1)
                    schedule_data.append({"Mata Kuliah": course, "Hari": day, "Jam": time_range})
            
            df = pd.DataFrame(schedule_data)
            
            # Terapkan styling untuk mata kuliah yang tidak terjadwal
            def highlight_unassigned(row):
                if "Tidak Dijadwalkan" in row["Hari"]:
                    return ['background-color: #ffcccc'] * len(row) # Latar belakang merah muda
                return [''] * len(row)

            st.dataframe(df.style.apply(highlight_unassigned, axis=1), use_container_width=True)

            if not all_assigned:
                st.warning("Beberapa mata kuliah tidak dapat dijadwalkan sesuai preferensi Anda. Mohon sesuaikan pilihan jam atau mata kuliah.")
        else:
            st.error("Tidak ditemukan jadwal yang sesuai berdasarkan preferensi Anda.")