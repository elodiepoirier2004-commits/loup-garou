"""
NovaBank – Dashboard Churn · Direction
Basé sur les données réelles : novabank_etude_de_cas_donnees.xlsx

Lancer avec :
    streamlit run novabank_dashboard.py

Placez le fichier Excel dans le même dossier que ce script.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os

st.set_page_config(
    page_title="NovaBank · Churn Dashboard",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { background: #F4F6F9; }
  [data-testid="stSidebar"] { background: #0D1B3E; }
  [data-testid="stSidebar"] * { color: #CBD5E0 !important; }
  div[data-testid="metric-container"] {
    background: white; border-radius: 10px; padding: 16px 20px;
    box-shadow: 0 1px 4px rgba(0,0,0,0.08); border-left: 4px solid #D62828;
  }
</style>
""", unsafe_allow_html=True)

EXCEL_FILE = "novabank_etude_de_cas_donnees.xlsx"

@st.cache_data
def load_data(path):
    sheets = pd.read_excel(path, sheet_name=None)
    return sheets["mensuel"], sheets["segment"], sheets["channel"]

script_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in dir() else "."
excel_path = os.path.join(script_dir, EXCEL_FILE)

if not os.path.exists(excel_path):
    st.error(f"Fichier introuvable : `{EXCEL_FILE}`\nPlacez le fichier Excel dans le même dossier que ce script.")
    st.stop()

df_mens, df_seg, df_chan = load_data(excel_path)

MONTH_ORDER = ["Juil", "Août", "Sept", "Oct", "Nov", "Déc"]
df_mens["month"] = pd.Categorical(df_mens["month"], categories=MONTH_ORDER, ordered=True)
df_mens = df_mens.sort_values("month")

with st.sidebar:
    st.markdown("## 🏦 NovaBank")
    st.markdown("### Filtres")
    st.markdown("---")
    months_sel = st.multiselect("Mois", options=MONTH_ORDER, default=MONTH_ORDER)
    segments_sel = st.multiselect("Segments", options=df_seg["segment"].tolist(), default=df_seg["segment"].tolist())
    channels_sel = st.multiselect("Canaux", options=df_chan["service_channel"].tolist(), default=df_chan["service_channel"].tolist())
    st.markdown("---")
    st.markdown("**Période :** Juil–Déc 2024")
    st.markdown("**Portefeuille :** ~844 k clients")

df_m = df_mens[df_mens["month"].isin(months_sel)]
df_s = df_seg[df_seg["segment"].isin(segments_sel)]
df_c = df_chan[df_chan["service_channel"].isin(channels_sel)]

st.markdown("# 🏦 NovaBank · Tableau de bord Churn")
st.markdown("**Comité de Direction – Décembre 2024**")
st.markdown("---")

first = df_mens.iloc[0]
last  = df_mens.iloc[-1]

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("📊 Clients actifs",          f"{int(last['active_customers_k'])} k")
k2.metric("⚠️ Churn (Déc)",             f"{last['churn_rate_pct']} %",
          delta=f"+{last['churn_rate_pct'] - first['churn_rate_pct']:.1f} pts vs Juil", delta_color="inverse")
k3.metric("📉 NPS (Déc)",               f"{int(last['nps'])}",
          delta=f"{last['nps'] - first['nps']:+d} pts vs Juil", delta_color="inverse")
k4.metric("🔧 Incidents app (Déc)",     f"{int(last['app_incidents_count'])}",
          delta=f"×{last['app_incidents_count']/first['app_incidents_count']:.1f} vs Juil", delta_color="inverse")
k5.metric("📱 Connexion mobile",         f"{last['mobile_login_success_pct']} %",
          delta=f"{last['mobile_login_success_pct'] - first['mobile_login_success_pct']:.1f} pts", delta_color="inverse")

st.markdown("---")

# Ligne 1
col1, col2 = st.columns([1.1, 1])

