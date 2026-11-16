import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
import os

# 1. 페이지 설정
st.set_page_config(page_title="COSMAX PET 연장근무 상세조회", page_icon="🐾", layout="wide")

# 2. 스타일 (파란 통계 네모 + 달력 폰트 적용)
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    html, body, [class*="css"]  { font-family: 'Pretendard', sans-serif !important; }
    h1 { text-align: center; color: #333333; margin-bottom: 20px; }
    .search-box { background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 30px; border: 1px solid #e9ecef; }
    .stat-box { text-align: center; padding: 15px; border-radius: 8px; border: 1px solid #e0e0e0; background-color: white; }
    .stat-title { font-size: 0.9em; color: #666; margin-bottom: 5px; }
    .stat-value { font-size: 1.5em; font-weight: bold; color: #1f77b4; }
    .stat-unit { font-size: 0.8em; color: #333; font-weight: normal; }
</style>
""", unsafe_allow_html=True)

st.markdown("<h1>🐾 COSMAX PET 연장근무 상세조회</h1>", unsafe_allow_html=True)
st.markdown("---")

# 3. 달력 함수 (파란 동그라미의 마법)
def create_calendar(year, month, work_dates):
    cal = calendar.monthcalendar(year, month)
    html = f'''
    <div style="font-family: 'Pretendard', sans-serif;">
        <h4 style="text-align: center; color: #444; margin-bottom: 10px;">{year}년 {month}월</h4>
        <table style="width: 100%; border-collapse: collapse; text-align: center;">
            <tr style="background-color: #f1f3f5; color: #555; font-size: 0.9em;">
                <th style="padding: 8px; color: #e74c3c;">일</th>
                <th style="padding: 8px;">월</th><th style="padding: 8px;">화</th><th style="padding: 8px;">수</th>
                <th style="padding: 8px;">목</th><th style="padding: 8px;">금</th><th style="padding: 8px; color: #3498db;">토</th>
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
                font_weight = "bold" if is_work else "normal"
                if is_work: color = "#1565c0"
                elif i == 0: color = "#e74c3c"
                elif i == 6: color = "#3498db"
                else: color = "#333"
                html += f"<td style='padding: 10px; border: 1px solid #eee; background-color: {bg_color}; color: {color}; font-weight: {font_weight};'>{'<div style=\"background-color:#1565c0; color:white; border-radius:50%; width:24px; height:24px; line-height:24px; margin:auto;\">'+str(day)+'</div>' if is_work else day}</td>"
        html += "</tr>"
    html += "</table></div>"
    return html

# 4. 데이터 로딩 (가장 처음 썼던 그 튼튼한 방식)
@st.cache_data(ttl=60)
def load_data(file_path):
    if not file_path or not os.path.exists(file_path): return None
    try:
        all_sheets = pd.read_excel(file_path, sheet_name=None)
        combined_df = pd.DataFrame()
        for sheet_name, df in all_sheets.items():
            if df.empty: continue
            df.columns = [str(c).replace(" ", "").replace("\n", "").strip() for c in df.columns]
            combined_df = pd.concat([combined_df, df], ignore_index=True)
        return combined_df if not combined_df.empty else None
    except Exception as e:
        return None

# 5. 본문 로직
excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx') and not f.startswith('~')]
FILE_NAME = excel_files[0] if excel_files else None
df = load_data(FILE_NAME)

if df is None:
    st.warning("⚠️ 서버에 엑셀 데이터 파일(.xlsx)이 없습니다.")
else:
    with st.container():
        st.markdown('<div class="search-box">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            input_name = st.text_input("👤 성명", placeholder="이름을 입력하세요 (예: 홍길동)")
        with col2:
            input_birth = st.text_input("🎂 생년월일 (6자리)", placeholder="예: 900101", type="password")
            
        search_btn = st.button("내역 조회하기", use_container_width=True, type="primary")
        st.markdown('</div>', unsafe_allow_html=True)

    if search_btn:
        if not input_name or not input_birth:
            st.error("이름과 생년월일을 모두 입력해주세요.")
        else:
            filtered_df = pd.DataFrame()
            
            # 제일 처음 성공했던 그 검색 방식 그대로
            if '성명' in df.columns:
                filtered_df = df[df['성명'].astype(str) == input_name]
            elif '이름' in df.columns:
                filtered_df = df[df['이름'].astype(str) == input_name]
            
            if not filtered_df.empty and '생년월일' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['생년월일'].astype(str) == input_birth]
                
            if '성명' in filtered_df.columns:
                filtered_df = filtered_df[~filtered_df['성명'].astype(str).str.contains("합계", na=False)]
                
            if filtered_df.empty:
                st.info("조건에 맞는 연장근무 내역이 없습니다.")
            else:
                total_count = len(filtered_df)
                total_hours = 0
                
                if '연장시간' in filtered_df.columns:
                    total_hours = pd.to_numeric(filtered_df['연장시간'], errors='coerce').sum()
                elif '시간' in filtered_df.columns:
                    total_hours = pd.to_numeric(filtered_df['시간'], errors='coerce').sum()
                
                # 파란 통계 네모
                st.markdown("### 📊 연장근무 요약")
                col_stat1, col_stat2 = st.columns(2)
                with col_stat1:
                    st.markdown(f'<div class="stat-box"><div class="stat-title">🗓️ 발생 일수</div><div class="stat-value">{total_count}<span class="stat-unit"> 건</span></div></div>', unsafe_allow_html=True)
                with col_stat2:
                    st.markdown(f'<div class="stat-box" style="background-color: #3b5998; border:none;"><div class="stat-title" style="color: white;">⏱️ 총 연장시간 합계</div><div class="stat-value" style="color: white;">{total_hours:g}<span class="stat-unit" style="color: rgba(255,255,255,0.8);"> 시간</span></div></div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                
                # ★ 우리가 환호했던 파란 동그라미 달력 ★
                date_col_name = None
                if '날짜' in filtered_df.columns: date_col_name = '날짜'
                elif '근무일자' in filtered_df.columns: date_col_name = '근무일자'
                
                if date_col_name:
                    try:
                        work_dates_dt = pd.to_datetime(filtered_df[date_col_name], errors='coerce').dropna()
                        if not work_dates_dt.empty:
                            st.markdown("### 📅 연장근무 발생 달력")
                            st.caption("파란색 동그라미 표시된 날이 연장근무 발생일입니다.")
                            
                            work_dates_str = work_dates_dt.dt.strftime('%Y-%m-%d').tolist()
                            unique_months = sorted(list(set([(dt.year, dt.month) for dt in work_dates_dt])))
                            cols = st.columns(min(len(unique_months), 3))
                            
                            for i, (y, m) in enumerate(unique_months):
                                with cols[i % 3]:
                                    st.markdown(create_calendar(y, m, work_dates_str), unsafe_allow_html=True)
                                    st.markdown("<br>", unsafe_allow_html=True)
                    except: pass
                
                st.markdown("### 📝 상세 내역")
                display_cols = [c for c in filtered_df.columns if not str(c).startswith('Unnamed')]
                st.dataframe(filtered_df[display_cols], use_container_width=True, hide_index=True)
