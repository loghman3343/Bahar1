
import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="پنل هوشمند بهار ۱", layout="wide")

# استایل‌دهی
st.markdown("""<style> .stButton>button {width:100%; border-radius:10px; background-color:#17a2b8; color:white;} </style>""", unsafe_allow_html=True)

if "logged_in" not in st.session_state: st.session_state.logged_in = False
if "members" not in st.session_state: st.session_state.members = {} 

if not st.session_state.logged_in:
    st.title("🔑 ورود به سامانه")
    u = st.text_input("نام کاربری")
    p = st.text_input("رمز عبور", type="password")
    if st.button("ورود"):
        if u == "admin" and p == "1234":
            st.session_state.logged_in = True
            st.rerun()
else:
    st.title("🗓️ سامانه هوشمند بهار ۱ (نسخه ارتقا یافته)")
    
    t1, t2, t3 = st.tabs(["👥 تعریف پرسنل", "🏖️ مرخصی", "🚀 چیدمان هوشمند"])

    with t1:
        col1, col2 = st.columns([2, 1])
        name = col1.text_input("نام همکار:")
        gender = col2.selectbox("جنسیت:", ["خانم", "آقا"])
        if st.button("➕ افزودن به لیست"):
            if name and name not in st.session_state.members:
                st.session_state.members[name] = {"gender": gender, "offs": []}
                st.success(f"{name} ({gender}) اضافه شد")
        
        if st.session_state.members:
            st.write("لیست پرسنل:")
            display_df = pd.DataFrame([{"نام": k, "جنسیت": v["gender"]} for k, v in st.session_state.members.items()])
            st.table(display_df)

    with t2:
        if st.session_state.members:
            person = st.selectbox("انتخاب فرد برای مرخصی:", list(st.session_state.members.keys()))
            day_off = st.number_input("روز ماه:", 1, 31)
            if st.button("🚫 ثبت مرخصی"):
                st.session_state.members[person]["offs"].append(day_off)
                st.info(f"مرخصی {person} ثبت شد")
        else: st.info("لیست پرسنل خالی است")

    with t3:
        days = st.number_input("تعداد روزهای ماه:", 1, 31, 30)
        if st.button("🔥 اجرای چیدمان با رعایت استراحت"):
            if len(st.session_state.members) < 4:
                st.error("برای رعایت قانون استراحت، حداقل به ۴ یا ۵ نفر نیرو نیاز دارید")
            else:
                schedule = []
                last_night_shift = [] # لیست کسانی که دیشب شب‌کار بودند
                
                for d in range(1, days + 1):
                    # ۱. فیلتر مرخصی و ۲. فیلتر استراحت بعد از شب‌کاری
                    available = [n for n in st.session_state.members if d not in st.session_state.members[n]["offs"] and n not in last_night_shift]
                    
                    if len(available) < 3:
                        schedule.append([f"روز {d}", "❌ کمبود نیرو", "❌ کمبود نیرو", "❌ کمبود نیرو"])
                        last_night_shift = [] # ریست برای روز بعد
                    else:
                        chosen = random.sample(available, 3)
                        
                        # نمایش نام با جنسیت در جدول
                        s_names = [f"{c} ({st.session_state.members[c]['gender']})" for c in chosen]
                        schedule.append([f"روز {d}", s_names[0], s_names[1], s_names[2]])
                        
                        # نفر سوم (شب‌کار) برای روز بعد در لیست استراحت قرار می‌گیرد
                        last_night_shift = [chosen[2]]
                
                df_final = pd.DataFrame(schedule, columns=["تاریخ", "صبح", "عصر", "شب"])
                st.table(df_final)
                
                csv = df_final.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 دانلود خروجی نهایی", csv, "bahar_plan.csv", "text/csv")
