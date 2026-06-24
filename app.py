import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Simulator Kebijakan Ekonomi",
    page_icon="🧭",
    layout="wide",
)


st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;600;700;800&display=swap');

:root {
    --bg: #0b0f1a;
    --card: rgba(255,255,255,0.06);
    --border: rgba(255,255,255,0.12);
    --text: #f1f5f9;
    --muted: #94a3b8;

    --primary: #3b82f6;
    --accent: #a855f7;

    --orange: #fb923c;
    --pink: #ec4899;
    --yellow: #facc15;

    --good: #22c55e;
    --bad: #ef4444;
}

/* FONT */
html, body, [class*="css"] {
    font-family: 'Plus Jakarta Sans', sans-serif;
}

/* BACKGROUND */
.stApp {
    background:
        radial-gradient(circle at 20% 10%, rgba(59,130,246,0.25), transparent 30%),
        radial-gradient(circle at 80% 0%, rgba(168,85,247,0.2), transparent 30%),
        linear-gradient(145deg, #05070f, #0b0f1a);
    color: var(--text);
}

/* CONTAINER */
.block-container {
    max-width: 1350px;
}

/* NAVBAR */
.main-nav {
    display: flex;
    justify-content: space-between;
    padding: 14px 18px;
    border-radius: 18px;
    background: var(--card);
    border: 1px solid var(--border);
    backdrop-filter: blur(14px);
}

/* HERO */
.hero-shell {
    padding: 30px;
    border-radius: 26px;
    background:
        linear-gradient(135deg, rgba(59,130,246,0.25), rgba(168,85,247,0.25));
    border: 1px solid var(--border);
    backdrop-filter: blur(18px);
}

/* CONTROL PANEL */
.control-card {
    background: var(--card);
    border-radius: 20px;
    padding: 20px;
    border: 1px solid var(--border);
    backdrop-filter: blur(12px);
}

/* SLIDER */
[data-testid="stSlider"] {
    background: rgba(255,255,255,0.05);
    border-radius: 12px;
    padding: 10px;
}

[data-testid="stSlider"] [role="slider"] {
    background: var(--yellow) !important;
    border-color: var(--yellow) !important;
}

/* BUTTON */
.stButton>button {
    background: linear-gradient(135deg, var(--primary), var(--accent));
    color: white;
    border-radius: 12px;
    font-weight: 700;
    border: none;
}

.stButton>button:hover {
    opacity: 0.85;
}

/* METRIC CARD */
.metric-card {
    background: var(--card);
    border-radius: 20px;
    padding: 18px;
    border: 1px solid var(--border);
    backdrop-filter: blur(12px);
}

.metric-value {
    font-size: 28px;
    font-weight: 800;
}

/* DELTA */
.delta-good {
    color: var(--good);
}

.delta-bad {
    color: var(--bad);
}

.delta-flat {
    color: var(--muted);
}

/* STATUS */
.status-box {
    padding: 16px;
    border-radius: 14px;
    background: var(--card);
    border: 1px solid var(--border);
}

/* CHART */
.chart-card {
    background: var(--card);
    border-radius: 20px;
    padding: 20px;
    border: 1px solid var(--border);
}

/* TABLE */
[data-testid="stDataFrame"] {
    border-radius: 12px;
    border: 1px solid var(--border);
}

/* FOOTER */
.footer-box {
    text-align: center;
    font-size: 12px;
    color: var(--muted);
    margin-top: 20px;
}

/* RESPONSIVE */
@media(max-width: 900px) {
    .hero-inner {
        grid-template-columns: 1fr;
    }
}
</style>
""",
    unsafe_allow_html=True,
)


BASELINE = {"iklan": 10, "diskon": 5, "harga": 100}


def hitung_skenario(iklan: float, diskon: float, harga: float) -> dict[str, float]:
    """Model demonstrasi untuk simulasi what-if, seluruh nilai dalam juta rupiah."""
    permintaan_dasar = 1_000
    efek_iklan = 420 * (1 - np.exp(-iklan / 28))
    efek_diskon = 13 * diskon - 0.16 * diskon**2
    efek_harga = -9 * (harga - 100)

    permintaan = max(
        100,
        permintaan_dasar + efek_iklan + efek_diskon + efek_harga,
    )

    harga_jual = harga * (1 - diskon / 100)
    omzet = permintaan * harga_jual / 1_000
    biaya_produk = permintaan * 58 / 1_000
    biaya_iklan = iklan
    keuntungan = omzet - biaya_produk - biaya_iklan - 12

    kapasitas_stok = 1_450
    risiko_stok = np.clip((permintaan - kapasitas_stok) / kapasitas_stok * 100 + 5, 0, 100)

    return {
        "permintaan": permintaan,
        "omzet": omzet,
        "keuntungan": keuntungan,
        "risiko_stok": risiko_stok,
    }


@st.cache_data
def buat_kurva_respons(anggaran_maksimum: int, diskon: int, harga: int) -> pd.DataFrame:
    """Membuat data kurva respons iklan untuk visualisasi."""
    rentang_iklan = np.arange(0, anggaran_maksimum + 1, 5)
    keuntungan = [hitung_skenario(i, diskon, harga)["keuntungan"] for i in rentang_iklan]
    return pd.DataFrame({"Anggaran iklan": rentang_iklan, "Keuntungan": keuntungan})


def format_rupiah(nilai: float) -> str:
    return f"Rp {nilai:,.1f} juta".replace(",", "X").replace(".", ",").replace("X", ".")


def kembali_ke_baseline() -> None:
    st.session_state["iklan"] = BASELINE["iklan"]
    st.session_state["diskon"] = BASELINE["diskon"]
    st.session_state["harga"] = BASELINE["harga"]


def delta_class(nilai: float, inverse: bool = False) -> str:
    if abs(nilai) < 0.01:
        return "delta-flat"
    baik = nilai > 0
    if inverse:
        baik = nilai < 0
    return "delta-good" if baik else "delta-bad"


def metric_card(judul: str, nilai: str, delta: str, ikon: str, kelas_delta: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-head">
                <div class="metric-name">{judul}</div>
                <div class="metric-icon">{ikon}</div>
            </div>
            <div class="metric-value">{nilai}</div>
            <div class="delta-pill {kelas_delta}">{delta}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


baseline = hitung_skenario(**BASELINE)

st.markdown(
    """
    <div class="main-nav">
        <div class="nav-left">
            <div class="nav-logo">SE</div>
            <div>
                <div class="nav-title">Simulator Kebijakan Ekonomi</div>
                <div class="nav-subtitle">Tampilan baru tanpa sidebar · semua kontrol ada di dashboard</div>
            </div>
        </div>
        <div class="nav-badge">LIVE WHAT-IF DASHBOARD</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="hero-shell">
        <div class="hero-inner">
            <div>
                <div class="hero-eyebrow">● Scenario Strategy Room</div>
                <h1 class="hero-title">Ubah angka, lihat <span>dampak bisnis</span>.</h1>
                <p class="hero-desc">
                    Dashboard ini dibuat ulang dengan layout horizontal, kartu neon, dan grafik gelap.
                    Parameter iklan, diskon, dan harga tetap sama, tetapi tampilannya sudah berbeda total.
                </p>
            </div>
            <div class="hero-side">
                <div class="mini-card">
                    <div class="mini-label">Baseline keuntungan</div>
                    <div class="mini-value">{format_rupiah(baseline['keuntungan'])}</div>
                </div>
                <div class="mini-card">
                    <div class="mini-label">Baseline omzet</div>
                    <div class="mini-value">{format_rupiah(baseline['omzet'])}</div>
                </div>
                <div class="mini-card">
                    <div class="mini-label">Baseline permintaan</div>
                    <div class="mini-value">{baseline['permintaan']:,.0f} unit</div>
                </div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="control-card">
        <div class="control-title">
            <div>
                <h2>Panel Pengaturan</h2>
                <p>Ubah slider di bawah, hasil simulasi langsung berubah.</p>
            </div>
        </div>
    """,
    unsafe_allow_html=True,
)

slider_col1, slider_col2, slider_col3, reset_col = st.columns([1, 1, 1, 0.75], gap="medium")

with slider_col1:
    iklan = st.slider("Anggaran iklan (juta Rp)", 0, 100, BASELINE["iklan"], 1, key="iklan")

with slider_col2:
    diskon = st.slider("Besaran diskon (%)", 0, 40, BASELINE["diskon"], 1, key="diskon")

with slider_col3:
    harga = st.slider("Harga awal per unit (ribu Rp)", 70, 130, BASELINE["harga"], 1, key="harga")

with reset_col:
    st.write("")
    st.write("")
    st.button("↻ Reset", on_click=kembali_ke_baseline, use_container_width=True)

st.markdown("</div>", unsafe_allow_html=True)

skenario = hitung_skenario(iklan, diskon, harga)

delta_untung = skenario["keuntungan"] - baseline["keuntungan"]
delta_omzet = skenario["omzet"] - baseline["omzet"]
delta_permintaan = skenario["permintaan"] - baseline["permintaan"]
delta_risiko = skenario["risiko_stok"] - baseline["risiko_stok"]

st.markdown('<div class="section-title"><span></span>Ringkasan Performa</div>', unsafe_allow_html=True)

m1, m2, m3, m4 = st.columns(4, gap="medium")

with m1:
    metric_card(
        "Keuntungan",
        format_rupiah(skenario["keuntungan"]),
        f"{delta_untung:+.1f} juta vs baseline",
        "💰",
        delta_class(delta_untung),
    )

with m2:
    metric_card(
        "Omzet",
        format_rupiah(skenario["omzet"]),
        f"{delta_omzet:+.1f} juta vs baseline",
        "🧾",
        delta_class(delta_omzet),
    )

with m3:
    metric_card(
        "Permintaan",
        f"{skenario['permintaan']:,.0f} unit",
        f"{delta_permintaan:+.0f} unit vs baseline",
        "📦",
        delta_class(delta_permintaan),
    )

with m4:
    metric_card(
        "Risiko Stok",
        f"{skenario['risiko_stok']:.1f}%",
        f"{delta_risiko:+.1f} poin",
        "⚠️",
        delta_class(delta_risiko, inverse=True),
    )

if delta_untung > 3:
    status_class = "status-good"
    status_text = (
        f"✅ Skenario ini diperkirakan meningkatkan keuntungan sebesar "
        f"{format_rupiah(delta_untung)} dibandingkan baseline."
    )
elif delta_untung < -3:
    status_class = "status-warn"
    status_text = (
        f"⚠️ Skenario ini diperkirakan menurunkan keuntungan sebesar "
        f"{format_rupiah(abs(delta_untung))}. Periksa lagi kombinasi harga, diskon, dan iklan."
    )
else:
    status_class = "status-info"
    status_text = "ℹ️ Keuntungan skenario ini relatif sama dengan baseline."

st.markdown(f'<div class="status-box {status_class}">{status_text}</div>', unsafe_allow_html=True)

st.markdown('<div class="section-title"><span></span>Analisis Skenario</div>', unsafe_allow_html=True)

chart_col, line_col = st.columns([1.05, 1], gap="large")

with chart_col:
    st.markdown(
        """
        <div class="chart-card">
            <h3>Perbandingan Kinerja</h3>
            <p>Baseline dibandingkan dengan skenario aktif.</p>
        """,
        unsafe_allow_html=True,
    )

    kategori = ["Keuntungan", "Omzet"]
    nilai_baseline = [baseline["keuntungan"], baseline["omzet"]]
    nilai_skenario = [skenario["keuntungan"], skenario["omzet"]]
    posisi = np.arange(len(kategori))

    fig, ax = plt.subplots(figsize=(8, 4.3))
    fig.patch.set_alpha(0)
    ax.set_facecolor((0, 0, 0, 0))

    lebar = 0.34
    bar_baseline = ax.bar(
        posisi - lebar / 2,
        nilai_baseline,
        lebar,
        label="Baseline",
        color="#52525b",
        zorder=3,
    )
    bar_skenario = ax.bar(
        posisi + lebar / 2,
        nilai_skenario,
        lebar,
        label="Skenario aktif",
        color="#fb923c",
        zorder=3,
    )

    ax.bar_label(bar_baseline, fmt="%.1f", padding=4, color="#d4d4d8", fontsize=9)
    ax.bar_label(bar_skenario, fmt="%.1f", padding=4, color="#ffffff", fontsize=9, fontweight="bold")
    ax.set_xticks(posisi, kategori)
    ax.legend(frameon=False, labelcolor="#e4e4e7")
    ax.spines[:].set_visible(False)
    ax.tick_params(axis="both", colors="#d4d4d8", length=0)
    ax.grid(axis="y", color=(1, 1, 1, 0.10), linewidth=1, zorder=0)
    ax.margins(y=0.2)

    st.pyplot(fig, use_container_width=True)
    plt.close(fig)
    st.markdown("</div>", unsafe_allow_html=True)

with line_col:
    st.markdown(
        """
        <div class="chart-card">
            <h3>Kurva Respons Iklan</h3>
            <p>Diskon dan harga mengikuti skenario aktif.</p>
        """,
        unsafe_allow_html=True,
    )

    kurva = buat_kurva_respons(100, diskon, harga)
    fig2, ax2 = plt.subplots(figsize=(8, 4.3))
    fig2.patch.set_alpha(0)
    ax2.set_facecolor((0, 0, 0, 0))
    ax2.plot(kurva["Anggaran iklan"], kurva["Keuntungan"], linewidth=3, color="#ec4899")
    ax2.fill_between(
        kurva["Anggaran iklan"],
        kurva["Keuntungan"],
        kurva["Keuntungan"].min(),
        color="#ec4899",
        alpha=0.15,
    )
    ax2.axvline(iklan, color="#facc15", linestyle="--", linewidth=2, label="Iklan aktif")
    ax2.scatter([iklan], [skenario["keuntungan"]], s=80, color="#facc15", zorder=5)
    ax2.set_xlabel("Anggaran iklan", color="#d4d4d8")
    ax2.set_ylabel("Keuntungan", color="#d4d4d8")
    ax2.legend(frameon=False, labelcolor="#e4e4e7")
    ax2.spines[:].set_visible(False)
    ax2.tick_params(axis="both", colors="#d4d4d8", length=0)
    ax2.grid(color=(1, 1, 1, 0.10), linewidth=1)

    st.pyplot(fig2, use_container_width=True)
    plt.close(fig2)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div class="section-title"><span></span>Detail Kebijakan</div>', unsafe_allow_html=True)

left_detail, right_detail = st.columns([1.1, 1], gap="large")

with left_detail:
    st.markdown(
        """
        <div class="chart-card">
            <h3>Komposisi Kebijakan</h3>
            <p>Perbandingan nilai baseline dan skenario yang sedang aktif.</p>
        """,
        unsafe_allow_html=True,
    )
    tabel = pd.DataFrame(
        {
            "Variabel": ["Anggaran iklan", "Diskon", "Harga awal"],
            "Baseline": ["Rp10 juta", "5%", "Rp100 ribu"],
            "Skenario": [f"Rp{iklan} juta", f"{diskon}%", f"Rp{harga} ribu"],
        }
    )
    st.dataframe(tabel, hide_index=True, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

with right_detail:
    st.markdown(
        f"""
        <div class="chart-card">
            <h3>Snapshot Skenario</h3>
            <p>Ringkasan cepat dari parameter yang sedang dipilih.</p>
            <div class="mini-card">
                <div class="mini-label">Iklan</div>
                <div class="mini-value">Rp{iklan} juta</div>
            </div>
            <br>
            <div class="mini-card">
                <div class="mini-label">Diskon dan harga</div>
                <div class="mini-value">{diskon}% · Rp{harga} ribu</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

st.markdown(
    '<div class="footer-box">Simulator Kebijakan Ekonomi · Tampilan super beda: tanpa sidebar, tema neon, layout horizontal</div>',
    unsafe_allow_html=True,
)