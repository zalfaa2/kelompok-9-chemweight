import streamlit as st
import re
import pandas as pd

# ==================================================
# PAGE CONFIG
# ==================================================
st.set_page_config(
    page_title="Chemical Weighing Calculator",
    page_icon="🧪",
    layout="wide"
)

# ==================================================
# DATABASE Ar (118 UNSUR)
# ==================================================
AR = {
    "H": 1.008, "He": 4.0026,
    "Li": 6.94, "Be": 9.0122, "B": 10.81, "C": 12.011,
    "N": 14.007, "O": 15.999, "F": 18.998, "Ne": 20.180,
    "Na": 22.990, "Mg": 24.305, "Al": 26.982, "Si": 28.085,
    "P": 30.974, "S": 32.06, "Cl": 35.45, "Ar": 39.948,
    "K": 39.098, "Ca": 40.078,
    "Sc": 44.956, "Ti": 47.867, "V": 50.942, "Cr": 51.996,
    "Mn": 54.938, "Fe": 55.845, "Co": 58.933, "Ni": 58.693,
    "Cu": 63.546, "Zn": 65.38,
    "Ga": 69.723, "Ge": 72.630, "As": 74.922, "Se": 78.971,
    "Br": 79.904, "Kr": 83.798,
    "Rb": 85.468, "Sr": 87.62, "Y": 88.906, "Zr": 91.224,
    "Nb": 92.906, "Mo": 95.95, "Tc": 98,
    "Ru": 101.07, "Rh": 102.91, "Pd": 106.42,
    "Ag": 107.87, "Cd": 112.41, "In": 114.82, "Sn": 118.71,
    "Sb": 121.76, "Te": 127.60, "I": 126.90, "Xe": 131.29,
    "Cs": 132.91, "Ba": 137.33,
    "La": 138.91, "Ce": 140.12, "Pr": 140.91, "Nd": 144.24,
    "Pm": 145, "Sm": 150.36, "Eu": 151.96, "Gd": 157.25,
    "Tb": 158.93, "Dy": 162.50, "Ho": 164.93,
    "Er": 167.26, "Tm": 168.93, "Yb": 173.05,
    "Lu": 174.97, "Hf": 178.49, "Ta": 180.95, "W": 183.84,
    "Re": 186.21, "Os": 190.23, "Ir": 192.22,
    "Pt": 195.08, "Au": 196.97, "Hg": 200.59,
    "Tl": 204.38, "Pb": 207.2, "Bi": 208.98, "Po": 209,
    "At": 210, "Rn": 222,
    "Fr": 223, "Ra": 226, "Ac": 227, "Th": 232.04,
    "Pa": 231.04, "U": 238.03, "Np": 237, "Pu": 244,
    "Am": 243, "Cm": 247, "Bk": 247, "Cf": 251,
    "Es": 252, "Fm": 257,
    "Md": 258, "No": 259, "Lr": 266,
    "Rf": 267, "Db": 268, "Sg": 269, "Bh": 270,
    "Hs": 277, "Mt": 278, "Ds": 281,
    "Rg": 282, "Cn": 285, "Nh": 286, "Fl": 289,
    "Mc": 290, "Lv": 293, "Ts": 294, "Og": 294
}

# ==================================================
# PARSER FORMULA (KURUNG) - AMAN
# ==================================================
def parse_formula(formula: str) -> dict:
    tokens = re.findall(r'([A-Z][a-z]?|\(|\)|\d+)', formula)
    if not tokens:
        raise ValueError(f"Rumus tidak valid: '{formula}'")

    stack = [{}]
    i = 0

    while i < len(tokens):
        token = tokens[i]

        if token == "(":
            stack.append({})

        elif token == ")":
            if len(stack) == 1:
                raise ValueError("Kurung tutup ')' tanpa kurung buka '('")
            group = stack.pop()

            mult = 1
            if i + 1 < len(tokens) and tokens[i + 1].isdigit():
                mult = int(tokens[i + 1])
                i += 1

            for el, cnt in group.items():
                stack[-1][el] = stack[-1].get(el, 0) + cnt * mult

        elif token.isdigit():
            if not stack[-1]:
                raise ValueError(f"Angka '{token}' muncul di posisi tidak valid pada '{formula}'")
            prev = list(stack[-1].keys())[-1]
            stack[-1][prev] += int(token) - 1

        else:
            stack[-1][token] = stack[-1].get(token, 0) + 1

        i += 1

    if len(stack) != 1:
        raise ValueError("Ada kurung '(' yang belum ditutup")

    return stack[0]

