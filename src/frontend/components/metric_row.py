"""
Component for displaying KPI metrics.
"""
import streamlit as st

def render_metric_row(metrics):
    cols = st.columns(len(metrics))

    for col, metric in zip(cols, metrics):
        with col:
            st.metric(
                metric["label"],
                metric["value"],
                metric.get("delta", "")
            )