with col1:
    st.markdown("### 📈 Churn (%) et incidents applicatifs")
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df_m["month"], y=df_m["churn_rate_pct"], name="Churn (%)",
        mode="lines+markers+text", text=[f"{v}%" for v in df_m["churn_rate_pct"]],
        textposition="top center", line=dict(color="#D62828", width=3),
        marker=dict(size=8, color="#D62828"), yaxis="y1"
    ))
    fig.add_trace(go.Bar(
        x=df_m["month"], y=df_m["app_incidents_count"], name="Incidents app",
        marker_color="rgba(14,165,233,0.35)", yaxis="y2"
    ))
    fig.update_layout(
        plot_bgcolor="white", paper_bgcolor="white", height=330,
        margin=dict(l=10, r=10, t=10, b=30), legend=dict(orientation="h", y=-0.2),
        yaxis=dict(title="Churn (%)", color="#D62828", gridcolor="#F0F0F0"),
        yaxis2=dict(title="Incidents", side="right", overlaying="y", showgrid=False, color="#0EA5E9"),
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.markdown("### 📣 Plaintes et NPS")
    fig2 = go.Figure()
    fig2.add_trace(go.Bar(
        x=df_m["month"], y=df_m["complaints_count"], name="Plaintes",
        marker_color="rgba(214,40,40,0.45)", yaxis="y1"
    ))
    fig2.add_trace(go.Scatter(
        x=df_m["month"], y=df_m["nps"], name="NPS",
        mode="lines+markers+text", text=df_m["nps"].astype(str),
        textposition="top center", line=dict(color="#0EA5E9", width=3),
        marker=dict(size=8, color="#0EA5E9"), yaxis="y2"
    ))
    fig2.update_layout(
        plot_bgcolor="white", paper_bgcolor="white", height=330,
        margin=dict(l=10, r=10, t=10, b=30), legend=dict(orientation="h", y=-0.2),
        yaxis=dict(title="Plaintes", color="#D62828", gridcolor="#F0F0F0"),
        yaxis2=dict(title="NPS", side="right", overlaying="y", showgrid=False, color="#0EA5E9"),
    )
    st.plotly_chart(fig2, use_container_width=True)

# Ligne 2
col3, col4 = st.columns(2)

with col3:
    st.markdown("### 🎯 Churn et NPS par segment")
    df_s2 = df_s.sort_values("churn_rate_pct", ascending=False)
    seg_colors = ["#D62828","#F59E0B","#0EA5E9","#7C3AED","#10B981"]
    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        name="Churn (%)", x=df_s2["segment"], y=df_s2["churn_rate_pct"],
        marker_color=seg_colors[:len(df_s2)], yaxis="y1",
        text=[f"{v}%" for v in df_s2["churn_rate_pct"]], textposition="outside"
    ))
    fig3.add_trace(go.Scatter(
        name="NPS", x=df_s2["segment"], y=df_s2["nps"],
        mode="markers", marker=dict(size=14, color="#1E293B", symbol="diamond"),
        yaxis="y2"
    ))
    fig3.update_layout(
        plot_bgcolor="white", paper_bgcolor="white", height=330,
        margin=dict(l=10, r=10, t=10, b=30), legend=dict(orientation="h", y=-0.2),
        yaxis=dict(title="Churn (%)", gridcolor="#F0F0F0"),
        yaxis2=dict(title="NPS", side="right", overlaying="y", showgrid=False),
    )
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.markdown("### 🔧 Incidents et satisfaction par canal")
    df_c2 = df_c.sort_values("incident_rate_pct", ascending=True)
    fig4 = go.Figure()
    fig4.add_trace(go.Bar(
        name="Taux incident (%)", y=df_c2["service_channel"], x=df_c2["incident_rate_pct"],
        orientation="h", marker_color="#D62828",
        text=[f"{v}%" for v in df_c2["incident_rate_pct"]], textposition="outside"
    ))
    fig4.add_trace(go.Scatter(
        name="Satisfaction (/5)", y=df_c2["service_channel"], x=df_c2["customer_satisfaction"],
        mode="markers", marker=dict(size=13, color="#10B981", symbol="circle"), xaxis="x2"
    ))
    fig4.update_layout(
        plot_bgcolor="white", paper_bgcolor="white", height=330,
        margin=dict(l=10, r=10, t=10, b=30), legend=dict(orientation="h", y=-0.2),
        xaxis=dict(title="Taux d'incident (%)", gridcolor="#F0F0F0"),
        xaxis2=dict(title="Satisfaction (/5)", side="top", overlaying="x", showgrid=False, range=[0,5]),
    )
    st.plotly_chart(fig4, use_container_width=True)

# Ligne 3
col5, col6 = st.columns([1.2, 1])

