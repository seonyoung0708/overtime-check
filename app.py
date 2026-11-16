import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
import os

# 1. 페이지 설정
st.set_page_config(page_title="COSMAX PET 연장근무 상세조회", page_icon="🐾", layout="wide")

# 2. 스타일 (가장 깔끔하다고 하셨던 그 디자인)
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    html, body, [class*="css"]  { font-family: 'Pretendard', sans-serif !important; }
    h1 { text-align: center; color: #333333; margin-bottom: 20px; }
    .search-box { background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 30px; border: 1px solid #e9ecef; }
    .stat-box { text-align: center; padding: 15px; border-radius: 8px; border: 1px solid #e0e0e0; background-color: white; }
    .stat-title { font-size: 0.9em; color: #666; margin-bottom: 5px; }
    .stat-value { font-size: 1.5em; font-weight: bold; color: #1f77b4; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🐾 COSMAX PET 연장근무 상세조회</h1>", unsafe_allow_html=True)
st.markdown("---")

# 3. 데이터 로딩 (가장 처음 성공했던 그 방식)
@st.cache_data(ttl=60)
def load_data(file_path):
    if not file_path or not os.path.exists(file_path): return None
    try:
        # 모든 시트를 통합해서 읽어오는 가장 확실한 방법
        all_sheets = pd.read_excel(file_path, sheet_name=None)
        combined_df = pd.DataFrame()
        for _, df in all_sheets.items():
            if df.empty: continue
            combined_df = pd.concat([combined_df, df], ignore_index=True)
        return combined_df
    except:
        return None

# 4. 파란 동그라미 달력 함수
def create_calendar(year, month, work_dates):
    cal = calendar.monthcalendar(year, month)
    html = f'''
    <div style="font-family: 'Pretendard', sans-serif;">
        <h4 style="text-align: center; color: #444; margin-bottom: 10px;">{year}년 {month}월</h4>
        <table style="width: 100%; border-collapse: collapse; text-align: center;">
            <tr style="background-color: #f1f3f5; color: #555; font-size: 0.9em;">
                <th style="padding: 8px; color: #e74c3c;">일</th>
                <th>월</th><th>화</th><th>수</th><th>목</th><th>금</th>
                <th style="padding: 8px; color: #3498db;">토</th>
            </tr>
    '''
    for week in cal:
        html += "<tr>"
        for i, day in enumerate(week):
            if day == 0:
                html += "<td style='padding: 10px; border: 1px solid #eee;'></td>"
            else:
                date_str = f"{year}-{month:02d}-{day:02d}"
                is_work = date_str in work_dates
                bg_color = "#e3f2fd" if is_work else "white"
                color = "#1565c0" if is_work else ("#e74c3c" if i==0 else "#3498db" if i==6 else "#333")
                day_display = f'<div style="background-color:#1565c0; color:white; border-radius:50%; width:24px; height:24px; line-height:24px; margin:auto; font-weight:bold;">{day}</div>' if is_work else day
                html += f"<td style='padding: 10px; border: 1px solid #eee; background-color: {bg_color}; color: {color};'>{day_display}</td>"
        html += "</tr>"
    return html + "</table></div>"

# 5. 본문 실행
excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx') and not f.startswith('~')]
FILE_NAME = excel_files[0] if excel_files else None
df = load_data(FILE_NAME)

if df is None:
    st.warning("⚠️ 서버에 엑셀 파일이 없습니다.")
else:
    # 정보 기억하기 세션
    if 's_name' not in st.session_state: st.session_state['s_name'] = ""
    if 's_birth' not in st.session_state: st.session_state['s_birth'] = ""

    st.markdown('<div class="search-box">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        name = st.text_input("👤 성명", value=st.session_state['s_name'], placeholder="이름 입력")
    with c2:
        birth = st.text_input("🎂 생년월일", value=st.session_state['s_birth'], placeholder="6자리 입력", type="password")
    
    chk = st.checkbox("내 정보 기억하기", value=bool(st.session_state['s_name']))
    btn = st.button("내역 조회하기", use_container_width=True, type="primary")
    st.markdown('</div>', unsafe_allow_html=True)

    if btn:
        if chk:
            st.session_state['s_name'], st.session_state['s_birth'] = name, birth
        else:
            st.session_state['s_name'], st.session_state['s_birth'] = "", ""

        if not name:
            st.error("이름을 입력해주세요.")
        else:
            # ★ 어떤 컬럼명이든 상관없이 '김원태'와 '생년월일'이 들어있는 줄을 찾는 무적의 검색!
            mask = df.astype(str).apply(lambda x: x.str.contains(name, na=False)).any(axis=1)
            res = df[mask]
            
            if birth: # 생년월일도 입력했다면 한 번 더 필터링
                mask2 = res.astype(str).apply(lambda x: x.str.contains(birth, na=False)).any(axis=1)
                res = res[mask2]

            if res.empty:
                st.info("내역을 찾을 수 없습니다.")
            else:
                # 13건/0시간 통계박스
                st.markdown("### 📊 연장근무 요약")
                cnt = len(res)
                # 시간 컬럼 자동 찾기
                time_col = next((c for c in res.columns if '시간' in str(c) or 'Unnamed: 7' in str(c)), None)
                hours = pd.to_numeric(res[time_col], errors='coerce').sum() if time_col else 0
                
                sc1, sc2 = st.columns(2)
                sc1.markdown(f'<div class="stat-box"><div class="stat-title">🗓️ 건수</div><div class="stat-value">{cnt} 건</div></div>', unsafe_allow_html=True)
                sc2.markdown(f'<div class="stat-box"><div class="stat-title">⏱️ 총 시간</div><div class="stat-value">{hours:g} 시간</div></div>', unsafe_allow_html=True)
                
                # 달력 (날짜 컬럼 자동 찾기)
                date_col = next((c for c in res.columns if '날짜' in str(c) or '일자' in str(c) or 'Unnamed: 4' in str(c)), None)
                if date_col:
                    st.markdown("<br>### 📅 근무 달력", unsafe_allow_html=True)
                    dts = pd.to_datetime(res[date_col], errors='coerce').dropna()
                    if not dts.empty:
                        dts_str = dts.dt.strftime('%Y-%m-%d').tolist()
                        months = sorted(list(set([(d.year, d.month) for d in dts])))
                        m_cols = st.columns(min(len(months), 3))
                        for i, (y, m) in enumerate(months):
                            with m_cols[i % 3]:
                                st.markdown(create_calendar(y, m, dts_str), unsafe_allow_html=True)

                st.markdown("<br>### 📝 상세 내역", unsafe_allow_html=True)
                st.dataframe(res, use_container_width=True, hide_index=True)
