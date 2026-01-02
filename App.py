import streamlit as st
import pandas as pd
import random

# تنظیمات اصلی برای نمایش بهتر در موبایل
st.set_page_config(page_title="سامانه هوشمند بهار", layout="wide")

# استایل‌دهی اختصاصی برای دکمه‌ها و فونت
st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 10px; height: 3em; background-color: #007BFF; color: white; }
    .stDataFrame { border: 1px solid #ddd; border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# سیستم ورود (Login)
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "staff_list" not in st.session_state:
    st.session_state.staff_list = []

def login_page():
    st.title("🔐 ورود به پنل مدیریت")
    user = st.text_input("نام کاربری (admin)")
    pw = st.text_input("رمز عبور (1234)", type="password")
    if st.button("ورود به سامانه"):
        if user == "admin" and pw == "1234":
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("اطلاعات ورود اشتباه است")

def main_app():
    st.title("🗓️ سامانه مدیریت شیفت بهار")
    
    # استفاده از منوی تب‌بندی شده بزرگ برای موبایل
    tab1, tab2, tab3 = st.tabs(["👥 افزودن نفرات", "🏖️ مرخصی‌ها", "🚀 چیدمان نهایی"])

    with tab1:
        st.subheader("لیست پرسنل")
        new_person = st.text_input("نام همکار را بنویسید:")
        if st.button("➕ اضافه کردن به لیست"):
            if new_person and new_person not in st.session_state.staff_list:
                st.session_state.staff_list.append(new_person)
                st.success(f"{new_person} اضافه شد")
            else:
                st.warning("نام را وارد کنید یا تکراری نباشد")
        
        if st.session_state.staff_list:
            st.write("افراد ثبت شده:")
            for i, p in enumerate(st.session_state.staff_list):
                st.text(f"{i+1}. {p}")
            if st.button("🗑️ پاک کردن کل لیست"):
                st.session_state.staff_list = []
                st.rerun()

    with tab2:
        st.subheader("ثبت محدودیت‌ها")
        if not st.session_state.staff_list:
            st.info("ابتدا در تب اول نفرات را اضافه کنید")
        else:
            st.write("در این بخش می‌توانید روزهایی که افراد مرخصی هستند را (در آپدیت بعدی) مدیریت کنید.")

    with tab3:
        st.subheader("تنظیمات شیفت")
        num_days = st.number_input("تعداد روزهای ماه:", min_value=1, max_value=31, value=30)
        
        if st.button("🎲 تولید هوشمند برنامه"):
            if len(st.session_state.staff_list) < 3:
                st.error("برای چیدن ۳ شیفت، حداقل به ۳ نفر نیرو نیاز دارید!")
            else:
                # منطق چیدمان رندوم عادلانه
                schedule_data = []
                staff = st.session_state.staff_list.copy()
                
                for d in range(1, num_days + 1):
                    random.shuffle(staff)
                    day_shifts = staff[:3] # انتخاب ۳ نفر برای صبح، عصر، شب
                    schedule_data.append([f"روز {d}", day_shifts[0], day_shifts[1], day_shifts[2]])
                
                df = pd.DataFrame(schedule_data, columns=["تاریخ", "صبح", "عصر", "شب"])
                st.success("برنامه با موفقیت چیده شد!")
                st.dataframe(df, use_container_width=True)
                
                # خروجی اکسل
                csv = df.to_csv(index=False).encode('utf-8-sig')
                st.download_button("📥 دانلود فایل اکسل برنامه", csv, "shift.csv", "text/csv")

if not st.session_state.authenticated:
    login_page()
else:
    main_app()
