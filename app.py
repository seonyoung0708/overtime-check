import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
import os

# 1. 페이지 설정
st.set_page_config(page_title="COSMAX PET 연장근무 상세조회", page_icon="🐾", layout="wide")

# 2. 스타일 설정 (가장 깔끔했던 금요일 버전)
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    html, body, [class*="css"]  { font-family: 'Pretendard', sans-serif !important; }
    h1 { text-align: center; color: #333333; margin-bottom: 20px; }
    .search-box { background-color: #f8f9fa; padding: 25px; border-radius: 15px; margin-bottom: 30px; border: 1px solid #e9ecef; box-shadow: 0 4px 6px rgba(0,0,0,0.05); }
    .stat-box { text-align: center; padding: 20px; border-radius: 12px; border: 1px solid #e0e0e0; background-color: white; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .stat-title { font-size: 1em; color: #666; margin-bottom: 8px; }
    .stat-value { font-size: 1.8em; font-weight: bold; color: #1f77b4; }
    .stat-unit { font-size: 0.6em; color: #333; font-weight: normal; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🐾 COSMAX PET 연장근무 상세조회</h1>", unsafe_allow_html=True)

# 3. 달력 렌더링 함수
def create_calendar(year, month, work_dates):
    cal = calendar.monthcalendar(year, month)
    html = f'''
    <div style="font-family: 'Pretendard', sans-serif;">
        <h4 style="text-align: center; color: #444; margin-bottom: 10px;">{year}년 {month}월</h4>
        <table style="width: 100%; border-collapse: collapse; text-align: center; font-size: 0.9em;">
            <tr style="background-color: #f8f9fa; color: #555;">
                <th style="padding: 8px; color: #e74c3c;">일</th>
                <th>월</th><th>화</th><th>수</th><th>목</th><th>금</th>
                <th style="padding: 8px; color: #3498db;">토</th>
            </tr>
    '''
    for week in cal:
        html += "<tr>"
        for i, day in enumerate(week):
            if day == 0:
                html += "<td style='padding: 8px; border: 1px solid #eee;'></td>"
            else:
                date_str = f"{year}-{month:02d}-{day:02d}"
                is_work = date_str in work_dates
                bg_color = "#e3f2fd" if is_work else "white"
                color = "#1565c0" if is_work else ("#e74c3c" if i==0 else "#3498db" if i==6 else "#333")
                day_html = f'<div style="background-color:#1565c0; color:white; border-radius:50%; width:24px; height:24px; line-height:24px; margin:auto; font-weight:bold;">{day}</div>' if is_work else day
                html += f"<td style='padding: 8px; border: 1px solid #eee; background-color: {bg_color}; color: {color};'>{day_html}</td>"
        html += "</tr>"
    return html + "</table></div>"

# 4. 데이터 로딩 (가장 안정적이었던 방식)
@st.cache_data(ttl=60)
def load_data(file_path):
    if not file_path or not os.path.exists(file_path): return None
    try:
        all_sheets = pd.read_excel(file_path, sheet_name=None)
        combined_df = pd.DataFrame()
        for _, df in all_sheets.items():
            if df.empty: continue
            df.columns = [str(c).replace(" ", "").replace("\n", "").strip() for c in df.columns]
            combined_df = pd.concat([combined_df, df], ignore_index=True)
            
        # '합계' 처리
        for col in combined_df.columns:
            if '성명' in col or '이름' in col:
                combined_df = combined_df[~combined_df[col].astype(str).str.contains("합계", na=False)]
        return combined_df
    except:
        return None

# 5. 본문 로직
excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx') and not f.startswith('~')]
FILE_NAME = excel_files[0] if excel_files else None
df = load_data(FILE_NAME)

if df is None:
    st.warning("⚠️ 서버에 엑셀 데이터 파일(.xlsx)이 없습니다.")
else:
    # 세션 상태 초기화
    if 'saved_name' not in st.session_state: st.session_state['saved_name'] = ""
    if 'saved_birth' not in st.session_state: st.session_state['saved_birth'] = ""

    st.markdown('<div class="search-box">', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        input_name = st.text_input("👤 성명", value=st.session_state['saved_name'], placeholder="이름을 입력하세요")
    with c2:
        input_birth = st.text_input("🎂 생년월일 (6자리)", value=st.session_state['saved_birth'], placeholder="예: 900101", type="password")
    
    remember = st.checkbox("내 정보 기억하기", value=bool(st.session_state['saved_name']))
    search_btn = st.button("내역 조회하기", use_container_width=True, type="primary")
    st.markdown('</div>', unsafe_allow_html=True)

    if search_btn:
        if remember:
            st.session_state['saved_name'], st.session_state['saved_birth'] = input_name, input_birth
        else:
            st.session_state['saved_name'], st.session_state['saved_birth'] = "", ""

        if not input_name or not input_birth:
            st.error("이름과 생년월일을 모두 입력해주세요.")
        else:
            result = df.copy()
            
            # 금요일의 강력한 검색 엔진 (컬럼명이 틀어져도 찾아냄)
            name_found = False
            for col in result.columns:
                if '성명' in str(col) or '이름' in str(col):
                    result = result[result[col].astype(str).str.replace(" ", "").str.contains(input_name.replace(" ", ""), na=False)]
                    name_found = True
                    break
            
            if not name_found or result.empty: # 못 찾았으면 전체 뒤지기
                mask = df.astype(str).apply(lambda x: x.str.replace(" ", "").str.contains(input_name.replace(" ", ""), na=False))
                result = df[mask.any(axis=1)]
                
            if not result.empty:
                birth_found = False
                for col in result.columns:
                    if '생년' in str(col):
                        result = result[result[col].astype(str).str.replace(" ", "").str.contains(input_birth.replace(" ", ""), na=False)]
                        birth_found = True
                        break
                if not birth_found:
                    mask2 = result.astype(str).apply(lambda x: x.str.replace(" ", "").str.contains(input_birth.replace(" ", ""), na=False))
                    result = result[mask2.any(axis=1)]

            # '합계' 줄 제거 한 번 더 확인
            mask_sum = result.astype(str).apply(lambda x: x.str.contains('합계', na=False)).any(axis=1)
            result = result[~mask_sum]

            if result.empty:
                st.info("조건에 맞는 연장근무 내역이 없습니다. (이름 또는 생년월일을 확인해주세요)")
            else:
                st.markdown("### 📊 연장근무 요약")
                time_col = next((c for c in result.columns if '시간' in str(c) or 'Unnamed: 7' in str(c)), None)
                total_hours = pd.to_numeric(result[time_col], errors='coerce').sum() if time_col else 0
                
                s1, s2 = st.columns(2)
                s1.markdown(f'<div class="stat-box"><div class="stat-title">🗓️ 발생 일수</div><div class="stat-value">{len(result)}<span class="stat-unit"> 건</span></div></div>', unsafe_allow_html=True)
                s2.markdown(f'<div class="stat-box" style="background-color:#3b5998;"><div class="stat-title" style="color:white;">⏱️ 총 연장시간 합계</div><div class="stat-value" style="color:white;">{total_hours:g}<span class="stat-unit" style="color:#eee;"> 시간</span></div></div>', unsafe_allow_html=True)
                
                date_col = next((c for c in result.columns if '날짜' in str(c) or '일자' in str(c) or 'Unnamed: 4' in str(c)), None)
                if date_col:
                    st.markdown("<br>### 📅 연장근무 발생 달력", unsafe_allow_html=True)
                    work_dates_dt = pd.to_datetime(result[date_col], errors='coerce').dropna()
                    if not work_dates_dt.empty:
                        work_dates_str = work_dates_dt.dt.strftime('%Y-%m-%d').tolist()
                        unique_months = sorted(list(set([(dt.year, dt.month) for dt in work_dates_dt])))
                        cols = st.columns(min(len(unique_months), 3))
                        for i, (y, m) in enumerate(unique_months):
                            with cols[i % 3]:
                                st.markdown(create_calendar(y, m, work_dates_str), unsafe_allow_html=True)

                st.markdown("<br>### 📝 상세 내역", unsafe_allow_html=True)
                final_cols = [c for c in result.columns if "Unnamed" not in str(c)]
                st.dataframe(result[final_cols] if final_cols else result, use_container_width=True, hide_index=True)
