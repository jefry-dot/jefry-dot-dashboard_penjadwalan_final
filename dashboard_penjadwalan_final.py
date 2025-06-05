import streamlit as st
import pandas as pd

# Class untuk merepresentasikan Mata Kuliah
class Course:
    def __init__(self, course_name, slots):
        self.course_name = course_name
        self.slots = slots

# Fungsi untuk mengecek bentrok antar slot waktu
def do_slots_overlap(slot1, slot2):
    if slot1 is None or slot2 is None:
        return False

    day1, time1 = slot1.split(" ", 1) # Split hanya pada spasi pertama untuk menangani nama hari dengan spasi
    day2, time2 = slot2.split(" ", 1)

    if day1 != day2:
        return False

    def time_to_minutes(time_str):
        h, m = map(int, time_str.split(":"))
        return h * 60 + m

    start1_str, end1_str = time1.split("-")
    start2_str, end2_str = time2.split("-")

    start1_min = time_to_minutes(start1_str)
    end1_min = time_to_minutes(end1_str)
    start2_min = time_to_minutes(start2_str)
    end2_min = time_to_minutes(end2_str)

    # Mengecek apakah ada tumpang tindih waktu
    return max(start1_min, start2_min) < min(end1_min, end2_min)

# Fungsi utama untuk menghasilkan jadwal
def generate_schedule(selected_courses, all_courses_data):
    # Mengonversi data course yang dipilih ke objek Course
    courses_to_schedule = []
    for course_name in selected_courses:
        for course_data in all_courses_data:
            if course_data.course_name == course_name:
                courses_to_schedule.append(course_data)
                break

    if not courses_to_schedule:
        return [], [] # Tidak ada mata kuliah yang dipilih

    n = len(courses_to_schedule)
    current_schedule = [None] * n
    best_schedule = None
    max_courses_scheduled = 0

    # Menggunakan rekursi dan backtracking untuk mencari jadwal terbaik
    def find_best_schedule(k):
        nonlocal best_schedule, max_courses_scheduled
        if k == n:
            # Semua mata kuliah telah dicoba dijadwalkan
            scheduled_count = sum(1 for slot in current_schedule if slot is not None)
            if scheduled_count > max_courses_scheduled:
                max_courses_scheduled = scheduled_count
                best_schedule = list(current_schedule) # Salin jadwal terbaik saat ini
            return

        current_course = courses_to_schedule[k]
        found_slot_for_current_course = False
        for slot in current_course.slots:
            is_valid_slot = True
            for i in range(k):
                if do_slots_overlap(slot, current_schedule[i]):
                    is_valid_slot = False
                    break
            if is_valid_slot:
                current_schedule[k] = slot
                find_best_schedule(k + 1)
                found_slot_for_current_course = True
                current_schedule[k] = None # Backtrack

        # Jika tidak ada slot yang valid untuk mata kuliah saat ini, coba tanpa menjadwalkannya
        if not found_slot_for_current_course:
            current_schedule[k] = None
            find_best_schedule(k + 1)

    find_best_schedule(0)

    optimal_schedule_output = []
    if best_schedule:
        for i in range(n):
            course_name = courses_to_schedule[i].course_name
            slot = best_schedule[i]
            if slot:
                optimal_schedule_output.append((course_name, slot))
            else:
                optimal_schedule_output.append((course_name, "Tidak tersedia slot tanpa bentrok"))

    # Menentukan slot yang tidak terpakai/belum dipilih
    all_possible_slots = set()
    for course_data in all_courses_data:
        for slot in course_data.slots:
            all_possible_slots.add((course_data.course_name, slot))

    used_slots_in_optimal_schedule = set()
    for course_name, slot in optimal_schedule_output:
        if slot != "Tidak tersedia slot tanpa bentrok":
            used_slots_in_optimal_schedule.add((course_name, slot))

    unused_slots_suggestions = sorted(list(all_possible_slots - used_slots_in_optimal_schedule))

    return optimal_schedule_output, unused_slots_suggestions

# --- Streamlit UI ---
st.set_page_config(layout="wide")
st.title("Aplikasi Penjadwalan Kuliah Otomatis")

if 'courses' not in st.session_state:
    st.session_state.courses = []

# Kolom untuk input mata kuliah
col1, col2 = st.columns([1, 2])

