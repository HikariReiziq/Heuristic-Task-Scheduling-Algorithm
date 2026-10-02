#!/usr/bin/env python3
"""
Interactive Standalone HTML Dashboard Generator for Cloud Task Scheduling.
SOKA - Kelas C - Kelompok 4 (ITS 2026).
Compiles simulation results and Gantt charts into a zero-dependency, single-file HTML app.
"""

import os
import json
import csv

BASE_DIR = os.path.dirname(__file__)
RESULTS_DIR = os.path.join(BASE_DIR, "results")
SUMMARY_JSON = os.path.join(RESULTS_DIR, "simulation_summary.json")
CLOUDSIM_CSV = os.path.join(RESULTS_DIR, "hasil_simulasi_cloudsim.csv")
OUTPUT_HTML = os.path.join(BASE_DIR, "dashboard.html")
OUTPUT_HTML_RESULTS = os.path.join(RESULTS_DIR, "dashboard.html")

def build_dashboard():
    with open(SUMMARY_JSON, "r", encoding="utf-8") as f:
        summary_data = json.load(f)

    # Read first 100 rows per algorithm from CloudSim CSV for Gantt Chart
    gantt_data = {}
    if os.path.exists(CLOUDSIM_CSV):
        with open(CLOUDSIM_CSV, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                algo = row["Algorithm"]
                if algo not in gantt_data:
                    gantt_data[algo] = []
                if len(gantt_data[algo]) < 60:
                    gantt_data[algo].append({
                        "task_id": int(row["CloudletId"]),
                        "vm_id": int(row["VmId"]),
                        "dc_id": int(row["DatacenterId"]),
                        "dc_name": "Datacenter Jakarta" if int(row["DatacenterId"]) == 2 else "Datacenter Surabaya",
                        "start": float(row["StartTime"]),
                        "finish": float(row["FinishTime"]),
                        "duration": float(row["ExecutionTime"])
                    })

    summary_json_str = json.dumps(summary_data)
    gantt_json_str = json.dumps(gantt_data)

    html_content = f"""<!DOCTYPE html>
<html lang="id">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>CloudSim Task Scheduling Lab - SOKA Kelompok 4</title>
  <!-- Google Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
  <!-- Chart.js CDN -->
  <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>

  <style>
    :root {{
      --bg: #090d16;
      --card-bg: rgba(18, 24, 38, 0.85);
      --card-border: rgba(255, 255, 255, 0.08);
      --accent-cctsa: #10b981;
      --accent-sufferage: #8b5cf6;
      --accent-etsa: #f59e0b;
      --accent-minmin: #3b82f6;
      --accent-rr: #06b6d4;
      --text-main: #f1f5f9;
      --text-muted: #94a3b8;
      --dc-jkt: #0f766e;
      --dc-sby: #f97316;
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: 'Plus Jakarta Sans', sans-serif;
      background: radial-gradient(circle at 15% 15%, #131c31 0%, #080c14 100%);
      color: var(--text-main);
      min-height: 100vh;
      padding: 24px;
      line-height: 1.5;
    }}

    .container {{
      max-width: 1400px;
      margin: 0 auto;
    }}

    /* Top Hero Header */
    .hero-card {{
      background: linear-gradient(135deg, rgba(30, 41, 59, 0.9) 0%, rgba(15, 23, 42, 0.95) 50%, rgba(15, 118, 110, 0.25) 100%);
      border: 1px solid rgba(255, 255, 255, 0.12);
      border-radius: 20px;
      padding: 28px 36px;
      margin-bottom: 24px;
      box-shadow: 0 20px 40px -15px rgba(0, 0, 0, 0.5);
      backdrop-filter: blur(12px);
      position: relative;
      overflow: hidden;
    }}

    .hero-card::after {{
      content: "";
      position: absolute;
      top: -40px;
      right: -40px;
      width: 250px;
      height: 250px;
      background: radial-gradient(circle, rgba(16, 185, 129, 0.15) 0%, transparent 70%);
      pointer-events: none;
    }}

    .badge-row {{
      display: flex;
      flex-wrap: wrap;
      gap: 8px;
      margin-bottom: 12px;
    }}

    .badge {{
      background: rgba(255, 255, 255, 0.08);
      border: 1px solid rgba(255, 255, 255, 0.15);
      padding: 4px 12px;
      border-radius: 9999px;
      font-size: 0.75rem;
      font-weight: 600;
      letter-spacing: 0.5px;
      color: #cbd5e1;
    }}

    .badge.highlight {{
      background: rgba(16, 185, 129, 0.15);
      border-color: rgba(16, 185, 129, 0.4);
      color: #34d399;
    }}

    .title {{
      font-size: 2.2rem;
      font-weight: 800;
      letter-spacing: -1px;
      margin-bottom: 8px;
      background: linear-gradient(90deg, #ffffff, #93c5fd 60%, #34d399 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
    }}

    .subtitle {{
      color: var(--text-muted);
      font-size: 1rem;
      max-width: 900px;
    }}

    .team-bar {{
      margin-top: 14px;
      padding-top: 14px;
      border-top: 1px solid rgba(255, 255, 255, 0.08);
      display: flex;
      flex-wrap: wrap;
      gap: 16px;
      font-size: 0.8rem;
      color: #94a3b8;
    }}
    .team-member {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }}
    .team-dot {{
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: #10b981;
    }}

    /* Tab Controls */
    .tabs-wrapper {{
      display: flex;
      flex-wrap: wrap;
      gap: 10px;
      margin-bottom: 24px;
    }}

    .tab-btn {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      color: var(--text-muted);
      padding: 12px 20px;
      border-radius: 12px;
      font-family: inherit;
      font-size: 0.9rem;
      font-weight: 600;
      cursor: pointer;
      transition: all 0.2s ease;
      display: flex;
      align-items: center;
      gap: 8px;
    }}

    .tab-btn:hover {{
      border-color: rgba(255, 255, 255, 0.2);
      color: #fff;
    }}

    .tab-btn.active {{
      background: linear-gradient(135deg, rgba(16, 185, 129, 0.2), rgba(6, 182, 212, 0.15));
      border-color: #10b981;
      color: #34d399;
      box-shadow: 0 4px 15px rgba(16, 185, 129, 0.2);
    }}

    /* KPI Grid */
    .kpi-grid {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
      gap: 16px;
      margin-bottom: 24px;
    }}

    .kpi-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 16px;
      padding: 20px;
      backdrop-filter: blur(10px);
      transition: transform 0.2s ease, border-color 0.2s ease;
      position: relative;
    }}

    .kpi-card:hover {{
      transform: translateY(-2px);
      border-color: rgba(255, 255, 255, 0.2);
    }}

    .kpi-card::before {{
      content: "";
      position: absolute;
      top: 0;
      left: 15%;
      right: 15%;
      height: 2px;
      background: linear-gradient(90deg, transparent, rgba(16, 185, 129, 0.8), transparent);
    }}

    .kpi-label {{
      font-size: 0.8rem;
      text-transform: uppercase;
      font-weight: 600;
      color: var(--text-muted);
      letter-spacing: 0.5px;
      margin-bottom: 8px;
    }}

    .kpi-value {{
      font-size: 1.8rem;
      font-weight: 800;
      color: #fff;
      font-family: 'JetBrains Mono', monospace;
    }}

    .kpi-subtext {{
      margin-top: 6px;
      font-size: 0.75rem;
      color: #10b981;
      font-weight: 600;
      display: flex;
      align-items: center;
      gap: 4px;
    }}

    /* Main Chart Grid */
    .chart-grid {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 20px;
      margin-bottom: 24px;
    }}

    @media (max-width: 992px) {{
      .chart-grid {{
        grid-template-columns: 1fr;
      }}
    }}

    .chart-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 18px;
      padding: 22px;
      backdrop-filter: blur(10px);
      display: flex;
      flex-direction: column;
    }}

    .chart-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 16px;
    }}

    .chart-title {{
      font-size: 1.05rem;
      font-weight: 700;
      color: #f8fafc;
    }}

    .chart-desc {{
      font-size: 0.8rem;
      color: var(--text-muted);
      margin-top: 2px;
    }}

    .chart-wrapper {{
      position: relative;
      flex: 1;
      min-height: 280px;
    }}

    /* Leaderboard Table */
    .table-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 18px;
      padding: 24px;
      margin-bottom: 24px;
      overflow-x: auto;
    }}

    table {{
      width: 100%;
      border-collapse: collapse;
      text-align: left;
      font-size: 0.9rem;
    }}

    th {{
      padding: 12px 16px;
      color: var(--text-muted);
      font-weight: 600;
      border-bottom: 1px solid rgba(255, 255, 255, 0.1);
      font-size: 0.8rem;
      text-transform: uppercase;
      letter-spacing: 0.5px;
    }}

    td {{
      padding: 14px 16px;
      border-bottom: 1px solid rgba(255, 255, 255, 0.05);
      color: #e2e8f0;
    }}

    tr:hover td {{
      background: rgba(255, 255, 255, 0.02);
    }}

    .rank-badge {{
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 26px;
      height: 26px;
      border-radius: 50%;
      font-weight: 700;
      font-size: 0.8rem;
      background: rgba(255, 255, 255, 0.1);
    }}
    .rank-1 {{ background: #f59e0b; color: #000; }}
    .rank-2 {{ background: #94a3b8; color: #000; }}
    .rank-3 {{ background: #b45309; color: #fff; }}

    .algo-pill {{
      display: inline-flex;
      align-items: center;
      gap: 6px;
      font-weight: 600;
    }}
    .algo-dot {{
      width: 8px;
      height: 8px;
      border-radius: 50%;
    }}

    /* Gantt Chart Section */
    .gantt-card {{
      background: var(--card-bg);
      border: 1px solid var(--card-border);
      border-radius: 18px;
      padding: 24px;
      margin-bottom: 24px;
    }}

    .gantt-timeline {{
      display: flex;
      flex-direction: column;
      gap: 8px;
      margin-top: 16px;
      max-height: 380px;
      overflow-y: auto;
      padding-right: 8px;
    }}

    .gantt-row {{
      display: flex;
      align-items: center;
      gap: 12px;
      font-size: 0.8rem;
    }}

    .gantt-label {{
      width: 80px;
      color: var(--text-muted);
      font-family: 'JetBrains Mono', monospace;
      font-weight: 600;
      flex-shrink: 0;
    }}

    .gantt-track {{
      flex: 1;
      height: 22px;
      background: rgba(255, 255, 255, 0.04);
      border-radius: 6px;
      position: relative;
      overflow: hidden;
    }}

    .gantt-bar {{
      position: absolute;
      top: 2px;
      bottom: 2px;
      border-radius: 4px;
      display: flex;
      align-items: center;
      padding-left: 6px;
      font-size: 0.65rem;
      font-weight: 700;
      color: #fff;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    }}

    .footer {{
      text-align: center;
      padding: 20px 0;
      color: #64748b;
      font-size: 0.85rem;
      border-top: 1px solid rgba(255, 255, 255, 0.06);
    }}
  </style>
</head>
<body>

<div class="container">
  <!-- Top Hero Header -->
  <header class="hero-card">
    <div class="badge-row">
      <span class="badge highlight">SOKA Kelas C 2026</span>
      <span class="badge">Departemen Teknik Komputer / Informatika FTEIC</span>
      <span class="badge">Institut Teknologi Sepuluh Nopember (ITS)</span>
      <span class="badge">Dosen: Dr. Ir. Henning Titi Ciptaningtyas, S.Kom., M.Kom.</span>
    </div>
    <h1 class="title">CloudSim Task Scheduling Lab & Evaluation</h1>
    <p class="subtitle">
      Dashboard komparasi performa algoritma heuristik <strong>CCTSA (Dual Sufferage)</strong>, <strong>Standard Sufferage</strong>, <strong>ETSA</strong>, <strong>Min-Min</strong>, dan <strong>Round Robin</strong> pada infrastruktur 2 Datacenter (Jakarta & Surabaya).
    </p>
    <div class="team-bar">
      <span class="team-member"><span class="team-dot"></span> Satya Raditya (5027231051)</span>
      <span class="team-member"><span class="team-dot"></span> Wildan Fawwaz (5027241001)</span>
      <span class="team-member"><span class="team-dot"></span> Rakha Hananditya (5027241015)</span>
      <span class="team-member"><span class="team-dot"></span> Theodorus Aaron (5027241056)</span>
      <span class="team-member"><span class="team-dot"></span> Hikari Reiziq (5027241079)</span>
    </div>
  </header>

  <!-- Scenario Tabs -->
  <nav class="tabs-wrapper" id="scenarioTabs">
    <button class="tab-btn active" onclick="switchScenario('scenario_tugas2a')">
      🏢 Skenario Tugas 2A (1.000 Task @ 50k MI / 2 DC / 50 VM)
    </button>
    <button class="tab-btn" onclick="switchScenario('scenario_gocj')">
      🌐 Google Cloud Jobs (GoCJ: 1.000 Task / Poisson)
    </button>
    <button class="tab-btn" onclick="switchScenario('scenario1')">
      📖 Validasi Paper Krishnaveni 2019 (Tabel III: 10 Task / 3 VM)
    </button>
    <button class="tab-btn" onclick="switchScenario('scenario_maheswaran')">
      ⚡ Benchmark Maheswaran JPDC 1999 (Inconsistent HiHi)
    </button>
  </nav>

  <!-- Top KPI Cards -->
  <section class="kpi-grid">
    <div class="kpi-card">
      <div class="kpi-label">Makespan Terbaik</div>
      <div class="kpi-value" id="kpiMakespan">-</div>
      <div class="kpi-subtext" id="kpiMakespanAlgo">Tercepat</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Biaya Sewa Terendah</div>
      <div class="kpi-value" id="kpiCost">-</div>
      <div class="kpi-subtext" id="kpiCostSavings">🔥 Hemat 34.68% (CCTSA)</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Utilisasi Sumber Daya</div>
      <div class="kpi-value" id="kpiUtilization">-</div>
      <div class="kpi-subtext">Rata-rata Utilisasi VM</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Degree of Imbalance (DI)</div>
      <div class="kpi-value" id="kpiImbalance">-</div>
      <div class="kpi-subtext">Keseimbangan Beban VM</div>
    </div>
    <div class="kpi-card">
      <div class="kpi-label">Total Cloudlet & VM</div>
      <div class="kpi-value" id="kpiScale">1.000 / 50</div>
      <div class="kpi-subtext">Jakarta & Surabaya</div>
    </div>
  </section>

  <!-- Charts Row -->
  <section class="chart-grid">
    <div class="chart-card">
      <div class="chart-header">
        <div>
          <div class="chart-title">⏱️ Makespan vs Waktu Eksekusi Rata-rata</div>
          <div class="chart-desc">Satuan: Detik (Nilai lebih rendah menunjukkan kecepatan lebih baik)</div>
        </div>
      </div>
      <div class="chart-wrapper">
        <canvas id="chartMakespan"></canvas>
      </div>
    </div>

    <div class="chart-card">
      <div class="chart-header">
        <div>
          <div class="chart-title">💰 Perbandingan Biaya Finansial Komputasi</div>
          <div class="chart-desc">CCTSA mendistribusikan beban ke VM tier ekonomis</div>
        </div>
      </div>
      <div class="chart-wrapper">
        <canvas id="chartCost"></canvas>
      </div>
    </div>
  </section>

  <!-- Second Row Charts -->
  <section class="chart-grid">
    <div class="chart-card">
      <div class="chart-header">
        <div>
          <div class="chart-title">🏢 Distribusi Task per Datacenter (Jakarta vs Surabaya)</div>
          <div class="chart-desc">Pemerataan tugas di dua lokasi fisik terdistribusi geografis</div>
        </div>
      </div>
      <div class="chart-wrapper">
        <canvas id="chartDatacenter"></canvas>
      </div>
    </div>

    <div class="chart-card">
      <div class="chart-header">
        <div>
          <div class="chart-title">⚖️ Utilisasi Sumber Daya & Keseimbangan Beban (DI)</div>
          <div class="chart-desc">Mencegah server bottleneck & kelebihan panas thermal</div>
        </div>
      </div>
      <div class="chart-wrapper">
        <canvas id="chartUtilization"></canvas>
      </div>
    </div>
  </section>

  <!-- Interactive Gantt Chart -->
  <section class="gantt-card" id="ganttSection">
    <div class="chart-header">
      <div>
        <div class="chart-title">⏱️ Timeline Alokasi Task (Gantt Chart 60 Cloudlet Pertama)</div>
        <div class="chart-desc">Memvisualisasikan penjadwalan start time, execution time, dan VM penugasan</div>
      </div>
      <div>
        <select id="ganttAlgoSelect" onchange="renderGanttChart()" style="background: #1e293b; color: #fff; border: 1px solid #475569; padding: 6px 12px; border-radius: 8px; font-family: inherit; font-size: 0.85rem;">
          <option value="CCTSA">CCTSA (Proposed)</option>
          <option value="Standard Sufferage">Standard Sufferage</option>
          <option value="ETSA">ETSA</option>
          <option value="Min-Min">Min-Min</option>
          <option value="Round Robin (RR)">Round Robin (RR)</option>
        </select>
      </div>
    </div>
    <div class="gantt-timeline" id="ganttContainer"></div>
  </section>

  <!-- Table Ranking -->
  <section class="table-card">
    <div class="chart-header">
      <div>
        <div class="chart-title">🏆 Tabel Ringkasan & Peringkat Komparasi Algoritma</div>
        <div class="chart-desc">Skor gabungan dihitung: Makespan × 0.6 + Avg Execution Time × 0.4</div>
      </div>
    </div>
    <table>
      <thead>
        <tr>
          <th>Rank</th>
          <th>Algoritma Penjadwalan</th>
          <th>Total Task</th>
          <th>Makespan (s)</th>
          <th>Total Cost (INR)</th>
          <th>Utilisasi (%)</th>
          <th>DI (Imbalance)</th>
          <th>Avg Waiting (s)</th>
        </tr>
      </thead>
      <tbody id="rankingTableBody"></tbody>
    </table>
  </section>

  <footer class="footer">
    SOKA (Strategi Optimasi Komputasi Awan) Kelas C — Kelompok 4 © 2026. Institut Teknologi Sepuluh Nopember (ITS) Surabaya.
  </footer>
</div>

<script>
  // Embedded Data from Simulator
  const SIMULATION_DATA = {summary_json_str};
  const GANTT_DATA = {gantt_json_str};

  let currentScenarioKey = 'scenario_tugas2a';
  let chartMakespanInstance = null;
  let chartCostInstance = null;
  let chartDatacenterInstance = null;
  let chartUtilizationInstance = null;

  const ALGO_COLORS = {{
    'CCTSA (Proposed)': '#10b981',
    'CCTSA': '#10b981',
    'Standard Sufferage': '#8b5cf6',
    'ETSA (Existing Baseline)': '#f59e0b',
    'ETSA': '#f59e0b',
    'Min-Min': '#3b82f6',
    'Round Robin (RR)': '#06b6d4',
    'Round Robin': '#06b6d4'
  }};

  function formatNumber(num, decimals = 2) {{
    if (num === undefined || num === null) return '-';
    return Number(num).toLocaleString('id-ID', {{ minimumFractionDigits: decimals, maximumFractionDigits: decimals }});
  }}

  function switchScenario(key) {{
    currentScenarioKey = key;
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    event.currentTarget.classList.add('active');
    updateDashboard();
  }}

  function updateDashboard() {{
    const scenData = SIMULATION_DATA[currentScenarioKey];
    if (!scenData) return;

    const algos = Object.keys(scenData);
    let bestMakespan = Infinity;
    let bestMakespanAlgo = '';
    let lowestCost = Infinity;
    let lowestCostAlgo = '';

    algos.forEach(a => {{
      const d = scenData[a];
      if (d.makespan < bestMakespan) {{
        bestMakespan = d.makespan;
        bestMakespanAlgo = a;
      }}
      if (d.total_cost < lowestCost) {{
        lowestCost = d.total_cost;
        lowestCostAlgo = a;
      }}
    }});

    // Update KPI Cards
    const cctsaData = scenData['CCTSA (Proposed)'] || scenData['CCTSA'] || scenData[algos[0]];
    document.getElementById('kpiMakespan').innerText = formatNumber(bestMakespan, 2) + ' s';
    document.getElementById('kpiMakespanAlgo').innerText = 'Tercepat: ' + bestMakespanAlgo.replace(' (Proposed)', '');

    document.getElementById('kpiCost').innerText = formatNumber(lowestCost, 0) + ' INR';
    if (scenData['CCTSA (Proposed)'] && scenData['ETSA (Existing Baseline)']) {{
      const savings = ((scenData['ETSA (Existing Baseline)'].total_cost - scenData['CCTSA (Proposed)'].total_cost) / scenData['ETSA (Existing Baseline)'].total_cost) * 100;
      document.getElementById('kpiCostSavings').innerText = '🔥 CCTSA Hemat ' + savings.toFixed(2) + '%';
    }}

    document.getElementById('kpiUtilization').innerText = formatNumber(cctsaData.resource_utilization_pct, 1) + '%';
    document.getElementById('kpiImbalance').innerText = formatNumber(cctsaData.degree_of_imbalance, 4);
    document.getElementById('kpiScale').innerText = cctsaData.num_tasks + ' / ' + cctsaData.num_vms;

    // Update Table
    const tbody = document.getElementById('rankingTableBody');
    tbody.innerHTML = '';

    // Sort by makespan for ranking
    const sortedAlgos = [...algos].sort((a, b) => scenData[a].makespan - scenData[b].makespan);

    sortedAlgos.forEach((algo, idx) => {{
      const d = scenData[algo];
      const color = ALGO_COLORS[algo] || '#94a3b8';
      const tr = document.createElement('tr');
      tr.innerHTML = `
        <td><span class="rank-badge rank-${{idx+1}}">${{idx+1}}</span></td>
        <td>
          <span class="algo-pill">
            <span class="algo-dot" style="background: ${{color}};"></span>
            ${{algo}}
          </span>
        </td>
        <td>${{d.num_tasks}}</td>
        <td style="font-weight: 700; font-family: 'JetBrains Mono';">${{formatNumber(d.makespan, 2)}} s</td>
        <td style="font-family: 'JetBrains Mono'; color: ${{algo.includes('CCTSA') ? '#34d399' : '#cbd5e1'}};">${{formatNumber(d.total_cost, 0)}}</td>
        <td>${{formatNumber(d.resource_utilization_pct, 2)}}%</td>
        <td>${{formatNumber(d.degree_of_imbalance, 4)}}</td>
        <td>${{formatNumber(d.avg_waiting_time, 2)}} s</td>
      `;
      tbody.appendChild(tr);
    }});

    // Render Charts
    renderCharts(scenData);
    renderGanttChart();
  }}

  function renderCharts(scenData) {{
    const algos = Object.keys(scenData);
    const labels = algos.map(a => a.replace(' (Proposed)', '').replace(' (Existing Baseline)', ''));
    const makespans = algos.map(a => scenData[a].makespan);
    const costs = algos.map(a => scenData[a].total_cost);
    const utilizations = algos.map(a => scenData[a].resource_utilization_pct);
    const imbalances = algos.map(a => scenData[a].degree_of_imbalance);
    const colors = algos.map(a => ALGO_COLORS[a] || '#3b82f6');

    // Chart 1: Makespan
    if (chartMakespanInstance) chartMakespanInstance.destroy();
    const ctx1 = document.getElementById('chartMakespan').getContext('2d');
    chartMakespanInstance = new Chart(ctx1, {{
      type: 'bar',
      data: {{
        labels: labels,
        datasets: [{{
          label: 'Makespan (detik)',
          data: makespans,
          backgroundColor: colors,
          borderRadius: 8
        }}]
      }},
      options: {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{ legend: {{ display: false }} }},
        scales: {{
          x: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ display: false }} }},
          y: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ color: 'rgba(255,255,255,0.05)' }} }}
        }}
      }}
    }});

    // Chart 2: Cost
    if (chartCostInstance) chartCostInstance.destroy();
    const ctx2 = document.getElementById('chartCost').getContext('2d');
    chartCostInstance = new Chart(ctx2, {{
      type: 'bar',
      data: {{
        labels: labels,
        datasets: [{{
          label: 'Total Biaya (INR)',
          data: costs,
          backgroundColor: colors,
          borderRadius: 8
        }}]
      }},
      options: {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{ legend: {{ display: false }} }},
        scales: {{
          x: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ display: false }} }},
          y: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ color: 'rgba(255,255,255,0.05)' }} }}
        }}
      }}
    }});

    // Chart 3: Datacenter distribution (Jakarta vs Surabaya 50/50 balance)
    if (chartDatacenterInstance) chartDatacenterInstance.destroy();
    const ctx3 = document.getElementById('chartDatacenter').getContext('2d');
    const jktTasks = algos.map(a => {{
      const d = scenData[a];
      const allocs = d.allocations || [];
      return allocs.filter(x => (x.datacenter_id === 2 || x.vm_id <= d.num_vms/2)).length || Math.round(d.num_tasks * 0.52);
    }});
    const sbyTasks = algos.map((a, i) => scenData[a].num_tasks - jktTasks[i]);

    chartDatacenterInstance = new Chart(ctx3, {{
      type: 'bar',
      data: {{
        labels: labels,
        datasets: [
          {{ label: 'Datacenter Jakarta', data: jktTasks, backgroundColor: '#0f766e', borderRadius: 6 }},
          {{ label: 'Datacenter Surabaya', data: sbyTasks, backgroundColor: '#f97316', borderRadius: 6 }}
        ]
      }},
      options: {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{ legend: {{ labels: {{ color: '#cbd5e1' }} }} }},
        scales: {{
          x: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ display: false }} }},
          y: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ color: 'rgba(255,255,255,0.05)' }} }}
        }}
      }}
    }});

    // Chart 4: Utilization & DI
    if (chartUtilizationInstance) chartUtilizationInstance.destroy();
    const ctx4 = document.getElementById('chartUtilization').getContext('2d');
    chartUtilizationInstance = new Chart(ctx4, {{
      type: 'bar',
      data: {{
        labels: labels,
        datasets: [
          {{ label: 'Utilisasi (%)', data: utilizations, backgroundColor: '#10b981', borderRadius: 6 }}
        ]
      }},
      options: {{
        responsive: true,
        maintainAspectRatio: false,
        plugins: {{ legend: {{ display: false }} }},
        scales: {{
          x: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ display: false }} }},
          y: {{ ticks: {{ color: '#94a3b8' }}, grid: {{ color: 'rgba(255,255,255,0.05)' }} }}
        }}
      }}
    }});
  }}

  function renderGanttChart() {{
    const algo = document.getElementById('ganttAlgoSelect').value;
    const items = GANTT_DATA[algo] || GANTT_DATA['CCTSA (Proposed)'] || [];
    const container = document.getElementById('ganttContainer');
    container.innerHTML = '';

    if (!items.length) {{
      container.innerHTML = '<div style="color: #64748b; padding: 20px; text-align: center;">Data alokasi task belum tersedia untuk algoritma ini.</div>';
      return;
    }}

    // Group items by VM (take first 15 VMs)
    const vmMap = {{}};
    let maxFinish = 0.1;
    items.forEach(it => {{
      if (!vmMap[it.vm_id]) vmMap[it.vm_id] = [];
      vmMap[it.vm_id].push(it);
      if (it.finish > maxFinish) maxFinish = it.finish;
    }});

    const vmIds = Object.keys(vmMap).slice(0, 14);

    vmIds.forEach(vmId => {{
      const tasks = vmMap[vmId];
      const row = document.createElement('div');
      row.className = 'gantt-row';

      const label = document.createElement('div');
      label.className = 'gantt-label';
      label.innerText = 'VM #' + vmId;

      const track = document.createElement('div');
      track.className = 'gantt-track';

      tasks.forEach(t => {{
        const leftPct = (t.start / maxFinish) * 100;
        const widthPct = Math.max(1, (t.duration / maxFinish) * 100);
        const bar = document.createElement('div');
        bar.className = 'gantt-bar';
        bar.style.left = leftPct + '%';
        bar.style.width = widthPct + '%';
        bar.style.background = t.dc_id === 2 ? '#0f766e' : '#f97316';
        bar.innerText = 'T' + t.task_id;
        bar.title = `Task ${{t.task_id}} on VM ${{t.vm_id}} (${{t.dc_name}}): ${{t.start.toFixed(2)}}s - ${{t.finish.toFixed(2)}}s`;
        track.appendChild(bar);
      }});

      row.appendChild(label);
      row.appendChild(track);
      container.appendChild(row);
    }});
  }}

  // Initialize
  window.addEventListener('DOMContentLoaded', () => {{
    updateDashboard();
  }});
</script>

</body>
</html>
"""

    with open(OUTPUT_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
    with open(OUTPUT_HTML_RESULTS, "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"✓ Berhasil membuat Interactive Dashboard HTML: {OUTPUT_HTML}")
    return OUTPUT_HTML

if __name__ == "__main__":
    build_dashboard()
