import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="COSMAX PET 연장근무 상세조회", page_icon="🐾", layout="wide")

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

excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx') and not f.startswith('~')]
FILE_NAME = excel_files[0] if excel_files else None

if not FILE_NAME:
    st.warning("⚠️ 서버에 엑셀 파일이 없습니다.")
else:
    # 엑셀을 가장 무식하고 확실하게 읽어옵니다.
    df = pd.read_excel(FILE_NAME)
    
    with st.container():
        st.markdown('<div class="search-box">', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            input_name = st.text_input("👤 성명", placeholder="이름을 입력하세요 (예: 김원태)")
        with col2:
            input_birth = st.text_input("🎂 생년월일", placeholder="조건 무시됨", type="password", disabled=True)
            st.caption("※ 현재 검색 문제 해결을 위해 이름으로만 검색됩니다.")
            
        search_btn = st.button("내역 조회하기", use_container_width=True, type="primary")
        st.markdown('</div>', unsafe_allow_html=True)

    if search_btn:
        if not input_name:
            st.error("이름을 입력해주세요.")
        else:
            search_term = input_name.replace(" ", "")
            
            # ★ 핵심: 컬럼명이 뭐든 상관없이 엑셀 전체를 다 뒤져서 이름(띄어쓰기 제거)이 포함된 줄을 싹 다 가져옴 ★
            mask = df.astype(str).apply(lambda x: x.str.replace(" ", "").str.contains(search_term, na=False)).any(axis=1)
            filtered_df = df[mask]
            
            # '합계'라는 글자가 있는 줄은 제외
            mask_sum = filtered_df.astype(str).apply(lambda x: x.str.contains('합계', na=False)).any(axis=1)
            filtered_df = filtered_df[~mask_sum]
            
            if filtered_df.empty:
                st.error(f"정말 이상합니다. 현재 올려진 엑셀 파일 안에는 '{input_name}' 이라는 글자가 단 하나도 존재하지 않습니다. 엑셀 파일을 다시 확인해 주세요.")
            else:
                total_count = len(filtered_df)
                total_hours = 0
                
                # 시간 찾기 로직도 가장 강력하게
                for col in filtered_df.columns:
                    if '시간' in str(col) or 'Unnamed: 7' in str(col):
                        total_hours = pd.to_numeric(filtered_df[col], errors='coerce').sum()
                        break
                
                st.markdown("### 📊 연장근무 요약")
                col_stat1, col_stat2 = st.columns(2)
                with col_stat1:
                    st.markdown(f'<div class="stat-box"><div class="stat-title">🗓️ 발생 일수</div><div class="stat-value">{total_count}<span class="stat-unit"> 건</span></div></div>', unsafe_allow_html=True)
                with col_stat2:
                    st.markdown(f'<div class="stat-box" style="background-color: #3b5998; border:none;"><div class="stat-title" style="color: white;">⏱️ 총 연장시간 합계</div><div class="stat-value" style="color: white;">{total_hours:g}<span class="stat-unit" style="color: rgba(255,255,255,0.8);"> 시간</span></div></div>', unsafe_allow_html=True)
                st.markdown("<br>", unsafe_allow_html=True)
                
                st.markdown("### 📝 상세 내역")
                st.dataframe(filtered_df, use_container_width=True, hide_index=True)
