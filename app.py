import streamlit as st
import re
import pandas as pd

# ==================================================
# KONFIGURASI HALAMAN
# ==================================================
st.set_page_config(
    page_title="Chemical Weighing Calculator",
    page_icon="🧪",
    layout="wide"
)

# ==================================================
# SIDEBAR
# ==================================================
st.sidebar.title("🧪 Chemical Weighing Calculator")
st.sidebar.write(
    "Web praktikum profesional untuk menghitung "
    "**Mr otomatis** dan **massa zat (gram)** "
    "berdasarkan berbagai **jenis konsentrasi**."
)
st.sidebar.markdown("---")

# ==================================================
# DATABASE Ar (PRAKTIKUM-FRIENDLY)
# ==================================================
AR = {
    "H": 1.0, "He": 4.0,
    "Li": 6.9, "Be": 9.0, "B": 10.8, "C": 12.0, "N": 14.0, "O": 16.0,
    "F": 19.0, "Ne": 20.2,
    "Na": 23.0, "Mg": 24.3, "Al": 27.0, "Si": 28.1, "P": 31.0, "S": 32.1,
    "Cl": 35.5, "Ar": 39.9,
    "K": 39.1, "Ca": 40.1, "Sc": 45.0, "Ti": 47.9, "V": 50.9,
    "Cr": 52.0, "Mn": 54.9, "Fe": 55.8, "Co": 58.9, "Ni": 58.7,
    "Cu": 63.5, "Zn": 65.4, "Ga": 69.7, "Ge": 72.6, "As": 74.9,
    "Se": 79.0, "Br": 79.9, "Kr": 83.8,
    "Rb": 85.5, "Sr": 87.6, "Y": 88.9, "Zr": 91.2, "Nb": 92.9,
    "Mo": 95.9, "Tc": 98.0, "Ru": 101.1, "Rh": 102.9, "Pd": 106.4,
    "Ag": 107.9, "Cd": 112.4, "In": 114.8, "Sn": 118.7,
    "Sb": 121.8, "I": 126.9, "Xe": 131.3,
    "Cs": 132.9, "Ba": 137.3, "La": 138.9, "Ce": 140.1,
    "Pr": 140.9, "Nd": 144.2, "Pm": 145.0, "Sm": 150.4,
    "Eu": 152.0, "Gd": 157.3, "Tb": 158.9, "Dy": 162.5,
    "Ho": 164.9, "Er": 167.3, "Tm": 168.9, "Yb": 173.0,
    "Lu": 175.0, "Hf": 178.5, "Ta": 180.9, "W": 183.8,
    "Re": 186.2, "Os": 190.2, "Ir": 192.2, "Pt": 195.1,
    "Au": 197.0, "Hg": 200.6, "Pb": 207.2,
    "Bi": 209.0, "Po": 209.0, "At": 210.0, "Rn": 222.0,
    "Fr": 223.0, "Ra": 226.0, "Ac": 227.0, "Th": 232.0,
    "Pa": 231.0, "U": 238.0, "Np": 237.0, "Pu": 244.0
}

# ==================================================
# PARSER RUMUS KIMIA (KURUNG + HIDRAT)
# ==================================================
def parse_formula(formula):
    tokens = re.findall(r'([A-Z][a-z]?|\(|\)|\d+)', formula)
    stack = [{}]

    i = 0
    while i < len(tokens):
        token = tokens[i]

        if token == "(":
            stack.append({})
        elif token == ")":
            group = stack.pop()
            multiplier = 1
            if i + 1 < len(tokens) and tokens[i + 1].isdigit():
                multiplier = int(tokens[i + 1])
                i += 1
            for el, cnt in group.items():
                stack[-1][el] = stack[-1].get(el, 0) + cnt * multiplier
        elif token.isdigit():
            prev = list(stack[-1].keys())[-1]
            stack[-1][prev] += int(token) - 1
        else:
            stack[-1][token] = stack[-1].get(token, 0) + 1
        i += 1

    return stack[0]