with col5:
    st.markdown("### 🔗 Satisfaction digitale vs Churn par canal")
    fig5 = px.scatter(
        df_c, x="customer_satisfaction", y="churn_rate_pct",
        size="contact_volume_k", color="incident_rate_pct",
        text="service_channel",
        color_continuous_scale=["#10B981","#F59E0B","#D62828"],
        labels={"customer_satisfaction": "Satisfaction (/5)", "churn_rate_pct": "Churn (%)",
                "contact_volume_k": "Volume (k)", "incident_rate_pct": "Incident (%)"},
        size_max=55,
    )
    fig5.update_traces(textposition="top center")
    fig5.update_layout(
        plot_bgcolor="white", paper_bgcolor="white", height=310,
        margin=dict(l=10, r=10, t=10, b=30),
    )
    st.plotly_chart(fig5, use_container_width=True)

with col6:
    st.markdown("### 📱 Taux succès connexion mobile")
    login_val = float(last["mobile_login_success_pct"])
    fig6 = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=login_val,
        delta={"reference": float(first["mobile_login_success_pct"]), "valueformat": ".1f",
               "suffix": " pts", "decreasing": {"color": "#D62828"}},
        title={"text": "Connexion mobile réussie (Déc)<br><span style='font-size:11px;color:#6B7280'>Cible : ≥ 97 %</span>"},
        number={"suffix": " %", "valueformat": ".1f"},
        gauge={
            "axis": {"range": [90, 100]},
            "bar": {"color": "#D62828" if login_val < 95 else "#F59E0B" if login_val < 97 else "#10B981"},
            "bgcolor": "white", "borderwidth": 2, "bordercolor": "#E2E8F0",
            "steps": [
                {"range": [90, 95], "color": "#FEE2E2"},
                {"range": [95, 97], "color": "#FEF3C7"},
                {"range": [97, 100], "color": "#D1FAE5"},
            ],
            "threshold": {"line": {"color": "#D62828", "width": 3}, "value": 97}
        }
    ))
    fig6.update_layout(height=310, margin=dict(l=30, r=30, t=30, b=10), paper_bgcolor="white")
    st.plotly_chart(fig6, use_container_width=True)

# Diagnostic
st.markdown("---")
st.markdown("""
<div style="background:#FEF2F2;border:1px solid #D62828;border-left:6px solid #D62828;
            border-radius:8px;padding:16px 20px;margin:4px 0;">
  <b style="color:#D62828;font-size:15px;">⚠ Diagnostic consolidé</b><br><br>
  <span style="color:#374151;line-height:1.9;">
    Le churn a <b>doublé en 6 mois</b> (2,1 % → 4,2 %) tandis que le NPS s'effondrait de 41 à 19.
    L'application mobile affiche <b>8,9 % de taux d'incident</b> (vs 1,1 % en agence) et une satisfaction de <b>2,8/5</b>.
    Les <b>Nouveaux clients</b> (110 k, usage digital 96 %) atteignent 6,8 % de churn — <b>3× la moyenne</b>.
    Le taux de connexion mobile est tombé à <b>93,5 %</b> au pic de crise.
    Les plaintes ont doublé et le temps d'attente support aussi. <b>Priorité n°1 : corriger l'application mobile.</b>
  </span>
</div>
""", unsafe_allow_html=True)

# Onglets données brutes
st.markdown("---")
tab1, tab2, tab3 = st.tabs(["📅 Données mensuelles", "🎯 Segments", "📡 Canaux"])

with tab1:
    st.dataframe(df_m.rename(columns={
        "month": "Mois", "active_customers_k": "Clients actifs (k)",
        "new_customers_k": "Nouveaux clients (k)", "churn_rate_pct": "Churn (%)",
        "complaints_count": "Plaintes", "app_incidents_count": "Incidents app",
        "mobile_login_success_pct": "Connexion mobile (%)", "nps": "NPS",
        "avg_wait_time_min": "Attente support (min)", "digital_adoption_pct": "Adoption digitale (%)"
    }), use_container_width=True, hide_index=True)

with tab2:
    st.dataframe(df_s.rename(columns={
        "segment": "Segment", "customers_count_k": "Clients (k)",
        "churn_rate_pct": "Churn (%)", "avg_balance_eur": "Solde moyen (€)",
        "nps": "NPS", "complaint_rate_pct": "Taux réclamation (%)", "digital_usage_pct": "Usage digital (%)"
    }), use_container_width=True, hide_index=True)

with tab3:
    st.dataframe(df_c.rename(columns={
        "service_channel": "Canal", "incident_rate_pct": "Taux incident (%)",
        "avg_resolution_time_h": "Résolution (h)", "customer_satisfaction": "Satisfaction (/5)",
        "contact_volume_k": "Volume contacts (k)", "churn_rate_pct": "Churn (%)"
    }), use_container_width=True, hide_index=True)

st.caption("NovaBank · Data Science Team · Données Juil–Déc 2024")
