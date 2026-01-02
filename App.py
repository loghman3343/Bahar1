
import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="مدیریت پیشرفته بیمارستان بهار ۱", layout="wide")

# استایل اختصاصی برای موبایل
st.markdown("""<style> .stButton>button {width:100%; border-radius:12px; height:3em; background-color:#1e3c72; color:white; font-weight:bold;} </style>""", unsafe_allow_html=True)

if "login" not in st.session_state: st.session_state.login = False
if "staff" not in st.session_state: st.session_state.staff = {} 
if "wards" not in st.session_state: st.session_state.wards = {
    "تریاژ": {"morn": 2, "eve": 2, "night": 2},
    "سرم تراپی": {"morn": 1, "eve": 1, "night": 2}
}
if "final_df" not in st.session_state: st.session_state.final_df = None

if not st.session_state.login:
    st.title("🔐 ورود به سیستم")
    u = st.text_input("نام کاربری")
    p = st.text_input("رمز عبور", type="password")
    if st.button("ورود"):
        if u == "admin" and p == "1234":
            st.session_state.login = True
            st.rerun()
        else: st.error("نام کاربری یا رمز عبور اشتباه است")
else:
    st.title("🏥 سامانه بیمارستانی بهار ۱ (نسخه آماری)")
    t1, t2, t3, t4 = st.tabs(["👥 پرسنل و آمار", "🏖️ مرخصی و درخواست", "🏢 تنظیمات بخش‌ها", "🚀 تولید و ویرایش برنامه"])

    # تب ۱: پرسنل و نمایش آمار شیفت‌ها
    with t1:
        st.subheader("تعریف پرسنل")
        c1, c2 = st.columns(2)
        name = c1.text_input("نام:")
        gender = c2.selectbox("جنسیت:", ["خانم", "آقا"])
        if st.button("➕ ثبت فرد"):
            if name:
                st.session_state.staff[name] = {"gender": gender, "offs": [], "prefs": [], "total_shifts": 0}
                st.success(f"{name} اضافه شد")
        
        if st.session_state.staff:
            st.subheader("📊 آمار فعالیت ماهانه")
            stats_data = [{"نام": k, "جنسیت": v["gender"], "تعداد شیفت": v.get("total_shifts", 0)} for k, v in st.session_state.staff.items()]
            st.table(pd.DataFrame(stats_data))
            
            if st.button("🗑️ پاک کردن لیست پرسنل"):
                st.session_state.staff = {}
                st.rerun()

    # تب ۲: مرخصی و اولویت‌ها
    with t2:
        if st.session_state.staff:
            p_sel = st.selectbox("انتخاب فرد:", list(st.session_state.staff.keys()))
            c_off, c_pref = st.columns(2)
            with c_off:
                day_off = st.number_input("روز مرخصی:", 1, 31)
                if st.button("ثبت مرخصی"):
                    st.session_state.staff[p_sel]["offs"].append(day_off)
                    st.success("مرخصی ثبت شد.")
            with c_pref:
                p_type = st.multiselect("محدودیت شیفت (نمی‌تواند باشد):", ["صبح", "عصر", "شب"])
                if st.button("ثبت درخواست"):
                    st.session_state.staff[p_sel]["prefs"] = p_type
                    st.success("درخواست ثبت شد.")

    # تب ۳: مدیریت بخش‌ها
    with t3:
        st.subheader("تنظیم ظرفیت بخش‌ها")
        for w_name, config in st.session_state.wards.items():
            with st.expander(f"تنظیمات {w_name}", expanded=True):
                cc1, cc2, cc3 = st.columns(3)
                st.session_state.wards[w_name]["morn"] = cc1.number_input(f"صبح", 0, 10, config["morn"], key=f"m_{w_name}")
                st.session_state.wards[w_name]["eve"] = cc2.number_input(f"عصر", 0, 10, config["eve"], key=f"e_{w_name}")
                st.session_state.wards[w_name]["night"] = cc3.number_input(f"شب", 0, 10, config["night"], key=f"n_{w_name}")

    # تب ۴: تولید و ویرایش دستی
    with t4:
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
            st.subheader("✍️ ویرایش و دانلود")
            st.info("می‌توانید مستقیماً نام‌ها را در جدول زیر تغییر دهید.")
            edited_df = st.data_editor(st.session_state.final_df, use_container_width=True)
            
            csv = edited_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 دانلود اکسل برنامه نهایی", csv, "Bahar_Hospital_Plan.csv", "text/csv")
