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
Silakan pilih **satu per satu** mata kuliah dan preferensi jam kuliah untuk masing-masing hari. Mata kuliah yang sudah berhasil dijadwalkan akan dihapus dari daftar pilihan.
""")

# --- Inisialisasi Session State ---
if 'remaining_courses' not in st.session_state:
    st.session_state.remaining_courses = list(COURSES) # Salin daftar mata kuliah awal
if 'current_schedule' not in st.session_state:
    st.session_state.current_schedule = {} # Menyimpan jadwal yang sudah dibuat
if 'used_slots_tracker' not in st.session_state:
    st.session_state.used_slots_tracker = [] # Untuk melacak slot yang sudah terpakai

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

def generate_schedule_single(course, available_slots, current_used_slots):
    """
    Mencoba menjadwalkan satu mata kuliah menggunakan slot yang tersedia,
    memperhitungkan slot yang sudah digunakan sebelumnya.
    """
    assigned_slot = "❌ Tidak tersedia slot yang cocok"
    
    for slot in available_slots:
        # Periksa apakah slot ini bertabrakan dengan slot yang sudah digunakan
        if all(not do_slots_overlap(slot, us) for us in current_used_slots):
            assigned_slot = slot
            break
    
    return assigned_slot

# --- Sidebar untuk Input ---
st.sidebar.header("📚 Pilih Mata Kuliah")

# Gunakan selectbox untuk memilih satu mata kuliah
# Pastikan ada mata kuliah yang tersisa untuk dipilih
if st.session_state.remaining_courses:
    selected_single_course = st.sidebar.selectbox(
        "Pilih mata kuliah yang akan dijadwalkan",
        st.session_state.remaining_courses,
        key="single_course_selector" # Tambahkan key untuk mengatasi peringatan Streamlit
    )
else:
    st.sidebar.info("Tidak ada mata kuliah tersisa untuk dijadwalkan.")
    selected_single_course = None


st.sidebar.header("🕒 Pilih Jam Kuliah")
user_preferences = defaultdict(list)

for day in WEEKDAYS:
    # Bold hari dalam multiselect
    selected_times = st.sidebar.multiselect(f"**{day}**", TIME_SLOTS, key=day)
    if selected_times: # Hanya tambahkan jika ada waktu yang dipilih untuk hari itu
        user_preferences[day] = selected_times

# --- Proses Penjadwalan Utama dan Tampilan ---

st.sidebar.markdown("---") # Garis pemisah di sidebar

if st.sidebar.button("Jadwalkan Mata Kuliah Ini"):
    if not selected_single_course:
        st.warning("Pilih mata kuliah terlebih dahulu.")
    elif not user_preferences:
        st.warning("Mohon pilih setidaknya satu jam kuliah di sidebar untuk hari yang Anda inginkan.")
    else:
        with st.spinner(f'Mencoba menjadwalkan **{selected_single_course}**...'):
            available_slots = get_available_slots(user_preferences)
            if not available_slots:
                st.error("Tidak ada slot waktu yang tersedia berdasarkan preferensi Anda.")
            else:
                # Gunakan used_slots_tracker dari session_state
                assigned_slot = generate_schedule_single(
                    selected_single_course, 
                    available_slots, 
                    st.session_state.used_slots_tracker
                )
                
                if "❌" not in assigned_slot:
                    st.session_state.current_schedule[selected_single_course] = assigned_slot
                    st.session_state.used_slots_tracker.append(assigned_slot)
                    # Hapus mata kuliah yang sudah dijadwalkan dari daftar sisa
                    if selected_single_course in st.session_state.remaining_courses:
                        st.session_state.remaining_courses.remove(selected_single_course)
                    st.success(f"'{selected_single_course}' berhasil dijadwalkan!")
                    st.experimental_rerun() # Refresh UI untuk memperbarui daftar pilihan
                else:
                    st.error(f"'{selected_single_course}': {assigned_slot}. Coba ubah preferensi jam atau cek konflik.")

st.sidebar.markdown("---")
if st.sidebar.button("Reset Jadwal"):
    st.session_state.remaining_courses = list(COURSES)
    st.session_state.current_schedule = {}
    st.session_state.used_slots_tracker = []
    st.experimental_rerun() # Refresh UI untuk kembali ke kondisi awal

# --- Tampilan Jadwal yang Sudah Dibuat ---
st.subheader("📅 Jadwal Kuliah yang Direkomendasikan")

if st.session_state.current_schedule:
    schedule_data = []
    for course, slot in st.session_state.current_schedule.items():
        if "❌" in slot:
            # Hapus simbol silang untuk tampilan yang lebih bersih di tabel
            schedule_data.append({"Mata Kuliah": course, "Hari": "Tidak Dijadwalkan", "Jam": slot.replace("❌ ", "")})
        else:
            day, time_range = slot.split(" ", 1)
            schedule_data.append({"Mata Kuliah": course, "Hari": day, "Jam": time_range})
    
    df = pd.DataFrame(schedule_data)
    
    # Terapkan styling untuk mata kuliah yang tidak terjadwal (jika ada)
    def highlight_unassigned(row):
        if "Tidak Dijadwalkan" in row["Hari"]:
            return ['background-color: #ffcccc'] * len(row) # Latar belakang merah muda
        return [''] * len(row)

    st.dataframe(df.style.apply(highlight_unassigned, axis=1), use_container_width=True)
else:
    st.info("Belum ada mata kuliah yang dijadwalkan. Pilih mata kuliah dan jam di sidebar, lalu klik 'Jadwalkan Mata Kuliah Ini'.")

if st.session_state.remaining_courses:
    st.markdown(f"**Mata Kuliah Tersisa untuk Dijadwalkan:** {', '.join(st.session_state.remaining_courses)}")
else:
    st.success("🎉 Semua mata kuliah telah berhasil dijadwalkan!")