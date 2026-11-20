# 1. 라이브러리 임포트 (이 부분이 반드시 가장 위에 있어야 합니다!)
import streamlit as st
import pandas as pd
import os
import re
import base64
import datetime
import calendar
import holidays

# 2. 페이지 기본 설정
st.set_page_config(page_title="코스맥스펫 연장근무 조회", page_icon="⏰", layout="wide")

# 3. 스타일 설정
st.markdown("""
<style>
    /* ... (기존에 있던 style 코드 내용) ... */
</style>
""", unsafe_allow_html=True)

# 4. 타이틀 및 헤더
logo_html = "<span style='font-size: 2.0rem; vertical-align: middle; margin-right: 8px;'>🐾</span>" 
st.markdown(f"<h3>{logo_html}코스맥스펫(주)</h3>", unsafe_allow_html=True)
st.markdown("<h1>⏰ 개인별 연장근무 상세 조회</h1>", unsafe_allow_html=True)
st.markdown("<br><br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. 여기에 추가 문구(표) 코드를 넣으세요! (여기가 적당한 위치입니다)
st.markdown("""
<div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 25px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
    <h3 style="color: #004aad; font-size: 1.4rem !important; margin-bottom: 15px !important; text-align: left; font-weight: 900;">1. 수당 지급 기준 (150% 가산 적용)</h3>
    <table style="width: 100%; border-collapse: collapse; background-color: white; border-radius: 8px; overflow: hidden; border: 1px solid #cbd5e1;">
        <thead>
            <tr style="background-color: #f1f5f9;">
                <th style="padding: 15px; border: 1px solid #cbd5e1; width: 15%; text-align: center; color: #475569; font-weight: 800;">구분</th>
                <th style="padding: 15px; border: 1px solid #cbd5e1; width: 45%; text-align: left; color: #475569; font-weight: 800;">발생 기준</th>
                <th style="padding: 15px; border: 1px solid #cbd5e1; width: 40%; text-align: left; color: #475569; font-weight: 800;">수당 지급률</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td style="padding: 15px; border: 1px solid #cbd5e1; text-align: center; font-weight: 800; color: #1e293b; background-color: #fff;">연장근로</td>
                <td style="padding: 15px; border: 1px solid #cbd5e1; color: #334155; font-weight: 600;">
                    • 평일 정규 근무시간(08:30~17:30) 외 근무<br>
                    • <b>점심 휴게시간(12:30~13:30) 중 근무</b>
                </td>
                <td style="padding: 15px; border: 1px solid #cbd5e1; color: #1e293b; font-weight: 700;">통상임금의 <span style="color: #ef4444;">150% (1.5배)</span></td>
            </tr>
            <tr>
                <td style="padding: 15px; border: 1px solid #cbd5e1; text-align: center; font-weight: 800; color: #1e293b; background-color: #fff;">휴일근로</td>
                <td style="padding: 15px; border: 1px solid #cbd5e1; color: #334155; font-weight: 600;">
                    • 주말, 법정 공휴일, 근로자의 날 근무
                </td>
                <td style="padding: 15px; border: 1px solid #cbd5e1; color: #1e293b; font-weight: 700;">
                    • 8시간 이내: 통상임금의 <span style="color: #ef4444;">150%</span><br>
                    • 8시간 초과: 통상임금의 <span style="color: #ef4444;">200% (2배)</span>
                </td>
            </tr>
        </tbody>
    </table>
    <p style="margin-top: 12px; font-size: 0.95rem; color: #64748b; font-weight: 600;">※ 휴일근로는 8시간을 초과하면 '휴일+연장'이 중복되어 200%가 적용됩니다.</p>
</div>
""", unsafe_allow_html=True)
# ---------------------------------------------------------

# 6. 기존 나머지 코드 시작 (데이터 로드 등)
kr_holidays = holidays.KR()
excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx') and not f.startswith('~')]
FILE_NAME = excel_files[0] if excel_files else None

# ... (기존 코드 계속) ...
