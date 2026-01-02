
import streamlit as st
import pandas as pd
import random

st.set_page_config(page_title="مدیریت پیشرفته بهار ۱", layout="wide")

# استایل اختصاصی برای دکمه‌ها و رابط کاربری
st.markdown("""<style> .stButton>button {width:100%; border-radius:12px; height:3em; background-color:#1e3c72; color:white; font-weight:bold;} .stExpander {border: 1px solid #ddd; border-radius: 10px; margin-bottom: 10px;} </style>""", unsafe_allow_html=True)

# --- مدیریت حافظه (Session State) ---
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
else:
    st.title("🏥 سامانه بیمارستانی هوشمند بهار ۱")
    t1, t2, t3, t4, t5 = st.tabs(["👥 مدیریت پرسنل", "🏖️ ثبت مرخصی", "💡 محدودیت روزانه", "🏢 تنظیمات بخش", "🚀 تولید برنامه"])

    # تب ۱: مدیریت پرسنل و آمار
    with t1:
        st.subheader("➕ تعریف نیرو")
        c1, c2 = st.columns(2)
        name = c1.text_input("نام و نام خانوادگی:")
        gender = c2.selectbox("جنسیت:", ["خانم", "آقا"])
        if st.button("ثبت در سیستم"):
            if name and name not in st.session_state.staff:
                st.session_state.staff[name] = {"gender": gender, "offs": [], "day_prefs": {}, "total_shifts": 0}
                st.success(f"«{name}» اضافه شد.")
                st.rerun()
        
        if st.session_state.staff:
            st.subheader("📊 آمار فعالیت پرسنل")
            stats_list = [{"نام": k, "جنسیت": v["gender"], "شیفت‌های ماه": v.get("total_shifts", 0)} for k, v in st.session_state.staff.items()]
            st.table(pd.DataFrame(stats_list))

            with st.expander("🛠️ مدیریت لیست (حذف یا پاک‌سازی)"):
                del_name = st.selectbox("حذف تکی فرد:", [""] + list(st.session_state.staff.keys()))
                if st.button("🗑️ حذف فرد انتخاب شده"):
                    if del_name in st.session_state.staff:
                        del st.session_state.staff[del_name]
                        st.rerun()
                
                st.divider()
                if st.button("🚨 پاک کردن کل اطلاعات (شروع ماه جدید)"):
                    st.session_state.staff = {}
                    st.session_state.final_df = None
                    st.warning("تمام اطلاعات پرسنل، مرخصی‌ها و برنامه‌ها پاک شد.")
                    st.rerun()

    # تب ۲: مرخصی (انتخاب چندتایی روزها)
    with t2:
        st.subheader("🏖️ تعیین روزهای مرخصی")
        if st.session_state.staff:
            p_off = st.selectbox("انتخاب فرد:", list(st.session_state.staff.keys()), key="p_off")
            current_offs = st.session_state.staff[p_off]["offs"]
            days_off = st.multiselect("روزهای عدم حضور (۱-۳۱):", list(range(1, 32)), default=current_offs)
            if st.button("تایید مرخصی‌ها"):
                st.session_state.staff[p_off]["offs"] = days_off
                st.success(f"مرخصی‌های {p_off} ثبت شد.")
        else: st.info("ابتدا پرسنل را تعریف کنید.")

    # تب ۳: محدودیت روزانه (انتخاب دقیق روز و شیفت)
    with t3:
        st.subheader("💡 محدودیت شیفت در روز خاص")
        if st.session_state.staff:
            p_pref = st.selectbox("انتخاب فرد:", list(st.session_state.staff.keys()), key="p_pref")
            target_day = st.selectbox("انتخاب روز مورد نظر:", list(range(1, 32)))
            no_shift = st.multiselect(f"در روز {target_day}، {p_pref} در کدام شیفت نباشد؟", ["صبح", "عصر", "شب"])
            
            if st.button("ثبت این محدودیت"):
                st.session_state.staff[p_pref]["day_prefs"][target_day] = no_shift
                st.success(f"محدودیت اعمال شد.")
            
            if st.session_state.staff[p_pref]["day_prefs"]:
                st.write("محدودیت‌های این فرد:", st.session_state.staff[p_pref]["day_prefs"])
        else: st.info("لیست پرسنل خالی است.")

    # تب ۴: تنظیمات بخش‌ها
    with t4:
        st.subheader("🏢 ظرفیت مورد نیاز بخش‌ها")
        for w_name in list(st.session_state.wards.keys()):
            with st.expander(f"⚙️ تنظیمات {w_name}", expanded=True):
                c1, c2, c3 = st.columns(3)
                st.session_state.wards[w_name]["morn"] = c1.number_input(f"صبح {w_name}", 0, 10, st.session_state.wards[w_name]["morn"], key=f"m_{w_name}")
                st.session_state.wards[w_name]["eve"] = c2.number_input(f"عصر {w_name}", 0, 10, st.session_state.wards[w_name]["eve"], key=f"e_{w_name}")
                st.session_state.wards[w_name]["night"] = c3.number_input(f"شب {w_name}", 0, 10, st.session_state.wards[w_name]["night"], key=f"n_{w_name}")

    # تب ۵: تولید و ویرایش نهایی
    with t5:
        month_days = st.number_input("تعداد روزهای ماه:", 1, 31, 30)
        if st.button("🚀 تولید برنامه هوشمند"):
            # صفر کردن آمار برای محاسبه جدید
            for s in st.session_state.staff: st.session_state.staff[s]["total_shifts"] = 0
            
            all_schedules = []
            last_night_shift = []
            
            for d in range(1, month_days + 1):
                # فیلتر: مرخصی نباشد و دیشب شب‌کار نباشد
                available = [n for n in st.session_state.staff if d not in st.session_state.staff[n]["offs"] and n not in last_night_shift]
                random.shuffle(available)
                
                day_data = {"تاریخ": f"روز {d}"}
                current_night = []

                for ward, req in st.session_state.wards.items():
                    for s_type in ["صبح", "عصر", "شب"]:
                        needed = req[{"صبح": "morn", "عصر": "eve", "شب": "night"}[s_type]]
                        chosen_names = []
                        for _ in range(needed):
                            # چک کردن محدودیت روزانه
                            eligible = [a for a in available if s_type not in st.session_state.staff[a]["day_prefs"].get(d, [])]
                            if eligible:
                                p = eligible[0]
                                sex = "خ" if st.session_state.staff[p]['gender'] == "خانم" else "آ"
                                chosen_names.append(f"{p} ({sex})")
                                available.remove(p)
                                st.session_state.staff[p]["total_shifts"] += 1
                                if s_type == "شب": current_night.append(p)
                            else: chosen_names.append("⚠️ کمبود")
                        day_data[f"{ward}-{s_type}"] = " / ".join(chosen_names)
                
                all_schedules.append(day_data)
                last_night_shift = current_night

            st.session_state.final_df = pd.DataFrame(all_schedules)

        if st.session_state.final_df is not None:
            st.subheader("✍️ مشاهده و ویرایش برنامه")
            edited_df = st.data_editor(st.session_state.final_df, use_container_width=True)
            st.download_button("📥 دانلود اکسل برنامه نهایی", edited_df.to_csv(index=False).encode('utf-8-sig'), "Hospital_Plan.csv", "text/csv")
