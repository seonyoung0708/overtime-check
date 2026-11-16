import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="COSMAX PET 진단 모드", layout="wide")
st.title("🚨 엑셀 데이터 원본 까보기 진단!")

# 제일 단순하고 무식하게 엑셀을 읽어옵니다. (어떤 꼼수나 변형도 없이!)
try:
    excel_files = [f for f in os.listdir('.') if f.endswith('.xlsx') and not f.startswith('~')]
    if not excel_files:
        st.error("엑셀 파일이 없습니다.")
    else:
        df = pd.read_excel(excel_files[0])
        
        st.markdown("### 1️⃣ 엑셀의 진짜 컬럼(열) 이름들")
        st.write(df.columns.tolist())
        
        st.markdown("### 2️⃣ '김원태'라는 글자가 들어간 모든 데이터 찾아보기")
        # 데이터프레임 전체에서 '김원태' 글자가 하나라도 있는 줄(Row)을 싹 다 찾습니다.
        mask = df.astype(str).apply(lambda x: x.str.contains('김원태', na=False)).any(axis=1)
        kim_data = df[mask]
        
        if kim_data.empty:
            st.error("충격! 엑셀 파일 안에 '김원태'라는 글자가 아예 존재하지 않거나 이상하게 저장되어 있습니다.")
        else:
            st.success("✅ 다행히 '김원태' 데이터를 찾았습니다! 이렇게 생겼습니다:")
            st.dataframe(kim_data)
            
except Exception as e:
    st.error(f"오류 발생: {e}")
