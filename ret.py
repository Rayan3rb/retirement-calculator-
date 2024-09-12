# Retirement Calculator
import streamlit as st
import pandas as pd
import numpy as np

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

# Streamlit App
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Amiri&display=swap');

    .title {
        font-family: 'Amiri', serif;
        text-align: center;
    }
    </style>
    <div class="title">
        <p><strong>حاسبة التخطيط للتقاعد </strong></p>
    </div>
    """, unsafe_allow_html=True)
# Sidebar input fields with sliders
age = st.sidebar.slider("العمر", min_value=16, max_value=80, value=21)
retirement_age = st.sidebar.slider("تبي تتقاعد بأي عمر؟", min_value=50, max_value=65, value=65)
initial_payment = st.sidebar.slider("كم عندك مبلغ ودك تبدأ فيه؟", min_value=500, max_value=500000, value=10000, step=500)
retirement_income = st.sidebar.slider("كم راتب الشهري الي يكفيك عند التقاعد؟", min_value=8000, max_value=100000, value=20000, step=1000)*12

gosi = st.sidebar.slider("كم تتوقع التأمينات الاجتماعية بتعطيك معاش تقاعد شهريا؟", min_value=0, max_value=50000, value=0, step=1000)
st.sidebar.markdown(
    """
    <div class="title">
        <a href='https://www.gosi.gov.sa/ar/PensionCalculator' target='_blank'>المؤسسة العامة للتأمينات الاجتماعية: حاسبة المعاش</a>
    </div>
    """, 
    unsafe_allow_html=True
)

st.sidebar.markdown(blue_line, unsafe_allow_html=True)




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


st.bar_chart(Tamra[['العمر', 'مجموع الاستثمارات']].set_index('العمر'))

st.markdown(
    f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Amiri&display=swap');

        .tt th , .tt {{
            font-family: 'Amiri', serif;
            text-align: center;
            color: #333;
        }}

        .tt td, .tt th {{
            border: 2px 
            padding: 8px; /* Padding for cell content */
            border-radius: 10px; /* Rounded corners */
        }}

        table.tt {{
            width: 100%;
            border-collapse: separate; /* Ensures cells can have rounded corners */
            border-spacing: 0; /* Optional: removes space between cells */
            box-shadow: 0 4px 8px rgba(0,0,0,0.1); /* Subtle shadow around the table */
            margin-bottom: 10px; /* Space below the table */
        }}
    </style>

    <div class="tt">
        <table class="tt">
            <tr>
                <td>المبلغ المراد جمعه عند سن التقاعد<br><b>{top:,.0f} SAR</b></td>
                <td>السنوات المتبقية حتى سن التقاعد<br><b>{years_to_retirement}</b></td>
            </tr>
            <tr>
                <td>العائد التراكمي المتوقع<br><b>{rate*100:,.1f} %</b></td>
                <td>لتحقيق الهدف استثمر شهريا بمبلغ<br><b>{recommended_contribution/12:,.2f} SAR</b></td>
            </tr>
        </table>
    </div>
    """,
    unsafe_allow_html=True
)


st.markdown(blue_line, unsafe_allow_html=True)

Tamra = Tamra[ Tamra['العمر']>= retirement_age]
with st.expander("شرح خطة التقاعد🎓✨"):
                st.markdown(
                    f"""
                    <div class="intro" style="direction: rtl;">
                        <p>
                            بناء على خطتك للتقاعد، انت ترغب ان تقدم لنفسك راتبا شهريا من استثماراتك يساوي {retirement_income/12:,.0f}.
                            <br><br>
                            قمنا بوضع التضخم في الاعتبار بالتالي يصبح الراتب الشهري المناسب لك عند التقاعد {Tamra['راتب التقاعد السنوي'].iloc[0]/12:,.0f}.
                            <br><br>
                            لذلك عند سن التقاعد قم بسحب {Tamra['راتب التقاعد السنوي'].iloc[0]:,.0f} من محفظتك الاستثمارية وقم بتقسيمها على 12 شهر.
                            <br><br>
                            وكل سنة المبلغ المسحوب سيرتفع بسبب التضخم. الى ان تنفق جميع استثماراتك كمعاش تقاعد الى عمر 85.
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

                st.markdown(
    """
    <div class="title">
        <br><br>
        <p><strong>المبلغ المراد سحبه سنويا لمعاش التقاعد</strong></p>
    </div>
    """,
    unsafe_allow_html=True
)
                st.bar_chart(Tamra[['العمر', 'راتب التقاعد السنوي']].set_index('العمر'))

with st.expander("الشركات الاستثمارية التي تقدم لك محفظة استثمارية تساهم في تحقيق خطة التقاعد"):
        st.markdown(
    """
    <div class="intro">
        <p><a href='https://tamracapital.sa' target='_blank'>تمرة المالية</a><br></p>
        <p><a href='https://drahim.sa' target='_blank'>دراهم</a><br></p>
        <p><a href='https://abyancapital.sa' target='_blank'>ابيان المالية</a><br></p>
        <p><a href='https://www.malaa.tech' target='_blank'>ملاءة</a></p>
    </div>
    """,
    unsafe_allow_html=True
)




from streamlit_extras.buy_me_a_coffee import button
button(username="rayan3rab7", floating=False, width=221)
