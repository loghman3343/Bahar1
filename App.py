
import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="مدیریت پیشرفته بهار ۱", layout="wide")

# استایل اختصاصی برای دکمه‌ها
st.markdown("""<style> .stButton>button {width:100%; border-radius:12px; height:3em; background-color:#1e3c72; color:white; font-weight:bold;} </style>""", unsafe_allow_html=True)

# --- مدیریت حافظه برنامه برای جلوگیری از پاک شدن داده‌ها ---
if "login" not in st.session_state: st.session_state.login = False
if "staff" not in st.session_state: st.session_state.staff = {} 
if "wards" not in st.session_state: st.session_state.wards = {
    "تریاژ": {"morn": 2, "eve": 2, "night": 2},
    "سرم تراپی": {"morn": 1, "eve": 1, "night": 2}
}
if "final_df" not in st.session_state: st.session_state.final_df = None

# --- صفحه ورود ---
if not st.session_state.login:
    st.title("🔐 ورود به سیستم")
    u = st.text_input("نام کاربری")
    p = st.text_input("رمز عبور", type="password")
    if st.button("ورود"):
        if u == "admin" and p == "1234":
            st.session_state.login = True
            st.rerun()
        else: st.error("نام کاربری یا رمز عبور اشتباه است")

# --- پنل اصلی مدیریت ---
else:
    st.title("🏥 سامانه بیمارستانی بهار ۱")
    t1, t2, t3, t4, t5 = st.tabs(["👥 پرسنل و آمار", "🏖️ ثبت مرخصی", "💡 ثبت درخواست", "🏢 تنظیمات بخش‌ها", "🚀 تولید برنامه"])

    # تب ۱: پرسنل و آمار
    with t1:
        st.subheader("تعریف پرسنل")
        c1, c2 = st.columns(2)
        name = c1.text_input("نام:")
        gender = c2.selectbox("جنسیت:", ["خانم", "آقا"])
        if st.button("➕ ثبت فرد"):
            if name and name not in st.session_state.staff:
                st.session_state.staff[name] = {"gender": gender, "offs": [], "prefs": [], "total_shifts": 0}
                st.success(f"{name} اضافه شد")
                st.rerun()
        
        if st.session_state.staff:
            st.subheader("📊 آمار فعالیت")
            stats_list = [{"نام": k, "جنسیت": v["gender"], "تعداد شیفت": v.get("total_shifts", 0)} for k, v in st.session_state.staff.items()]
            st.table(pd.DataFrame(stats_list))
            
            del_name = st.selectbox("انتخاب فرد برای حذف:", [""] + list(st.session_state.staff.keys()))
            if st.button("🗑️ حذف پرسنل"):
                if del_name in st.session_state.staff:
                    del st.session_state.staff[del_name]
                    st.rerun()

    # تب ۲: ثبت مرخصی
    with t2:
        st.subheader("🏖️ ثبت روزهای مرخصی")
        if st.session_state.staff:
            p_off = st.selectbox("نام پرسنل:", list(st.session_state.staff.keys()), key="p_off_box")
            d_off = st.number_input("روز ماه (۱-۳۱):", 1, 31, key="d_off_box")
            if st.button("🚫 ثبت مرخصی"):
                if d_off not in st.session_state.staff[p_off]["offs"]:
                    st.session_state.staff[p_off]["offs"].append(d_off)
                    st.success(f"مرخصی {p_off} ثبت شد.")
            st.write("لیست مرخصی‌های این فرد:", st.session_state.staff[p_off]["offs"])
        else: st.info("لیست پرسنل خالی است.")

    # تب ۳: درخواست‌های خاص
    with t3:
        st.subheader("💡 محدودیت شیفت (مثلاً عصر نباشم)")
        if st.session_state.staff:
            p_pref = st.selectbox("نام پرسنل:", list(st.session_state.staff.keys()), key="p_pref_box")
            prefs = st.multiselect("در این شیفت‌ها نمی‌توانم باشم:", ["صبح", "عصر", "شب"])
            if st.button("💾 ثبت درخواست"):
                st.session_state.staff[p_pref]["prefs"] = prefs
                st.success("درخواست با موفقیت ثبت شد.")
        else: st.info("پرسنلی تعریف نشده است.")

    # تب ۴: تنظیمات بخش‌ها
    with t4:
        st.subheader("🏢 تنظیم ظرفیت هر بخش")
        for w_name, config in st.session_state.wards.items():
            with st.expander(f"تنظیمات {w_name}", expanded=True):
                cc1, cc2, cc3 = st.columns(3)
                st.session_state.wards[w_name]["morn"] = cc1.number_input(f"صبح", 0, 10, config["morn"], key=f"m_{w_name}")
                st.session_state.wards[w_name]["eve"] = cc2.number_input(f"عصر", 0, 10, config["eve"], key=f"e_{w_name}")
                st.session_state.wards[w_name]["night"] = cc3.number_input(f"شب", 0, 10, config["night"], key=f"n_{w_name}")

    # تب ۵: تولید و ویرایش نهایی
    with t5:
        days = st.number_input("تعداد روزها:", 1, 31, 30)
        if st.button("🔥 تولید برنامه هوشمند"):
            for s in st.session_state.staff: st.session_state.staff[s]["total_shifts"] = 0
            
            last_night_shift = []
            all_schedules = []

            for d in range(1, days + 1):
                available = [n for n in st.session_state.staff if d not in st.session_state.staff[n]["offs"] and n not in last_night_shift]
                random.shuffle(available)
                
                day_data = {"تاریخ": f"روز {d}"}
                current_night = []

                for ward, req in st.session_state.wards.items():
                    for s_type in ["صبح", "عصر", "شب"]:
                        needed = req[{"صبح": "morn", "عصر": "eve", "شب": "night"}[s_type]]
                        chosen_list = []
                        for _ in range(needed):
                            eligible = [a for a in available if s_type not in st.session_state.staff[a]["prefs"]]
                            if eligible:
                                pick = eligible[0]
                                sex = "خ" if st.session_state.staff[pick]['gender'] == "خانم" else "آ"
                                chosen_list.append(f"{pick} ({sex})")
                                available.remove(pick)
                                st.session_state.staff[pick]["total_shifts"] += 1
                                if s_type == "شب": current_night.append(pick)
                            else: chosen_list.append("⚠️ کمبود")
                        day_data[f"{ward}-{s_type}"] = " / ".join(chosen_list)
                
                all_schedules.append(day_data)
                last_night_shift = current_night

            st.session_state.final_df = pd.DataFrame(all_schedules)

        if st.session_state.final_df is not None:
            st.subheader("✍️ ویرایش و دانلود نهایی")
            edited_df = st.data_editor(st.session_state.final_df, use_container_width=True)
            csv = edited_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 دانلود اکسل برنامه", csv, "Bahar_Hospital_Plan.csv", "text/csv")
