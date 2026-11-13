import streamlit as st
import pandas as pd
from datetime import datetime
import holidays

# 1. 페이지 설정 (브라우저 탭에 표시될 이름)
st.set_page_config(page_title="COSMAX PET 연장근무 체크", page_icon="🐾")

# 2. 앱 상단 타이틀
st.title("🐾 COSMAX PET 연장근무 체크 시스템")
st.markdown("---") # 구분선

# 2. 스타일 설정
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    html, body, [class*="css"]  { font-family: 'Pretendard', sans-serif !important; font-size: 20px !important; font-weight: 700 !important; color: #111; }
    h1 { font-size: 2.8rem !important; font-weight: 900 !important; margin-bottom: 0px !important; color: #000; letter-spacing: -1px; text-align: center; }
    h3 { font-size: 1.8rem !important; font-weight: 900 !important; color: #004aad !important; margin-bottom: 5px !important; text-align: center; }
    input { font-size: 1.4rem !important; padding: 12px !important; font-weight: 800 !important; text-align: center; }
    .stButton>button { font-size: 1.4rem !important; font-weight: 900 !important; padding: 12px 24px !important; border-radius: 8px !important; letter-spacing: -0.5px; }
    
    .cal-wrapper { background: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05); height: 100%; display: flex; flex-direction: column; justify-content: center; }
    .cal-header { text-align: center !important; font-size: 1.3rem !important; font-weight: 900 !important; color: #1e293b !important; margin-bottom: 15px !important; }
    .cal-table { width: 100%; border-collapse: collapse; }
    .cal-table th { text-align: center; padding: 8px 0; font-size: 0.95rem; color: #64748b; font-weight: 800; border-bottom: 1px solid #f1f5f9; }
    .cal-table td { text-align: center; padding: 6px 0; }
    .cal-day { width: 34px; height: 34px; line-height: 34px; margin: 0 auto; border-radius: 50%; font-weight: 700; font-size: 1.05rem; color: #334155; }
    .cal-sat { color: #3b82f6 !important; } 
    .cal-sun { color: #ef4444 !important; } 
    .cal-worked { background-color: #004aad; color: white !important; box-shadow: 0 4px 10px rgba(0,74,173,0.4); font-weight: 900; transform: scale(1.15); }
    
    .summary-box-container { display: flex; gap: 15px; margin-bottom: 20px; align-items: center; min-height: 160px; padding: 10px 0; }
    .summary-box-1 { flex: 1; background: #fafafa; border: 1px solid #ddd; border-radius: 10px; display: flex; flex-direction: column; justify-content: center; align-items: center; min-height: 140px; }
    .summary-box-2 { flex: 2; background: #004aad; color: white; border-radius: 10px; display: flex; flex-direction: column; justify-content: center; align-items: center; min-height: 140px; }
    
    .center-table { width: 100%; border-collapse: collapse; font-size: 17px; margin-top: 10px; background-color: white; border-radius: 8px; box-shadow: 0 1px 3px rgba(0,0,0,0.1); }
    .center-table th { background-color: #f8fafc; color: #1e293b; font-weight: 900 !important; text-align: center !important; padding: 10px 8px !important; border-bottom: 2px solid #cbd5e1; white-space: nowrap; vertical-align: middle !important; line-height: normal !important; }
    .center-table td { text-align: center !important; padding: 10px 8px !important; border-bottom: 1px solid #e2e8f0; color: #334155; vertical-align: middle !important; }
    .center-table tr:last-child td { background-color: #f1f5f9 !important; font-weight: 900 !important; color: #004aad !important; border-top: 2px solid #94a3b8; }
    .center-table tr:hover { background-color: #f8fafc; }
    .stRadio label { font-size: 1.2rem !important; font-weight: 800 !important; }
</style>
""", unsafe_allow_html=True)

# 3. 로고 설정
logo_html = "<span style='font-size: 2.0rem; vertical-align: middle; margin-right: 8px;'>🐾</span>" 
if os.path.exists("logo.png"):
    with open("logo.png", "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
        logo_html = f"<img src='data:image/png;base64,{b64}' style='height: 55px; vertical-align: middle; margin-right: 12px; padding-bottom: 5px;'>"

st.markdown(f"<h3>{logo_html}코스맥스펫(주)</h3>", unsafe_allow_html=True)
st.markdown("<h1>⏰ 개인별 연장근무 상세 조회</h1>", unsafe_allow_html=True)
st.markdown("<br><br>", unsafe_allow_html=True)

# 💡 한국 공휴일 정보 가져오기 (이 한 줄로 2100년까지 자동 계산됩니다!)
kr_holidays = holidays.KR()

excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx') and not f.startswith('~')]
FILE_NAME = excel_files[0] if excel_files else None

@st.cache_data(ttl=60)
def load_data(file_path):
    if not file_path or not os.path.exists(file_path): return None
    try:
        all_sheets = pd.read_excel(file_path, sheet_name=None, header=None)
        combined_df = pd.DataFrame()
        
        for sheet_name, temp_df in all_sheets.items():
            if temp_df.empty: continue
            header_row = -1
            for i in range(min(20, len(temp_df))):
                row_text = "".join([str(v) for v in temp_df.iloc[i].values if pd.notna(v)])
                if any(k in row_text for k in ["이름", "성명", "생년월일"]):
                    header_row = i
                    break
            if header_row != -1:
                df_part = pd.read_excel(file_path, sheet_name=sheet_name, header=header_row)
                df_part.columns = [str(c).replace(" ", "").replace("\n", "").strip() for c in df_part.columns]
                
                merge_map = {
                    '연장시간': ['연장시간', '연장근무', '총연장시간', '총연장시간(일)'],
                    '휴일근무': ['휴일근무', '총휴일근무', '휴일시간'],
                    '휴일연장근무': ['휴일연장근무', '총휴일연장근무', '휴일연장시간']
                }
                for target, variants in merge_map.items():
                    present = [c for c in df_part.columns if c in variants]
                    if present:
                        df_part[target] = df_part[present].apply(pd.to_numeric, errors='coerce').max(axis=1)
                        drops = [c for c in present if c != target]
                        if drops:
                            df_part.drop(columns=drops, inplace=True)

                if '구분' in df_part.columns: df_part = df_part[~df_part['구분'].astype(str).str.contains('합계|소계|총', na=False)]
                date_c = next((c for c in ['일자', '날짜', '근무일자'] if c in df_part.columns), None)
                if date_c: df_part = df_part[~df_part[date_c].astype(str).str.contains('합계|소계|총', na=False)]
                
                ffill_cols = [c for c in df_part.columns if any(k in c for k in ['이름', '성명', '부서', '소속', '생년월일', '구분', '일자', '날짜', '근무일자'])]
                for c in ffill_cols: df_part[c] = df_part[c].ffill()
                
                combined_df = pd.concat([combined_df, df_part], ignore_index=True)
            
        if combined_df.empty: return None
        
        def clean_h(val):
            if pd.isna(val): return val
            s = str(val).strip().lower()
            return float(s.replace('h', '').strip()) if s.endswith('h') else val
            
        for c in combined_df.columns:
            if any(k in c for k in ['시간', '근무', '출근', '연장']):
                combined_df[c] = combined_df[c].apply(clean_h)
                combined_df[c] = pd.to_numeric(combined_df[c], errors='coerce')
        
        if '생년월일' in combined_df.columns:
            def fmt_birth(x):
                if isinstance(x, datetime.datetime): return x.strftime('%y%m%d')
                s = str(x).split(' ')[0].replace('-', '').replace('.', '').replace('/', '').strip()
                return s[2:] if len(s) == 8 else (s[-6:] if len(s) >= 6 else s.replace('.0','').zfill(6))
            combined_df['생년월일_검색용'] = combined_df['생년월일'].apply(fmt_birth)
            
        return combined_df
    except: return None

df = load_data(FILE_NAME)

if df is None:
    st.error("⚠️ 서버에 엑셀 데이터 파일(.xlsx)이 등록되지 않았습니다. 깃허브에 파일을 올려주세요.")
else:
    try: 
        s_name = st.query_params.get("name", "")
        s_birth = st.query_params.get("birth", "")
    except: 
        s_name, s_birth = "", ""

    col_s1, col_login, col_s2 = st.columns([1, 2, 1])
    with col_login:
        with st.form("login_form"):
            c1, c2 = st.columns(2)
            input_name = c1.text_input("👤 이름", value=s_name)
            input_birth = c2.text_input("🔒 생년월일(6자리)", value=s_birth, type="password")
            remember_me = st.checkbox("💾 내 정보 계속 기억하기", value=True if s_name else False)
            submit = st.form_submit_button("내역 조회하기", use_container_width=True)

    if submit:
        if not input_name or not input_birth:
            st.warning("이름과 생년월일을 모두 입력해주세요.")
        else:
            if remember_me:
                st.query_params["name"] = input_name
                st.query_params["birth"] = input_birth
            else:
                st.query_params.clear()

            name_col = next((c for c in ['이름', '성명'] if c in df.columns), None)
            if name_col:
                mask = (df[name_col].astype(str).str.strip() == input_name.strip()) & (df['생년월일_검색용'] == input_birth.strip())
                user_data = df[mask].copy()

                if user_data.empty: st.error("정보가 일치하지 않습니다. 이름과 생년월일을 다시 확인해주세요.")
                else:
                    date_col = next((c for c in ['일자', '날짜', '근무일자'] if c in user_data.columns), None)
                    if date_col:
                        def clean_date_val(d):
                            if pd.isna(d): return d
                            if isinstance(d, datetime.datetime): return d
                            return re.sub(r'$.*?$', '', str(d)).strip()
                        user_data[date_col] = user_data[date_col].apply(clean_date_val)
                        user_data = user_data[user_data[date_col].apply(lambda d: True if pd.to_datetime(d, errors='coerce') is not pd.NaT else False)]
                        user_data[date_col] = pd.to_datetime(user_data[date_col])
                        user_data = user_data.dropna(subset=[date_col])
                        user_data = user_data.sort_values(by=date_col)
                        
                        # 💡 날짜가 토/일이거나 자동계산 공휴일에 포함되면 휴일로 인식!
                        user_data['휴일여부'] = user_data[date_col].apply(lambda d: True if d.dayofweek >= 5 or d.date() in kr_holidays else False)
                        
                        user_data['년도'] = user_data[date_col].dt.year
                        user_data['월'] = user_data[date_col].dt.month

                    years = sorted(user_data['년도'].unique(), reverse=True)
                    st.markdown("<hr style='margin:20px 0;'>", unsafe_allow_html=True)
                    selected_year = st.radio("📅 조회할 년도를 선택하세요:", years, horizontal=True)
                    
                    year_data = user_data[user_data['년도'] == selected_year].copy()
                    months = sorted(year_data['월'].unique())
                    
                    if not months:
                        st.info("해당 년도의 데이터가 없습니다.")
                    else:
                        tabs = st.tabs([f"{m}월" for m in months])

                        def fmt_num(v):
                            if pd.isna(v) or v == 0 or str(v).strip() in ["", "0", "0.0"]: return ""
                            try:
                                f = float(v)
                                return f"{int(f)}" if f.is_integer() else f"{f}"
                            except: return str(v)

                        def fmt_time(v):
                            if pd.isna(v) or str(v).strip() == "": return ""
                            try:
                                val_s = str(int(float(v)))
                                if len(val_s)==3: return f"0{val_s[0]}:{val_s[1:]}"
                                if len(val_s)==4: return f"{val_s[:2]}:{val_s[2:]}"
                                return str(v)
                            except: return str(v)

                        for i, m_num in enumerate(months):
                            with tabs[i]:
                                m_df = year_data[year_data['월'] == m_num].copy()
                                worked_dates = m_df[date_col].dt.date.unique().tolist()
                                
                                for idx in m_df.index:
                                    if m_df.at[idx, '휴일여부']:
                                        if '연장시간' in m_df.columns:
                                            m_df.at[idx, '연장시간'] = None
                                    else:
                                        if '조기출근' in m_df.columns and '연장시간' in m_df.columns:
                                            early = pd.to_numeric(m_df.at[idx, '조기출근'], errors='coerce')
                                            ot = pd.to_numeric(m_df.at[idx, '연장시간'], errors='coerce')
                                            if pd.notna(early) and pd.notna(ot) and early > 0:
                                                calc_ot = ot - early
                                                if calc_ot <= 0:
                                                    m_df.at[idx, '연장시간'] = None
                                                else:
                                                    m_df.at[idx, '연장시간'] = calc_ot
                                
                                keywords = ['조기출근', '점심근무', '연장시간', '야간연장근무', '휴일근무', '휴일연장근무', '휴일야간연장근무', '야간근무']
                                time_cols = [kw for kw in keywords if kw in m_df.columns]
                                
                                m_total = m_df[time_cols].fillna(0).sum().sum()
                                
                                col_cal, col_sum = st.columns([1, 2.5])
                                with col_cal:
                                    cal = calendar.monthcalendar(selected_year, m_num)
                                    cal_html = f'<div class="cal-wrapper"><div class="cal-header">🗓️ {selected_year}년 {m_num}월</div><table class="cal-table"><tr><th>월</th><th>화</th><th>수</th><th>목</th><th>금</th><th class="cal-sat">토</th><th class="cal-sun">일</th></tr>'
                                    for week in cal:
                                        cal_html += "<tr>"
                                        for j, day in enumerate(week):
                                            if day == 0: cal_html += "<td></td>"
                                            else:
                                                curr_date = datetime.date(selected_year, m_num, day)
                                                is_worked = curr_date in worked_dates
                                                
                                                # 💡 요일이 일요일(6)이거나, 자동 공휴일 리스트에 포함되면 빨간색!
                                                if j == 6 or curr_date in kr_holidays:
                                                    classes = ["cal-sun"]
                                                elif j == 5:
                                                    classes = ["cal-sat"]
                                                else:
                                                    classes = [""]
                                                    
                                                if is_worked: cal_html += f"<td><div class='cal-day cal-worked'>{day}</div></td>"
                                                else: cal_html += f"<td><div class='cal-day {' '.join(classes)}'>{day}</div></td>"
                                        cal_html += "</tr>"
                                    cal_html += '</table></div>'
                                    st.markdown(cal_html, unsafe_allow_html=True)
                                
                                with col_sum:
                                    box_html = f"""
                                    <div class="summary-box-container">
                                        <div class="summary-box-1">
                                            <div style="font-size:1.15rem; color:#666; margin-bottom:0px !important;">📅 {m_num}월 발생 일수</div>
                                            <div style="font-size:3.5rem; font-weight:900; line-height:1.2;">{len(m_df)}<span style="font-size:1.5rem;">건</span></div>
                                        </div>
                                        <div class="summary-box-2">
                                            <div style="font-size:1.15rem; color:rgba(255,255,255,0.9); margin-bottom:0px !important;">💰 {m_num}월 총 연장시간 합계</div>
                                            <div style="font-size:3.8rem; font-weight:900; line-height:1.2;">{m_total:g}<span style="font-size:1.5rem;">시간</span></div>
                                        </div>
                                    </div>
                                    """
                                    st.markdown(box_html, unsafe_allow_html=True)
                                    
                                    b_html = "".join([f'<div style="background:#f8fafc; border:1px solid #e2e8f0; border-radius:8px; padding:12px; min-width:110px; text-align:center;"><div style="font-size:0.95rem; color:#64748b; font-weight:800;">{kw}</div><div style="font-size:1.4rem; font-weight:900; color:#1e293b;">{m_df[kw].fillna(0).sum():g}시간</div></div>' for kw in time_cols])
                                    st.markdown(f'<div style="font-size:1.1rem; font-weight:900; margin-bottom:12px; color:#475569;">📊 항목별 연장 상세</div><div style="display:flex; flex-wrap:wrap; gap:12px;">{b_html}</div>', unsafe_allow_html=True)

                                st.markdown("<br>", unsafe_allow_html=True)
                                
                                display_cols = []
                                for bc in ['이름', '성명', '일자', '근무일자', '시작시간', '종료시간']:
                                    c = next((col for col in m_df.columns if bc == str(col).strip()), None)
                                    if c: display_cols.append(c)
                                display_cols.extend(time_cols)
                                
                                f_df = m_df[display_cols].copy()
                                f_df[date_col] = m_df.apply(lambda r: f"{r[date_col].strftime('%Y-%m-%d')} (휴일)" if r['휴일여부'] else r[date_col].strftime('%Y-%m-%d'), axis=1)
                                if '구분' in m_df.columns: f_df.insert(0, '구분', m_df['구분'])
                                else: f_df.insert(0, '구분', '')
                                f_df.loc[m_df['휴일여부'] == True, '구분'] = '휴일근무'
                                f_df.insert(0, '순번', range(1, len(f_df) + 1))
                                
                                sum_row = {col: "" for col in f_df.columns}
                                sum_row['순번'], sum_row['구분'] = "합계", f"{m_num}월 총합"
                                for col in time_cols: sum_row[col] = f_df[col].fillna(0).sum()
                                f_df = pd.concat([f_df, pd.DataFrame([sum_row])], ignore_index=True)

                                for col in f_df.columns:
                                    if col in time_cols: f_df[col] = f_df[col].apply(fmt_num)
                                    elif '시간' in str(col): f_df[col] = f_df[col].apply(fmt_time)
                                
                                st.markdown(f_df.fillna("").to_html(index=False, escape=False).replace('<table border="1" class="dataframe">', '<table class="center-table">'), unsafe_allow_html=True)
