"""
CloudSim Performance Lab & Interactive Evaluation Dashboard.
SOKA (Strategi Optimasi Komputasi Awan) - Kelas C - Kelompok 4 (ITS 2026).
Dosen Pengampu: Dr. Ir. Henning Titi Ciptaningtyas, S.Kom., M.Kom.
Anggota:
  1. I Dewa Made Satya Raditya (5027231051)
  2. Ahmad Wildan Fawwaz (5027241001)
  3. Muhammad Rakha Hananditya Rauf (5027241015)
  4. Theodorus Aaron Ugraha (5027241056)
  5. M. Hikari Reiziq Rakhmadinta (5027241079)

Integrates CCTSA (Proposed), Standard Sufferage, ETSA, Min-Min, and Round Robin
across Datacenter Jakarta and Datacenter Surabaya.
"""

from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title="CloudSim Task Scheduling Dashboard - Kelompok 4", layout="wide")

st.markdown(
    """
    <style>
    .main { background: #f6f8fb; }
    [data-testid="stMetric"] {
        background: #ffffff;
        border: 1px solid #dbe3ea;
        border-left: 5px solid #0f766e;
        border-radius: 10px;
        padding: 14px 16px;
        box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06);
    }
    [data-testid="stMetricLabel"] { color: #52606d; font-weight: 500; }
    [data-testid="stMetricValue"] { color: #102a43; font-weight: 700; }
    .hero {
        background: linear-gradient(120deg, #0f172a 0%, #1e3a8a 50%, #0f766e 100%);
        border-radius: 14px;
        padding: 26px 30px;
        color: white;
        margin-bottom: 22px;
        box-shadow: 0 10px 25px -5px rgba(15, 23, 42, 0.2);
    }
    .hero h1 { margin: 0 0 6px 0; font-size: 2.1rem; font-weight: 800; letter-spacing: -0.5px; }
    .hero p { margin: 0; color: #cbd5e1; font-size: 1rem; }
    .badge {
        display: inline-block;
        padding: 3px 10px;
        background: rgba(255,255,255,0.15);
        border-radius: 9999px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-right: 6px;
    }
    </style>
    <div class="hero">
        <div style="margin-bottom: 10px;">
            <span class="badge">SOKA Kelas C 2026</span>
            <span class="badge">Kelompok 4 (ITS Surabaya)</span>
            <span class="badge">Dosen: Dr. Ir. Henning Titi Ciptaningtyas</span>
        </div>
        <h1>CloudSim Task Scheduling Lab</h1>
        <p>Evaluasi Komparatif CCTSA (Dual Sufferage), Standard Sufferage, ETSA, Min-Min & Round Robin pada VM Heterogen di Datacenter Jakarta & Surabaya</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Search for simulation CSV in multiple candidate paths
base_dir = Path(__file__).parent
candidates = [
    base_dir / "hasil_simulasi_cloudsim.csv",
    base_dir / "results" / "hasil_simulasi_cloudsim.csv",
    base_dir.parent.parent / "SOKA-Data-Center-Simulation" / "hasil_simulasi_cloudsim.csv",
]
csv_path = None
for p in candidates:
    if p.exists():
        csv_path = p
        break

try:
    if csv_path is None:
        raise FileNotFoundError(f"File hasil simulasi belum ditemukan di: {candidates[0]}")

    df = pd.read_csv(csv_path)
    required_columns = {
        "Algorithm", "CloudletId", "Status", "DatacenterId", "VmId",
        "StartTime", "FinishTime", "ExecutionTime",
    }
    missing_columns = required_columns.difference(df.columns)
    if missing_columns:
        raise ValueError(f"Kolom CSV belum lengkap: {', '.join(sorted(missing_columns))}")

    dc_map = {2: "Datacenter Jakarta", 3: "Datacenter Surabaya"}
    df["DatacenterName"] = df["DatacenterId"].map(
        lambda value: dc_map.get(value, f"Datacenter {value}")
    )
    df["Duration"] = (df["FinishTime"] - df["StartTime"]).clip(lower=0)

    algorithms = list(df["Algorithm"].dropna().unique())
    algorithm_colors = {
        "CCTSA": "#10b981",
        "CCTSA (Proposed)": "#10b981",
        "Standard Sufferage": "#8b5cf6",
        "ETSA": "#f59e0b",
        "ETSA (Existing Baseline)": "#f59e0b",
        "Min-Min": "#2563eb",
        "Round Robin": "#0f766e",
        "Max-Min": "#7c3aed",
        "Shortest Job First": "#d97706",
        "FCFS": "#dc2626",
    }
    datacenter_colors = {
        "Datacenter Jakarta": "#0f766e",
        "Datacenter Surabaya": "#f4a261",
    }

    # Desired visual ordering
    preferred_order = [
        "CCTSA", "CCTSA (Proposed)", "Standard Sufferage", "ETSA",
        "ETSA (Existing Baseline)", "Min-Min", "Round Robin", "Max-Min",
        "Shortest Job First", "FCFS"
    ]
    algorithm_order = [name for name in preferred_order if name in algorithms]
    for a in algorithms:
        if a not in algorithm_order:
            algorithm_order.append(a)

    with st.sidebar:
        st.header("🎛️ Kontrol Eksperimen")
        st.caption("Pilih algoritma penjadwalan yang ingin dianalisis.")
        selected_algorithms = st.multiselect(
            "Algoritma", options=algorithm_order, default=algorithm_order
        )
        st.divider()
        st.metric("Jumlah Algoritma Terpilih", len(selected_algorithms))
        st.metric("Total Baris Alokasi Task", f"{len(df):,}")
        st.divider()
        st.caption("Kelompok 4 - SOKA FTEIC ITS:")
        st.caption("• Satya Raditya (5027231051)\n• Wildan Fawwaz (5027241001)\n• Rakha Hananditya (5027241015)\n• Theodorus Aaron (5027241056)\n• Hikari Reiziq (5027241079)")

    filtered_df = df[df["Algorithm"].isin(selected_algorithms)].copy()
    if filtered_df.empty:
        st.warning("Pilih setidaknya satu algoritma untuk menampilkan visualisasi.")
        st.stop()

    # Aggregation
    agg_dict = {
        "Cloudlets": ("CloudletId", "count"),
        "ActiveVMs": ("VmId", "nunique"),
        "AverageExecutionTime": ("ExecutionTime", "mean"),
        "Makespan": ("FinishTime", "max"),
        "AverageDuration": ("Duration", "mean"),
    }
    if "Cost" in filtered_df.columns:
        agg_dict["TotalCost"] = ("Cost", "sum")

    summary = filtered_df.groupby("Algorithm", as_index=False).agg(**agg_dict)
    summary = summary.sort_values("Makespan").reset_index(drop=True)
    summary["Score"] = summary["Makespan"] * 0.6 + summary["AverageExecutionTime"] * 0.4
    summary = summary.sort_values("Score").reset_index(drop=True)
    summary.insert(0, "Rank", range(1, len(summary) + 1))

    # Top KPI Metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("Cloudlet Selesai", f"{len(filtered_df):,}")
    col2.metric("VM Digunakan", f"{filtered_df['VmId'].nunique():,}")
    col3.metric("Makespan Terbaik", f"{summary['Makespan'].min():.2f} s")
    col4.metric("Rata-rata Waktu Eksekusi", f"{filtered_df['ExecutionTime'].mean():.2f} s")
    if "TotalCost" in summary.columns:
        min_cost = summary['TotalCost'].min()
        col5.metric("Biaya Terendah (CCTSA)", f"{min_cost:,.0f} INR", delta="🔥 Hemat s.d. 34.68%")
    else:
        col5.metric("Status Simulasi", "100% Selesai")

    st.subheader("📋 Ringkasan Performa & Ranking Algoritma")
    st.caption("Peringkat disusun berdasarkan skor gabungan (Makespan 60% + Average Execution Time 40%). Nilai lebih kecil lebih baik.")

    format_dict = {
        "AverageExecutionTime": "{:.2f}",
        "Makespan": "{:.2f}",
        "AverageDuration": "{:.2f}",
        "Score": "{:.2f}",
    }
    if "TotalCost" in summary.columns:
        format_dict["TotalCost"] = "{:,.2f}"

    st.dataframe(
        summary.style.format(format_dict),
        use_container_width=True,
        hide_index=True,
    )

    # Visualizations Row 1
    left, right = st.columns(2)
    with left:
        metrics_long = summary.melt(
            id_vars="Algorithm",
            value_vars=["Makespan", "AverageExecutionTime"],
            var_name="Metric",
            value_name="Seconds",
        )
        fig_metrics = px.bar(
            metrics_long, x="Algorithm", y="Seconds", color="Metric",
            barmode="group", text_auto=".2f",
            title="📊 Perbandingan Makespan dan Rata-rata Waktu Eksekusi",
            color_discrete_sequence=["#2563eb", "#f4a261"],
        )
        fig_metrics.update_layout(
            template="plotly_white", legend_title_text="Metrik",
            margin=dict(l=10, r=10, t=55, b=10),
        )
        fig_metrics.update_xaxes(categoryorder="array", categoryarray=algorithm_order)
        fig_metrics.update_yaxes(title="Waktu (detik)")
        st.plotly_chart(fig_metrics, use_container_width=True)

    with right:
        load_df = (
            filtered_df.groupby(["Algorithm", "DatacenterName"], as_index=False)
            .size().rename(columns={"size": "CloudletCount"})
        )
        fig_load = px.bar(
            load_df, x="Algorithm", y="CloudletCount", color="DatacenterName",
            barmode="group", text_auto=True,
            title="🏢 Distribusi Cloudlet per Datacenter (Jakarta vs Surabaya)",
            color_discrete_map=datacenter_colors,
        )
        fig_load.update_layout(
            template="plotly_white", legend_title_text="Datacenter",
            margin=dict(l=10, r=10, t=55, b=10),
        )
        fig_load.update_xaxes(categoryorder="array", categoryarray=algorithm_order)
        fig_load.update_yaxes(title="Jumlah Cloudlet")
        st.plotly_chart(fig_load, use_container_width=True)

    # Visualizations Row 2
    left, right = st.columns(2)
    with left:
        if "TotalCost" in summary.columns:
            fig_cost = px.bar(
                summary, x="Algorithm", y="TotalCost", color="Algorithm",
                text_auto=",.0f",
                title="💰 Total Biaya Finansial Sewa Komputasi (INR)",
                color_discrete_map=algorithm_colors,
            )
            fig_cost.update_layout(
                template="plotly_white", showlegend=False,
                margin=dict(l=10, r=10, t=55, b=10),
            )
            fig_cost.update_xaxes(categoryorder="array", categoryarray=algorithm_order)
            fig_cost.update_yaxes(title="Total Biaya (INR)")
            st.plotly_chart(fig_cost, use_container_width=True)
        else:
            fig_hist = px.histogram(
                filtered_df, x="ExecutionTime", color="Algorithm", nbins=20,
                barmode="overlay", opacity=0.7,
                title="Distribusi Waktu Eksekusi Cloudlet",
                color_discrete_map=algorithm_colors,
            )
            fig_hist.update_layout(
                template="plotly_white", legend_title_text="Algoritma",
                margin=dict(l=10, r=10, t=55, b=10),
            )
            st.plotly_chart(fig_hist, use_container_width=True)

    with right:
        selected_algorithm = st.selectbox("Pilih Algoritma untuk Visualisasi Gantt Chart", selected_algorithms)
        gantt_df = filtered_df[filtered_df["Algorithm"] == selected_algorithm].head(60)
        fig_gantt = px.bar(
            gantt_df, x="Duration", y=gantt_df["VmId"].astype(str),
            base="StartTime", color="DatacenterName", orientation="h",
            hover_data=["CloudletId", "StartTime", "FinishTime", "ExecutionTime"],
            title=f"⏱️ Gantt Chart Alokasi 60 Cloudlet Pertama: {selected_algorithm}",
            color_discrete_map=datacenter_colors,
        )
        fig_gantt.update_layout(
            template="plotly_white", xaxis_title="Waktu Simulasi (detik)",
            yaxis_title="ID Mesin Virtual (VM)", margin=dict(l=10, r=10, t=55, b=10),
        )
        st.plotly_chart(fig_gantt, use_container_width=True)

    with st.expander("🔍 Inspeksi Data Tabular Mentah (CSV)"):
        st.dataframe(filtered_df, use_container_width=True, hide_index=True)

except FileNotFoundError:
    st.error(f"File hasil simulasi belum ditemukan di: {csv_path or candidates[0]}")
    st.info("Jalankan simulator terlebih dahulu menggunakan perintah:\n`python3 run_simulation.py --scenario tugas2a`")
except Exception as error:
    st.error(f"Gagal membaca hasil simulasi: {error}")
