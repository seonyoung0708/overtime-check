# ⏰ 타이틀 아래에 수당 지급 기준 문구 추가
st.markdown("""
<div style="background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 25px; margin: 20px 0; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
    <h3 style="color: #004aad; font-size: 1.4rem !important; margin-bottom: 15px !important; text-align: left; font-weight: 900;">1. 수당 지급 기준 (150% 가산 적용)</h3>
    <table style="width: 100%; border-collapse: collapse; background-color: white; border-radius: 8px; overflow: hidden; border: 1px solid #cbd5e1;">
        <thead>
            <tr style="background-color: #f1f5f9;">
                <th style="padding: 15px; border: 1px solid #cbd5e1; width: 15%; text-align: center; color: #475569; font-weight: 800;">구분</th>
                <th style="padding: 15px; border: 1px solid #cbd5e1; width: 45%; text-align: left; color: #475569; font-weight: 800;">발생 기준</th>
                <th style="padding: 15px; border: 1px solid #cbd5e1; width: 40%; text-align: left; color: #475569; font-weight: 800;">수당 지급률</th>
            </tr>
        </thead>
        <tbody>
            <tr>
                <td style="padding: 15px; border: 1px solid #cbd5e1; text-align: center; font-weight: 800; color: #1e293b; background-color: #fff;">연장근로</td>
                <td style="padding: 15px; border: 1px solid #cbd5e1; color: #334155; font-weight: 600;">
                    • 평일 정규 근무시간(08:30~17:30) 외 근무<br>
                    • <b>점심 휴게시간(12:30~13:30) 중 근무</b>
                </td>
                <td style="padding: 15px; border: 1px solid #cbd5e1; color: #1e293b; font-weight: 700;">통상임금의 <span style="color: #ef4444;">150% (1.5배)</span></td>
            </tr>
            <tr>
                <td style="padding: 15px; border: 1px solid #cbd5e1; text-align: center; font-weight: 800; color: #1e293b; background-color: #fff;">휴일근로</td>
                <td style="padding: 15px; border: 1px solid #cbd5e1; color: #334155; font-weight: 600;">
                    • 주말, 법정 공휴일, 근로자의 날 근무
                </td>
                <td style="padding: 15px; border: 1px solid #cbd5e1; color: #1e293b; font-weight: 700;">
                    • 8시간 이내: 통상임금의 <span style="color: #ef4444;">150%</span><br>
                    • 8시간 초과: 통상임금의 <span style="color: #ef4444;">200% (2배)</span>
                </td>
            </tr>
        </tbody>
    </table>
    <p style="margin-top: 12px; font-size: 0.95rem; color: #64748b; font-weight: 600;">※ 휴일근로는 8시간을 초과하면 '휴일+연장'이 중복되어 200%가 적용됩니다.</p>
</div>
""", unsafe_allow_html=True)
