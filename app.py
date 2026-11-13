import streamlit as st
import pandas as pd
from datetime import datetime
import holidays
import os
import base64

# 1. 페이지 설정
st.set_page_config(page_title="COSMAX PET 연장근무 상세조회", page_icon="🐾")

# 2. 앱 상단 타이틀
st.title("🐾 COSMAX PET 연장근무 상세조회")
st.markdown("---") 

# 3. 아주 튼튼한 데이터 로딩 함수!
@st.cache_data(ttl=60)
def load_data(file_path):
    if not file_path or not os.path.exists(file_path): 
        return None
    try:
        # 엑셀의 모든 시트를 한 번에 다 읽어옵니다. (위쪽 빈칸 무시)
        all_sheets = pd.read_excel(file_path, sheet_name=None) 
        combined_df = pd.DataFrame()

        for sheet_name, df in all_sheets.items():
            if df.empty: continue
            
            # 혹시라도 열 이름에 공백이 있으면 지워줍니다.
            df.columns = [str(c).replace(" ", "").replace("\n", "").strip() for c in df.columns]
            combined_df = pd.concat([combined_df, df], ignore_index=True)
            
        return combined_df if not combined_df.empty else None
    except Exception as e:
        st.error(f"데이터를 읽는 중 오류가 발생했습니다: {e}")
        return None

# 4. 엑셀 파일 찾기
excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx') and not f.startswith('~')]
FILE_NAME = excel_files[0] if excel_files else None

df = load_data(FILE_NAME)

# 5. 검색창 만들기!
if df is None:
    st.warning("⚠️ 서버에 엑셀 데이터 파일(.xlsx)이 등록되지 않았습니다.")
else:
    st.success("✅ 데이터를 성공적으로 불러왔습니다!")
    st.markdown("### 🔍 본인의 연장근무 내역을 검색하세요")
    
    # 이름 입력받는 칸
    search_name = st.text_input("👤 이름을 입력하세요 (예: 홍길동)")
    
    # 검색 버튼
    if st.button("조회하기"):
        if search_name:
            # 입력한 이름이 포함된 데이터만 찾기 (열 이름 중 '성명'이나 '이름'이 있다고 가정)
            if '성명' in df.columns:
                result = df[df['성명'].astype(str).str.contains(search_name, na=False)]
            elif '이름' in df.columns:
                result = df[df['이름'].astype(str).str.contains(search_name, na=False)]
            else:
                # 성명이나 이름 열을 못 찾으면 전체 데이터에서 검색
                result = df[df.apply(lambda row: row.astype(str).str.contains(search_name).any(), axis=1)]
                
            if result.empty:
                st.info(f"'{search_name}' 님의 연장근무 내역이 없습니다. (이름을 다시 확인해주세요)")
            else:
                st.write(f"🎉 **{search_name}** 님의 연장근무 상세 내역입니다.")
                st.dataframe(result)
        else:
            st.warning("이름을 입력한 후 조회하기 버튼을 눌러주세요!")
