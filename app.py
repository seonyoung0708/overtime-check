import streamlit as st
import pandas as pd
import calendar
import os

# 1. 페이지 설정
st.set_page_config(page_title="COSMAX PET 연장근무 상세조회", page_icon="🐾", layout="wide")

# 2. 스타일 (우리가 사랑했던 파란 네모 디자인)
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

# 3. 달력 함수 (파란 동그라미 마법)
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

# 4. 데이터 읽기
excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx') and not f.startswith('~')]
if not excel_files:
    st.warning("⚠️ 서버에 엑셀 데이터 파일(.xlsx)이 없습니다.")
    st.stop()
    
df = pd.read_excel(excel_files[0])

# 5. 본문 로직
if 's_name' not in st.session_state: st.session_state['s_name'] = ""
if 's_birth' not in st.session_state: st.session_state['s_birth'] = ""

with st.container():
    st.markdown('<div class="search-box">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        input_name = st.text_input("👤 성명", value=st.session_state['s_name'], placeholder="이름을 입력하세요 (예: 김원태)")
    with col2:
        input_birth = st.text_input("🎂 생년월일 (6자리)", value=st.session_state['s_birth'], placeholder="예: 900101", type="password")
        
    remember = st.checkbox("내 정보 기억하기", value=bool(st.session_state['s_name']))
    search_btn = st.button("내역 조회하기", use_container_width=True, type="primary")
    st.markdown('</div>', unsafe_allow_html=True)

if search_btn:
    if remember:
        st.session_state['s_name'], st.session_state['s_birth'] = input_name, input_birth
    else:
        st.session_state['s_name'], st.session_state['s_birth'] = "", ""
        
    if not input_name:
        st.error("이름을 입력해주세요.")
    else:
        # ★ 무적의 검색 로직: 컬럼명이 뭐든 상관없이 엑셀 전체를 뒤져서 이름 찾기
        search_name = input_name.replace(" ", "")
        mask_name = df.astype(str).apply(lambda x: x.str.replace(" ", "").str.contains(search_name, na=False)).any(axis=1)
        res = df[mask_name]
        
        # '합계' 줄 제거
        mask_sum = res.astype(str).apply(lambda x: x.str.contains('합계', na=False)).any(axis=1)
        res = res[~mask_sum]
        
        # ★ 무적의 생년월일 로직: '1997-04-16 00:00:00' 에서 기호 다 빼고 '19970416'으로 만든 뒤 '970416'이 포함되어 있는지 검사!
        if not res.empty and input_birth:
            search_birth = input_birth.replace(" ", "")
            clean_str_df = res.astype(str).apply(lambda x: x.str.replace("-", "").str.replace(" ", "").str.replace("00:00:00", ""))
            mask_birth = clean_str_df.apply(lambda x: x.str.contains(search_birth, na=False)).any(axis=1)
            if mask_birth.any():
                res = res[mask_birth]
        
        if res.empty:
            st.info("조건에 맞는 연장근무 내역이 없습니다.")
        else:
            # 진단 화면에서 알아낸 엑셀 기둥 번호들 적용
            time_col = 'Unnamed: 7' if 'Unnamed: 7' in res.columns else None
            hours = pd.to_numeric(res[time_col], errors='coerce').sum() if time_col else 0
            
            date_col = 'Unnamed: 4' if 'Unnamed: 4' in res.columns else None
            
            # 통계 네모 렌더링
            st.markdown("### 📊 연장근무 요약")
            sc1, sc2 = st.columns(2)
            sc1.markdown(f'<div class="stat-box"><div class="stat-title">🗓️ 발생 일수</div><div class="stat-value">{len(res)}<span class="stat-unit"> 건</span></div></div>', unsafe_allow_html=True)
            sc2.markdown(f'<div class="stat-box" style="background-color: #3b5998; border:none;"><div class="stat-title" style="color: white;">⏱️ 총 연장시간 합계</div><div class="stat-value" style="color: white;">{hours:g}<span class="stat-unit" style="color: rgba(255,255,255,0.8);"> 시간</span></div></div>', unsafe_allow_html=True)
            
            # 달력 렌더링
            if date_col:
                st.markdown("<br>### 📅 연장근무 발생 달력", unsafe_allow_html=True)
                dts = pd.to_datetime(res[date_col], errors='coerce').dropna()
                if not dts.empty:
                    dts_str = dts.dt.strftime('%Y-%m-%d').tolist()
                    months = sorted(list(set([(d.year, d.month) for d in dts])))
                    m_cols = st.columns(min(len(months), 3))
                    for i, (y, m) in enumerate(months):
                        with m_cols[i % 3]:
                            st.markdown(create_calendar(y, m, dts_str), unsafe_allow_html=True)
            
            st.markdown("<br>### 📝 상세 내역", unsafe_allow_html=True)
            
            # 지저분한 Unnamed 기둥 이름들을 예쁜 한국어로 싹 바꿔서 표출
            disp_df = res.copy()
            rename_map = {
                'Unnamed: 1': '부서', 'Unnamed: 2': '성명', 'Unnamed: 3': '생년월일',
                'Unnamed: 4': '발생일자', 'Unnamed: 5': '시작시간', 'Unnamed: 6': '종료시간',
                'Unnamed: 7': '연장시간', 'Unnamed: 9': '업무내용'
            }
            disp_df.rename(columns=rename_map, inplace=True)
            
            # 예쁘게 바뀐 기둥들만 골라서 화면에 보여줌 (쓸데없는 빈칸 숨김)
            final_cols = [c for c in rename_map.values() if c in disp_df.columns]
            st.dataframe(disp_df[final_cols], use_container_width=True, hide_index=True)