def hitung_mr_lengkap(rumus):
    parts = re.split(r'[·\.]', rumus)
    total = {}
    detail = []

    for part in parts:
        parsed = parse_formula(part)
        for el, cnt in parsed.items():
            total[el] = total.get(el, 0) + cnt

    mr = 0
    for el, cnt in total.items():
        if el not in AR:
            return None, f"Unsur '{el}' tidak ada di database"
        kontribusi = AR[el] * cnt
        mr += kontribusi
        detail.append(f"{el} × {cnt} = {kontribusi:.2f}")

    return mr, detail, total


# ==================================================
# VALIDASI FAKTOR EKUIVALEN (ASAM–BASA)
# ==================================================
def auto_equivalent_factor(komposisi):
    if "H" in komposisi:
        return komposisi["H"]  # asam
    if "OH" in komposisi:
        return komposisi["OH"]  # basa
    return 1


# ==================================================
# UI UTAMA
# ==================================================
st.title("🧪 Chemical Weighing Calculator")
st.write(
    "Aplikasi ini menghitung **Mr secara otomatis dari rumus kimia (kurung & hidrat)**, "
    "lalu menentukan **massa zat (gram)** yang harus ditimbang "
    "berdasarkan **M, N, ppm, atau % b/v**."
)

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    rumus = st.text_input("Rumus kimia", placeholder="Contoh: Ca(OH)2, CuSO4·5H2O")
    jenis = st.selectbox("Jenis konsentrasi", ["Molaritas (M)", "Normalitas (N)", "ppm", "% b/v"])
    nilai = st.number_input("Nilai konsentrasi", min_value=0.0)

with col2:
    satuan_volume = st.radio("Satuan volume", ["mL", "L"])
    volume = st.number_input("Volume larutan", min_value=0.0)

    faktor_manual = None
    if jenis == "Normalitas (N)":
        faktor_manual = st.number_input(
            "Faktor ekuivalen (opsional, otomatis jika dikosongkan)",
            min_value=1,
            step=1
        )

# ==================================================
# HITUNG
# ==================================================
if st.button("⚖️ Hitung Massa", use_container_width=True):
    if rumus == "" or nilai == 0 or volume == 0:
        st.warning("⚠️ Semua data harus diisi")
    else:
        mr, detail, komposisi = hitung_mr_lengkap(rumus)

        if mr is None:
            st.error(detail)
        else:
            volume_l = volume / 1000 if satuan_volume == "mL" else volume

            if jenis == "Molaritas (M)":
                massa = nilai * volume_l * mr
                ekuivalen = "-"

            elif jenis == "Normalitas (N)":
                ekuivalen = faktor_manual if faktor_manual else auto_equivalent_factor(komposisi)
                massa = nilai * volume_l * (mr / ekuivalen)

            elif jenis == "ppm":
                massa = (nilai * volume_l) / 1000
                ekuivalen = "-"

            elif jenis == "% b/v":
                massa = (nilai * volume) / 100
                ekuivalen = "-"

            # ==================================================
            # TABEL RINGKASAN
            # ==================================================
            data = {
                "Parameter": [
                    "Rumus kimia",
                    "Mr (g/mol)",
                    "Jenis konsentrasi",
                    "Nilai konsentrasi",
                    "Volume",
                    "Faktor ekuivalen",
                    "Massa ditimbang (g)"
                ],
                "Nilai": [
                    rumus,
                    f"{mr:.2f}",
                    jenis,
                    nilai,
                    f"{volume} {satuan_volume}",
                    ekuivalen,
                    f"{massa:.4f}"
                ]
            }

            df = pd.DataFrame(data)

            st.success("✅ Perhitungan Berhasil")

            st.subheader("🔬 Detail Perhitungan Mr")
            for d in detail:
                st.write(d)

            st.subheader("📊 Ringkasan Perhitungan")
            st.table(df)

            st.subheader("⚖️ Massa yang Harus Ditimbang")
            st.markdown(f"## **{massa:.4f} gram**")

st.markdown("---")
st.caption("Professional Chemical Web App – Ar, Mr, Kurung, Hidrat, M/N/ppm/% b/v")
