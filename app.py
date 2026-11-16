import streamlit as st
import pandas as pd
import calendar
import os

# 1. 페이지 설정
st.set_page_config(page_title="COSMAX PET 연장근무 상세조회", page_icon="🐾", layout="wide")

# 2. 스타일 설정
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

# 3. 달력 렌더링 함수
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

# 4. 휴일 체크 함수
def get_day_type(date_obj):
    if pd.isna(date_obj): return ""
    if date_obj.weekday() >= 5: return "🔴 휴일근무"
    else: return "🟢 평일근무"

# 5. 본문 로직
excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx') and not f.startswith('~')]
FILE_NAME = excel_files[0] if excel_files else None

if not FILE_NAME:
    st.warning("⚠️ 서버에 엑셀 데이터 파일(.xlsx)이 없습니다.")
else:
    # 엑셀 파일 그대로 가져오기
    df = pd.read_excel(FILE_NAME)
    
    if 'saved_name' not in st.session_state: st.session_state['saved_name'] = ""
    if 'saved_birth' not in st.session_state: st.session_state['saved_birth'] = ""

    with st.container():
        st.markdown('<div class="search-box">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            input_name = st.text_input("👤 성명", value=st.session_state['saved_name'], placeholder="이름을 입력하세요")
        with col2:
            input_birth = st.text_input("🎂 생년월일 (6자리 또는 8자리)", value=st.session_state['saved_birth'], placeholder="예: 900101 또는 19900101", type="password")
            
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
            # ★ 캡처본 완벽 분석 반영 검색 ★
            # Unnamed: 2 가 '성명', Unnamed: 3 이 '생년월일' 입니다!
            name_col = 'Unnamed: 2' if 'Unnamed: 2' in df.columns else None
            birth_col = 'Unnamed: 3' if 'Unnamed: 3' in df.columns else None
            
            if name_col and birth_col:
                # 1. 이름 검색 ('합계' 행은 제외)
                mask_name = (df[name_col].astype(str) == input_name) & (~df.astype(str).apply(lambda x: x.str.contains('합계', na=False)).any(axis=1))
                filtered_df = df[mask_name]
                
                # 2. 생년월일 검색 (앞에 연도가 붙어있을 수 있으므로 포함 여부로 검색)
                mask_birth = filtered_df[birth_col].astype(str).str.contains(input_birth, na=False)
                filtered_df = filtered_df[mask_birth]
                
                if filtered_df.empty:
                    st.info("조건에 맞는 연장근무 내역이 없습니다.")
                else:
                    # Unnamed: 7 을 '연장시간'으로 추정 (캡처본에 '1'이라고 적혀있음)
                    total_count = len(filtered_df)
                    time_col = 'Unnamed: 7' if 'Unnamed: 7' in filtered_df.columns else None
                    total_hours = pd.to_numeric(filtered_df[time_col], errors='coerce').sum() if time_col else 0
                    
                    # 평일/휴일 구분 추가
                    date_col = 'Unnamed: 4' if 'Unnamed: 4' in filtered_df.columns else None
                    if date_col:
                        filtered_df.insert(0, '구분', pd.to_datetime(filtered_df[date_col], errors='coerce').apply(get_day_type))
                        
                    st.markdown("### 📊 연장근무 요약")
                    col_stat1, col_stat2 = st.columns(2)
                    with col_stat1:
                        st.markdown(f'<div class="stat-box"><div class="stat-title">🗓️ 발생 일수</div><div class="stat-value">{total_count}<span class="stat-unit"> 건</span></div></div>', unsafe_allow_html=True)
                    with col_stat2:
                        st.markdown(f'<div class="stat-box" style="background-color: #3b5998; border:none;"><div class="stat-title" style="color: white;">⏱️ 총 연장시간 합계</div><div class="stat-value" style="color: white;">{total_hours:g}<span class="stat-unit" style="color: rgba(255,255,255,0.8);"> 시간</span></div></div>', unsafe_allow_html=True)
                    st.markdown("<br>", unsafe_allow_html=True)
                    
                    # 달력 렌더링
                    if date_col:
                        try:
                            work_dates_dt = pd.to_datetime(filtered_df[date_col], errors='coerce').dropna()
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
                    
                    # 상세 표는 예쁘게 보이도록 필요 없는 컬럼들을 숨깁니다.
                    display_df = filtered_df.copy()
                    
                    # 컬럼 이름 예쁘게 바꾸기 (캡처본 기반)
                    rename_dict = {}
                    if 'Unnamed: 1' in display_df.columns: rename_dict['Unnamed: 1'] = '부서'
                    if 'Unnamed: 2' in display_df.columns: rename_dict['Unnamed: 2'] = '성명'
                    if 'Unnamed: 3' in display_df.columns: rename_dict['Unnamed: 3'] = '생년월일'
                    if 'Unnamed: 4' in display_df.columns: rename_dict['Unnamed: 4'] = '발생일자'
                    if 'Unnamed: 5' in display_df.columns: rename_dict['Unnamed: 5'] = '시작시간'
                    if 'Unnamed: 6' in display_df.columns: rename_dict['Unnamed: 6'] = '종료시간'
                    if 'Unnamed: 7' in display_df.columns: rename_dict['Unnamed: 7'] = '연장시간'
                    if 'Unnamed: 9' in display_df.columns: rename_dict['Unnamed: 9'] = '업무내용'
                    
                    display_df = display_df.rename(columns=rename_dict)
                    
                    # 화면에 보여줄 컬럼만 선택
                    show_cols = ['구분'] + [c for c in rename_dict.values() if c in display_df.columns]
                    st.dataframe(display_df[show_cols], use_container_width=True, hide_index=True)
            else:
                st.error("엑셀 파일의 구조가 달라서 검색할 수 없습니다.")
