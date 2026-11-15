import streamlit as st
import pandas as pd
from datetime import datetime
import holidays
import os

# 1. 페이지 설정
st.set_page_config(page_title="COSMAX PET 연장근무 상세조회", page_icon="🐾", layout="wide")

# 2. 아주 튼튼한 데이터 로딩 함수 (절대 에러 안 남!)
@st.cache_data(ttl=60)
def load_data(file_path):
    if not file_path or not os.path.exists(file_path): 
        return None
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

# 3. 평일/휴일 판독기
def check_holiday(date_val):
    try:
        dt = pd.to_datetime(date_val)
        kr_holidays = holidays.KR()
        if dt.weekday() >= 5: return "🔴 휴일근무"
        elif dt in kr_holidays: return "🔴 휴일근무(공휴일)"
        else: return "🟢 평일근무"
    except:
        return "알수없음"

# 4. 앱 화면 시작
st.markdown("<h1>🐾 COSMAX PET 연장근무 상세조회</h1>", unsafe_allow_html=True)
st.markdown("---")

excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx') and not f.startswith('~')]
FILE_NAME = excel_files[0] if excel_files else None
df = load_data(FILE_NAME)

if df is None:
    st.warning("⚠️ 서버에 엑셀 데이터 파일이 등록되지 않았습니다.")
else:
    # 검색창
    col1, col2 = st.columns(2)
    with col1:
        input_name = st.text_input("👤 성명", placeholder="이름을 입력하세요 (예: 김원태)")
    with col2:
        input_birth = st.text_input("🎂 생년월일 (6자리)", placeholder="예: 900101", type="password")
    
    if st.button("내역 조회하기", type="primary", use_container_width=True):
        if not input_name or not input_birth:
            st.error("이름과 생년월일을 모두 입력해주세요.")
        else:
            # 1) 이름으로 먼저 검색 (엄청 유연하게!)
            name_cols = [c for c in df.columns if '성명' in c or '이름' in c]
            if name_cols:
                result = df[df[name_cols[0]].astype(str).str.contains(input_name, na=False)]
            else:
                result = df[df.apply(lambda row: row.astype(str).str.contains(input_name).any(), axis=1)]
                
            # 2) 생년월일 검색 (있을 때만!)
            birth_cols = [c for c in df.columns if '생년' in c]
            if not result.empty and birth_cols:
                result = result[result[birth_cols[0]].astype(str).str.contains(input_birth, na=False)]

            if result.empty:
                st.info(f"'{input_name}' 님의 검색 조건에 맞는 연장근무 내역이 없습니다.")
            else:
                st.success(f"🎉 {input_name}님의 내역을 찾았습니다!")
                
                # 3) 평일/휴일 구분선 추가
                date_cols = [c for c in result.columns if '일자' in c or '날짜' in c or '근무일' in c]
                if date_cols:
                    result.insert(0, '구분', result[date_cols[0]].apply(check_holiday))

                # 4) 통계 계산
                time_cols = [c for c in result.columns if '시간' in c]
                total_hours = pd.to_numeric(result[time_cols[0]], errors='coerce').sum() if time_cols else 0
                
                st.markdown("### 📊 요약")
                c1, c2 = st.columns(2)
                c1.metric("🗓️ 총 발생 건수", f"{len(result)} 건")
                c2.metric("⏱️ 총 연장시간", f"{total_hours:g} 시간")
                
                st.markdown("### 📝 상세 내역")
                st.dataframe(result, use_container_width=True, hide_index=True)
