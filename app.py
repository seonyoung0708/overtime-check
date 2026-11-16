import streamlit as st
import pandas as pd
import calendar
from datetime import datetime
import holidays
import os

# 1. 페이지 설정
st.set_page_config(page_title="COSMAX PET 연장근무 상세조회", page_icon="🐾", layout="wide")

# 2. 스타일 (화면 예쁘게 꾸미기)
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    html, body, [class*="css"]  { font-family: 'Pretendard', sans-serif !important; }
    h1 { text-align: center; color: #2c3e50; margin-bottom: 30px;}
    .search-box { background-color: #f8f9fa; padding: 25px; border-radius: 15px; margin-bottom: 30px; box-shadow: 0 4px 6px rgba(0,0,0,0.05); border: 1px solid #e9ecef; }
    .stat-box { text-align: center; padding: 20px; border-radius: 12px; background-color: white; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #e0e0e0;}
    .stat-title { font-size: 1em; color: #7f8c8d; margin-bottom: 8px; font-weight: 500;}
    .stat-value { font-size: 2em; font-weight: 700; color: #2980b9; }
    .stat-unit { font-size: 0.5em; color: #95a5a6; font-weight: normal; }
    .calendar-container { background-color: white; padding: 20px; border-radius: 12px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); border: 1px solid #e0e0e0; }
</style>
""", unsafe_allow_html=True)

# 3. 데이터 로딩 (에러 방지용 튼튼한 함수)
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
            
        # '합계' 줄 지우기
        if '성명' in combined_df.columns:
            combined_df = combined_df[~combined_df['성명'].astype(str).str.contains("합계", na=False)]
        elif '이름' in combined_df.columns:
            combined_df = combined_df[~combined_df['이름'].astype(str).str.contains("합계", na=False)]
            
        return combined_df if not combined_df.empty else None
    except Exception as e:
        return None

# 4. 달력 그리기 함수
def create_calendar(year, month, work_dates):
    cal = calendar.monthcalendar(year, month)
    html = f'''
    <div style="font-family: 'Pretendard', sans-serif;">
        <h4 style="text-align: center; color: #2c3e50; margin-bottom: 15px;">🗓️ {year}년 {month}월</h4>
        <table style="width: 100%; border-collapse: separate; border-spacing: 5px; text-align: center;">
            <tr style="color: #7f8c8d; font-size: 0.9em;">
                <th style="color:#e74c3c">일</th><th>월</th><th>화</th><th>수</th><th>목</th><th>금</th><th style="color:#3498db">토</th>
            </tr>
    '''
    for week in cal:
        html += "<tr>"
        for i, day in enumerate(week):
            if day == 0:
                html += "<td></td>"
            else:
                date_str = f"{year}-{month:02d}-{day:02d}"
                is_work = date_str in work_dates
                bg_color = "#e8f4f8" if is_work else "white"
                border = "2px solid #3498db" if is_work else "1px solid #eee"
                color = "#3498db" if is_work else ("#e74c3c" if i==0 else "#3498db" if i==6 else "#333")
                font_weight = "bold" if is_work else "normal"
                
                html += f'''
                <td style="
                    background-color: {bg_color};
                    border: {border};
                    border-radius: 8px;
                    padding: 10px 5px;
                    color: {color};
                    font-weight: {font_weight};
                    width: 14%;
                ">{day}</td>
                '''
        html += "</tr>"
    html += "</table></div>"
    return html

# 5. 화면 시작!
st.markdown("<h1>🐾 COSMAX PET 연장근무 상세조회</h1>", unsafe_allow_html=True)

excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx') and not f.startswith('~')]
FILE_NAME = excel_files[0] if excel_files else None
df = load_data(FILE_NAME)

if df is None:
    st.warning("⚠️ 서버에 엑셀 데이터 파일(.xlsx)이 없습니다.")
else:
    st.markdown('<div class="search-box">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        input_name = st.text_input("👤 성명", placeholder="이름을 입력하세요 (예: 김원태)")
    with col2:
        input_birth = st.text_input("🎂 생년월일 (6자리)", placeholder="예: 900101", type="password")
    
    search_btn = st.button("내역 조회하기", use_container_width=True, type="primary")
    st.markdown('</div>', unsafe_allow_html=True)

    if search_btn:
        if not input_name or not input_birth:
            st.error("이름과 생년월일을 모두 입력해주세요.")
        else:
            # 1) 유연하게 검색!
            name_cols = [c for c in df.columns if '성명' in c or '이름' in c]
            if name_cols:
                result = df[df[name_cols[0]].astype(str).str.contains(input_name, na=False)]
            else:
                result = df[df.apply(lambda row: row.astype(str).str.contains(input_name).any(), axis=1)]
                
            birth_cols = [c for c in df.columns if '생년' in c]
            if not result.empty and birth_cols:
                result = result[result[birth_cols[0]].astype(str).str.contains(input_birth, na=False)]

            if result.empty:
                st.info("조건에 맞는 연장근무 내역이 없습니다.")
            else:
                st.success(f"🎉 {input_name}님의 내역을 찾았습니다!")
                
                # ★ 여기서 평일/휴일 구분칸 추가!! ★
                date_cols = [c for c in result.columns if '일자' in c or '날짜' in c or '근무일' in c]
                if date_cols:
                    kr_holidays = holidays.KR()
                    result.insert(0, '구분(평일/휴일)', pd.to_datetime(result[date_cols[0]], errors='coerce').apply(
                        lambda x: "알수없음" if pd.isna(x) else ("🔴 휴일근무" if x.weekday() >= 5 or x in kr_holidays else "🟢 평일근무")
                    ))
                
                # 통계 계산
                time_cols = [c for c in result.columns if '시간' in c]
                total_hours = pd.to_numeric(result[time_cols[0]], errors='coerce').sum() if time_cols else 0
                
                st.markdown("### 📊 요약")
                c1, c2 = st.columns(2)
                with c1:
                    st.markdown(f'<div class="stat-box"><div class="stat-title">🗓️ 총 발생 건수</div><div class="stat-value">{len(result)}<span class="stat-unit"> 건</span></div></div>', unsafe_allow_html=True)
                with c2:
                    st.markdown(f'<div class="stat-box" style="border-color:#3498db;"><div class="stat-title">⏱️ 총 연장시간</div><div class="stat-value">{total_hours:g}<span class="stat-unit"> 시간</span></div></div>', unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # 달력 표시 (날짜 컬럼이 있을 때만)
                if date_cols:
                    st.markdown("### 📅 발생일 달력")
                    work_dates = pd.to_datetime(result[date_cols[0]], errors='coerce').dt.strftime('%Y-%m-%d').dropna().tolist()
                    
                    if work_dates:
                        months_worked = sorted(list(set([d[:7] for d in work_dates])))
                        cal_cols = st.columns(min(len(months_worked), 3))
                        for i, ym in enumerate(months_worked):
                            with cal_cols[i % 3]:
                                y, m = map(int, ym.split('-'))
                                st.markdown(f'<div class="calendar-container">{create_calendar(y, m, work_dates)}</div>', unsafe_allow_html=True)
                
                st.markdown("<br>### 📝 상세 내역", unsafe_allow_html=True)
                
                # Unnamed 이상한 열 숨기고 표 보여주기!
                display_cols = [c for c in result.columns if not str(c).startswith('Unnamed')]
                st.dataframe(result[display_cols], use_container_width=True, hide_index=True)
