import streamlit as st
import cv2
import os
import sys
import json
import time
import tempfile
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed
from PIL import Image
import hashlib
import re
from collections import Counter
import io

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

st.set_page_config(
    page_title="AI Visual Insight Pro - Advanced Analysis",
    page_icon="�",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    [data-testid="stSidebar"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=Poppins:wght@400;500;600;700;800;900&display=swap');
    
    .stApp {
        background: linear-gradient(135deg, #0a0a1a 0%, #1a1a2e 50%, #16213e 100%);
        font-family: 'Inter', sans-serif;
        font-size: 16px !important;
    }
    
    /* Medium-sized fonts for balanced appearance */
    * {
        font-size: 16px !important;
    }
    
    h1 {
        font-size: 2.5rem !important;
        font-weight: 700 !important;
        margin-bottom: 1rem !important;
    }
    
    h2 {
        font-size: 2rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.9rem !important;
    }
    
    h3 {
        font-size: 1.6rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.8rem !important;
    }
    
    h4 {
        font-size: 1.3rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.7rem !important;
    }
    
    p, div, span, label {
        font-size: 1rem !important;
        line-height: 1.6 !important;
    }
    
    .stButton button {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        padding: 0.7rem 1.8rem !important;
        border-radius: 10px !important;
    }
    
    /* Medium-spaced layout */
    .block-container {
        padding-top: 1rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 100% !important;
        padding-left: 2rem !important;
        padding-right: 2rem !important;
    }
    
    section.main > div {
        padding-top: 0 !important;
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    ::-webkit-scrollbar {width: 12px; height: 12px;}
    ::-webkit-scrollbar-track {background: rgba(255,255,255,0.05); border-radius: 10px;}
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(180deg, #00d4ff, #0066ff); 
        border-radius: 10px;
        border: 2px solid rgba(255,255,255,0.1);
    }
    
    .search-container {
        position: relative;
        width: 100%;
        max-width: 750px;
        margin: 1.2rem auto;
    }
    
    .search-box {
        width: 100%;
        padding: 0.9rem 2.5rem 0.9rem 3rem;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(15px);
        border: 2px solid rgba(0, 212, 255, 0.35);
        border-radius: 30px;
        color: #ffffff;
        font-size: 1rem !important;
        font-weight: 500;
        transition: all 0.3s ease;
        outline: none;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.2);
    }
    
    .search-box:focus {
        border-color: #00d4ff;
        background: rgba(255, 255, 255, 0.08);
        box-shadow: 0 10px 35px rgba(0, 212, 255, 0.35);
        transform: translateY(-2px);
    }
    
    .search-box::placeholder {
        color: rgba(255, 255, 255, 0.7);
        font-size: 1rem !important;
    }
    
    input[type="text"] {
        color: #ffffff !important;
        font-size: 1rem !important;
    }
    
    input[type="text"]::placeholder {
        color: rgba(255, 255, 255, 0.7) !important;
        font-size: 1rem !important;
    }
    
    .search-icon {
        position: absolute;
        left: 1.2rem;
        top: 50%;
        transform: translateY(-50%);
        color: #00d4ff;
        font-size: 1.3rem;
    }
    
    .search-filters {
        display: flex;
        gap: 0.6rem;
        justify-content: center;
        flex-wrap: wrap;
        margin-top: 1rem;
        margin-bottom: 1.2rem;
    }
    
    .filter-chip {
        padding: 0.5rem 1.2rem;
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border: 2px solid rgba(0, 212, 255, 0.3);
        border-radius: 25px;
        color: #ffffff;
        font-size: 0.95rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .filter-chip:hover {
        background: linear-gradient(135deg, #00d4ff 0%, #0066ff 100%);
        border-color: #00d4ff;
        transform: translateY(-2px);
        box-shadow: 0 8px 25px rgba(0, 212, 255, 0.3);
    }
    
    .filter-chip.active {
        background: linear-gradient(135deg, #764ba2 0%, #f093fb 100%);
        border-color: #f093fb;
    }
    
    .hero-banner {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 25%, #f093fb 50%, #4facfe 75%, #00f2fe 100%);
        border-radius: 20px;
        padding: 3rem 2.5rem;
        margin: 0 0 2.5rem 0;
        box-shadow: 0 20px 70px rgba(102, 126, 234, 0.6);
        animation: gradientShift 20s ease infinite;
        background-size: 400% 400%;
        position: relative;
        overflow: hidden;
        border-bottom: 4px solid rgba(0, 212, 255, 0.4);
        min-height: 220px;
    }
    
    .hero-banner::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
        animation: pulse 6s ease-in-out infinite;
    }
    
    .hero-banner::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        height: 2px;
        background: linear-gradient(90deg, #00d4ff, #0066ff, #764ba2, #f093fb, #00d4ff);
        background-size: 200% 100%;
        animation: shimmer 3s linear infinite;
    }
    
    @keyframes shimmer {
        0% { background-position: 0% 0%; }
        100% { background-position: 200% 0%; }
    }
    
    @keyframes gradientShift {
        0% {background-position: 0% 50%;}
        50% {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    
    @keyframes pulse {
        0%, 100% {transform: scale(1) rotate(0deg);}
        50% {transform: scale(1.1) rotate(180deg);}
    }
    
    .hero-title {
        font-family: 'Poppins', sans-serif;
        font-size: 3.2rem !important;
        font-weight: 900;
        color: #ffffff;
        text-align: center;
        margin-bottom: 1rem;
        text-shadow: 0 10px 30px rgba(0,0,0,0.6);
        letter-spacing: -2px;
        position: relative;
        z-index: 1;
        line-height: 1.1;
    }
    
    .hero-subtitle {
        font-size: 1.4rem !important;
        font-weight: 600;
        color: #ffffff;
        text-align: center;
        margin-bottom: 1.5rem;
        text-shadow: 0 5px 15px rgba(0,0,0,0.4);
        position: relative;
        z-index: 1;
        line-height: 1.5;
    }
    
    .pro-badge {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: #ffffff;
        padding: 0.6rem 1.3rem;
        border-radius: 28px;
        font-weight: 700;
        display: inline-block;
        margin: 0.3rem;
        box-shadow: 0 8px 20px rgba(245, 87, 108, 0.5);
        font-size: 0.9rem !important;
        transition: all 0.3s ease;
        position: relative;
        z-index: 1;
        white-space: nowrap;
    }
    
    .pro-badge:hover {
        transform: translateY(-3px) scale(1.05);
        box-shadow: 0 12px 30px rgba(245, 87, 108, 0.7);
    }
    
    .metric-box {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.2) 0%, rgba(118, 75, 162, 0.2) 100%);
        backdrop-filter: blur(10px);
        border: 2px solid rgba(0, 212, 255, 0.3);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        box-shadow: 0 10px 35px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .metric-box::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
        transition: left 0.5s ease;
    }
    
    .metric-box:hover::before {
        left: 100%;
    }
    
    .metric-box:hover {
        transform: translateY(-5px) scale(1.03);
        box-shadow: 0 18px 55px rgba(102, 126, 234, 0.5);
        border-color: #00d4ff;
    }
    
    .metric-value {
        font-family: 'Poppins', sans-serif;
        font-size: 2.5rem !important;
        font-weight: 900;
        background: linear-gradient(135deg, #00d4ff 0%, #0066ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
        text-shadow: 0 3px 15px rgba(0, 212, 255, 0.3);
    }
    
    .metric-label {
        font-size: 0.95rem !important;
        color: #ffffff;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-weight: 600 !important;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
        line-height: 1.3 !important;
    }
    
    p, span, label, div[class*="st"] {
        color: #f0f0f0 !important;
        font-size: 1rem !important;
    }
    
    .stMarkdown, .stText, .stCaption {
        color: #e8e8e8 !important;
        font-size: 1rem !important;
    }
    
    .stMetric label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
    }
    
    .stMetric [data-testid="stMetricDelta"] {
        font-size: 0.95rem !important;
    }
    .stMetric .metric-value {
        color: #00d4ff !important;
    }
    
    .streamlit-expanderHeader {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    .feature-card {
        background: linear-gradient(135deg, rgba(30, 30, 60, 0.7) 0%, rgba(20, 20, 50, 0.7) 100%);
        backdrop-filter: blur(10px);
        border: 2px solid rgba(255,255,255,0.1);
        border-radius: 15px;
        padding: 1.2rem;
        margin: 1rem 0;
        box-shadow: 0 10px 35px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
        text-align: left;
    }
    
    .feature-card h4 {
        color: #00d4ff !important;
        font-size: 1.2rem !important;
        font-weight: 600 !important;
        margin-bottom: 0.7rem !important;
        text-align: center;
    }
    
    .feature-card p {
        color: #f0f0f0 !important;
        font-size: 0.95rem !important;
        line-height: 1.6 !important;
        margin: 0.4rem 0 !important;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }
    
    .feature-card strong {
        color: #00d4ff !important;
        font-weight: 600 !important;
    }
    
    .feature-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 12px 40px rgba(0, 212, 255, 0.3);
        border-color: rgba(0, 212, 255, 0.5);
    }
        color: #ffffff !important;
        font-weight: 700 !important;
        min-width: 100px;
        display: inline-block;
    }
    
    .feature-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 30px 80px rgba(102, 126, 234, 0.4);
        border-color: rgba(0, 212, 255, 0.5);
    }
    
    .summary-box {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(0, 102, 255, 0.1) 100%);
        border-left: 5px solid #00d4ff;
        border-radius: 15px;
        padding: 2rem;
        margin: 1.5rem 0;
        color: #ffffff;
        font-size: 1.1rem;
        line-height: 1.8;
        box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    }
    
    .content-flag {
        background: linear-gradient(135deg, rgba(255, 87, 87, 0.15) 0%, rgba(255, 107, 107, 0.15) 100%);
        border-left: 3px solid #ff5757;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.8rem 0;
        color: #ffffff;
        font-weight: 600;
    }
    
    .safe-content {
        background: linear-gradient(135deg, rgba(87, 255, 153, 0.15) 0%, rgba(107, 255, 173, 0.15) 100%);
        border-left: 3px solid #57ff99;
        border-radius: 12px;
        padding: 1rem;
        margin: 0.8rem 0;
        color: #ffffff;
        font-weight: 600;
    }
    
    .stButton>button {
        width: 100%;
        height: 65px;
        border-radius: 35px;
        font-size: 1.2rem;
        font-weight: 700;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: 2px solid rgba(102, 126, 234, 0.4);
        box-shadow: 0 18px 50px rgba(102, 126, 234, 0.6);
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        color: #ffffff;
        text-transform: uppercase;
        letter-spacing: 2.5px;
        position: relative;
        overflow: hidden;
        text-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
    }
    
    .stButton>button::before {
        content: '';
        position: absolute;
        top: 50%;
        left: 50%;
        width: 0;
        height: 0;
        border-radius: 50%;
        background: rgba(255, 255, 255, 0.25);
        transform: translate(-50%, -50%);
        transition: width 0.6s, height 0.6s;
    }
    
    .stButton>button:hover::before {
        width: 300px;
        height: 300px;
    }
    
    .stButton>button:hover {
        transform: translateY(-6px) scale(1.04);
        box-shadow: 0 35px 90px rgba(102, 126, 234, 0.9);
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
        border-color: rgba(0, 212, 255, 0.8);
    }
    
    .stButton>button:active {
        transform: translateY(-2px) scale(1.01);
    }
    
    /* Search box styling */
    .stTextInput input {
        background: rgba(255, 255, 255, 0.05) !important;
        border: 2px solid rgba(0, 212, 255, 0.3) !important;
        border-radius: 50px !important;
        color: #ffffff !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
        padding: 0.9rem 1.5rem !important;
        backdrop-filter: blur(15px) !important;
        transition: all 0.4s ease !important;
        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.3) !important;
    }
    
    .stTextInput input:focus {
        border-color: #00d4ff !important;
        background: rgba(255, 255, 255, 0.08) !important;
        box-shadow: 0 15px 60px rgba(0, 212, 255, 0.4) !important;
        transform: translateY(-2px);
    }
    
    .stTextInput input::placeholder {
        color: rgba(255, 255, 255, 0.6) !important;
    }
    
    /* Keyframe card styling */
    .keyframe-card {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(0,212,255,0.25);
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 15px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.25);
    }
    
    .keyframe-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(0,212,255,0.35);
        border-color: #00d4ff;
    }
    
    .keyframe-title {
        color: #00d4ff;
        font-weight: 600;
        font-size: 0.8rem;
        margin-bottom: 8px;
        text-align: center;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* File Uploader Styling */
    .stFileUploader {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.08), rgba(240, 147, 251, 0.08));
        border: 2px dashed rgba(0, 212, 255, 0.4);
        border-radius: 15px;
        padding: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .stFileUploader:hover {
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.15), rgba(240, 147, 251, 0.15));
        border-color: #00d4ff;
        box-shadow: 0 8px 30px rgba(0, 212, 255, 0.25);
        transform: translateY(-2px);
    }
    
    .stFileUploader>div>div>div>div {
        color: #ffffff !important;
        font-weight: 600;
    }
    
    .stFileUploader label {
        color: #ffffff !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
    }
    
    .stFileUploader button {
        background: linear-gradient(135deg, #00d4ff 0%, #0066ff 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 15px !important;
        padding: 0.8rem 2rem !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
    }
    
    .stFileUploader button:hover {
        background: linear-gradient(135deg, #0066ff 0%, #667eea 100%) !important;
        transform: scale(1.05) !important;
        box-shadow: 0 10px 30px rgba(0, 212, 255, 0.5) !important;
    }
    
    .stProgress>div>div {
        background: linear-gradient(90deg, #00d4ff 0%, #0066ff 50%, #667eea 100%);
        border-radius: 10px;
        height: 20px;
        box-shadow: 0 5px 20px rgba(0, 212, 255, 0.5);
    }
    
    .stProgress>div {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 10px;
        border: 2px solid rgba(0, 212, 255, 0.3);
    }
    
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: rgba(30, 30, 60, 0.8);
        backdrop-filter: blur(15px);
        border-radius: 50px;
        padding: 1.2rem;
        border: 3px solid rgba(0, 212, 255, 0.4);
        box-shadow: 0 15px 50px rgba(0, 0, 0, 0.5);
        margin-bottom: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 65px;
        font-size: 1.1rem;
        font-weight: 700;
        border-radius: 50px;
        color: #ffffff;
        background: rgba(255, 255, 255, 0.08);
        border: 2px solid rgba(0, 212, 255, 0.3);
        transition: all 0.3s ease;
        padding: 0 2rem;
        text-shadow: 0 2px 5px rgba(0, 0, 0, 0.3);
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        background: rgba(0, 212, 255, 0.15);
        border-color: #00d4ff;
        transform: translateY(-3px);
        box-shadow: 0 15px 40px rgba(0, 212, 255, 0.4);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #00d4ff 0%, #0066ff 100%) !important;
        border-color: #00d4ff !important;
        color: #ffffff !important;
        box-shadow: 0 15px 50px rgba(0, 212, 255, 0.6) !important;
        transform: scale(1.05);
    }
    
    /* Download Button Styling */
    .stDownloadButton>button {
        width: 100%;
        height: 55px;
        border-radius: 15px;
        font-size: 1rem;
        font-weight: 700;
        background: linear-gradient(135deg, #57ff99 0%, #00d4ff 100%) !important;
        border: 2px solid rgba(87, 255, 153, 0.5) !important;
        box-shadow: 0 10px 30px rgba(87, 255, 153, 0.4);
        transition: all 0.3s ease;
        color: #000000 !important;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stDownloadButton>button:hover {
        transform: translateY(-3px);
        box-shadow: 0 15px 40px rgba(87, 255, 153, 0.6);
        background: linear-gradient(135deg, #00d4ff 0%, #57ff99 100%) !important;
        border-color: #57ff99 !important;
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
        gap: 2rem;
        margin: 2rem 0;
    }
    
    .stat-card {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.15) 0%, rgba(118, 75, 162, 0.15) 100%);
        backdrop-filter: blur(15px);
        border: 2px solid rgba(0, 212, 255, 0.3);
        border-radius: 25px;
        padding: 2rem;
        text-align: center;
        transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
        position: relative;
        overflow: hidden;
    }
    
    .stat-card::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(0, 212, 255, 0.1) 0%, transparent 70%);
        opacity: 0;
        transition: opacity 0.4s ease;
    }
    
    .stat-card:hover::before {
        opacity: 1;
    }
    
    .stat-card:hover {
        transform: translateY(-10px) scale(1.03);
        border-color: #00d4ff;
        box-shadow: 0 25px 70px rgba(0, 212, 255, 0.4);
    }
    
    .stat-value {
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(135deg, #00d4ff 0%, #0066ff 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.5rem;
    }
    
    .stat-label {
        font-size: 1.1rem;
        color: #f0f0f0;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: white;
        background: rgba(255,255,255,0.1);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
    }
    
    .info-chip {
        display: inline-block;
        background: rgba(0, 212, 255, 0.15);
        border: 1px solid rgba(0, 212, 255, 0.4);
        padding: 0.4rem 1rem;
        border-radius: 18px;
        margin: 0.4rem;
        color: #00d4ff;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    .warning-chip {
        display: inline-block;
        background: rgba(255, 193, 7, 0.15);
        border: 1px solid rgba(255, 193, 7, 0.4);
        padding: 0.4rem 1rem;
        border-radius: 18px;
        margin: 0.4rem;
        color: #ffc107;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    .danger-chip {
        display: inline-block;
        background: rgba(255, 87, 87, 0.15);
        border: 1px solid rgba(255, 87, 87, 0.4);
        padding: 0.4rem 1rem;
        border-radius: 18px;
        margin: 0.4rem;
        color: #ff5757;
        font-weight: 600;
        font-size: 0.85rem;
    }
    
    h1, h2, h3 {
        color: white;
        font-weight: 700;
    }
    
    /* Info Card Hover Effects */
    @keyframes card-hover {
        0% { transform: translateY(0) scale(1); }
        100% { transform: translateY(-5px) scale(1.02); }
    }
    
    .info-card-container {
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    .info-card-container:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 15px 40px rgba(0, 212, 255, 0.4) !important;
    }
    
    .stTextArea textarea {
        background: rgba(30, 30, 60, 0.5);
        border: 2px solid rgba(255,255,255,0.1);
        border-radius: 15px;
        color: white;
        font-size: 1.05rem;
        line-height: 1.8;
    }
    
    [data-testid="stFileUploader"] {
        background: linear-gradient(135deg, rgba(102, 126, 234, 0.1) 0%, rgba(118, 75, 162, 0.1) 100%);
        backdrop-filter: blur(15px);
        border: 3px dashed rgba(0, 212, 255, 0.4);
        border-radius: 30px;
        padding: 3rem;
        transition: all 0.4s ease;
    }
    
    [data-testid="stFileUploader"]:hover {
        border-color: #00d4ff;
        background: linear-gradient(135deg, rgba(0, 212, 255, 0.15) 0%, rgba(0, 102, 255, 0.15) 100%);
        transform: scale(1.02);
        box-shadow: 0 20px 60px rgba(0, 212, 255, 0.3);
    }
    
    [data-testid="stFileUploader"] label {
        color: #ffffff !important;
        font-size: 1.3rem !important;
        font-weight: 700 !important;
    }
    
    .stSidebar {
        background: linear-gradient(180deg, #0a0a1a 0%, #1a1a2e 100%);
        border-right: 3px solid rgba(0, 212, 255, 0.4);
    }
    
    .stSidebar [data-testid="stMarkdownContainer"] {
        color: #f0f0f0 !important;
    }
    
    .stSidebar .stCheckbox label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
    }
    
    .stSidebar .stSlider label {
        color: #ffffff !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
    }
    
    .stSidebar h3 {
        color: #00d4ff !important;
        font-size: 1.4rem !important;
        text-shadow: 0 2px 10px rgba(0, 212, 255, 0.5);
    }
    
    .stSidebar h4 {
        color: #f093fb !important;
        font-size: 1.2rem !important;
    }
    
    .video-container {
        border-radius: 25px;
        overflow: hidden;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
        border: 3px solid rgba(0, 212, 255, 0.3);
        transition: all 0.3s ease;
        max-width: 600px;
        margin: 0 auto;
    }
    
    .video-container:hover {
        transform: scale(1.02);
        box-shadow: 0 30px 80px rgba(0, 212, 255, 0.4);
        border-color: #00d4ff;
    }
    
    [data-testid="stVideo"] {
        max-width: 600px !important;
        margin: 0 auto !important;
    }
    
    [data-testid="stVideo"] video {
        border-radius: 20px;
        max-height: 400px;
        object-fit: contain;
    }
    
    .loading-spinner {
        display: inline-block;
        width: 50px;
        height: 50px;
        border: 5px solid rgba(0, 212, 255, 0.2);
        border-top-color: #00d4ff;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }

</style>
""", unsafe_allow_html=True)

def format_duration(seconds: float) -> str:
    td = timedelta(seconds=int(seconds))
    hours, remainder = divmod(td.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

def check_system_capabilities():
    capabilities = {
        'opencv': False,
        'scenedetect': False,
        'speech_recognition': False,
        'moviepy': False,
        'textblob': False
    }
    
    try:
        import cv2
        capabilities['opencv'] = True
    except ImportError:
        pass
    
    try:
        from scenedetect import detect, ContentDetector
        capabilities['scenedetect'] = True
    except ImportError:
        pass
    
    try:
        import speech_recognition as sr
        capabilities['speech_recognition'] = True
    except ImportError:
        pass
    
    try:
        from moviepy import VideoFileClip
        capabilities['moviepy'] = True
    except ImportError:
        pass
    
    try:
        from textblob import TextBlob
        capabilities['textblob'] = True
    except ImportError:
        pass
    
    return capabilities

def extract_video_metadata(video_path: str) -> Dict:
    cap = cv2.VideoCapture(video_path)
    metadata = {
        'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        'fps': float(cap.get(cv2.CAP_PROP_FPS)),
        'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
        'duration': float(cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)) if cap.get(cv2.CAP_PROP_FPS) > 0 else 0,
        'resolution': f"{int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}",
        'codec': int(cap.get(cv2.CAP_PROP_FOURCC))
    }
    cap.release()
    return metadata

def detect_scenes_fast(video_path: str, threshold: float = 27.0):
    try:
        from scenedetect import detect, ContentDetector
        scenes = detect(video_path, ContentDetector(threshold=threshold))
        return [(scene[0].get_seconds(), scene[1].get_seconds()) for scene in scenes]
    except Exception as e:
        metadata = extract_video_metadata(video_path)
        duration = metadata['duration']
        num_segments = max(1, int(duration / 10))
        segment_duration = duration / num_segments
        return [(i * segment_duration, (i + 1) * segment_duration) for i in range(num_segments)]

def extract_keyframes_parallel(video_path: str, scenes: List[Tuple], output_dir: str):
    cap = cv2.VideoCapture(video_path)
    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    
    keyframes = []
    storyboard_dir = os.path.join(output_dir, "storyboard")
    os.makedirs(storyboard_dir, exist_ok=True)
    
    def extract_single_keyframe(idx, start, end):
        try:
            local_cap = cv2.VideoCapture(video_path)
            mid = (start + end) / 2.0
            frame_no = int(mid * fps)
            local_cap.set(cv2.CAP_PROP_POS_FRAMES, frame_no)
            ret, frame = local_cap.read()
            local_cap.release()
            
            if ret:
                outpath = os.path.join(storyboard_dir, f"scene_{idx:03d}.jpg")
                cv2.imwrite(outpath, frame)
                return {
                    'scene_idx': idx,
                    'start': start,
                    'end': end,
                    'timestamp': mid,
                    'frame_path': outpath
                }
        except Exception as e:
            return None
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {executor.submit(extract_single_keyframe, i, s, e): i for i, (s, e) in enumerate(scenes)}
        for future in as_completed(futures):
            result = future.result()
            if result:
                keyframes.append(result)
    
    cap.release()
    return sorted(keyframes, key=lambda x: x['scene_idx'])

def extract_audio_from_video(video_path: str, output_dir: str) -> str | None:
    try:
        from moviepy import VideoFileClip
        audio_path = os.path.join(output_dir, "audio.wav")
        
        video = VideoFileClip(video_path)
        if video.audio is not None:
            video.audio.write_audiofile(
                audio_path, 
                fps=16000,
                nbytes=2,
                codec='pcm_s16le',
                logger=None
            )
            video.close()
            if os.path.exists(audio_path) and os.path.getsize(audio_path) > 1000:
                return audio_path
        video.close()
        return None
    except Exception as e:
        st.warning(f"⚠️ Audio extraction warning: {str(e)}")
        return None

def analyze_audio_properties(audio_path: str) -> Dict:
    """Analyze audio properties and quality"""
    try:
        from pydub import AudioSegment
        
        audio = AudioSegment.from_wav(audio_path)
        
        duration_sec = len(audio) / 1000.0
        sample_rate = audio.frame_rate
        channels = audio.channels
        sample_width = audio.sample_width * 8
        loudness = audio.dBFS
        max_amplitude = audio.max
        
        return {
            'duration': round(duration_sec, 2),
            'sample_rate': sample_rate,
            'channels': channels,
            'bit_depth': sample_width,
            'loudness_db': round(loudness, 2),
            'max_amplitude': max_amplitude,
            'file_size_mb': round(os.path.getsize(audio_path) / (1024*1024), 2),
            'quality_score': min(100, int((sample_rate/16000) * 50 + (abs(loudness)/60) * 50))
        }
    except Exception as e:
        return {
            'duration': 0,
            'sample_rate': 0,
            'channels': 0,
            'bit_depth': 0,
            'loudness_db': 0,
            'max_amplitude': 0,
            'file_size_mb': 0,
            'quality_score': 0
        }

def create_audio_waveform(audio_path: str) -> Optional[str]:
    """Generate audio waveform visualization"""
    try:
        from pydub import AudioSegment
        import matplotlib.pyplot as plt
        import numpy as np
        
        audio = AudioSegment.from_wav(audio_path)
        samples = np.array(audio.get_array_of_samples())
        
        if audio.channels == 2:
            samples = samples.reshape((-1, 2))
            samples = samples.mean(axis=1)
        
        sample_rate = audio.frame_rate
        duration = len(audio) / 1000.0
        time = np.linspace(0, duration, num=len(samples))
        
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(12, 4), facecolor='#1a1a2e')
        ax.set_facecolor('#16213e')
        
        ax.plot(time, samples, color='#00d4ff', linewidth=0.5, alpha=0.8)
        ax.fill_between(time, samples, color='#00d4ff', alpha=0.3)
        
        ax.set_xlabel('Time (seconds)', color='#ffffff', fontsize=12)
        ax.set_ylabel('Amplitude', color='#ffffff', fontsize=12)
        ax.set_title('🎵 Audio Waveform Analysis', color='#ffffff', fontsize=14, pad=15)
        
        ax.tick_params(colors='#ffffff')
        ax.spines['bottom'].set_color('#00d4ff')
        ax.spines['left'].set_color('#00d4ff')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        ax.grid(True, alpha=0.2, color='#ffffff', linestyle='--')
        
        plt.tight_layout()
        
        waveform_path = audio_path.replace('audio.wav', 'waveform.png')
        plt.savefig(waveform_path, dpi=150, facecolor='#1a1a2e', edgecolor='none')
        plt.close()
        
        return waveform_path if os.path.exists(waveform_path) else None
        
    except Exception as e:
        print(f"Waveform generation error: {str(e)}")
        return None

def transcribe_audio_advanced(audio_path: str, target_language: str = 'auto') -> Dict:
    """
    Advanced multi-language audio transcription with automatic language detection
    
    Supported languages:
    - English (en-US), Spanish (es-ES), French (fr-FR), German (de-DE)
    - Chinese (zh-CN), Japanese (ja-JP), Korean (ko-KR), Hindi (hi-IN)
    - Arabic (ar-SA), Russian (ru-RU), Portuguese (pt-BR), Italian (it-IT)
    - Dutch (nl-NL), Polish (pl-PL), Turkish (tr-TR), Vietnamese (vi-VN)
    """
    if not audio_path or not os.path.exists(audio_path):
        return {
            'text': 'No audio detected in video.',
            'word_count': 0,
            'estimated_words': 0,
            'confidence': 0,
            'status': 'no_audio',
            'language': 'unknown',
            'detected_language': 'unknown'
        }
    
    try:
        import speech_recognition as sr
        recognizer = sr.Recognizer()
        
        # Enhanced settings for multi-language
        recognizer.energy_threshold = 300
        recognizer.dynamic_energy_threshold = True
        recognizer.pause_threshold = 0.8
        
        audio_file = sr.AudioFile(audio_path)
        with audio_file as source:
            recognizer.adjust_for_ambient_noise(source, duration=1)
            audio_data = recognizer.record(source)
        
        # Language mapping for Google Speech API
        language_codes = {
            'auto': None,  # Auto-detect
            'English': 'en-US',
            'Spanish': 'es-ES',
            'French': 'fr-FR',
            'German': 'de-DE',
            'Chinese': 'zh-CN',
            'Japanese': 'ja-JP',
            'Korean': 'ko-KR',
            'Hindi': 'hi-IN',
            'Arabic': 'ar-SA',
            'Russian': 'ru-RU',
            'Portuguese': 'pt-BR',
            'Italian': 'it-IT',
            'Dutch': 'nl-NL',
            'Polish': 'pl-PL',
            'Turkish': 'tr-TR',
            'Vietnamese': 'vi-VN'
        }
        
        # Determine language code
        lang_code = language_codes.get(target_language, 'en-US') if target_language != 'auto' else 'en-US'
        
        # Try transcription with selected/detected language
        try:
            if target_language == 'auto':
                # Try multiple languages for auto-detection
                languages_to_try = ['en-US', 'es-ES', 'fr-FR', 'de-DE', 'zh-CN', 'hi-IN', 'ar-SA', 'ru-RU']
                best_result = None
                best_confidence = 0
                
                for lang in languages_to_try:
                    try:
                        text = recognizer.recognize_google(audio_data, language=lang, show_all=False)  # type: ignore
                        if text and len(text.strip()) > 10:  # Valid transcription
                            # Simple confidence heuristic: longer = more likely correct
                            confidence = min(0.95, 0.6 + (len(text) / 500))
                            if confidence > best_confidence:
                                best_confidence = confidence
                                best_result = {
                                    'text': text,
                                    'language': lang,
                                    'detected_language': lang.split('-')[0].upper()
                                }
                    except:
                        continue
                
                if best_result:
                    words = len(best_result['text'].split())
                    return {
                        'text': best_result['text'],
                        'word_count': words,
                        'estimated_words': words,
                        'confidence': best_confidence,
                        'status': 'success',
                        'language': best_result['language'],
                        'detected_language': best_result['detected_language']
                    }
            else:
                # Use specified language
                text = recognizer.recognize_google(audio_data, language=lang_code, show_all=False)  # type: ignore
                if text and len(text.strip()) > 0:
                    words = len(text.split())
                    return {
                        'text': text,
                        'word_count': words,
                        'estimated_words': words,
                        'confidence': 0.85,
                        'status': 'success',
                        'language': lang_code,
                        'detected_language': target_language
                    }
            
            return {
                'text': 'No clear speech detected in audio.',
                'word_count': 0,
                'estimated_words': 0,
                'confidence': 0,
                'status': 'no_speech',
                'language': lang_code,
                'detected_language': 'unknown'
            }
            
        except sr.UnknownValueError:
            return {
                'text': 'Speech was unclear or no speech detected.',
                'word_count': 0,
                'estimated_words': 0,
                'confidence': 0,
                'status': 'no_speech',
                'language': lang_code,
                'detected_language': 'unknown'
            }
        except sr.RequestError as e:
            return {
                'text': f'Speech recognition service error: {str(e)}',
                'word_count': 0,
                'estimated_words': 0,
                'confidence': 0,
                'status': 'error',
                'language': lang_code,
                'detected_language': 'unknown'
            }
    
    except Exception as e:
        return {
            'text': f'Transcription error: {str(e)}',
            'word_count': 0,
            'estimated_words': 0,
            'confidence': 0,
            'status': 'error',
            'language': 'unknown',
            'detected_language': 'unknown'
        }

def generate_text_summary(text: str, max_sentences: int = 3) -> Dict:
    """Generate concise, accurate AI summary from transcribed text"""
    if not text or len(text.strip()) == 0:
        return {
            'summary': 'No speech detected in video.',
            'key_points': [],
            'sentiment': 'neutral',
            'topics': []
        }
    
    try:
        from textblob import TextBlob
        import nltk
        from nltk.tokenize import sent_tokenize
        from nltk.corpus import stopwords
        
        # Download required NLTK data
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt', quiet=True)
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords', quiet=True)
        
        blob = TextBlob(text)
        sentences = list(blob.sentences)  # type: ignore
        
        if len(sentences) == 0:
            return {
                'summary': text[:200] + '...' if len(text) > 200 else text,
                'key_points': [],
                'sentiment': 'neutral',
                'topics': []
            }
        
        # Score sentences by importance (word frequency + position)
        stop_words = set(stopwords.words('english'))
        word_frequencies = {}
        
        for word in blob.words:  # type: ignore
            if word.lower() not in stop_words and len(word) > 3:
                word_frequencies[word.lower()] = word_frequencies.get(word.lower(), 0) + 1
        
        # Normalize frequencies
        max_freq = max(word_frequencies.values()) if word_frequencies else 1
        for word in word_frequencies:
            word_frequencies[word] = word_frequencies[word] / max_freq
        
        # Score sentences
        sentence_scores = {}
        for i, sentence in enumerate(sentences):
            score = 0
            word_count = 0
            for word in sentence.words:
                if word.lower() in word_frequencies:
                    score += word_frequencies[word.lower()]
                    word_count += 1
            
            # Boost first and last sentences
            if i == 0:
                score *= 1.5
            elif i == len(sentences) - 1:
                score *= 1.2
            
            if word_count > 0:
                sentence_scores[i] = score / word_count
        
        # Select top sentences
        if len(sentence_scores) > 0:
            top_indices = sorted(sentence_scores, key=lambda x: sentence_scores.get(x, 0), reverse=True)[:max_sentences]
            top_indices.sort()  # Maintain original order
            selected_sentences = [str(sentences[i]) for i in top_indices]
        else:
            selected_sentences = [str(s) for s in sentences[:max_sentences]]
        
        summary = ' '.join(selected_sentences)
        
        # Extract key points (top 3 most important sentences)
        key_points = selected_sentences[:3] if len(selected_sentences) >= 3 else selected_sentences
        
        # Sentiment analysis with improved accuracy
        sentiment_score = blob.sentiment.polarity  # type: ignore
        subjectivity = blob.sentiment.subjectivity  # type: ignore
        
        if sentiment_score > 0.15:
            sentiment = 'positive'
        elif sentiment_score < -0.15:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        # Extract topics (most frequent meaningful words)
        words = [word.lower() for word in blob.words if word.lower() not in stop_words and len(word) > 4]  # type: ignore
        word_freq = Counter(words)
        topics = [word for word, count in word_freq.most_common(5)]
        
        return {
            'summary': summary[:500] + '...' if len(summary) > 500 else summary,  # Limit to 500 chars
            'key_points': key_points,
            'sentiment': sentiment,
            'sentiment_score': sentiment_score,
            'subjectivity': subjectivity,
            'topics': topics,
            'word_count': len(text.split())
        }
    
    except Exception as e:
        # Fallback to simple sentence splitting
        sentences = text.split('.')
        sentences = [s.strip() for s in sentences if s.strip()]
        summary = '. '.join(sentences[:max_sentences]) + '.' if len(sentences) > max_sentences else text
        return {
            'summary': summary[:300] + '...' if len(summary) > 300 else summary,
            'key_points': sentences[:3] if len(sentences) >= 3 else sentences,
            'sentiment': 'neutral',
            'topics': [],
            'word_count': len(text.split())
        }

def detect_content_issues(text: str, keyframes: List, language: str = 'en') -> Dict:
    """
    Multi-language content moderation supporting 16+ languages
    Detects profanity, violence, adult content across different languages
    """
    
    # Multi-language profanity lists
    profanity_lists = {
        'en': {'fuck', 'shit', 'damn', 'hell', 'bitch', 'ass', 'bastard', 'dick', 'pussy', 'cunt', 'whore', 'slut'},
        'es': {'mierda', 'puta', 'coño', 'joder', 'cabrón', 'pendejo', 'verga', 'chingar'},
        'fr': {'merde', 'putain', 'con', 'salope', 'connard', 'chier', 'bordel'},
        'de': {'scheiße', 'fick', 'arsch', 'hure', 'verdammt', 'schlampe'},
        'zh': {'操', '妈的', '傻逼', '混蛋', '婊子', '狗屎'},
        'ja': {'くそ', 'ばか', 'あほ', 'しね', 'ちくしょう'},
        'ko': {'씨발', '개새끼', '병신', '지랄', '엿먹어'},
        'hi': {'बकवास', 'कमीना', 'चूतिया', 'हरामी'},
        'ar': {'تبا', 'لعنة', 'قذر', 'عاهرة'},
        'ru': {'блять', 'сука', 'хуй', 'пизда', 'ебать'},
        'pt': {'merda', 'porra', 'caralho', 'puta', 'foda'},
        'it': {'cazzo', 'merda', 'puttana', 'stronzo', 'figa'},
        'nl': {'kut', 'shit', 'klootzak', 'hoer', 'lul'},
        'pl': {'kurwa', 'pierdolić', 'gówno', 'suka'},
        'tr': {'siktir', 'amk', 'orospu', 'piç', 'bok'},
        'vi': {'địt', 'đụ', 'cứt', 'đĩ', 'chó'}
    }
    
    # Multi-language violence keywords
    violence_keywords = {
        'en': {'kill', 'murder', 'death', 'blood', 'gun', 'shoot', 'fight', 'attack', 'violence', 'weapon', 'bomb', 'terrorist', 'war'},
        'es': {'matar', 'asesinar', 'muerte', 'sangre', 'pistola', 'disparar', 'pelear', 'atacar', 'violencia', 'arma', 'bomba', 'guerra'},
        'fr': {'tuer', 'assassiner', 'mort', 'sang', 'pistolet', 'tirer', 'combattre', 'attaquer', 'violence', 'arme', 'bombe', 'guerre'},
        'de': {'töten', 'morden', 'tod', 'blut', 'waffe', 'schießen', 'kämpfen', 'angriff', 'gewalt', 'bombe', 'krieg'},
        'zh': {'杀', '谋杀', '死亡', '血', '枪', '射击', '打架', '攻击', '暴力', '武器', '炸弹', '战争'},
        'ja': {'殺す', '殺人', '死', '血', '銃', '撃つ', '戦う', '攻撃', '暴力', '武器', '爆弾', '戦争'},
        'ko': {'죽이다', '살인', '죽음', '피', '총', '쏘다', '싸우다', '공격', '폭력', '무기', '폭탄', '전쟁'},
        'hi': {'मारना', 'हत्या', 'मौत', 'खून', 'बंदूक', 'गोली', 'लड़ाई', 'हमला', 'हिंसा', 'हथियार', 'बम', 'युद्ध'},
        'ar': {'قتل', 'جريمة قتل', 'موت', 'دم', 'مسدس', 'إطلاق نار', 'قتال', 'هجوم', 'عنف', 'سلاح', 'قنبلة', 'حرب'},
        'ru': {'убить', 'убийство', 'смерть', 'кровь', 'пистолет', 'стрелять', 'драться', 'атака', 'насилие', 'оружие', 'бомба', 'война'},
        'pt': {'matar', 'assassinar', 'morte', 'sangue', 'arma', 'atirar', 'lutar', 'atacar', 'violência', 'bomba', 'guerra'},
        'it': {'uccidere', 'omicidio', 'morte', 'sangue', 'pistola', 'sparare', 'combattere', 'attacco', 'violenza', 'arma', 'bomba', 'guerra'},
        'nl': {'doden', 'moord', 'dood', 'bloed', 'pistool', 'schieten', 'vechten', 'aanval', 'geweld', 'wapen', 'bom', 'oorlog'},
        'pl': {'zabić', 'morderstwo', 'śmierć', 'krew', 'pistolet', 'strzelać', 'walczyć', 'atak', 'przemoc', 'broń', 'bomba', 'wojna'},
        'tr': {'öldürmek', 'cinayet', 'ölüm', 'kan', 'silah', 'ateş', 'kavga', 'saldırı', 'şiddet', 'bomba', 'savaş'},
        'vi': {'giết', 'giết người', 'chết', 'máu', 'súng', 'bắn', 'đánh nhau', 'tấn công', 'bạo lực', 'vũ khí', 'bom', 'chiến tranh'}
    }
    
    # Multi-language adult content keywords
    adult_keywords = {
        'en': {'sex', 'porn', 'nude', 'naked', 'adult', 'xxx', 'explicit', 'erotic', 'sexual', 'nsfw'},
        'es': {'sexo', 'porno', 'desnudo', 'adulto', 'xxx', 'explícito', 'erótico', 'sexual'},
        'fr': {'sexe', 'porno', 'nu', 'adulte', 'xxx', 'explicite', 'érotique', 'sexuel'},
        'de': {'sex', 'porno', 'nackt', 'erwachsene', 'xxx', 'explizit', 'erotisch', 'sexuell'},
        'zh': {'性', '色情', '裸体', '成人', 'xxx', '露骨', '情色', '性的'},
        'ja': {'セックス', 'ポルノ', 'ヌード', '裸', 'アダルト', 'xxx', '露骨', 'エロ', '性的'},
        'ko': {'섹스', '포르노', '누드', '벌거벗은', '성인', 'xxx', '노골적인', '에로틱', '성적인'},
        'hi': {'यौन', 'पोर्न', 'नग्न', 'वयस्क', 'xxx', 'स्पष्ट', 'कामुक', 'यौन'},
        'ar': {'جنس', 'إباحي', 'عاري', 'بالغ', 'xxx', 'صريح', 'مثير', 'جنسي'},
        'ru': {'секс', 'порно', 'обнаженный', 'взрослый', 'xxx', 'откровенный', 'эротический', 'сексуальный'},
        'pt': {'sexo', 'pornô', 'nu', 'adulto', 'xxx', 'explícito', 'erótico', 'sexual'},
        'it': {'sesso', 'porno', 'nudo', 'adulto', 'xxx', 'esplicito', 'erotico', 'sessuale'},
        'nl': {'sex', 'porno', 'naakt', 'volwassen', 'xxx', 'expliciet', 'erotisch', 'seksueel'},
        'pl': {'seks', 'porno', 'nagi', 'dorosły', 'xxx', 'wyraźny', 'erotyczny', 'seksualny'},
        'tr': {'seks', 'porno', 'çıplak', 'yetişkin', 'xxx', 'açık', 'erotik', 'cinsel'},
        'vi': {'tình dục', 'khiêu dâm', 'khỏa thân', 'người lớn', 'xxx', 'rõ ràng', 'khiêu gợi', 'tình dục'}
    }
    
    # Detect language from code (e.g., 'en-US' -> 'en')
    lang_code = language.split('-')[0].lower() if '-' in language else language.lower()
    
    # Get appropriate word lists for detected language
    profanity_set = profanity_lists.get(lang_code, profanity_lists['en'])
    violence_set = violence_keywords.get(lang_code, violence_keywords['en'])
    adult_set = adult_keywords.get(lang_code, adult_keywords['en'])
    
    # Also include English keywords for multilingual content
    if lang_code != 'en':
        profanity_set = profanity_set.union(profanity_lists['en'])
        violence_set = violence_set.union(violence_keywords['en'])
        adult_set = adult_set.union(adult_keywords['en'])
    
    text_lower = text.lower()
    words = re.findall(r'\b\w+\b', text_lower)
    
    profanity_found = [word for word in words if word in profanity_set]
    violence_found = [word for word in words if word in violence_set]
    adult_found = [word for word in words if word in adult_set]
    
    issues = []
    severity_score = 0
    
    if profanity_found:
        issues.append({
            'type': 'Profanity',
            'severity': 'Medium',
            'count': len(profanity_found),
            'examples': list(set(profanity_found))[:5]
        })
        severity_score += len(profanity_found) * 2
    
    if violence_found:
        issues.append({
            'type': 'Violence',
            'severity': 'High',
            'count': len(violence_found),
            'examples': list(set(violence_found))[:5]
        })
        severity_score += len(violence_found) * 3
    
    if adult_found:
        issues.append({
            'type': 'Adult Content',
            'severity': 'High',
            'count': len(adult_found),
            'examples': list(set(adult_found))[:5]
        })
        severity_score += len(adult_found) * 3
    
    # Visual content analysis
    avg_brightness = 128
    if keyframes:
        try:
            sample_frames = keyframes[:min(5, len(keyframes))]
            brightness_values = []
            for kf in sample_frames:
                if os.path.exists(kf['frame_path']):
                    img = cv2.imread(kf['frame_path'])
                    if img is not None:
                        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
                        brightness_values.append(float(np.mean(gray)))  # type: ignore
            if brightness_values:
                avg_brightness = np.mean(brightness_values)
        except Exception:
            pass
    
    if avg_brightness < 50:
        issues.append({
            'type': 'Dark Content',
            'severity': 'Low',
            'count': 1,
            'examples': ['Video contains predominantly dark scenes']
        })
        severity_score += 5
    
    if severity_score > 20:
        rating = 'Not Safe'
        recommendation = 'Content requires moderation and age restriction'
    elif severity_score > 10:
        rating = 'Caution'
        recommendation = 'Content may require age verification'
    else:
        rating = 'Safe'
        recommendation = 'Content is suitable for general audiences'
    
    return {
        'issues': issues,
        'severity_score': severity_score,
        'rating': rating,
        'recommendation': recommendation,
        'is_safe': severity_score <= 10,
        'total_flags': len(issues),
        'language': language,
        'moderation_language': lang_code
    }

def analyze_video_quality(video_path: str, keyframes: List) -> Dict:
    metadata = extract_video_metadata(video_path)
    
    width = metadata['width']
    height = metadata['height']
    fps = metadata['fps']
    
    resolution_quality = 'Low'
    if width >= 3840:
        resolution_quality = '4K Ultra HD'
    elif width >= 1920:
        resolution_quality = 'Full HD 1080p'
    elif width >= 1280:
        resolution_quality = 'HD 720p'
    elif width >= 854:
        resolution_quality = 'SD 480p'
    
    fps_quality = 'Standard'
    if fps >= 60:
        fps_quality = 'High (60+ FPS)'
    elif fps >= 30:
        fps_quality = 'Good (30 FPS)'
    else:
        fps_quality = 'Low (< 30 FPS)'
    
    sharpness_scores = []
    if keyframes:
        sample_frames = keyframes[:min(10, len(keyframes))]
        for kf in sample_frames:
            if os.path.exists(kf['frame_path']):
                img = cv2.imread(kf['frame_path'], cv2.IMREAD_GRAYSCALE)
                if img is not None:
                    laplacian = cv2.Laplacian(img, cv2.CV_64F)
                    sharpness = laplacian.var()
                    sharpness_scores.append(sharpness)
    
    avg_sharpness = np.mean(sharpness_scores) if sharpness_scores else 0
    sharpness_quality = 'Good'
    if avg_sharpness > 500:
        sharpness_quality = 'Excellent'
    elif avg_sharpness > 100:
        sharpness_quality = 'Good'
    else:
        sharpness_quality = 'Poor'
    
    overall_score = 0
    if resolution_quality in ['4K Ultra HD', 'Full HD 1080p']:
        overall_score += 40
    elif resolution_quality in ['HD 720p']:
        overall_score += 30
    else:
        overall_score += 15
    
    if fps >= 60:
        overall_score += 30
    elif fps >= 30:
        overall_score += 25
    else:
        overall_score += 10
    
    if sharpness_quality == 'Excellent':
        overall_score += 30
    elif sharpness_quality == 'Good':
        overall_score += 20
    else:
        overall_score += 5
    
    return {
        'resolution_quality': resolution_quality,
        'fps_quality': fps_quality,
        'sharpness_quality': sharpness_quality,
        'overall_score': overall_score,
        'overall_rating': 'Excellent' if overall_score >= 85 else 'Good' if overall_score >= 60 else 'Fair' if overall_score >= 40 else 'Poor'
    }

def process_video_pro(
    video_path: str,
    output_dir: str,
    scene_threshold: float = 27.0,
    target_language: str = 'auto',
    progress_callback=None
):
    start_time = time.time()
    results = {
        'success': False,
        'video_info': {},
        'scenes': [],
        'keyframes': [],
        'transcription': {},
        'summary': {},
        'content_moderation': {},
        'quality_analysis': {},
        'processing_time': 0,
        'language': target_language
    }
    
    try:
        if progress_callback:
            progress_callback("📊 Analyzing video metadata...", 0.05)
        
        video_info = extract_video_metadata(video_path)
        results['video_info'] = video_info
        
        if progress_callback:
            progress_callback("🎬 Detecting scenes with AI...", 0.15)
        
        scenes = detect_scenes_fast(video_path, threshold=scene_threshold)
        results['scenes'] = scenes
        
        if progress_callback:
            progress_callback("🖼️ Extracting keyframes (parallel processing)...", 0.30)
        
        keyframes = extract_keyframes_parallel(video_path, scenes, output_dir)
        results['keyframes'] = keyframes
        
        if progress_callback:
            progress_callback("🎵 Extracting audio from video...", 0.45)
        
        audio_path = extract_audio_from_video(video_path, output_dir)
        
        if audio_path:
            if progress_callback:
                progress_callback("🎵 Analyzing audio properties...", 0.50)
            
            audio_properties = analyze_audio_properties(audio_path)
            results['audio_properties'] = audio_properties
            
            if progress_callback:
                progress_callback("📊 Generating audio waveform...", 0.55)
            
            waveform_path = create_audio_waveform(audio_path)
            results['waveform_path'] = waveform_path
        
        if progress_callback:
            lang_display = 'Auto-Detecting' if target_language == 'auto' else target_language
            progress_callback(f"🎤 Transcribing speech ({lang_display})...", 0.60)
        
        if audio_path:
            transcription = transcribe_audio_advanced(audio_path, target_language)
        else:
            transcription = {
                'text': 'No audio detected in video.',
                'word_count': 0,
                'status': 'no_audio',
                'language': 'en-US',
                'detected_language': 'English'
            }
        results['transcription'] = transcription
        
        # Get detected language for content moderation
        detected_lang = transcription.get('language', 'en-US')
        
        if progress_callback:
            progress_callback("📝 Generating intelligent summary...", 0.75)
        
        summary = generate_text_summary(transcription.get('text', ''))
        results['summary'] = summary
        
        if progress_callback:
            progress_callback("🛡️ Running multi-language content moderation...", 0.85)
        
        content_moderation = detect_content_issues(
            transcription.get('text', ''), 
            keyframes,
            detected_lang
        )
        results['content_moderation'] = content_moderation
        
        if progress_callback:
            progress_callback("📈 Analyzing video quality...", 0.92)
        
        quality_analysis = analyze_video_quality(video_path, keyframes)
        results['quality_analysis'] = quality_analysis
        
        if progress_callback:
            progress_callback("💾 Saving results...", 0.97)
        
        analysis_path = os.path.join(output_dir, "analysis.json")
        with open(analysis_path, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        
        summary_path = os.path.join(output_dir, "summary.txt")
        with open(summary_path, 'w', encoding='utf-8') as f:
            f.write("=== VIDEO ANALYSIS SUMMARY ===\n\n")
            f.write(f"Language: {transcription.get('detected_language', 'Unknown')}\n")
            f.write(f"Transcription:\n{transcription.get('text', 'No speech detected')}\n\n")
            f.write(f"Summary:\n{summary.get('summary', 'N/A')}\n\n")
            f.write(f"Sentiment: {summary.get('sentiment', 'neutral')}\n")
            f.write(f"Content Rating: {content_moderation.get('rating', 'Unknown')}\n")
        
        results['success'] = True
        results['processing_time'] = time.time() - start_time
        
        if progress_callback:
            progress_callback("✅ Analysis complete!", 1.0)
        
    except Exception as e:
        results['error'] = str(e)
        results['success'] = False
    
    return results

def main():
    # Initialize session state
    if 'favorites' not in st.session_state:
        st.session_state['favorites'] = []
    if 'filter_selection' not in st.session_state:
        st.session_state['filter_selection'] = 'All Videos'
    if 'search_query' not in st.session_state:
        st.session_state['search_query'] = ''
    
    st.markdown("""
    <div class="hero-banner" style="padding: 3rem 2.5rem; margin-bottom: 2.5rem;">
        <div class="hero-title" style="font-size: 3.2rem !important; margin-bottom: 1rem; letter-spacing: -2px;">
            🎬 AI Visual Insight Pro
        </div>
        <div class="hero-subtitle" style="font-size: 1.4rem !important; margin-bottom: 1.5rem; line-height: 1.5;">
            Advanced Video Analysis • AI Summarization • Content Moderation
        </div>
        <div style="font-size: 0.95rem; color: rgba(255,255,255,0.7); margin-bottom: 1.5rem; position: relative; z-index: 1;">
            Powered by cutting-edge AI technology for comprehensive video intelligence
        </div>
        <div style="text-align: center; position: relative; z-index: 1; display: flex; flex-wrap: wrap; justify-content: center; gap: 0.6rem; max-width: 900px; margin: 0 auto;">
            <span class="pro-badge" style="padding: 0.6rem 1.3rem; font-size: 0.9rem;">🌍 Multi-Language (16+)</span>
            <span class="pro-badge" style="padding: 0.6rem 1.3rem; font-size: 0.9rem;">🎤 Speech-to-Text</span>
            <span class="pro-badge" style="padding: 0.6rem 1.3rem; font-size: 0.9rem;">📝 AI Summarization</span>
            <span class="pro-badge" style="padding: 0.6rem 1.3rem; font-size: 0.9rem;">🛡️ Content Moderation</span>
            <span class="pro-badge" style="padding: 0.6rem 1.3rem; font-size: 0.9rem;">📊 Quality Analysis</span>
            <span class="pro-badge" style="padding: 0.6rem 1.3rem; font-size: 0.9rem;">⚡ Lightning Fast</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Functional search bar
    col_search1, col_search2, col_search3 = st.columns([1, 3, 1])
    with col_search2:
        search_query = st.text_input(
            "search_videos",
            placeholder="🔍 Search videos, features, or analysis results...",
            label_visibility="collapsed",
            key="video_search"
        )
        st.session_state['search_query'] = search_query
    
    # Functional filter buttons
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        if st.button("🎥 All Videos", use_container_width=True, type="primary" if st.session_state['filter_selection'] == 'All Videos' else "secondary"):
            st.session_state['filter_selection'] = 'All Videos'
            st.rerun()
    
    with col2:
        analyzed_count = 1 if 'results' in st.session_state and st.session_state.get('results', {}).get('success') else 0
        if st.button(f"✅ Analyzed ({analyzed_count})", use_container_width=True, type="primary" if st.session_state['filter_selection'] == 'Analyzed' else "secondary"):
            st.session_state['filter_selection'] = 'Analyzed'
            st.rerun()
    
    with col3:
        if st.button("⏳ Processing", use_container_width=True, type="primary" if st.session_state['filter_selection'] == 'Processing' else "secondary"):
            st.session_state['filter_selection'] = 'Processing'
            st.rerun()
    
    with col4:
        moderated_count = 1 if 'results' in st.session_state and st.session_state.get('results', {}).get('moderation') else 0
        if st.button(f"🛡️ Moderated ({moderated_count})", use_container_width=True, type="primary" if st.session_state['filter_selection'] == 'Moderated' else "secondary"):
            st.session_state['filter_selection'] = 'Moderated'
            st.rerun()
    
    with col5:
        fav_count = len(st.session_state['favorites'])
        if st.button(f"⭐ Favorites ({fav_count})", use_container_width=True, type="primary" if st.session_state['filter_selection'] == 'Favorites' else "secondary"):
            st.session_state['filter_selection'] = 'Favorites'
            st.rerun()
    
    # Analysis Settings in main page
    st.markdown("### ⚙️ Analysis Settings")
    settings_col1, settings_col2 = st.columns(2)
    
    with settings_col1:
        scene_threshold = st.slider(
            "🎬 Scene Detection Sensitivity", 
            10.0, 50.0, 27.0, 1.0, 
            help="Lower values detect more scenes"
        )
    
    with settings_col2:
        st.markdown("<br>", unsafe_allow_html=True)
        option_col1, option_col2, option_col3, option_col4 = st.columns(4)
        with option_col1:
            enable_transcription = st.checkbox("🎤 Speech", value=True)
        with option_col2:
            enable_summarization = st.checkbox("📝 Summary", value=True)
        with option_col3:
            enable_moderation = st.checkbox("🛡️ Moderate", value=True)
        with option_col4:
            enable_quality = st.checkbox("📊 Quality", value=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Display content based on filter selection
    current_filter = st.session_state.get('filter_selection', 'All Videos')
    
    if current_filter == 'Favorites':
        st.markdown("### ⭐ Your Favorite Videos")
        
        if st.session_state['favorites']:
            # Create grid layout for favorites
            cols_per_row = 3
            num_favs = len(st.session_state['favorites'])
            num_rows = (num_favs + cols_per_row - 1) // cols_per_row
            
            for row in range(num_rows):
                cols = st.columns(cols_per_row, gap="large")
                for col_idx in range(cols_per_row):
                    fav_idx = row * cols_per_row + col_idx
                    if fav_idx < num_favs:
                        fav = st.session_state['favorites'][fav_idx]
                        with cols[col_idx]:
                            st.markdown(f"""
                            <div style="
                                background: linear-gradient(135deg, rgba(0,212,255,0.08), rgba(240,147,251,0.08));
                                border: 1px solid rgba(0,212,255,0.25);
                                border-radius: 12px;
                                padding: 12px;
                                margin-bottom: 12px;
                                transition: all 0.3s ease;
                                box-shadow: 0 5px 20px rgba(0,0,0,0.2);
                            ">
                                <h4 style="color: #00d4ff; margin-bottom: 8px; font-size: 0.95rem !important;">⭐ {fav['name'][:40]}...</h4>
                                <p style="color: #f0f0f0; font-size: 0.75rem !important; margin: 4px 0;">🕒 {fav['timestamp']}</p>
                            </div>
                            """, unsafe_allow_html=True)
                            
                            if fav['results'].get('success'):
                                scenes = len(fav['results'].get('scenes', []))
                                duration = fav['results'].get('duration', 0)
                                
                                col_metric1, col_metric2 = st.columns(2)
                                with col_metric1:
                                    st.metric("🎬 Scenes", scenes)
                                with col_metric2:
                                    st.metric("⏱️ Duration", f"{duration:.1f}s")
                                
                                if st.button(f"👁️ View", key=f"view_main_fav_{fav_idx}", use_container_width=True):
                                    st.session_state['results'] = fav['results']
                                    st.session_state['uploaded_file_name'] = fav['name']
                                    st.session_state['video_id'] = fav['id']
                                    st.session_state['filter_selection'] = 'Analyzed'
                                    st.success(f"✅ Loaded '{fav['name']}'")
                                    st.rerun()
            
            st.markdown("---")
        else:
            st.info("💡 No favorites yet! Analyze a video and click '⭐ Add to Favorites' to save it.")
            st.markdown("---")
    
    elif current_filter == 'Analyzed':
        if 'results' in st.session_state and st.session_state['results']['success']:
            st.success(f"✅ Currently viewing analyzed video: **{st.session_state.get('uploaded_file_name', 'Unknown')}**")
            st.markdown("---")
        else:
            st.info("📊 No analyzed videos yet. Upload and process a video first.")
            st.markdown("---")
    
    elif current_filter == 'Processing':
        st.info("⏳ No videos currently being processed. Upload a video to start analysis.")
        st.markdown("---")
    
    elif current_filter == 'Moderated':
        if 'results' in st.session_state and st.session_state['results'].get('moderation'):
            st.success(f"🛡️ Content moderation results available for: **{st.session_state.get('uploaded_file_name', 'Unknown')}**")
            st.markdown("---")
        else:
            st.info("🛡️ No moderated content yet. Process a video with moderation enabled.")
            st.markdown("---")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🎬 Upload & Process",
        "📊 Analysis Dashboard",
        "🎤 Audio & Transcription",
        "🛡️ Content Safety",
        "📈 Quality Metrics"
    ])
    
    with tab1:
        st.markdown("### 📤 Upload Video for AI Analysis")
        
        uploaded_file = st.file_uploader(
            "Drop your video file here or click to browse",
            type=['mp4', 'avi', 'mov', 'mkv', 'webm'],
            help="Supported formats: MP4, AVI, MOV, MKV, WebM | Max size: 200MB recommended"
        )
        
        if uploaded_file:
            # Smaller video display with better layout
            col_left, col_vid, col_right = st.columns([1, 2, 1])
            
            with col_vid:
                st.markdown("""
                <div style="
                    max-width: 550px;
                    margin: 0 auto;
                    padding: 12px;
                    background: rgba(0,212,255,0.08);
                    border: 1px solid rgba(0,212,255,0.25);
                    border-radius: 15px;
                    box-shadow: 0 8px 30px rgba(0,0,0,0.25);
                ">
                """, unsafe_allow_html=True)
                st.video(uploaded_file)
                st.markdown('</div>', unsafe_allow_html=True)
            
            # File information below video
            st.markdown("---")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                file_size = len(uploaded_file.getvalue()) / (1024 * 1024)
                st.metric("📦 Size", f"{file_size:.2f} MB")
            
            with col2:
                st.metric("📄 Format", uploaded_file.type.split('/')[-1].upper())
            
            with col3:
                st.metric("📁 Name", uploaded_file.name[:15] + "..." if len(uploaded_file.name) > 15 else uploaded_file.name)
            
            with col4:
                st.metric("✅ Status", "Ready")
            
            st.markdown("---")
            
            # Multi-language selector
            st.markdown("### 🌍 Language Settings")
            
            col_lang1, col_lang2 = st.columns([2, 1])
            
            with col_lang1:
                selected_language = st.selectbox(
                    "Select video language for transcription",
                    options=[
                        'auto', 'English', 'Spanish', 'French', 'German',
                        'Chinese', 'Japanese', 'Korean', 'Hindi',
                        'Arabic', 'Russian', 'Portuguese', 'Italian',
                        'Dutch', 'Polish', 'Turkish', 'Vietnamese'
                    ],
                    index=0,
                    help="Choose 'auto' for automatic language detection or select a specific language"
                )
            
            with col_lang2:
                if selected_language == 'auto':
                    st.info("🔍 Auto-detect enabled")
                else:
                    st.success(f"🗣️ {selected_language} selected")
            
            st.markdown("---")
            
            # Center the button using columns
            col_btn_left, col_btn_center, col_btn_right = st.columns([1, 2, 1])
            
            with col_btn_center:
                # Custom CSS for medium-sized button
                st.markdown("""
                <style>
                .stButton > button {
                    font-size: 1.1rem !important;
                    padding: 0.7rem 1.5rem !important;
                    width: 100% !important;
                }
                </style>
                """, unsafe_allow_html=True)
                
                if st.button("🚀 Start Pro AI Analysis", type="primary", width='stretch'):
                    sys_info = check_system_capabilities()
                    missing_deps = [k for k, v in sys_info.items() if not v]
                    
                    if missing_deps:
                        st.warning(f"⚠️ Some features may not work. Missing: {', '.join(missing_deps)}")
                        st.info("📦 Install missing packages: `pip install moviepy SpeechRecognition textblob nltk`")
                    
                    try:
                        if 'temp_dir' not in st.session_state:
                            st.session_state['temp_dir'] = tempfile.mkdtemp()
                        
                        temp_dir = st.session_state['temp_dir']
                        video_path = os.path.join(temp_dir, uploaded_file.name)
                        
                        with open(video_path, 'wb') as f:
                            f.write(uploaded_file.getbuffer())
                        
                        output_dir = os.path.join(temp_dir, "outputs")
                        os.makedirs(output_dir, exist_ok=True)
                        
                        # Store video information for favorites
                        st.session_state['uploaded_file_name'] = uploaded_file.name
                        st.session_state['video_id'] = f"{uploaded_file.name}_{int(datetime.now().timestamp())}"
                        
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        def update_progress(msg, pct):
                            status_text.markdown(f"**{msg}**")
                            progress_bar.progress(pct)
                        
                        st.info("🤖 AI Processing started...")
                        
                        results = process_video_pro(
                            video_path,
                            output_dir,
                            scene_threshold,
                            target_language=selected_language,
                            progress_callback=update_progress
                        )
                        
                        if results['success']:
                            st.session_state['results'] = results
                            st.session_state['output_dir'] = output_dir
                            
                            keyframe_images = []
                            storyboard_dir = os.path.join(output_dir, "storyboard")
                            if os.path.exists(storyboard_dir):
                                for filename in sorted(os.listdir(storyboard_dir)):
                                    if filename.endswith('.jpg'):
                                        filepath = os.path.join(storyboard_dir, filename)
                                        try:
                                            with open(filepath, 'rb') as f:
                                                keyframe_images.append((filename, f.read()))
                                        except:
                                            pass
                            st.session_state['keyframe_images'] = keyframe_images
                            
                            st.balloons()
                            st.success(f"✅ Analysis completed in {results['processing_time']:.2f} seconds!")
                            st.info("🎯 Check other tabs for detailed results")
                            
                            transcription_status = results.get('transcription', {}).get('status', 'unknown')
                            if transcription_status == 'no_audio':
                                st.warning("⚠️ No audio detected in video")
                            elif transcription_status == 'no_speech':
                                st.warning("⚠️ No clear speech detected in audio")
                            elif transcription_status == 'error':
                                st.warning("⚠️ Speech recognition had issues - check internet connection")
                        else:
                            error_msg = results.get('error', 'Unknown error')
                            st.error(f"❌ Processing failed: {error_msg}")
                            st.info("💡 Try a different video or check system requirements")
                    
                    except Exception as e:
                        st.error(f"❌ Error during processing: {str(e)}")
                        st.info("💡 Please try again or check the console for details")
        else:
            st.info("📁 Upload a video file to begin advanced AI analysis")
    
    with tab2:
        if 'results' in st.session_state and st.session_state['results']['success']:
            results = st.session_state['results']
            
            st.markdown("### 📊 Comprehensive Analysis Overview")
            
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-value">{len(results['keyframes'])}</div>
                    <div class="metric-label">Scenes</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-value">{format_duration(results['video_info']['duration'])}</div>
                    <div class="metric-label">Duration</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-value">{results['video_info']['resolution']}</div>
                    <div class="metric-label">Resolution</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                word_count = results.get('transcription', {}).get('word_count', 0)
                st.markdown(f"""
                <div class="metric-box">
                    <div class="metric-value">{word_count}</div>
                    <div class="metric-label">Words</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col5:
                rating = results.get('content_moderation', {}).get('rating', 'Unknown')
                rating_color = '#57ff99' if rating == 'Safe' else '#ffc107' if rating == 'Caution' else '#ff5757'
                st.markdown(f"""
                <div class="metric-box" style="border-color: {rating_color};">
                    <div class="metric-value" style="background: linear-gradient(135deg, {rating_color}, {rating_color}); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{rating}</div>
                    <div class="metric-label">Rating</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            st.markdown("### 🎬 Scene Keyframes")
            if 'keyframe_images' in st.session_state:
                # Create proper grid layout with 4 columns
                num_images = len(st.session_state['keyframe_images'])
                num_rows = (num_images + 3) // 4  # Calculate number of rows needed
                
                for row in range(num_rows):
                    cols = st.columns(4, gap="medium")
                    for col_idx in range(4):
                        img_idx = row * 4 + col_idx
                        if img_idx < num_images:
                            filename, img_data = st.session_state['keyframe_images'][img_idx]
                            with cols[col_idx]:
                                img = Image.open(io.BytesIO(img_data))
                                scene_time = results['keyframes'][img_idx]['timestamp'] if img_idx < len(results['keyframes']) else 0
                                
                                # Create card for each keyframe with proper padding
                                st.markdown(f"""
                                <div style="
                                    background: rgba(255,255,255,0.05);
                                    border: 2px solid rgba(0,212,255,0.3);
                                    border-radius: 15px;
                                    padding: 12px;
                                    margin-bottom: 15px;
                                    transition: all 0.3s ease;
                                    box-shadow: 0 5px 20px rgba(0,0,0,0.3);
                                ">
                                    <div style="
                                        color: #00d4ff;
                                        font-weight: 600;
                                        font-size: 0.9rem;
                                        margin-bottom: 8px;
                                        text-align: center;
                                    ">Scene {img_idx + 1}</div>
                                </div>
                                """, unsafe_allow_html=True)
                                st.image(img, use_container_width=True)
                                st.caption(f"⏱️ {scene_time:.1f}s", unsafe_allow_html=False)
            
            st.markdown("---")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                analysis_json = json.dumps(results, indent=2, default=str)
                st.download_button(
                    "📥 Download Full Analysis (JSON)",
                    data=analysis_json,
                    file_name=f"analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )
            
            with col2:
                if 'output_dir' in st.session_state:
                    summary_path = os.path.join(st.session_state['output_dir'], "summary.txt")
                    if os.path.exists(summary_path):
                        with open(summary_path, 'r', encoding='utf-8') as f:
                            summary_text = f.read()
                        st.download_button(
                            "📄 Download Summary (TXT)",
                            data=summary_text,
                            file_name=f"summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            mime="text/plain"
                        )
            
            with col3:
                st.info(f"⚡ Processed in {results['processing_time']:.2f}s")
            
            # Favorite functionality
            st.markdown("---")
            col_fav1, col_fav2 = st.columns([3, 1])
            
            with col_fav1:
                st.markdown("### ⭐ Save to Favorites")
                st.caption("Bookmark this analysis for quick access later")
            
            with col_fav2:
                video_name = st.session_state.get('uploaded_file_name', 'Unknown Video')
                video_id = st.session_state.get('video_id', str(datetime.now().timestamp()))
                
                # Check if video is already in favorites
                is_favorite = any(fav['id'] == video_id for fav in st.session_state['favorites'])
                
                if is_favorite:
                    if st.button("💔 Remove from Favorites", key="remove_fav"):
                        st.session_state['favorites'] = [fav for fav in st.session_state['favorites'] if fav['id'] != video_id]
                        st.success("Removed from favorites!")
                        st.rerun()
                else:
                    if st.button("⭐ Add to Favorites", key="add_fav"):
                        favorite_data = {
                            'id': video_id,
                            'name': video_name,
                            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                            'results': results
                        }
                        st.session_state['favorites'].append(favorite_data)
                        st.success("Added to favorites! ⭐")
                        st.rerun()
        
        else:
            st.info("⚠️ No analysis results yet. Upload and process a video first.")
    
    with tab3:
        if 'results' in st.session_state and st.session_state['results']['success']:
            results = st.session_state['results']
            
            st.markdown("""
            <div class="feature-card" style="background: linear-gradient(135deg, rgba(0,212,255,0.08), rgba(240,147,251,0.08)); border-color: #00d4ff; padding: 12px; border-radius: 12px;">
                <h3 style="text-align: center; color: #00d4ff; margin: 0; font-size: 1.1rem !important;">🎤 Audio Transcription & Analysis</h3>
                <p style="text-align: center; margin: 6px 0; color: #f0f0f0; font-size: 0.8rem !important;">
                    <strong>Advanced Speech Recognition Pipeline:</strong> Audio extraction → Quality analysis → 
                    Speech-to-text conversion → NLP summarization → Sentiment detection
                </p>
                <p style="text-align: center; margin: 4px 0; font-size: 0.75rem !important; color: rgba(255,255,255,0.6);">
                    Powered by Google Speech Recognition API with 16kHz audio sampling and confidence scoring
                </p>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown("---")
            st.markdown("### 🎤 Speech Transcription")
            
            transcription = results.get('transcription', {})
            transcript_text = transcription.get('text', '')
            detected_lang = transcription.get('detected_language', 'Unknown')
            
            # Show detected language badge
            if transcript_text:
                st.markdown(f"""
                <div style="text-align: center; margin-bottom: 1rem;">
                    <span style="
                        background: linear-gradient(135deg, #00d4ff 0%, #0066ff 100%);
                        color: #ffffff;
                        padding: 0.6rem 1.5rem;
                        border-radius: 25px;
                        font-weight: 700;
                        font-size: 1rem;
                        box-shadow: 0 5px 20px rgba(0, 212, 255, 0.4);
                        display: inline-block;
                    ">
                        🌍 Detected Language: {detected_lang}
                    </span>
                </div>
                """, unsafe_allow_html=True)
            
            if transcript_text:
                st.markdown(f"""
                <div class="summary-box">
                    <h4>📝 Full Transcription</h4>
                    <p>{transcript_text}</p>
                </div>
                """, unsafe_allow_html=True)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.markdown(f"<div class='info-chip'>Words: {transcription.get('word_count', 0)}</div>", unsafe_allow_html=True)
                with col2:
                    confidence = transcription.get('confidence', 0)
                    st.markdown(f"<div class='info-chip'>Confidence: {confidence:.0%}</div>", unsafe_allow_html=True)
                with col3:
                    status = transcription.get('status', 'unknown')
                    st.markdown(f"<div class='info-chip'>Status: {status}</div>", unsafe_allow_html=True)
                with col4:
                    lang_code = transcription.get('language', 'N/A')
                    st.markdown(f"<div class='info-chip'>Lang Code: {lang_code}</div>", unsafe_allow_html=True)
            else:
                st.warning("🔇 No speech detected in the video")
            
            st.markdown("---")
            st.markdown("### 🎵 Audio Analysis")
            
            audio_info = results.get('audio_properties', {})
            if audio_info and 'duration' in audio_info and audio_info['duration'] > 0:
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.metric("🕐 Duration", f"{audio_info.get('duration', 0):.1f}s")
                
                with col2:
                    st.metric("🎚️ Sample Rate", f"{audio_info.get('sample_rate', 0)/1000:.0f}kHz")
                
                with col3:
                    st.metric("🔊 Loudness", f"{audio_info.get('loudness_db', 0):.1f}dB")
                
                with col4:
                    quality = audio_info.get('quality_score', 0)
                    st.metric("✨ Quality", f"{quality}%")
                
                waveform_path = results.get('waveform_path')
                if waveform_path and os.path.exists(waveform_path):
                    st.image(waveform_path, use_container_width=True)
                else:
                    st.info("🎵 Waveform visualization not available")
            else:
                st.info("⚠️ No audio detected in video")
            
            st.markdown("---")
            st.markdown("### 📝 AI-Generated Summary")
            
            summary = results.get('summary', {})
            summary_text = summary.get('summary', '')
            
            if summary_text:
                st.markdown(f"""
                <div class="feature-card">
                    <h4>🎯 Summary</h4>
                    <p style="font-size: 1.1rem; line-height: 1.8;">{summary_text}</p>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown("#### 💡 Key Points")
                key_points = summary.get('key_points', [])
                for i, point in enumerate(key_points, 1):
                    st.markdown(f"**{i}.** {point}")
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("#### 🎭 Sentiment Analysis")
                    sentiment = summary.get('sentiment', 'neutral')
                    sentiment_score = summary.get('sentiment_score', 0)
                    
                    sentiment_emoji = '😊' if sentiment == 'positive' else '😐' if sentiment == 'neutral' else '😟'
                    sentiment_color = '#57ff99' if sentiment == 'positive' else '#00d4ff' if sentiment == 'neutral' else '#ff5757'
                    
                    st.markdown(f"""
                    <div class="feature-card" style="border-color: {sentiment_color}; padding: 12px;">
                        <h2 style="text-align: center; font-size: 2rem !important; margin: 4px 0;">{sentiment_emoji}</h2>
                        <h4 style="text-align: center; color: {sentiment_color}; font-size: 1rem !important; margin: 4px 0;">{sentiment.title()}</h4>
                        <p style="text-align: center; font-size: 0.75rem !important; margin: 4px 0;">Score: {sentiment_score:.2f}</p>
                    </div>
                    """, unsafe_allow_html=True)
                
                with col2:
                    st.markdown("#### 🏷️ Main Topics")
                    topics = summary.get('topics', [])
                    if topics:
                        for topic in topics:
                            st.markdown(f"<div class='info-chip' style='padding: 6px 12px; font-size: 0.75rem;'>#{topic}</div>", unsafe_allow_html=True)
                    else:
                        st.info("No specific topics identified")
            else:
                st.info("No summary available")
        
        else:
            st.info("⚠️ No transcription data yet. Process a video first.")
    
    with tab4:
        if 'results' in st.session_state and st.session_state['results']['success']:
            results = st.session_state['results']
            
            st.markdown("### 🛡️ Content Moderation Report")
            
            moderation = results.get('content_moderation', {})
            rating = moderation.get('rating', 'Unknown')
            is_safe = moderation.get('is_safe', True)
            severity_score = moderation.get('severity_score', 0)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                rating_color = '#57ff99' if is_safe else '#ffc107' if rating == 'Caution' else '#ff5757'
                st.markdown(f"""
                <div class="metric-box" style="border-color: {rating_color}; padding: 12px;">
                    <div class="metric-value" style="background: linear-gradient(135deg, {rating_color}, {rating_color}); -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-size: 2rem !important;">{rating}</div>
                    <div class="metric-label" style="font-size: 0.8rem !important;">Content Rating</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-box" style="padding: 12px;">
                    <div class="metric-value" style="font-size: 2rem !important;">{severity_score}</div>
                    <div class="metric-label" style="font-size: 0.8rem !important;">Severity Score</div>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                total_flags = moderation.get('total_flags', 0)
                st.markdown(f"""
                <div class="metric-box" style="padding: 12px;">
                    <div class="metric-value" style="font-size: 2rem !important;">{total_flags}</div>
                    <div class="metric-label" style="font-size: 0.8rem !important;">Total Flags</div>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            recommendation = moderation.get('recommendation', '')
            if is_safe:
                st.markdown(f"""
                <div class="safe-content" style="padding: 12px; border-radius: 12px; margin: 12px 0;">
                    <h4 style="font-size: 1rem !important; margin: 0 0 6px 0;">✅ Content is Safe</h4>
                    <p style="font-size: 0.8rem !important; margin: 0;">{recommendation}</p>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="content-flag" style="padding: 12px; border-radius: 12px; margin: 12px 0;">
                    <h4 style="font-size: 1rem !important; margin: 0 0 6px 0;">⚠️ Content Requires Review</h4>
                    <p style="font-size: 0.8rem !important; margin: 0;">{recommendation}</p>
                </div>
                """, unsafe_allow_html=True)
            
            issues = moderation.get('issues', [])
            if issues:
                st.markdown("### 🚨 Detected Issues")
                
                for issue in issues:
                    issue_type = issue.get('type', 'Unknown')
                    severity = issue.get('severity', 'Low')
                    count = issue.get('count', 0)
                    examples = issue.get('examples', [])
                    
                    severity_color = '#ff5757' if severity == 'High' else '#ffc107' if severity == 'Medium' else '#00d4ff'
                    
                    st.markdown(f"""
                    <div class="feature-card" style="border-left: 3px solid {severity_color}; padding: 12px;">
                        <h4 style="font-size: 1rem !important; margin: 0 0 6px 0;">{issue_type}</h4>
                        <p style="margin: 4px 0; font-size: 0.75rem !important;"><span class="info-chip" style="padding: 4px 10px; font-size: 0.7rem;">Severity: {severity}</span> <span class="info-chip" style="padding: 4px 10px; font-size: 0.7rem;">Count: {count}</span></p>
                        <p style="font-size: 0.75rem !important; margin: 4px 0;"><strong>Examples:</strong> {', '.join(examples[:3])}</p>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.success("✨ No content issues detected!")
        
        else:
            st.info("⚠️ No moderation data yet. Process a video first.")
    
    with tab5:
        if 'results' in st.session_state and st.session_state['results']['success']:
            results = st.session_state['results']
            
            st.markdown("### 📈 Video Quality Analysis")
            
            quality = results.get('quality_analysis', {})
            video_info = results.get('video_info', {})
            
            overall_score = quality.get('overall_score', 0)
            overall_rating = quality.get('overall_rating', 'Unknown')
            
            col1, col2 = st.columns([1, 2])
            
            with col1:
                rating_color = '#57ff99' if overall_score >= 85 else '#00d4ff' if overall_score >= 60 else '#ffc107' if overall_score >= 40 else '#ff5757'
                st.markdown(f"""
                <div class="metric-box" style="border-color: {rating_color};">
                    <div class="metric-value" style="background: linear-gradient(135deg, {rating_color}, {rating_color}); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">{overall_score}</div>
                    <div class="metric-label">Quality Score</div>
                    <p style="color: {rating_color}; font-weight: 600; margin-top: 1rem;">{overall_rating}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown("#### 📊 Quality Metrics")
                
                resolution = quality.get('resolution_quality', 'Unknown')
                fps_quality = quality.get('fps_quality', 'Unknown')
                sharpness = quality.get('sharpness_quality', 'Unknown')
                
                st.markdown(f"<div class='info-chip'>Resolution: {resolution}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='info-chip'>Frame Rate: {fps_quality}</div>", unsafe_allow_html=True)
                st.markdown(f"<div class='info-chip'>Sharpness: {sharpness}</div>", unsafe_allow_html=True)
            
            st.markdown("---")
            
            st.markdown("### 📋 Technical Specifications")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                <div class="feature-card">
                    <h4>📐 Resolution</h4>
                    <p><strong>{video_info.get('width', 0)} × {video_info.get('height', 0)}</strong></p>
                    <p>{video_info.get('resolution', 'Unknown')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="feature-card">
                    <h4>🎞️ Frame Rate</h4>
                    <p><strong>{video_info.get('fps', 0):.2f} FPS</strong></p>
                    <p>{fps_quality}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="feature-card">
                    <h4>📦 Total Frames</h4>
                    <p><strong>{video_info.get('frame_count', 0):,}</strong></p>
                    <p>{format_duration(video_info.get('duration', 0))}</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            st.markdown("### 💡 Recommendations")
            
            if overall_score >= 85:
                st.success("✨ Excellent video quality! No improvements needed.")
            elif overall_score >= 60:
                st.info("👍 Good video quality. Consider increasing resolution for optimal viewing.")
            elif overall_score >= 40:
                st.warning("⚠️ Fair video quality. Recommend re-encoding at higher quality settings.")
            else:
                st.error("❌ Poor video quality. Significant improvements needed.")
        
        else:
            st.info("⚠️ No quality analysis yet. Process a video first.")

if __name__ == "__main__":
    main()
