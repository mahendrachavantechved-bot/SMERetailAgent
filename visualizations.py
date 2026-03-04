import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import networkx as nx
import flet as ft
import random

def sankey_pipeline_diagram(is_retail=True):
    stages = ["Intake","KYC","Underwriting","Decision","Disbursement"]
    values = [1000,850,700,650]
    fig = go.Figure(go.Sankey(
        node=dict(label=stages),
        link=dict(source=[0,1,2,3], target=[1,2,3,4], value=values)
    ))
    fig.update_layout(height=450)
    return ft.PlotlyChart(fig, expand=True)

def foir_dscr_gauge(value, title="FOIR"):
    fig = go.Figure(go.Indicator(mode="gauge+number", value=value,
                                 gauge={'axis':{'range':[0,100]}}))
    fig.update_layout(height=300)
    return ft.PlotlyChart(fig, expand=True)

def ltv_gauge(value):
    return foir_dscr_gauge(value, "LTV")

def radar_scorecard(result):
    metrics = ["CIBIL","Score"]
    values = [result.get("cibil_score",700)/8, random.uniform(60,90)]
    fig = go.Figure(go.Scatterpolar(r=values, theta=metrics, fill="toself"))
    fig.update_layout(polar=dict(radialaxis=dict(range=[0,100])), height=350)
    return ft.PlotlyChart(fig, expand=True)

def dpd_trend_chart():
    df = pd.DataFrame({
        "Month":["Jan","Feb","Mar","Apr","May","Jun"],
        "0-30":[600,580,550,520,500,470]
    })
    fig = px.line(df, x="Month", y="0-30")
    fig.update_layout(height=350)
    return ft.PlotlyChart(fig, expand=True)

def portfolio_treemap():
    df = pd.DataFrame({
        "City":["Bengaluru","Mumbai","Delhi"],
        "Amount":[150,120,100]
    })
    fig = px.treemap(df, path=["City"], values="Amount")
    fig.update_layout(height=350)
    return ft.PlotlyChart(fig, expand=True)

def cambridge_network(applicant):
    G = nx.spring_layout(nx.complete_graph(5))
    fig = go.Figure()
    for i in G:
        fig.add_trace(go.Scatter(x=[G[i][0]], y=[G[i][1]],
                                 mode="markers",
                                 marker=dict(size=20)))
    fig.update_layout(height=400)
    return ft.PlotlyChart(fig, expand=True)