with col1:
    st.header("1. Masukkan Mata Kuliah")
    with st.form("add_course_form"):
        new_course_name = st.text_input("Nama Mata Kuliah", key="new_course_name_input")
        new_course_slots_str = st.text_area(
            "Slot Waktu (pisahkan dengan koma, contoh: Senin 08:00-10:00, Selasa 10:00-12:00)",
            key="new_course_slots_input"
        )
        add_course_button = st.form_submit_button("Tambahkan Mata Kuliah")

        if add_course_button and new_course_name and new_course_slots_str:
            slots_list = [s.strip() for s in new_course_slots_str.split(',')]
            if len(st.session_state.courses) < 16:
                st.session_state.courses.append(Course(new_course_name, slots_list))
                st.success(f"Mata kuliah '{new_course_name}' berhasil ditambahkan.")
            else:
                st.warning("Maksimal 16 mata kuliah telah tercapai.")
        elif add_course_button:
            st.warning("Nama mata kuliah dan setidaknya satu slot waktu harus diisi.")

    st.subheader("Mata Kuliah yang Tersedia:")
    if st.session_state.courses:
        course_names = [course.course_name for course in st.session_state.courses]
        df_courses = pd.DataFrame({
            "Mata Kuliah": course_names,
            "Slot Tersedia": [", ".join(c.slots) for c in st.session_state.courses]
        })
        st.dataframe(df_courses, height=250)
        if st.button("Bersihkan Semua Mata Kuliah"):
            st.session_state.courses = []
            st.rerun()
    else:
        st.info("Belum ada mata kuliah yang ditambahkan.")

with col2:
    st.header("2. Pilih Mata Kuliah untuk Dijadwalkan")
    if st.session_state.courses:
        all_course_names = [course.course_name for course in st.session_state.courses]
        selected_courses = st.multiselect(
            "Pilih mata kuliah yang ingin dijadwalkan:",
            options=all_course_names,
            key="selected_courses_multiselect"
        )

        st.info(f"Anda memilih **{len(selected_courses)}** mata kuliah.")
        st.caption("Pastikan untuk memilih mata kuliah yang Anda inginkan.")

        if st.button("Buat Jadwal Optimal"):
            if len(selected_courses) < 3:
                st.warning("Anda harus memilih minimal 3 mata kuliah untuk dijadwalkan.")
            else:
                st.subheader("Jadwal Kuliah Optimal Anda:")
                optimal_schedule, unused_suggestions = generate_schedule(selected_courses, st.session_state.courses)

                scheduled_count = 0
                schedule_data = []
                for course_name, slot in optimal_schedule:
                    if slot != "Tidak tersedia slot tanpa bentrok":
                        schedule_data.append({"Mata Kuliah": course_name, "Slot Jadwal": slot})
                        scheduled_count += 1
                    else:
                        schedule_data.append({"Mata Kuliah": course_name, "Slot Jadwal": f"⚠️ {slot}"}) # Menandai yang bentrok

                if scheduled_count >= 3:
                    st.success(f"Ditemukan **{scheduled_count}** mata kuliah tanpa bentrok.")
                    df_schedule = pd.DataFrame(schedule_data)
                    st.dataframe(df_schedule, hide_index=True, use_container_width=True)

                    st.markdown("---")
                    st.subheader("Saran Slot Waktu Lain / Tidak Terpakai")
                    if unused_suggestions:
                        unused_df = pd.DataFrame(unused_suggestions, columns=["Mata Kuliah", "Slot Waktu"])
                        st.dataframe(unused_df, hide_index=True, use_container_width=True)
                        st.info("Ini adalah slot waktu dari mata kuliah yang tidak digunakan dalam jadwal optimal Anda, atau dari mata kuliah yang tidak Anda pilih.")
                    else:
                        st.info("Tidak ada slot waktu lain yang disarankan.")
                else:
                    st.error("Tidak dapat menemukan jadwal yang memenuhi minimal 3 mata kuliah tanpa bentrok dari pilihan Anda. Coba pilih mata kuliah atau slot waktu lain.")
                    df_schedule = pd.DataFrame(schedule_data)
                    st.dataframe(df_schedule, hide_index=True, use_container_width=True)


    else:
        st.info("Silakan masukkan mata kuliah terlebih dahulu di bagian 'Masukkan Mata Kuliah'.")

st.markdown("---")
st.caption("Aplikasi ini dibuat untuk membantu Anda menyusun jadwal kuliah. Jadwal akan hilang saat halaman di-refresh.")