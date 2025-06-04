
import streamlit as st
import pandas as pd
from collections import defaultdict
import time
import random
import math

st.set_page_config(page_title="Penjadwalan Kuliah", layout="wide")

# --- Fungsi Pembantu ---
def do_slots_overlap(slot1, slot2):
    if slot1 and slot2:
        day1, time1 = slot1.split(" ")
        day2, time2 = slot2.split(" ")
        if day1 != day2:
            return False
        start1, end1 = map(lambda t: int(t.split(":")[0]) * 60 + int(t.split(":")[1]), time1.split("-"))
        start2, end2 = map(lambda t: int(t.split(":")[0]) * 60 + int(t.split(":")[1]), time2.split("-"))
        return start1 < end2 and start2 < end1
    return False

class Course:
    def __init__(self, course_name, slots):
        self.course_name = course_name
        self.slots = slots

def get_mahasiswa_slot_tak_bisa_dict(df):
    mhs_dict = {}
    for _, row in df.iterrows():
        key = row["MataKuliah"]
        mhs_dict.setdefault(key, set()).add(row["SlotTakBisa"])
    return mhs_dict

def generate_schedule_greedy(course_list, mahasiswa_preferences):
    n = len(course_list)
    schedule = [None] * n
    for i in range(n):
        best_slot = None
        course = course_list[i]
        for slot in course.slots:
            is_valid_slot = True
            for j in range(i):
                if do_slots_overlap(slot, schedule[j]):
                    is_valid_slot = False
                    break
            if slot in mahasiswa_preferences.get(course.course_name, set()):
                is_valid_slot = False
            if is_valid_slot:
                best_slot = slot
                break
        schedule[i] = best_slot
    return [(course_list[i].course_name, schedule[i] if schedule[i] else "Tidak tersedia jadwal") for i in range(n)]

def generate_schedule_backtracking(course_list, mahasiswa_preferences):
    n = len(course_list)
    schedule = [None] * n
    found = [False]  # pakai list agar mutable di nested scope

    def is_valid(slot, index):
        for i in range(index):
            if do_slots_overlap(slot, schedule[i]):
                return False
        if slot in mahasiswa_preferences.get(course_list[index].course_name, set()):
            return False
        return True

    def backtrack(index):
        if index == n:
            found[0] = True
            return True
        course = course_list[index]
        for slot in course.slots:
            if is_valid(slot, index):
                schedule[index] = slot
                if backtrack(index + 1):
                    return True
                schedule[index] = None
        return False

    backtrack(0)

    # Jika tidak ketemu solusi penuh, kembalikan jadwal parsial (greedy-like fallback)
    if not found[0]:
        return [(course_list[i].course_name, schedule[i] if schedule[i] else "Tidak tersedia jadwal (parsial)") for i in range(n)]

    return [(course_list[i].course_name, schedule[i]) for i in range(n)]


def generate_schedule_simulated_annealing(course_list, mahasiswa_preferences, max_iter=1000, temp=100.0, cooling_rate=0.95):
    current_solution = []
    for course in course_list:
        valid_slots = [slot for slot in course.slots if slot not in mahasiswa_preferences.get(course.course_name, set())]
        current_solution.append(valid_slots[0] if valid_slots else None)

    def cost(solution):
        conflict = 0
        for i in range(len(solution)):
            if not solution[i]:
                conflict += 5
                continue
            for j in range(i + 1, len(solution)):
                if do_slots_overlap(solution[i], solution[j]):
                    conflict += 1
        return conflict

    best_solution = current_solution[:]
    best_cost = cost(best_solution)

    for _ in range(max_iter):
        i = random.randint(0, len(course_list) - 1)
        course = course_list[i]
        available_slots = [s for s in course.slots if s not in mahasiswa_preferences.get(course.course_name, set())]
        if not available_slots:
            continue
        new_slot = random.choice(available_slots)
        new_solution = current_solution[:]
        new_solution[i] = new_slot
        current_cost = cost(current_solution)
        new_cost = cost(new_solution)
        delta = new_cost - current_cost
        if delta < 0 or random.random() < math.exp(-delta / temp):
            current_solution = new_solution[:]
            if new_cost < best_cost:
                best_solution = new_solution[:]
                best_cost = new_cost
        temp *= cooling_rate
        if temp < 1e-3:
            break

    return [(course_list[i].course_name, best_solution[i] if best_solution[i] else "Tidak tersedia jadwal") for i in range(len(course_list))]

# --- Streamlit UI ---
st.title("📅 Dashboard Penjadwalan Kuliah")

dosen_file = st.file_uploader("Upload file preferensi dosen (.csv)", type="csv")
mahasiswa_file = st.file_uploader("Upload file preferensi mahasiswa (.csv)", type="csv")

if dosen_file and mahasiswa_file:
    dosen_df = pd.read_csv(dosen_file)
    mahasiswa_df = pd.read_csv(mahasiswa_file)

    dosen_grouped = defaultdict(list)
    for _, row in dosen_df.iterrows():
        dosen_grouped[row["MataKuliah"]].append(row["SlotPreferensi"])
    course_list = [Course(course, slots) for course, slots in dosen_grouped.items()]
    preferensi_mahasiswa = get_mahasiswa_slot_tak_bisa_dict(mahasiswa_df)

    algo = st.selectbox("Pilih Algoritma Penjadwalan", ["Greedy", "Backtracking", "Simulated Annealing"])

    if st.button("🔄 Jalankan Penjadwalan"):
        start = time.time()

        if algo == "Greedy":
            jadwal = generate_schedule_greedy(course_list, preferensi_mahasiswa)
        elif algo == "Backtracking":
            jadwal = generate_schedule_backtracking(course_list, preferensi_mahasiswa)
        elif algo == "Simulated Annealing":
            jadwal = generate_schedule_simulated_annealing(course_list, preferensi_mahasiswa)

        end = time.time()
        if jadwal:
            st.success(f"Penjadwalan selesai dalam {end - start:.2f} detik.")
            st.dataframe(pd.DataFrame(jadwal, columns=["Mata Kuliah", "Slot Terpilih"]))
else:
    st.info("Silakan upload dua file preferensi terlebih dahulu.")
