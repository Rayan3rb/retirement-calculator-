# Retirement Calculator
import streamlit as st
import pandas as pd
import numpy as np

# Streamlit App
st.markdown("<h1 class='title-font' style='text-align: center ;'>حاسبة التخطيط للتقاعد</h1>", unsafe_allow_html=True)

# Sidebar input fields with sliders
age = st.sidebar.slider("العمر", min_value=16, max_value=80, value=21)
retirement_age = st.sidebar.slider("تبي تتقاعد بأي عمر؟", min_value=50, max_value=65, value=65)
initial_payment = st.sidebar.slider("كم عندك مبلغ ودك تبدأ فيه؟", min_value=500, max_value=500000, value=10000, step=500)
retirement_income = st.sidebar.slider("كم راتب الشهري الي يكفيك عند التقاعد؟", min_value=8000, max_value=100000, value=20000, step=1000)*12

gosi = st.sidebar.slider("كم تتوقع التأمينات الاجتماعية بتعطيك معاش تقاعد شهريا؟", min_value=0, max_value=50000, value=0, step=1000)
st.sidebar.markdown(
    """
    <div style='position: absolute; bottom: 0; width: 100%;'>
        <a href='https://www.gosi.gov.sa/ar/PensionCalculator' target='_blank'>المؤسسة العامة للتأمينات الاجتماعية: حاسبة المعاش</a>
    </div>
    """, 
    unsafe_allow_html=True
)

age_limit = 85 + 1
years_to_retirement = retirement_age - age
years_to_age_limit = age_limit - retirement_age
if years_to_retirement < 5:
    rate = 0.06
elif years_to_retirement < 10:
    rate = 0.08
else:  # This covers the case where 7 <= age_limit <= 10
    rate = 0.12

inflation = 0.0224
return_after_retirement = 0.03
future_retirement_income = (abs(retirement_income - gosi)) * (1 + inflation) ** years_to_retirement
top = 0
payments = []
for t in range(1, years_to_age_limit + 1):
    FV_t = future_retirement_income * (1 + inflation) ** (t - 1)
    payments.append(FV_t)
    top += FV_t / (1 + return_after_retirement) ** t
recommended_contribution = (top - initial_payment * (1 + rate) ** years_to_retirement) / ((1 + rate) ** years_to_retirement - 1) * rate

years = range(0, years_to_retirement + years_to_age_limit + 1)
Tamra_contribution = []
tamra_retirment = []
tamra_returns = []
Tamra_total = []

for i in years:
    if i == 0:
        Tamra_contribution.append(0)
        tamra_retirment.append(0)
        tamra_returns.append(0)
        Tamra_total.append(initial_payment)
    elif i <= years_to_retirement:
        Tamra_contribution.append(recommended_contribution)
        tamra_retirment.append(0)
        tamra_returns.append(Tamra_total[i - 1] * rate)
        Tamra_total.append(Tamra_total[i - 1] + Tamra_contribution[i] - tamra_retirment[i] + tamra_returns[i])
    elif i == years_to_retirement + 1:
        Tamra_contribution.append(0)
        tamra_retirment.append(payments[0])
        tamra_returns.append(Tamra_total[i - 1] * return_after_retirement)
        Tamra_total.append(Tamra_total[i - 1] + Tamra_contribution[i] - tamra_retirment[i] + tamra_returns[i])
    else:
        Tamra_contribution.append(0)
        tamra_retirment.append(payments[i - (years_to_retirement + 1)])
        tamra_returns.append(Tamra_total[i - 1] * return_after_retirement)
        Tamra_total.append(Tamra_total[i - 1] + Tamra_contribution[i] - tamra_retirment[i] + tamra_returns[i])

AGES = pd.DataFrame(list(range(age - 1, 86)))
Tamra_contribution = pd.DataFrame(Tamra_contribution)
tamra_retirment = pd.DataFrame(tamra_retirment)
tamra_returns = pd.DataFrame(tamra_returns)
Tamra_total = pd.DataFrame(Tamra_total)
Tamra = pd.concat([AGES, Tamra_contribution, tamra_retirment, tamra_returns, Tamra_total], axis=1)
Tamra.columns = ['العمر', "Contribution", "راتب التقاعد السنوي", "Returns", "مجموع الاستثمارات"]

# Display results
st.markdown("<p style='text-align: right'>الرسم البياني لخطة التقاعد</p>", unsafe_allow_html=True)

st.bar_chart(Tamra[['العمر', 'مجموع الاستثمارات']].set_index('العمر'))

st.markdown(f"<p style='text-align: right'>المبلغ المراد جمعه عند سن التقاعد:<br> {top:,.2f} SAR</p>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: right'>السنوات المتبقية حتى سن التقاعد<br>{years_to_retirement}</p>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: right'>العائد التراكمي المتوقع<br>{rate*100:,.2f} %</p>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: right'>لتحقيق الهدف يجب الاستثمار الشهري بمبلغ<br>{recommended_contribution/12:,.2f} SAR</p>", unsafe_allow_html=True)

blue_line = ("""
        <style>
            @keyframes fadeInOut {
                0% {
                    opacity: 0;
                }
                50% {
                    opacity: 1;
                }
                100% {
                    opacity: 0;
                }
            }
            
            hr.customHR {
                border: none;
                border-top: 2px solid #335575;
                box-shadow: 2px 2px 5px rgba(0, 0, 0, 0.2);
                animation: fadeInOut 5s ease-in-out infinite;
            }
        </style>
        <hr class="customHR">
    """)
st.markdown(blue_line, unsafe_allow_html=True)

Tamra = Tamra[ Tamra['العمر']>= retirement_age]
with st.expander("جدول الراتب السنوي المستقطع من استثماراتك عند التقاعد🎓✨"):
                st.markdown(
                    """
                    <p style='text-align: right;'>
                        راتبك السنوي عند التقاعد<br>
                        <br>
                        الرسم البياني المبلغ السنوي الذي ستقوم بسحبه من محفظتك الاستثمارية<br>
                        <br>
                        المبلغ يرتفع سنويا بسبب التضخم بالتالي يصبح راتبك متغيرا ودائما في ارتفاع بسبب نمو استثماراتك بمعدل يساوي التضخم
                    </p>
                    """,
                    unsafe_allow_html=True
                )
                st.bar_chart(Tamra[['العمر', 'راتب التقاعد السنوي']].set_index('العمر'))

with st.expander("الشركات الاستثمارية التي تقدم لك محفظة استثمارية تساهم في تحقيق خطة التقاعد"):
    st.markdown(
        """
       <p style='text-align: right;'>
        <a href='https://tamracapital.sa' target='_blank'>تمرة المالية</a><br>
        <a href='https://drahim.sa' target='_blank'>دراهم</a><br>
        <a href='https://abyancapital.sa' target='_blank'>ابيان المالية</a><br>
        <a href='https://www.malaa.tech' target='_blank'>ملاءة</a>
        </p>
        """,
        unsafe_allow_html=True
    )



from streamlit_extras.buy_me_a_coffee import button
button(username="rayan3rab7", floating=False, width=221)
