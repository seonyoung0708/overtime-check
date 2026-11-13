import streamlit as st
import pandas as pd
from datetime import datetime
import holidays
import os

# 1. 페이지 설정 (브라우저 탭에 표시될 이름)
st.set_page_config(page_title="COSMAX PET 연장근무 상세조회", page_icon="🐾", layout="wide")

# 2. 스타일 설정 (가운데 정렬 및 폰트)
st.markdown("""
<style>
    @import url('https://cdn.jsdelivr.net/gh/orioncactus/pretendard/dist/web/static/pretendard.css');
    html, body, [class*="css"]  { font-family: 'Pretendard', sans-serif !important; }
    h1 { text-align: center; color: #333333; margin-bottom: 20px;}
    .search-box { background-color: #f8f9fa; padding: 20px; border-radius: 10px; margin-bottom: 30px; border: 1px solid #e9ecef; }
    .stat-box { text-align: center; padding: 15px; border-radius: 8px; border: 1px solid #e0e0e0; background-color: white;}
    .stat-title { font-size: 0.9em; color: #666; margin-bottom: 5px; }
    .stat-value { font-size: 1.5em; font-weight: bold; color: #1f77b4; }
    .stat-unit { font-size: 0.8em; color: #333; font-weight: normal; }
</style>
""", unsafe_allow_html=True)

# 3. 앱 상단 타이틀 (원하시는 이름으로 수정 완료!)
st.markdown("<h1>🐾 COSMAX PET 연장근무 상세조회</h1>", unsafe_allow_html=True)
st.markdown("---")

# 4. 데이터 로드 함수 (이전과 동일하게 아주 튼튼합니다!)
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

# 5. 파일 찾기 및 로드
excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx') and not f.startswith('~')]
FILE_NAME = excel_files[0] if excel_files else None
df = load_data(FILE_NAME)

if df is None:
    st.warning("⚠️ 서버에 엑셀 데이터 파일(.xlsx)이 없습니다.")
else:
    # --- 검색 영역 (원하시는 화면의 윗부분) ---
    with st.container():
        st.markdown('<div class="search-box">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            input_name = st.text_input("👤 성명", placeholder="이름을 입력하세요")
        with col2:
            input_birth = st.text_input("🎂 생년월일 (6자리)", placeholder="예: 900101", type="password")
        
        search_btn = st.button("내역 조회하기", use_container_width=True, type="primary")
        st.markdown('</div>', unsafe_allow_html=True)

    # --- 조회 결과 영역 ---
    if search_btn:
        if not input_name or not input_birth:
            st.error("이름과 생년월일을 모두 입력해주세요.")
        else:
            # 1) 데이터 필터링 (이름으로 먼저 검색)
            # (실제 엑셀의 열 이름이 '성명'인지 '이름'인지 확인이 필요할 수 있습니다. 
            # 일단 두 경우 모두 대비하여 작성합니다.)
            filtered_df = pd.DataFrame()
            if '성명' in df.columns:
                filtered_df = df[df['성명'].astype(str) == input_name]
            elif '이름' in df.columns:
                filtered_df = df[df['이름'].astype(str) == input_name]
            
            # 생년월일 검증 (데이터에 생년월일 열이 있는 경우)
            if not filtered_df.empty and '생년월일' in filtered_df.columns:
                filtered_df = filtered_df[filtered_df['생년월일'].astype(str) == input_birth]
                
            if filtered_df.empty:
                st.info("조건에 맞는 연장근무 내역이 없습니다.")
            else:
                # 2) 요약 통계 계산 (원하시는 화면의 중간 부분)
                total_count = len(filtered_df)
                
                # 연장시간 계산 (열 이름이 '연장시간' 또는 '시간'이라고 가정)
                total_hours = 0
                if '연장시간' in filtered_df.columns:
                    total_hours = pd.to_numeric(filtered_df['연장시간'], errors='coerce').sum()
                elif '시간' in filtered_df.columns:
                    total_hours = pd.to_numeric(filtered_df['시간'], errors='coerce').sum()
                
                # 3) 요약 대시보드 그리기
                st.markdown("### 📊 연장근무 요약")
                col_stat1, col_stat2 = st.columns(2)
                
                with col_stat1:
                    st.markdown(f"""
                    <div class="stat-box">
                        <div class="stat-title">🗓️ 발생 일수</div>
                        <div class="stat-value">{total_count}<span class="stat-unit"> 건</span></div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                with col_stat2:
                    st.markdown(f"""
                    <div class="stat-box" style="background-color: #3b5998; border:none;">
                        <div class="stat-title" style="color: white;">⏱️ 총 연장시간 합계</div>
                        <div class="stat-value" style="color: white;">{total_hours:g}<span class="stat-unit" style="color: rgba(255,255,255,0.8);"> 시간</span></div>
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                # 4) 상세 내역 표 그리기 (원하시는 화면의 아랫부분)
                st.markdown("### 📝 상세 내역")
                
                # 표를 깔끔하게 보여주기 위해 인덱스를 숨깁니다.
                st.dataframe(filtered_df, use_container_width=True, hide_index=True)
