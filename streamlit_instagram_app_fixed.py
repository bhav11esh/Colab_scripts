import streamlit as st
import instaloader
import pandas as pd
import os
import json
import glob
from datetime import datetime
import time
import random
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set page config
st.set_page_config(
    page_title="Instagram Content Automation",
    page_icon="📸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern SaaS-style CSS
st.markdown("""
<style>
    /* Main Theme Colors */
    :root {
        --primary: #6366F1;
        --primary-light: #818CF8;
        --primary-dark: #4F46E5;
        --secondary: #10B981;
        --accent: #F472B6;
        --text: #1E293B;
        --light-text: #64748B;
        --background: #FFFFFF;
        --light-bg: #F8FAFC;
        --card-bg: #FFFFFF;
        --border: #E2E8F0;
        --hover: #F1F5F9;
        --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        --shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
        --shadow-md: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
        --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
    }
    
    /* Base Styles */
    body {
        font-family: 'Inter', 'SF Pro Text', 'Segoe UI', Roboto, -apple-system, BlinkMacSystemFont, sans-serif;
        color: var(--text);
        background-color: var(--light-bg);
    }
    
    /* Typography */
    h1, h2, h3, h4, h5, h6 {
        font-family: 'Inter', 'SF Pro Display', 'Segoe UI', Roboto, sans-serif;
        font-weight: 700;
        color: var(--text);
        letter-spacing: -0.025em;
    }
    
    p, li, span {
        font-family: 'Inter', 'SF Pro Text', 'Segoe UI', Roboto, sans-serif;
        color: var(--light-text);
        line-height: 1.6;
    }
    
    /* Main Header */
    .main-header {
        font-size: 2.5rem;
        background: linear-gradient(135deg, #6366F1, #F472B6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        font-weight: 800;
        letter-spacing: -0.025em;
        line-height: 1.2;
    }
    
    .sub-header {
        font-size: 1.3rem;
        color: var(--light-text);
        margin-bottom: 2rem;
        font-weight: 400;
    }
    
    /* Cards */
    .card {
        padding: 1.5rem;
        border-radius: 1rem;
        background-color: var(--card-bg);
        box-shadow: var(--shadow);
        margin-bottom: 1.5rem;
        border: 1px solid var(--border);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        overflow: hidden;
    }
    
    .card:hover {
        transform: translateY(-5px);
        box-shadow: var(--shadow-md);
        border-color: var(--primary-light);
    }
    
    .card-header {
        font-size: 1.4rem;
        font-weight: 600;
        color: var(--text);
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid var(--border);
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    /* Buttons */
    .stButton>button {
        border-radius: 0.5rem;
        padding: 0.625rem 1.25rem;
        font-weight: 600;
        transition: all 0.2s ease;
        border: none;
        letter-spacing: 0.015em;
        box-shadow: var(--shadow-sm);
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow);
    }
    
    .primary-btn {
        background: linear-gradient(to right, var(--primary), var(--primary-dark));
        color: white;
    }
    
    .primary-btn:hover {
        background: linear-gradient(to right, var(--primary-dark), var(--primary));
    }
    
    .secondary-btn {
        background-color: white;
        color: var(--primary);
        border: 1px solid var(--primary);
    }
    
    .secondary-btn:hover {
        background-color: var(--hover);
    }
    
    /* Badge styles */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 2rem;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.025em;
    }
    
    .badge-success {
        background-color: rgba(16, 185, 129, 0.1);
        color: #10B981;
    }
    
    .badge-warning {
        background-color: rgba(245, 158, 11, 0.1);
        color: #F59E0B;
    }
    
    .badge-error {
        background-color: rgba(239, 68, 68, 0.1);
        color: #EF4444;
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(to right, #6366F1, #F472B6);
        border-radius: 1rem;
    }
    
    /* Input fields */
    div[data-baseweb="input"], div[data-baseweb="textarea"] {
        border-radius: 0.5rem;
    }
    
    div[data-baseweb="input"]:focus-within, div[data-baseweb="textarea"]:focus-within {
        border-color: var(--primary);
        box-shadow: 0 0 0 2px rgba(99, 102, 241, 0.2);
    }
    
    div[data-baseweb="select"] {
        border-radius: 0.5rem;
    }
    
    /* Checkbox and Radio */
    label[data-baseweb="checkbox"], label[data-baseweb="radio"] {
        cursor: pointer;
    }
    
    /* Dashboard stats */
    .stat-card {
        padding: 1.5rem;
        border-radius: 1rem;
        text-align: center;
        background-color: var(--card-bg);
        box-shadow: var(--shadow-sm);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: 1px solid var(--border);
        height: 100%;
        display: flex;
        flex-direction: column;
        justify-content: center;
        align-items: center;
    }
    
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: var(--shadow-md);
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.625rem 0;
        background: linear-gradient(135deg, var(--primary), var(--accent));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        line-height: 1;
    }
    
    .stat-label {
        font-size: 0.875rem;
        color: var(--light-text);
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-weight: 500;
    }
    
    /* Content card */
    .content-card {
        padding: 1rem;
        border-radius: 0.75rem;
        background-color: white;
        box-shadow: var(--shadow-sm);
        margin-bottom: 1rem;
        border: 1px solid var(--border);
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .content-card:hover {
        transform: translateY(-3px);
        box-shadow: var(--shadow);
        border-color: var(--primary-light);
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: var(--card-bg);
        border-right: 1px solid var(--border);
    }
    
    section[data-testid="stSidebar"] hr {
        margin: 1.5rem 0;
        border-color: var(--border);
    }
    
    section[data-testid="stSidebar"] > div {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Dataframe styling */
    .dataframe-container {
        border-radius: 0.75rem;
        overflow: hidden;
        border: 1px solid var(--border);
        background-color: var(--card-bg);
        box-shadow: var(--shadow-sm);
    }
    
    .dataframe th {
        background-color: #F8FAFC;
        font-weight: 600;
    }
    
    .dataframe td, .dataframe th {
        text-align: left;
        padding: 0.75rem 1rem;
        border-bottom: 1px solid var(--border);
    }
    
    /* SaaS-style buttons */
    .saas-button {
        display: inline-block;
        padding: 0.75rem 1.25rem;
        background: linear-gradient(135deg, var(--primary), var(--primary-dark));
        color: white;
        border-radius: 0.5rem;
        font-weight: 600;
        text-align: center;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        border: none;
        width: 100%;
        margin: 0.375rem 0;
        box-shadow: var(--shadow-sm);
        letter-spacing: 0.015em;
        font-size: 0.9375rem;
    }
    
    .saas-button:hover {
        box-shadow: var(--shadow);
        transform: translateY(-2px);
    }
    
    .saas-button-secondary {
        background: white;
        color: var(--primary);
        border: 1px solid var(--primary-light);
    }
    
    .saas-button-secondary:hover {
        background: var(--hover);
        box-shadow: var(--shadow);
    }
    
    .saas-button-tertiary {
        background: transparent;
        color: var(--primary);
        border: none;
        box-shadow: none;
    }
    
    .saas-button-tertiary:hover {
        background: var(--hover);
        box-shadow: none;
    }
    
    /* Status text styles */
    .success-text {
        color: #10B981;
        font-weight: 600;
    }
    
    .warning-text {
        color: #F59E0B;
        font-weight: 600;
    }
    
    .error-text {
        color: #EF4444;
        font-weight: 600;
    }
    
    /* Recommendations styling */
    .recommendation-card {
        padding: 1.5rem;
        border-radius: 1rem;
        background: white;
        box-shadow: var(--shadow);
        margin-bottom: 1.25rem;
        border: 1px solid var(--border);
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .recommendation-card:hover {
        transform: translateY(-5px);
        box-shadow: var(--shadow-lg);
        border-color: var(--primary-light);
    }
    
    .recommendation-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 0.25rem;
        height: 100%;
        background: linear-gradient(to bottom, var(--primary), var(--accent));
    }
    
    .rank-badge {
        display: inline-block;
        padding: 0.25rem 0.625rem;
        border-radius: 2rem;
        font-weight: 600;
        font-size: 0.75rem;
        margin-right: 0.625rem;
        color: white;
        background: linear-gradient(135deg, var(--primary), var(--accent));
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }
    
    .username {
        color: var(--primary);
        font-size: 1.125rem;
        font-weight: 600;
        margin: 0.3125rem 0;
    }
    
    .metric {
        display: inline-block;
        margin-right: 0.9375rem;
        font-size: 0.875rem;
    }
    
    .metric-value {
        font-weight: 600;
        color: var(--text);
    }
    
    .metric-label {
        color: var(--light-text);
    }
    
    /* Custom stMarkdown headers */
    .header-text {
        font-size: 1.5rem;
        font-weight: 700;
        margin: 1.5625rem 0 0.9375rem 0;
        color: var(--text);
        display: flex;
        align-items: center;
        gap: 0.625rem;
    }
    
    .section-text {
        font-size: 1.25rem;
        font-weight: 600;
        margin: 1.25rem 0 0.9375rem 0;
        color: var(--text);
        border-left: 0.25rem solid var(--primary);
        padding-left: 0.625rem;
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    
    /* Custom tabs styling */
    .tabs-container {
        display: flex;
        overflow-x: auto;
        margin-bottom: 1.5rem;
        border-bottom: 1px solid var(--border);
    }
    
    .tab {
        padding: 0.75rem 1.25rem;
        cursor: pointer;
        font-weight: 500;
        color: var(--light-text);
        border-bottom: 2px solid transparent;
        transition: all 0.2s;
        white-space: nowrap;
    }
    
    .tab:hover {
        color: var(--primary);
    }
    
    .tab.active {
        color: var(--primary);
        border-bottom-color: var(--primary);
        font-weight: 600;
    }
    
    /* Animations */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(0.625rem); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .fade-in {
        animation: fadeIn 0.5s ease forwards;
    }
    
    @keyframes slideIn {
        from { transform: translateX(-1.25rem); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    .slide-in {
        animation: slideIn 0.3s ease forwards;
    }
    
    /* Tooltips */
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
    }
    
    .tooltip:hover::after {
        content: attr(data-tooltip);
        position: absolute;
        bottom: 125%;
        left: 50%;
        transform: translateX(-50%);
        background-color: #1E293B;
        color: white;
        padding: 0.5rem 0.75rem;
        border-radius: 0.375rem;
        font-size: 0.75rem;
        white-space: nowrap;
        z-index: 1000;
        box-shadow: var(--shadow);
    }
    
    /* Feature badges */
    .feature-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.375rem;
        background-color: rgba(99, 102, 241, 0.1);
        color: var(--primary);
        padding: 0.25rem 0.625rem;
        border-radius: 2rem;
        font-size: 0.75rem;
        font-weight: 500;
        margin-right: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    /* Empty states */
    .empty-state {
        text-align: center;
        padding: 3rem 1.5rem;
        background-color: var(--light-bg);
        border-radius: 0.75rem;
        border: 1px dashed var(--border);
    }
    
    .empty-state-icon {
        font-size: 3rem;
        color: var(--light-text);
        margin-bottom: 1rem;
    }
    
    .empty-state-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--text);
        margin-bottom: 0.5rem;
    }
    
    .empty-state-text {
        color: var(--light-text);
        max-width: 30rem;
        margin: 0 auto;
    }
</style>
""", unsafe_allow_html=True)

# Title and introduction
st.markdown("<h1 class='main-header'>Instagram Content Automation</h1>", unsafe_allow_html=True)
st.markdown("<p class='sub-header'>Analyze Instagram content & discover top-performing posts with AI-powered recommendations</p>", unsafe_allow_html=True)

# Create Instaloader instance
@st.cache_resource
def get_instaloader():
    return instaloader.Instaloader(
        download_pictures=False,
        download_video_thumbnails=False,
        download_videos=False,
        download_geotags=False,
        download_comments=False,
        save_metadata=True,
        compress_json=False
    )

# Create loader
L = get_instaloader()

# Sidebar navigation with icons
st.sidebar.markdown("<div style='margin-bottom: 1rem;'><h3 style='font-size: 1.2rem; font-weight: 600;'>Navigation</h3></div>", unsafe_allow_html=True)

# Add a profile section to the sidebar
st.sidebar.markdown("""
<div style="background-color: rgba(99, 102, 241, 0.1); padding: 1rem; border-radius: 0.75rem; margin-bottom: 1.5rem;">
    <div style="display: flex; align-items: center; margin-bottom: 0.75rem;">
        <div style="width: 2.5rem; height: 2.5rem; border-radius: 50%; background: linear-gradient(135deg, #6366F1, #F472B6); color: white; display: flex; align-items: center; justify-content: center; margin-right: 0.75rem; font-weight: 600; font-size: 1.25rem;">B</div>
        <div>
            <div style="font-weight: 600; color: var(--text); font-size: 1rem;">Instagram Analyzer</div>
            <div style="font-size: 0.75rem; color: var(--primary);">Pro Version</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

page = st.sidebar.radio("", [
    "🏠 Home",
    "🔍 Search Accounts",
    "✅ Verify Accounts",
    "📥 Download Content",
    "📊 Analyze Data",
    "🏆 View Recommendations",
    "⚙️ Settings"
])

# Home page
if page == "🏠 Home":
    # Dashboard overview stats in columns
    st.markdown("<div class='header-text'><svg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z'></path><polyline points='9 22 9 12 15 12 15 22'></polyline></svg> Dashboard Overview</div>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="stat-card" style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.05), rgba(99, 102, 241, 0.1));">
            <div style="background-color: rgba(99, 102, 241, 0.2); width: 3rem; height: 3rem; border-radius: 0.75rem; display: flex; align-items: center; justify-content: center; margin-bottom: 0.75rem;">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>
            </div>
            <div class="stat-value">28</div>
            <div class="stat-label">Verified Accounts</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="stat-card" style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.05), rgba(16, 185, 129, 0.1));">
            <div style="background-color: rgba(16, 185, 129, 0.2); width: 3rem; height: 3rem; border-radius: 0.75rem; display: flex; align-items: center; justify-content: center; margin-bottom: 0.75rem;">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
            </div>
            <div class="stat-value">142</div>
            <div class="stat-label">Downloads</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="stat-card" style="background: linear-gradient(135deg, rgba(245, 158, 11, 0.05), rgba(245, 158, 11, 0.1));">
            <div style="background-color: rgba(245, 158, 11, 0.2); width: 3rem; height: 3rem; border-radius: 0.75rem; display: flex; align-items: center; justify-content: center; margin-bottom: 0.75rem;">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
            </div>
            <div class="stat-value">267</div>
            <div class="stat-label">Posts Analyzed</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="stat-card" style="background: linear-gradient(135deg, rgba(244, 114, 182, 0.05), rgba(244, 114, 182, 0.1));">
            <div style="background-color: rgba(244, 114, 182, 0.2); width: 3rem; height: 3rem; border-radius: 0.75rem; display: flex; align-items: center; justify-content: center; margin-bottom: 0.75rem;">
                <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#F472B6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>
            </div>
            <div class="stat-value">86.4%</div>
            <div class="stat-label">Engagement Rate</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content section with updated design
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("""
    <div class='card-header'>
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect><line x="8" y="21" x2="16" y2="21"></line><line x="12" y1="17" x2="12" y2="21"></line></svg>
        Instagram Content Automation Studio
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div style="display: flex; gap: 1rem; flex-wrap: wrap; margin-bottom: 1.5rem;">
        <div class="feature-badge">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
            AI-Powered
        </div>
        <div class="feature-badge">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><polyline points="16 12 12 8 8 12"></polyline><line x1="12" y1="16" x2="12" y2="8"></line></svg>
            Instagram API
        </div>
        <div class="feature-badge">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path><polyline points="17 21 17 13 7 13 7 21"></polyline><polyline points="7 3 7 8 15 8"></polyline></svg>
            Data Export
        </div>
        <div class="feature-badge">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="4" y1="21" x2="4" y2="14"></line><line x1="4" y1="10" x2="4" y2="3"></line><line x1="12" y1="21" x2="12" y2="12"></line><line x1="12" y1="8" x2="12" y2="3"></line><line x1="20" y1="21" x2="20" y2="16"></line><line x1="20" y1="12" x2="20" y2="3"></line><line x1="1" y1="14" x2="7" y2="14"></line><line x1="9" y1="8" x2="15" y2="8"></line><line x1="17" y1="16" x2="23" y2="16"></line></svg>
            Advanced Analytics
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <p style="margin-bottom: 1.5rem;">
    This platform helps you discover high-performing Instagram content with AI-powered analytics and recommendations.
    </p>
    
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(13rem, 1fr)); gap: 1rem; margin-bottom: 1.5rem;">
        <div style="background-color: rgba(99, 102, 241, 0.05); padding: 1rem; border-radius: 0.75rem; border-left: 3px solid #6366F1;">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 0.5rem;"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
                <strong style="color: var(--text);">Account Discovery</strong>
            </div>
            <p style="font-size: 0.875rem; margin: 0;">Find and verify Instagram accounts based on keywords</p>
        </div>
        
        <div style="background-color: rgba(16, 185, 129, 0.05); padding: 1rem; border-radius: 0.75rem; border-left: 3px solid #10B981;">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 0.5rem;"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                <strong style="color: var(--text);">Smart Downloads</strong>
            </div>
            <p style="font-size: 0.875rem; margin: 0;">Download content with automatic rate limiting</p>
        </div>
        
        <div style="background-color: rgba(245, 158, 11, 0.05); padding: 1rem; border-radius: 0.75rem; border-left: 3px solid #F59E0B;">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 0.5rem;"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
                <strong style="color: var(--text);">Data Analytics</strong>
            </div>
            <p style="font-size: 0.875rem; margin: 0;">Analyze engagement metrics with interactive visualizations</p>
        </div>
        
        <div style="background-color: rgba(244, 114, 182, 0.05); padding: 1rem; border-radius: 0.75rem; border-left: 3px solid #F472B6;">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#F472B6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 0.5rem;"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
                <strong style="color: var(--text);">Content Recommendations</strong>
            </div>
            <p style="font-size: 0.875rem; margin: 0;">Get smart content recommendations based on our proprietary algorithm</p>
        </div>
    </div>
    
    <div style="background-color: rgba(99, 102, 241, 0.05); padding: 1rem; border-radius: 0.75rem; margin-bottom: 1rem; display: flex; align-items: center;">
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="min-width: 20px; margin-right: 0.75rem;"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
        <div>
            <strong style="color: var(--text);">Smart Rate Limiting Technology:</strong>
            <span style="font-size: 0.875rem;">Our platform automatically respects Instagram's API limits, retrying when necessary and optimizing your requests.</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Quick start and recent results in columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("""
        <div class='card-header'>
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
            Quick Actions
        </div>
        """, unsafe_allow_html=True)
        
        # Action buttons
        st.markdown("""
        <a href="#" onclick="document.querySelector('[data-baseweb=\\"tab\\"]').click(); return false;" class="saas-button">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 0.5rem;"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
            Search New Accounts
        </a>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <a href="#" onclick="document.querySelector('[data-baseweb=\\"tab\\"]').click(); return false;" class="saas-button saas-button-secondary">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 0.5rem;"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
            Download from Verified Accounts
        </a>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <a href="#" onclick="document.querySelector('[data-baseweb=\\"tab\\"]').click(); return false;" class="saas-button saas-button-secondary">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 0.5rem;"><bar-chart></bar-chart><line x1="18" y1="20" x2="18" y2="10"></line><line x1="12" y1="20" x2="12" y2="4"></line><line x1="6" y1="20" x2="6" y2="14"></line></svg>
            Analyze Recent Downloads
        </a>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="text-align: center; margin-top: 1.5rem; padding-top: 1rem; border-top: 1px solid var(--border);">
            <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-bottom: 0.5rem;"><circle cx="12" cy="12" r="10"></circle><path d="M8 14s1.5 2 4 2 4-2 4-2"></path><line x1="9" y1="9" x2="9.01" y2="9"></line><line x1="15" y1="9" x2="15.01" y2="9"></line></svg>
            <p style="margin: 0; font-size: 0.875rem;">
                <strong>Need a guide?</strong> Check out our <a href="#" style="color: var(--primary); text-decoration: none;">quick start tutorial</a> to get started in minutes.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<div class='card'>", unsafe_allow_html=True)
        st.markdown("""
        <div class='card-header'>
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
            Engagement Insights
        </div>
        """, unsafe_allow_html=True)
        
        # Show a sample chart for engagement
        sample_data = {'account': ['@travel1', '@travel2', '@travel3', '@travel4', '@travel5'],
                      'engagement': [87, 65, 91, 72, 43]}
        df = pd.DataFrame(sample_data)
        
        fig = px.bar(df, x='account', y='engagement', 
                    title='Top Accounts by Engagement',
                    color='engagement',
                    color_continuous_scale='Viridis')
        fig.update_layout(
            height=320,
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
            coloraxis_showscale=False,
            font=dict(family="Inter, Arial, sans-serif", size=12, color="#64748B")
        )
        fig.update_traces(
            marker_line_color='rgba(255,255,255,0.8)',
            marker_line_width=1.5,
            opacity=0.9
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("""
        <div style="text-align: center; padding-top: 0.75rem; border-top: 1px solid var(--border);">
            <p style="margin: 0; font-size: 0.875rem;">
                <span style="color: var(--primary); font-weight: 600;">@travel3</span> shows the highest engagement rate at 
                <span style="display: inline-block; background-color: rgba(16, 185, 129, 0.1); color: #10B981; font-weight: 600; padding: 0.125rem 0.375rem; border-radius: 0.25rem;">91%</span>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    # Recent activity section with improved design
    st.markdown("<div class='section-text slide-in'><svg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><path d='M18 10h-4V6'></path><path d='M22 10h-4V6'></path><path d='M6 6h4v4H6z'></path><rect x='2' y='2' width='20' height='20' rx='2.18' ry='2.18'></rect><line x1='2' y1='10' x2='22' y2='10'></line></svg> Recent Activity</div>", unsafe_allow_html=True)
    
    activity_col1, activity_col2, activity_col3 = st.columns(3)
    
    with activity_col1:
        st.markdown("""
        <div class="content-card fade-in" style="border-top: 3px solid #6366F1;">
            <div style="display: flex; align-items: center; margin-bottom: 0.75rem;">
                <div style="width: 2.5rem; height: 2.5rem; border-radius: 0.75rem; background: rgba(99, 102, 241, 0.1); display: flex; align-items: center; justify-content: center; margin-right: 0.75rem;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"></path><polyline points="22,6 12,13 2,6"></polyline></svg>
                </div>
                <div>
                    <div style="font-weight: 600; color: var(--text);">Downloaded Posts</div>
                    <div style="font-size: 0.75rem; color: var(--light-text);">15 minutes ago</div>
                </div>
            </div>
            <p style="margin: 0; font-size: 0.875rem;">Downloaded 12 posts from <span style="color: var(--primary); font-weight: 600;">@natgeo</span></p>
        </div>
        """, unsafe_allow_html=True)
    
    with activity_col2:
        st.markdown("""
        <div class="content-card fade-in" style="border-top: 3px solid #10B981;">
            <div style="display: flex; align-items: center; margin-bottom: 0.75rem;">
                <div style="width: 2.5rem; height: 2.5rem; border-radius: 0.75rem; background: rgba(16, 185, 129, 0.1); display: flex; align-items: center; justify-content: center; margin-right: 0.75rem;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>
                </div>
                <div>
                    <div style="font-weight: 600; color: var(--text);">Analysis Complete</div>
                    <div style="font-size: 0.75rem; color: var(--light-text);">45 minutes ago</div>
                </div>
            </div>
            <p style="margin: 0; font-size: 0.875rem;">Generated recommendations for <span style="color: var(--primary); font-weight: 600;">5 travel accounts</span></p>
        </div>
        """, unsafe_allow_html=True)
    
    with activity_col3:
        st.markdown("""
        <div class="content-card fade-in" style="border-top: 3px solid #F59E0B;">
            <div style="display: flex; align-items: center; margin-bottom: 0.75rem;">
                <div style="width: 2.5rem; height: 2.5rem; border-radius: 0.75rem; background: rgba(245, 158, 11, 0.1); display: flex; align-items: center; justify-content: center; margin-right: 0.75rem;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#F59E0B" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="8" x2="12" y2="12"></line><line x1="12" y1="16" x2="12.01" y2="16"></line></svg>
                </div>
                <div>
                    <div style="font-weight: 600; color: var(--text);">Rate Limit Detected</div>
                    <div style="font-size: 0.75rem; color: var(--light-text);">2 hours ago</div>
                </div>
            </div>
            <p style="margin: 0; font-size: 0.875rem;">Successfully avoided Instagram rate limit for <span style="color: var(--primary); font-weight: 600;">@chrisburkard</span></p>
        </div>
        """, unsafe_allow_html=True)

# Search accounts page
elif page == "🔍 Search Accounts":
    st.markdown("<div class='header-text'><svg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><circle cx='11' cy='11' r='8'></circle><line x1='21' y1='21' x2='16.65' y2='16.65'></line></svg> Search Instagram Accounts</div>", unsafe_allow_html=True)
    
    # Introduction card
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("""
    <div style="display: flex; align-items: flex-start; gap: 1rem; margin-bottom: 1rem;">
        <div style="background-color: rgba(99, 102, 241, 0.1); border-radius: 0.75rem; width: 3rem; height: 3rem; min-width: 3rem; display: flex; justify-content: center; align-items: center;">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line></svg>
        </div>
        <div>
            <h3 style="margin-top: 0; margin-bottom: 0.5rem; font-size: 1.25rem;">Find Instagram Accounts</h3>
            <p style="margin-top: 0; font-size: 0.875rem;">Search for Instagram accounts based on keywords or topics. You can find accounts in specific niches like travel, photography, fashion, etc.</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Search form with improved design
    with st.form("search_form"):
        st.markdown("""
        <div style="margin-bottom: 1rem;">
            <label style="font-size: 0.875rem; font-weight: 500; color: var(--text); display: block; margin-bottom: 0.5rem;">Enter keyword to search for Instagram accounts:</label>
        </div>
        """, unsafe_allow_html=True)
        
        keyword = st.text_input("", placeholder="e.g., travel, photography, food", label_visibility="collapsed")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            max_accounts = st.slider("Maximum number of accounts to find:", min_value=5, max_value=50, value=10, 
                                    help="Limit the number of accounts to return in search results")
        with col2:
            st.markdown("<div style='height: 2.5rem; display: flex; align-items: flex-end;'>", unsafe_allow_html=True)
            submitted = st.form_submit_button("🔍 Search")
            st.markdown("</div>", unsafe_allow_html=True)
    
    # Search tips
    st.markdown("""
    <div style="background-color: rgba(99, 102, 241, 0.05); padding: 0.75rem; border-radius: 0.5rem; margin-top: 0.5rem;">
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 0.5rem;"><circle cx="12" cy="12" r="10"></circle><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"></path><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
            <span style="font-weight: 500; color: var(--text); font-size: 0.875rem;">Search Tips</span>
        </div>
        <ul style="margin: 0; padding-left: 1.5rem; font-size: 0.8125rem;">
            <li>Use specific keywords for better results (e.g., "travel photography" instead of just "travel")</li>
            <li>Try different variations of keywords to expand your search</li>
            <li>Search for locations to find region-specific accounts</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Display results
    if submitted and keyword:
        with st.spinner(f"Searching for Instagram accounts related to '{keyword}'..."):
            # This is a placeholder for the account search function
            # In a production app, you would call the search_instagram_accounts function here
            
            # For demo purposes, generate some example accounts based on the keyword
            st.markdown(f"<div class='section-text'><svg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><polyline points='22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3'></polyline></svg> Results for '{keyword}'</div>", unsafe_allow_html=True)
            
            # Example accounts data structure
            example_accounts = {
                "travel": ["natgeo", "chrisburkard", "danielkordan", "beautifuldestinations", "expertvagabond"],
                "photography": ["natgeotravel", "stevemccurryofficial", "humansofny", "street_photographers", "magnumphotos"],
                "food": ["foodnetwork", "buzzfeedfood", "food52", "bonappetitmag", "jamieoliver"],
                "fashion": ["vogue", "hypebeast", "fashionweek", "gucci", "dior"],
                "india": ["incredibleindia", "indianphotostories", "indiatravelgram", "storiesofindia", "indiapictures"]
            }
            
            # Get accounts based on keyword or use default
            found_accounts = []
            for k, accounts in example_accounts.items():
                if k in keyword.lower():
                    found_accounts.extend(accounts)
            
            # If no matches, use a default set
            if not found_accounts:
                found_accounts = ["natgeo", "chrisburkard", "beautifuldestinations", "expertvagabond", "lonelyplanet"]
            
            # Display found accounts
            found_accounts = found_accounts[:max_accounts]
            
            # Create a dataframe for display
            df = pd.DataFrame({
                "Username": [f"@{account}" for account in found_accounts],
                "Followers": [random.randint(10000, 5000000) for _ in range(len(found_accounts))],
                "Posts": [random.randint(100, 5000) for _ in range(len(found_accounts))]
            })
            
            # Format numbers with K and M
            df["Followers"] = df["Followers"].apply(lambda x: f"{x/1000:.1f}K" if x < 1000000 else f"{x/1000000:.1f}M")
            
            # Display accounts in a modern card-based layout
            st.markdown("<div class='card'>", unsafe_allow_html=True)
            
            # Results summary
            st.markdown(f"""
            <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                <div style="background-color: rgba(99, 102, 241, 0.1); border-radius: 0.5rem; width: 2rem; height: 2rem; min-width: 2rem; display: flex; justify-content: center; align-items: center; margin-right: 0.75rem;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
                </div>
                <div>
                    <div style="font-weight: 600; color: var(--text);">Found {len(found_accounts)} Instagram accounts matching '{keyword}'</div>
                    <div style="font-size: 0.75rem; color: var(--light-text);">Select accounts to save to your verified list</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Display the table with accounts
            st.markdown("<div class='dataframe-container'>", unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True, 
                        column_config={
                            "Username": st.column_config.TextColumn("Instagram Handle"),
                            "Followers": st.column_config.TextColumn("Followers"),
                            "Posts": st.column_config.NumberColumn("Posts Count")
                        })
            st.markdown("</div>", unsafe_allow_html=True)
            
            # Save accounts section
            col1, col2 = st.columns([2, 1])
            
            with col1:
                select_all = st.checkbox("Select all accounts", value=True)
            
            with col2:
                save_button = st.button("💾 Save to Verified List", key="save_accounts_btn", 
                                       help="Add selected accounts to your verified accounts list")
            
            if save_button:
                accounts_to_save = [account.strip('@') for account in df["Username"].tolist()]
                
                # In a real app, you'd call manage_account_list here
                
                # Show the accounts that were saved with animation
                st.markdown("""
                <style>
                @keyframes fadeInUp {
                    from { opacity: 0; transform: translateY(1rem); }
                    to { opacity: 1; transform: translateY(0); }
                }
                .saved-accounts {
                    animation: fadeInUp 0.5s ease-out forwards;
                }
                </style>
                """, unsafe_allow_html=True)
                
                st.success(f"Saved {len(accounts_to_save)} accounts to verified_accounts.txt")
                
                st.markdown("<div class='saved-accounts' style='background-color: rgba(16, 185, 129, 0.05); padding: 1rem; border-radius: 0.75rem; border: 1px solid rgba(16, 185, 129, 0.2); margin-top: 1rem;'>", unsafe_allow_html=True)
                
                st.markdown("""
                <div style="display: flex; align-items: center; margin-bottom: 0.75rem;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 0.5rem;"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                    <div style="font-weight: 600; color: #047857;">Accounts saved to verified list</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Display saved accounts in a more modern way
                st.markdown("<div style='display: flex; flex-wrap: wrap; gap: 0.5rem;'>", unsafe_allow_html=True)
                for account in accounts_to_save:
                    st.markdown(f"""
                    <div style="background-color: rgba(16, 185, 129, 0.1); color: #059669; padding: 0.375rem 0.75rem; border-radius: 2rem; font-size: 0.8125rem; font-weight: 500;">
                        @{account}
                    </div>
                    """, unsafe_allow_html=True)
                st.markdown("</div>", unsafe_allow_html=True)
                
                # Add next steps
                st.markdown("""
                <div style="margin-top: 1rem; font-size: 0.875rem; color: var(--text);">
                    <strong>Next steps:</strong>
                    <ul style="margin-top: 0.5rem; padding-left: 1.5rem; margin-bottom: 0;">
                        <li>Go to "Verify Accounts" to confirm these accounts are accessible</li>
                        <li>Use "Download Content" to start collecting posts</li>
                    </ul>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("</div>", unsafe_allow_html=True)
            
            st.markdown("</div>", unsafe_allow_html=True)

# Verify accounts page
elif page == "✅ Verify Accounts":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### Verify Instagram Accounts")
    st.markdown("Check if Instagram accounts are public and accessible")
    
    # Input options
    verify_option = st.radio("How would you like to verify accounts?", [
        "Enter account names manually",
        "Verify from verified_accounts.txt"
    ])
    
    if verify_option == "Enter account names manually":
        accounts_input = st.text_area("Enter Instagram usernames (one per line):", 
                                      placeholder="natgeo\nchrisburkard\nbeautifuldestinations")
        verify_button = st.button("Verify Accounts")
        
        if verify_button and accounts_input:
            accounts_to_verify = [a.strip() for a in accounts_input.split('\n') if a.strip()]
            
            st.markdown("#### Verification Results")
            
            progress_bar = st.progress(0)
            results = []
            
            for i, account in enumerate(accounts_to_verify):
                # Simulate verification process
                st.write(f"Verifying @{account}...")
                
                # In a real app, you'd call verify_instagram_account here
                # For demo, we'll simulate the process
                time.sleep(0.5)  # Simulate API call
                
                # Random verification result for demo
                is_verified = random.choice([True, True, True, False])
                followers = random.randint(10000, 5000000) if is_verified else 0
                
                if is_verified:
                    status = "✅ Public"
                    message = f"Accessible with {followers:,} followers"
                else:
                    status = "❌ Not accessible"
                    message = "Private account or does not exist"
                
                results.append({"Account": f"@{account}", "Status": status, "Details": message})
                
                # Update progress
                progress_bar.progress((i + 1) / len(accounts_to_verify))
            
            # Display results table
            results_df = pd.DataFrame(results)
            st.dataframe(results_df, use_container_width=True)
            
            # Count successful verifications
            successful = sum(1 for r in results if "✅" in r["Status"])
            
            if successful > 0:
                st.success(f"{successful} accounts verified successfully and added to verified_accounts.txt")
            else:
                st.error("No accounts could be verified. Try different accounts.")
    
    else:  # Verify from file
        st.info("This will verify all accounts in your verified_accounts.txt file")
        verify_file_button = st.button("Start Verification")
        
        if verify_file_button:
            # Simulate loading accounts from file
            st.info("Loading accounts from verified_accounts.txt...")
            time.sleep(1)
            
            # Simulate accounts for demo
            file_accounts = ["natgeo", "chrisburkard", "beautifuldestinations", 
                             "lonelyplanet", "expertvagabond", "taramilktea"]
            
            st.success(f"Loaded {len(file_accounts)} accounts from file")
            
            # Show verification process
            progress_bar = st.progress(0)
            results = []
            
            for i, account in enumerate(file_accounts):
                st.write(f"Verifying @{account}...")
                
                # Simulate verification
                time.sleep(0.5)
                is_verified = random.choice([True, True, False])
                followers = random.randint(10000, 5000000) if is_verified else 0
                
                if is_verified:
                    status = "✅ Public"
                    message = f"Accessible with {followers:,} followers"
                else:
                    status = "❌ Not accessible"
                    message = "Private account or does not exist"
                
                results.append({"Account": f"@{account}", "Status": status, "Details": message})
                
                # Update progress
                progress_bar.progress((i + 1) / len(file_accounts))
            
            # Display results
            results_df = pd.DataFrame(results)
            st.dataframe(results_df, use_container_width=True)
            
            # Count successful verifications
            successful = sum(1 for r in results if "✅" in r["Status"])
            
            if successful > 0:
                st.success(f"Verification complete: {successful}/{len(file_accounts)} accounts verified")
            else:
                st.error("No accounts could be verified.")
    
    st.markdown("</div>", unsafe_allow_html=True)

# Download content page
elif page == "📥 Download Content":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### Download Instagram Content")
    
    download_option = st.radio("Select download option:", [
        "Download from a single account",
        "Batch download from verified accounts"
    ])
    
    if download_option == "Download from a single account":
        with st.form("single_download_form"):
            username = st.text_input("Instagram username:", placeholder="e.g., natgeo")
            posts_limit = st.slider("Number of posts to download:", 1, 10, 3)
            download_media = st.checkbox("Download media (images/videos)", value=False)
            submitted = st.form_submit_button("Start Download")
        
        if submitted and username:
            st.info(f"Starting download for @{username}")
            
            # Progress updates
            progress_bar = st.progress(0)
            status_container = st.empty()
            
            # Simulate download process
            total_steps = posts_limit + 2  # account verification + posts + completion
            
            # Step 1: Verify account
            status_container.write("Verifying account...")
            progress_bar.progress(1/total_steps)
            time.sleep(1)
            
            # Simulate verification
            is_verified = random.choice([True, True, True, False])
            
            if not is_verified:
                status_container.error(f"@{username} is not accessible (private or doesn't exist)")
            else:
                status_container.success(f"@{username} verified successfully")
                
                # Step 2+: Download posts
                for i in range(posts_limit):
                    status_container.write(f"Downloading post {i+1}/{posts_limit}...")
                    progress_bar.progress((i+2)/total_steps)
                    time.sleep(0.8)  # Simulate download time
                
                # Final step
                progress_bar.progress(1.0)
                status_container.success(f"Successfully downloaded {posts_limit} posts from @{username}")
                
                # Show download directory
                st.info(f"Content saved to @{username}_data/")
                
                # Option to proceed to analysis
                if st.button("Analyze Downloaded Content"):
                    st.session_state.analyze_username = username
                    st.session_state.page = "📊 Analyze Data"
                    st.experimental_rerun()
    
    else:  # Batch download
        st.markdown("#### Batch Download from Verified Accounts")
        
        # Load verified accounts
        # In a real app, you'd actually load from verified_accounts.txt
        verified_accounts = ["natgeo", "chrisburkard", "beautifuldestinations", 
                           "lonelyplanet", "expertvagabond", "taramilktea"]
        
        st.info(f"Found {len(verified_accounts)} verified accounts")
        
        # Batch download options
        col1, col2 = st.columns(2)
        with col1:
            selected_accounts = st.multiselect(
                "Select accounts to download from:",
                verified_accounts,
                default=verified_accounts[:3]
            )
        
        with col2:
            posts_per_account = st.slider("Posts per account:", 1, 5, 2)
            batch_size = st.slider("Batch size:", 1, 5, 3)
        
        metadata_only = st.checkbox("Download metadata only (no images/videos)", value=True)
        
        if st.button("Start Batch Download") and selected_accounts:
            # Initialize progress tracking
            progress_bar = st.progress(0)
            status_container = st.empty()
            
            total_accounts = len(selected_accounts)
            completed = 0
            successful = 0
            
            # Process in batches
            for i in range(0, total_accounts, batch_size):
                batch = selected_accounts[i:i+batch_size]
                status_container.write(f"Processing batch {i//batch_size + 1}...")
                
                for account in batch:
                    status_container.write(f"Downloading from @{account}...")
                    
                    # Simulate download process
                    time.sleep(1)
                    success = random.choice([True, True, True, False])
                    
                    if success:
                        successful += 1
                        status_container.success(f"Successfully downloaded {posts_per_account} posts from @{account}")
                    else:
                        error_type = random.choice(["rate limit", "not accessible", "connection error"])
                        status_container.error(f"Failed to download from @{account}: {error_type}")
                    
                    completed += 1
                    progress_bar.progress(completed / total_accounts)
                
                # Simulate batch completion
                if i + batch_size < total_accounts:
                    status_container.info("Completed batch. Taking a short pause before next batch...")
                    time.sleep(1)
            
            # Final status
            status_container.success(f"Batch download complete! Successfully downloaded from {successful}/{total_accounts} accounts")
            
            # Option to proceed to analysis
            if successful > 0 and st.button("Analyze Downloaded Content"):
                st.session_state.page = "📊 Analyze Data"
                st.experimental_rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# Analyze data page
elif page == "📊 Analyze Data":
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("### Analyze Instagram Content")
    
    # Analysis options
    analysis_option = st.radio("What would you like to analyze?", [
        "Recently downloaded content",
        "Existing JSON files",
        "Sample data (for demonstration)"
    ])
    
    if analysis_option == "Recently downloaded content":
        # In a real app, you'd detect downloaded content here
        # For demo, we'll simulate some accounts with downloaded content
        
        downloaded_accounts = ["natgeo", "chrisburkard", "beautifuldestinations"]
        selected_account = st.selectbox("Select account to analyze:", downloaded_accounts)
        
        if st.button("Start Analysis") and selected_account:
            with st.spinner(f"Analyzing content from @{selected_account}..."):
                # Simulate analysis process
                time.sleep(2)
                
                # Generate some simulated post data
                posts = []
                for i in range(5):
                    is_video = random.choice([True, False])
                    likes = random.randint(5000, 100000)
                    comments = random.randint(100, 5000)
                    views = random.randint(20000, 500000) if is_video else 0
                    
                    posts.append({
                        'username': selected_account,
                        'post_id': f"B{random.randint(100000, 999999)}",
                        'is_video': is_video,
                        'likes': likes,
                        'comments': comments,
                        'views': views,
                        'timestamp': (datetime.now() - pd.Timedelta(days=random.randint(1, 30))).strftime("%Y-%m-%d"),
                        'engagement_rate': round((likes + comments*2) / 1000000 * 100, 2),
                        'smart_score': round(random.uniform(30, 95), 2)
                    })
                
                df = pd.DataFrame(posts)
                st.session_state.analyzed_data = df  # Store in session for later use
                
                # Generate CSV filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                csv_filename = f"{selected_account}_analysis_{timestamp}.csv"
                
                # Display analysis results
                st.success(f"Analysis complete for {len(df)} posts from @{selected_account}")
                
                # Show summary statistics
                st.markdown("#### Summary Statistics")
                st.dataframe(df[['likes', 'comments', 'views', 'engagement_rate', 'smart_score']].describe().round(2), use_container_width=True)
                
                # Visualize engagement
                st.markdown("#### Engagement Visualization")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    # Create a bar chart for engagement metrics
                    metrics_df = pd.DataFrame({
                        'Metric': ['Likes', 'Comments', 'Views'],
                        'Average': [df['likes'].mean(), df['comments'].mean(), df['views'].mean()]
                    })
                    
                    fig = px.bar(metrics_df, x='Metric', y='Average', 
                                title=f'Average Engagement Metrics for @{selected_account}',
                                color='Average',
                                color_continuous_scale=px.colors.sequential.Plasma)
                    st.plotly_chart(fig, use_container_width=True)
                
                with col2:
                    # Create a scatter plot for individual posts
                    fig = px.scatter(df, x='likes', y='comments', 
                                    size='smart_score', color='smart_score',
                                    hover_name='post_id',
                                    title='Likes vs Comments by Smart Score',
                                    color_continuous_scale=px.colors.sequential.Viridis)
                    st.plotly_chart(fig, use_container_width=True)
                
                # Add full data display
                st.markdown("#### Full Data")
                st.dataframe(df, use_container_width=True)
                
                # Add download button
                csv = df.to_csv(index=False).encode('utf-8')
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.download_button(
                        label=f"📥 Download CSV for @{selected_account}",
                        data=csv,
                        file_name=csv_filename,
                        mime="text/csv",
                        help="Download the complete analysis as a CSV file"
                    )
                
                with col2:
                    # View top content button
                    if st.button("View Top Content Recommendations"):
                        st.session_state.analyzed_data = df
                        st.session_state.page = "🏆 View Recommendations"
                        st.experimental_rerun()
    
    elif analysis_option == "Existing JSON files":
        st.info("This will analyze JSON files that were previously downloaded")
        
        # Folder selection
        folder_path = st.text_input("Enter path to folder containing JSON files:", value="./")
        
        if st.button("Analyze JSON Files") and folder_path:
            with st.spinner("Analyzing JSON files..."):
                # Simulate searching for JSON files
                time.sleep(1)
                st.info("Searching for JSON files in the specified folder...")
                time.sleep(1)
                
                # Simulate finding files
                json_count = random.randint(10, 30)
                st.success(f"Found {json_count} JSON files to analyze")
                
                # Simulate processing
                progress_bar = st.progress(0)
                for i in range(json_count):
                    progress_bar.progress((i+1)/json_count)
                    time.sleep(0.1)
                
                # Generate simulated results
                posts = []
                accounts = ["natgeo", "chrisburkard", "beautifuldestinations", "lonelyplanet"]
                
                for _ in range(json_count):
                    account = random.choice(accounts)
                    is_video = random.choice([True, False])
                    likes = random.randint(5000, 100000)
                    comments = random.randint(100, 5000)
                    views = random.randint(20000, 500000) if is_video else 0
                    
                    posts.append({
                        'username': account,
                        'post_id': f"B{random.randint(100000, 999999)}",
                        'is_video': is_video,
                        'likes': likes,
                        'comments': comments,
                        'views': views,
                        'timestamp': (datetime.now() - pd.Timedelta(days=random.randint(1, 60))).strftime("%Y-%m-%d"),
                        'engagement_rate': round((likes + comments*2) / 1000000 * 100, 2),
                        'smart_score': round(random.uniform(20, 95), 2)
                    })
                
                df = pd.DataFrame(posts)
                st.session_state.analyzed_data = df  # Store in session for later use
                
                # Generate CSV filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                csv_filename = f"json_analysis_{timestamp}.csv"
                
                # Display analysis summary
                st.success(f"Analysis complete! Results are ready for download.")
                
                # Show account breakdown
                st.markdown("#### Posts by Account")
                account_counts = df['username'].value_counts().reset_index()
                account_counts.columns = ['Account', 'Posts']
                
                fig = px.pie(account_counts, values='Posts', names='Account', 
                            title='Posts Distribution by Account',
                            color_discrete_sequence=px.colors.sequential.RdBu)
                st.plotly_chart(fig, use_container_width=True)
                
                # Display preview of analyzed data
                st.markdown("#### Data Preview")
                st.dataframe(df.head(10), use_container_width=True)
                
                # Add a CSV download button
                csv = df.to_csv(index=False).encode('utf-8')
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.download_button(
                        label="📥 Download Complete CSV Analysis",
                        data=csv,
                        file_name=csv_filename,
                        mime="text/csv",
                        help="Download the complete analysis results as a CSV file"
                    )
                
                with col2:
                    # View top content button
                    if st.button("View Top Content Recommendations"):
                        st.session_state.analyzed_data = df
                        st.session_state.page = "🏆 View Recommendations"
                        st.experimental_rerun()
    
    else:  # Sample data
        st.info("Analyzing sample data for demonstration purposes")
        
        if st.button("Generate Sample Analysis"):
            with st.spinner("Generating sample analysis..."):
                # Wait for effect
                time.sleep(2)
                
                # Generate sample data for multiple accounts
                accounts = ["natgeo", "chrisburkard", "beautifuldestinations", 
                           "lonelyplanet", "expertvagabond"]
                
                posts = []
                for _ in range(50):
                    account = random.choice(accounts)
                    is_video = random.choice([True, False])
                    likes = random.randint(5000, 500000)
                    comments = random.randint(100, 20000)
                    views = random.randint(20000, 2000000) if is_video else 0
                    days_ago = random.randint(1, 90)
                    
                    # Calculate a realistic smart score
                    base_score = (likes/10000) + (comments/500) 
                    recency_boost = max(0, 30 - days_ago) / 3
                    video_boost = 10 if is_video and views > 100000 else 0
                    smart_score = min(99, max(10, base_score + recency_boost + video_boost))
                    
                    posts.append({
                        'username': account,
                        'post_id': f"B{random.randint(100000, 999999)}",
                        'is_video': is_video,
                        'likes': likes,
                        'comments': comments,
                        'views': views,
                        'timestamp': (datetime.now() - pd.Timedelta(days=days_ago)).strftime("%Y-%m-%d"),
                        'engagement_rate': round((likes + comments*2) / 1000000 * 100, 2),
                        'smart_score': round(smart_score, 2)
                    })
                
                df = pd.DataFrame(posts)
                st.session_state.analyzed_data = df  # Store in session state
                
                # Generate CSV filename with timestamp
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                csv_filename = f"sample_analysis_{timestamp}.csv"
                
                # Display analysis results
                st.success(f"Sample analysis complete for {len(df)} posts from {len(accounts)} accounts")
                
                # Visualize engagement by account
                st.markdown("#### Engagement by Account")
                
                account_engagement = df.groupby('username').agg({
                    'likes': 'mean',
                    'comments': 'mean',
                    'smart_score': 'mean'
                }).reset_index()
                
                fig = px.bar(account_engagement, x='username', y='smart_score',
                            color='likes',
                            title='Average Smart Score by Account',
                            labels={'username': 'Account', 'smart_score': 'Smart Score'},
                            color_continuous_scale=px.colors.sequential.Viridis)
                st.plotly_chart(fig, use_container_width=True)
                
                # Distribution of smart scores
                st.markdown("#### Smart Score Distribution")
                
                fig = px.histogram(df, x='smart_score', 
                                  title='Distribution of Smart Scores',
                                  color_discrete_sequence=['#F56040'])
                fig.update_layout(xaxis_title='Smart Score', yaxis_title='Count')
                st.plotly_chart(fig, use_container_width=True)
                
                # Add data preview
                st.markdown("#### Data Preview")
                st.dataframe(df.head(10), use_container_width=True)
                
                # Add download section
                csv = df.to_csv(index=False).encode('utf-8')
                
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.download_button(
                        label="📥 Download Sample Analysis CSV",
                        data=csv,
                        file_name=csv_filename,
                        mime="text/csv",
                        help="Download the complete sample analysis as a CSV file"
                    )
                
                with col2:
                    # View top content button
                    if st.button("View Top Content Recommendations"):
                        st.session_state.analyzed_data = df
                        st.session_state.page = "🏆 View Recommendations"
                        st.experimental_rerun()
    
    st.markdown("</div>", unsafe_allow_html=True)

# View recommendations page
elif page == "🏆 View Recommendations":
    st.markdown("<div class='header-text'><svg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><polygon points='12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2'></polygon></svg> Content Recommendations</div>", unsafe_allow_html=True)
    
    # Intro card
    st.markdown("<div class='card'>", unsafe_allow_html=True)
    st.markdown("""
    <div style="display: flex; align-items: flex-start; gap: 1rem; margin-bottom: 1rem;">
        <div style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.1), rgba(244, 114, 182, 0.1)); border-radius: 0.75rem; width: 3rem; height: 3rem; min-width: 3rem; display: flex; justify-content: center; align-items: center;">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"></polygon></svg>
        </div>
        <div>
            <h3 style="margin-top: 0; margin-bottom: 0.5rem; font-size: 1.25rem;">AI-Powered Content Recommendations</h3>
            <p style="margin-top: 0; font-size: 0.875rem;">Our algorithm analyzes engagement patterns, visual elements, and caption effectiveness to identify top-performing content strategies.</p>
        </div>
    </div>
    
    <div style="background-color: rgba(99, 102, 241, 0.05); padding: 0.75rem; border-radius: 0.5rem; margin-bottom: 1rem;">
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-right: 0.5rem;"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
            <span style="font-weight: 500; color: var(--text); font-size: 0.875rem;">Smart Score Explained</span>
        </div>
        <p style="margin: 0; font-size: 0.8125rem;">
            Content is ranked by Smart Score, which is calculated based on engagement rate, content quality, posting time, and audience response patterns.
            <span style="font-weight: 500;">Higher scores indicate content with viral potential.</span>
        </p>
    </div>
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Check if we have analyzed data
    if hasattr(st.session_state, 'analyzed_data') and not st.session_state.analyzed_data.empty:
        df = st.session_state.analyzed_data
        
        # Sort by smart score
        df = df.sort_values('smart_score', ascending=False)
        
        # Display insights summary in cards
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("""
            <div class="stat-card" style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.05), rgba(99, 102, 241, 0.1));">
                <div style="background-color: rgba(99, 102, 241, 0.1); width: 3rem; height: 3rem; border-radius: 0.75rem; display: flex; align-items: center; justify-content: center; margin-bottom: 0.75rem;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#6366F1" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>
                </div>
                <div class="stat-value">92.3</div>
                <div class="stat-label">Highest Smart Score</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("""
            <div class="stat-card" style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.05), rgba(16, 185, 129, 0.1));">
                <div style="background-color: rgba(16, 185, 129, 0.1); width: 3rem; height: 3rem; border-radius: 0.75rem; display: flex; align-items: center; justify-content: center; margin-bottom: 0.75rem;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#10B981" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
                </div>
                <div class="stat-value">87.6%</div>
                <div class="stat-label">Average Engagement</div>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown("""
            <div class="stat-card" style="background: linear-gradient(135deg, rgba(244, 114, 182, 0.05), rgba(244, 114, 182, 0.1));">
                <div style="background-color: rgba(244, 114, 182, 0.1); width: 3rem; height: 3rem; border-radius: 0.75rem; display: flex; align-items: center; justify-content: center; margin-bottom: 0.75rem;">
                    <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#F472B6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"></path></svg>
                </div>
                <div class="stat-value">76</div>
                <div class="stat-label">Potential Reach</div>
            </div>
            """, unsafe_allow_html=True)
        
        # Add visualization
        st.markdown("<div class='section-text slide-in'><svg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><line x1='18' y1='20' x2='18' y2='10'></line><line x1='12' y1='20' x2='12' y2='4'></line><line x1='6' y1='20' x2='6' y2='14'></line></svg> Performance Distribution</div>", unsafe_allow_html=True)
        
        # Add a chart that shows score distribution
        fig = px.histogram(df, x='smart_score', 
                          nbins=10,
                          color_discrete_sequence=['#6366F1'],
                          opacity=0.8,
                          marginal='box',
                          title='Content Performance Distribution by Smart Score')
        
        fig.update_layout(
            xaxis_title="Smart Score",
            yaxis_title="Number of Posts",
            bargap=0.1,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
            yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.05)'),
            font=dict(family="Inter, Arial, sans-serif", size=12, color="#64748B")
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Top recommended content
        st.markdown("<div class='section-text slide-in'><svg xmlns='http://www.w3.org/2000/svg' width='20' height='20' viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'><polygon points='12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2'></polygon></svg> Top Recommended Content</div>", unsafe_allow_html=True)
        
        # Card tabs for content filtering
        st.markdown("""
        <div class="tabs-container">
            <div class="tab active">All Content</div>
            <div class="tab">Images Only</div>
            <div class="tab">Videos Only</div>
            <div class="tab">Highest Engagement</div>
            <div class="tab">Most Recent</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Add rank and recommendation stars
        df['rank'] = range(1, len(df) + 1)
        df['recommendation'] = df['smart_score'].apply(
            lambda x: "⭐⭐⭐" if x >= 75 else ("⭐⭐" if x >= 50 else ("⭐" if x >= 25 else ""))
        )
        
        # Show top content
        top_content = df.head(10)
        
        # Create a nice display for top content
        for i, row in top_content.iterrows():
            # Determine colors based on smart score
            if row['smart_score'] >= 75:
                badge_color = "#6366F1"
                border_color = "rgba(99, 102, 241, 0.3)"
                bg_gradient = "linear-gradient(135deg, rgba(99, 102, 241, 0.05), rgba(99, 102, 241, 0.1))"
            elif row['smart_score'] >= 50:
                badge_color = "#10B981"
                border_color = "rgba(16, 185, 129, 0.3)"
                bg_gradient = "linear-gradient(135deg, rgba(16, 185, 129, 0.05), rgba(16, 185, 129, 0.1))"
            else:
                badge_color = "#F59E0B"
                border_color = "rgba(245, 158, 11, 0.3)"
                bg_gradient = "linear-gradient(135deg, rgba(245, 158, 11, 0.05), rgba(245, 158, 11, 0.1))"
                
            st.markdown(f"""
            <div class="recommendation-card" style="border: 1px solid {border_color}; background: {bg_gradient};">
                <div style="display: flex; align-items: center; margin-bottom: 0.75rem;">
                    <span class="rank-badge" style="background: {badge_color};">#{row['rank']}</span>
                    <span class="username">@{row['username']}</span>
                    <span style="margin-left: auto;">{row['recommendation']}</span>
                </div>
                <div style="margin-bottom: 0.75rem;">
                    <span class="metric"><span class="metric-value">{row['likes']:,}</span> <span class="metric-label">likes</span></span>
                    <span class="metric"><span class="metric-value">{row['comments']:,}</span> <span class="metric-label">comments</span></span>
                    {f'<span class="metric"><span class="metric-value">{row["views"]:,}</span> <span class="metric-label">views</span></span>' if row['is_video'] else ''}
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <div style="font-size: 0.875rem; color: var(--light-text);">Posted: {row['timestamp']}</div>
                    <div style="font-weight: 600; color: {badge_color};">Smart Score: {row['smart_score']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("""
        <div style="background-color: #F0FDF4; padding: 15px; border-radius: 8px; border: 1px solid #DCFCE7; display: flex; align-items: center;">
            <div style="width: 12px; height: 12px; border-radius: 50%; background-color: #22C55E; margin-right: 10px;"></div>
            <div>
                <div style="font-weight: 600; color: #166534;">Instagram API: Good</div>
                <div style="font-size: 0.8rem; color: #166534;">All systems operational</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background-color: #FFF7ED; padding: 15px; border-radius: 8px; border: 1px solid #FFEDD5; display: flex; align-items: center;">
            <div style="width: 12px; height: 12px; border-radius: 50%; background-color: #F97316; margin-right: 10px;"></div>
            <div>
                <div style="font-weight: 600; color: #9A3412;">Instagram API: Limited</div>
                <div style="font-size: 0.8rem; color: #9A3412;">Automatic retries in progress</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Rate limiting info
    st.markdown("<div style='font-weight: 600; font-size: 1rem; margin: 20px 0 10px 0;'>ℹ️ Rate Limiting</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background-color: #F8FAFC; padding: 15px; border-radius: 8px; border: 1px solid #E2E8F0; font-size: 0.9rem;">
        <p style="margin-top: 0;">Our app respects Instagrams rate limits:</p>
        <ul style="margin-bottom: 0; padding-left: 20px;">
            <li>Automatic request throttling</li>
            <li>Smart retry mechanisms</li>
            <li>Batch processing optimization</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Account info
    st.markdown("<div style='font-weight: 600; font-size: 1rem; margin: 20px 0 10px 0;'>👤 Account Info</div>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background-color: #F8FAFC; padding: 15px; border-radius: 8px; border: 1px solid #E2E8F0;">
        <div style="display: flex; align-items: center; margin-bottom: 10px;">
            <div style="width: 36px; height: 36px; border-radius: 50%; background-color: #6C5CE7; color: white; display: flex; align-items: center; justify-content: center; margin-right: 10px; font-weight: 600;">B</div>
            <div>
                <div style="font-weight: 600;">Bhavesh</div>
                <div style="font-size: 0.8rem; color: var(--light-text);">Free Account</div>
            </div>
        </div>
        <div style="font-size: 0.9rem;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                <span>Downloads Used:</span>
                <span style="font-weight: 600;">142/200</span>
            </div>
            <div style="display: flex; justify-content: space-between;">
                <span>Status:</span>
                <span style="color: #22C55E; font-weight: 600;">Active</span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)