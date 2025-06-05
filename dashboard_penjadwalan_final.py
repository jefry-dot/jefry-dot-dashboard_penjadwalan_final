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

    # Saran slot tak terpakai
    all_slots = {(c.course_name, s) for c in all_courses_data for s in c.slots}
    used = {(c, s) for c, s in hasil if s != "Tidak tersedia slot tanpa bentrok"}
    saran = sorted(list(all_slots - used))

    return hasil, saran

# --- Streamlit UI ---
st.set_page_config(layout="wide")
st.title("📅 Aplikasi Penjadwalan Kuliah Otomatis")

if 'courses' not in st.session_state:
    st.session_state.courses = []

# ======================== Kolom 1: Input Data ========================
col1, col2 = st.columns([1, 2])

with col1:
    st.header("1. Masukkan Mata Kuliah")
    with st.form("form_add_course"):
        nama = st.text_input("Nama Mata Kuliah", key="new_course_name_input")
        slot_str = st.text_area("Slot Waktu (pisahkan dengan koma)", key="new_course_slots_input")
        submitted = st.form_submit_button("Tambahkan Mata Kuliah")

        if submitted:
            if nama.strip() and slot_str.strip():
                slot_list = [s.strip() for s in slot_str.split(",") if s.strip()]
                if len(st.session_state.courses) < 16:
                    st.session_state.courses.append(Course(nama.strip(), slot_list))
                    st.success(f"✅ '{nama}' berhasil ditambahkan.")
                else:
                    st.warning("⚠️ Maksimal 16 mata kuliah.")
            else:
                st.warning("⚠️ Nama dan slot tidak boleh kosong.")

    st.subheader("📚 Mata Kuliah yang Tersedia:")
    if st.session_state.courses:
        df = pd.DataFrame({
            "Mata Kuliah": [c.course_name for c in st.session_state.courses],
            "Slot Tersedia": [', '.join(c.slots) for c in st.session_state.courses]
        })
        st.dataframe(df, height=250)
        if st.button("🗑 Bersihkan Semua"):
            st.session_state.courses = []
            st.rerun()
    else:
        st.info("Belum ada data mata kuliah.")

# ======================== Kolom 2: Penjadwalan ========================
with col2:
    st.header("2. Pilih Mata Kuliah untuk Dijadwalkan")
    if st.session_state.courses:
        course_names = [c.course_name for c in st.session_state.courses]
        selected = st.multiselect("Pilih mata kuliah:", course_names)

        if st.button("📆 Buat Jadwal Optimal"):
            if len(selected) < 3:
                st.warning("Pilih minimal 3 mata kuliah.")
            else:
                jadwal, saran = generate_schedule(selected, st.session_state.courses)
                jadwal_data = []
                sukses = 0

                for nama, slot in jadwal:
                    if slot.startswith("Tidak"):
                        jadwal_data.append({"Mata Kuliah": nama, "Slot Jadwal": f"⚠️ {slot}"})
                    else:
                        jadwal_data.append({"Mata Kuliah": nama, "Slot Jadwal": slot})
                        sukses += 1

                if sukses >= 3:
                    st.success(f"🎉 {sukses} mata kuliah berhasil dijadwalkan.")
                else:
                    st.error("❌ Jadwal kurang dari 3 matkul valid.")

                st.dataframe(pd.DataFrame(jadwal_data), hide_index=True)

                st.markdown("---")
                st.subheader("🕐 Saran Slot Lain:")
                if saran:
                    df_saran = pd.DataFrame(saran, columns=["Mata Kuliah", "Slot Waktu"])
                    st.dataframe(df_saran, hide_index=True)
                else:
                    st.info("Tidak ada saran slot lain.")
    else:
        st.info("Silakan isi daftar mata kuliah terlebih dahulu.")

st.markdown("---")
st.caption("📌 Jadwal akan hilang saat halaman di-refresh. Simpan secara manual jika dibutuhkan.")
