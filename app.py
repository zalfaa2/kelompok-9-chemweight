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
    # 1–10
    "H": 1.008, "He": 4.0026,
    "Li": 6.94, "Be": 9.0122, "B": 10.81, "C": 12.011,
    "N": 14.007, "O": 15.999, "F": 18.998, "Ne": 20.180,

    # 11–20
    "Na": 22.990, "Mg": 24.305, "Al": 26.982, "Si": 28.085,
    "P": 30.974, "S": 32.06, "Cl": 35.45, "Ar": 39.948,
    "K": 39.098, "Ca": 40.078,

    # 21–30
    "Sc": 44.956, "Ti": 47.867, "V": 50.942, "Cr": 51.996,
    "Mn": 54.938, "Fe": 55.845, "Co": 58.933, "Ni": 58.693,
    "Cu": 63.546, "Zn": 65.38,

    # 31–40
    "Ga": 69.723, "Ge": 72.630, "As": 74.922, "Se": 78.971,
    "Br": 79.904, "Kr": 83.798,
    "Rb": 85.468, "Sr": 87.62, "Y": 88.906, "Zr": 91.224,

    # 41–50
    "Nb": 92.906, "Mo": 95.95, "Tc": 98,
    "Ru": 101.07, "Rh": 102.91, "Pd": 106.42,
    "Ag": 107.87, "Cd": 112.41, "In": 114.82, "Sn": 118.71,

    # 51–60
    "Sb": 121.76, "Te": 127.60, "I": 126.90, "Xe": 131.29,
    "Cs": 132.91, "Ba": 137.33,
    "La": 138.91, "Ce": 140.12, "Pr": 140.91, "Nd": 144.24,

    # 61–70
    "Pm": 145, "Sm": 150.36, "Eu": 151.96, "Gd": 157.25,
    "Tb": 158.93, "Dy": 162.50, "Ho": 164.93,
    "Er": 167.26, "Tm": 168.93, "Yb": 173.05,

    # 71–80
    "Lu": 174.97, "Hf": 178.49, "Ta": 180.95, "W": 183.84,
    "Re": 186.21, "Os": 190.23, "Ir": 192.22,
    "Pt": 195.08, "Au": 196.97, "Hg": 200.59,

    # 81–90
    "Tl": 204.38, "Pb": 207.2, "Bi": 208.98, "Po": 209,
    "At": 210, "Rn": 222,
    "Fr": 223, "Ra": 226, "Ac": 227, "Th": 232.04,

    # 91–100
    "Pa": 231.04, "U": 238.03, "Np": 237, "Pu": 244,
    "Am": 243, "Cm": 247, "Bk": 247, "Cf": 251,
    "Es": 252, "Fm": 257,

    # 101–110
    "Md": 258, "No": 259, "Lr": 266,
    "Rf": 267, "Db": 268, "Sg": 269, "Bh": 270,
    "Hs": 277, "Mt": 278, "Ds": 281,

    # 111–118
    "Rg": 282, "Cn": 285, "Nh": 286, "Fl": 289,
    "Mc": 290, "Lv": 293, "Ts": 294, "Og": 294
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
