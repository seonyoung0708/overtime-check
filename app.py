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

# 3. 데이터 로딩 함수 
@st.cache_data(ttl=60)
def load_data(file_path):
    if not file_path or not os.path.exists(file_path): 
        return None
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
                combined_df = pd.concat([combined_df, df_part], ignore_index=True)
                
        return combined_df if not combined_df.empty else None
    except Exception as e:
        st.error(f"데이터를 읽는 중 오류가 발생했습니다: {e}")
        return None

# 4. 엑셀 파일 찾기 (폴더 안에 있는 .xlsx 파일 중 아무거나 하나 찾음)
excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx') and not f.startswith('~')]
FILE_NAME = excel_files[0] if excel_files else None

df = load_data(FILE_NAME)

# 5. 화면 표시
if df is None:
    st.warning("⚠️ 서버에 엑셀 데이터 파일(.xlsx)이 등록되지 않았습니다. 깃허브에 파일을 올려주세요.")
else:
    st.success("✅ 데이터를 성공적으로 불러왔습니다! 아래에서 검색해주세요.")
    # (여기서부터는 원래 작성되어 있던 검색 기능 코드들이 들어가면 됩니다. 
    # 일단 화면이 뜨는지 확인하기 위해 샘플로 데이터 프레임만 보여주겠습니다.)
    st.dataframe(df)