# ==================================================
# HITUNG Mr (KURUNG + HIDRAT + KOEFISIEN DEPAN)
# ==================================================
def hitung_mr_lengkap(rumus: str, AR: dict):
    rumus = rumus.strip()
    if not rumus:
        raise ValueError("Rumus kosong")

    # split hidrat: titik tengah (·) atau titik biasa (.)
    parts = re.split(r'[·\.]', rumus)

    total = {}
    detail = []

    for part in parts:
        part = part.strip()
        if not part:
            continue

        # koefisien depan: 5H2O
        m = re.match(r'^(\d+)(.*)$', part)
        coef = 1
        core = part
        if m:
            coef = int(m.group(1))
            core = m.group(2).strip()
            if core == "":
                raise ValueError(f"Koefisien '{coef}' tanpa rumus pada '{rumus}'")

        parsed = parse_formula(core)

        for el, cnt in parsed.items():
            total[el] = total.get(el, 0) + cnt * coef

    mr = 0.0
    for el, cnt in total.items():
        if el not in AR:
            raise ValueError(f"Unsur '{el}' tidak ada di database Ar")
        kontribusi = AR[el] * cnt
        mr += kontribusi
        detail.append(f"{el} × {cnt} = {kontribusi:.4f}")

    return mr, detail, total

# ==================================================
# SIDEBAR
# ==================================================
st.sidebar.title("🧪 Chemical Weighing Calculator")
st.sidebar.write("Hitung Mr otomatis + massa (g/mg) dari M / N / ppm / % b/v")

# ==================================================
# UI INPUT
# ==================================================
st.title("🧪 Chemical Weighing Calculator")
st.write("Support: **kurung** (Ca(OH)2) dan **hidrat** (CuSO4·5H2O / CuSO4.5H2O).")
st.write("Gunakan kaidah penulisan yang sesuai")

col1, col2 = st.columns(2)

with col1:
    rumus = st.text_input("Rumus kimia", placeholder="Contoh: CuSO4·5H2O, Ca(OH)2")
    jenis = st.selectbox("Jenis Konsentrasi", ["Molaritas (M)", "Normalitas (N)", "ppm", "% b/v"])
    nilai = st.number_input("Nilai Konsentrasi", min_value=0.0)

with col2:
    satuan_vol = st.radio("Satuan Volume", ["mL", "L"])
    volume = st.number_input("Volume Larutan", min_value=0.0)

    satuan_massa = st.radio("Satuan Massa Hasil", ["gram (g)", "miligram (mg)"])

    faktor = 1
    if jenis == "Normalitas (N)":
        faktor = st.number_input("Faktor Ekuivalen (jumlah atom H)", min_value=1, step=1)

# ==================================================
# HITUNG
# ==================================================
if st.button("Hitung Massa", use_container_width=True):
    try:
        mr, detail, _ = hitung_mr_lengkap(rumus, AR)

        # konversi volume ke liter jika perlu
        volume_l = volume / 1000 if satuan_vol == "mL" else volume

        # hitung massa dalam GRAM sebagai basis
        if jenis == "Molaritas (M)":
            massa_g = nilai * volume_l * mr

        elif jenis == "Normalitas (N)":
            massa_g = nilai * volume_l * (mr / faktor)

        elif jenis == "ppm":
            # asumsi 1 ppm ≈ 1 mg/L (larutan encer)
            massa_g = (nilai * volume_l) / 1000  # mg -> g

        else:  # % b/v
            # % b/v = gram per 100 mL
            # gunakan volume dalam mL untuk rumus ini
            volume_ml = volume if satuan_vol == "mL" else volume * 1000
            massa_g = (nilai * volume_ml) / 100

        # konversi tampilan ke g atau mg
        if satuan_massa == "miligram (mg)":
            massa_tampil = massa_g * 1000
            label_massa = "mg"
        else:
            massa_tampil = massa_g
            label_massa = "g"

        st.success("Perhitungan Berhasil")

        # tabel ringkasan (format sesuai permintaan)
        df = pd.DataFrame({
            "Parameter": ["Rumus", "Mr (g/mol)", "Konsentrasi", "Volume", f"Massa ({label_massa})"],
            "Nilai": [
                rumus,
                f"{mr:.1f}",
                f"{nilai:.2f}",                 # konsentrasi 2 angka belakang koma
                f"{volume:.1f} {satuan_vol}",
                f"{massa_tampil:.4f}"           # massa 4 angka belakang koma
            ]
        })

        st.subheader("Ringkasan")
        st.table(df)

        st.subheader("Detail Perhitungan Mr")
        for d in detail:
            st.write(d)

        st.subheader("✅Hasil Akhir")
        st.markdown(f"## **{massa_tampil:.4f} {label_massa}**")

    except Exception as e:
        st.error(f"❌ Error input/rumus: {e}")

st.markdown("---")
st.caption("Web Praktikum Kimia – Mr & Massa Otomatis (Stable Final)")
