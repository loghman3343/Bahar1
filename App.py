
import streamlit as st
import pandas as pd
import random

# تنظیمات اصلی صفحه
st.set_page_config(page_title="مدیریت هوشمند بهار ۱", layout="wide")

# استایل اختصاصی برای ظاهر پیشرفته
st.markdown("""
<style>
.main { background-color: #f0f2f6; }
.stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #1e3c72; color: white; }
.reportview-container .main .block-container { padding-top: 2rem; }
</style>
""", unsafe_allow_html=True)

# --- مدیریت حافظه (Session State) ---
if "login" not in st.session_state: st.session_state.login = False
if "staff" not in st.session_state: st.session_state.staff = {}
if "wards" not in st.session_state:
    st.session_state.wards = {
        "تریاژ": {"morn": 2, "eve": 2, "night": 2},
        "سرم تراپی": {"morn": 1, "eve": 1, "night": 2},
    }
if "final_df" not in st.session_state: st.session_state.final_df = None

# ================== ورود به سیستم ==================
if not st.session_state.login:
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.title("🔐 ورود به سامانه بهار ۱")
        u = st.text_input("نام کاربری")
        p = st.text_input("رمز عبور", type="password")
        if st.button("ورود"):
            if u == "admin" and p == "1234":
                st.session_state.login = True
                st.rerun()
            else: st.error("نام کاربری یا رمز عبور اشتباه است.")
else:
    # هدر برنامه
    h_col1, h_col2 = st.columns([4,1])
    h_col1.title("🏥 سامانه برنامه‌ریزی هوشمند")
    if h_col2.button("خروج 🚪"):
        st.session_state.login = False
        st.rerun()

    # نمایش آمار سریع (Metrics)
    m1, m2, m3 = st.columns(3)
    m1.metric("تعداد کل پرسنل", len(st.session_state.staff))
    m2.metric("بخش‌های فعال", len(st.session_state.wards))
    m3.metric("درخواست‌های ثبت شده", sum(len(v["day_prefs"]) for v in st.session_state.staff.values()))

    # --- ایجاد تب‌های پیشرفته ---
    t1, t2, t3, t4, t5 = st.tabs(["👥 مدیریت پرسنل", "🏖️ ثبت مرخصی", "💡 محدودیت روزانه", "⚙️ تنظیم بخش‌ها", "🚀 تولید برنامه"])

    with t1:
        st.subheader("➕ افزودن پرسنل جدید")
        col_n, col_g, col_b = st.columns([3, 2, 1])
        new_name = col_n.text_input("نام و نام خانوادگی:")
        new_gen = col_g.selectbox("جنسیت:", ["خانم", "آقا"])
        if col_b.button("ثبت"):
            if new_name:
                st.session_state.staff[new_name] = {"gender": new_gen, "offs": [], "day_prefs": {}, "total_shifts": 0}
                st.success(f"{new_name} اضافه شد.")
                st.rerun()
        
        if st.session_state.staff:
            st.divider()
            df_staff = pd.DataFrame([{"نام": k, "جنسیت": v["gender"], "شیفت‌های ماه": v["total_shifts"]} for k, v in st.session_state.staff.items()])
            st.dataframe(df_staff, use_container_width=True)
            
            del_target = st.selectbox("حذف فرد:", [""] + list(st.session_state.staff.keys()))
            if st.button("🗑️ حذف قطعی"):
                if del_target:
                    del st.session_state.staff[del_target]
                    st.rerun()

    with t2:
        st.subheader("🏖️ ثبت روزهای مرخصی")
        if st.session_state.staff:
            p_off = st.selectbox("انتخاب فرد:", list(st.session_state.staff.keys()), key="p_off")
            current_offs = st.session_state.staff[p_off]["offs"]
            offs = st.multiselect("روزهایی که مرخصی است را انتخاب کنید:", range(1, 32), default=current_offs)
            if st.button("ذخیره مرخصی‌ها"):
                st.session_state.staff[p_off]["offs"] = offs
                st.success("مرخصی‌ها با موفقیت ثبت شد.")
        else: st.info("ابتدا پرسنل را اضافه کنید.")

    with t3:
        st.subheader("💡 محدودیت شیفت در روز خاص")
        if st.session_state.staff:
            p_pref = st.selectbox("انتخاب فرد:", list(st.session_state.staff.keys()), key="p_pref")
            d_pref = st.selectbox("کدام روز ماه؟", range(1, 32))
            s_pref = st.multiselect("در این شیفت‌ها نباشد:", ["صبح", "عصر", "شب"])
            if st.button("ثبت محدودیت"):
                st.session_state.staff[p_pref]["day_prefs"][d_pref] = s_pref
                st.toast(f"محدودیت برای {p_pref} ثبت شد.")
            
            # نمایش محدودیت‌های ثبت شده
            if st.session_state.staff[p_pref]["day_prefs"]:
                st.write("محدودیت‌های این فرد:", st.session_state.staff[p_pref]["day_prefs"])
        else: st.info("پرسنلی ثبت نشده است.")

    with t4:
        st.subheader("⚙️ تنظیم ظرفیت بخش‌ها")
        for w, cfg in st.session_state.wards.items():
            with st.expander(f"تنظیمات {w}", expanded=True):
                c1, c2, c3 = st.columns(3)
                st.session_state.wards[w]["morn"] = c1.number_input(f"صبح {w}", 0, 10, cfg["morn"], key=w+"m")
                st.session_state.wards[w]["eve"] = c2.number_input(f"عصر {w}", 0, 10, cfg["eve"], key=w+"e")
                st.session_state.wards[w]["night"] = c3.number_input(f"شب {w}", 0, 10, cfg["night"], key=w+"n")

    with t5:
        st.subheader("📅 تولید برنامه نهایی")
        total_days = st.number_input("تعداد روزهای برنامه:", 1, 31, 30)
        
        if st.button("🚀 شروع چیدمان هوشمند"):
            # ریست کردن آمار شیفت‌ها قبل از شروع
            for s in st.session_state.staff.values(): s["total_shifts"] = 0
            
            final_rows = []
            last_night_staff = []

            for d in range(1, total_days + 1):
                day_data = {"تاریخ": f"روز {d}"}
                # فیلتر کردن افراد در دسترس (مرخصی نباشند و دیشب شبکار نباشند)
                available = [n for n, v in st.session_state.staff.items() if d not in v["offs"] and n not in last_night_staff]
                random.shuffle(available)
                
                today_nights = []
                for ward, req in st.session_state.wards.items():
                    for s_type in ["صبح", "عصر", "شب"]:
                        needed = req[{"صبح": "morn", "عصر": "eve", "شب": "night"}[s_type]]
                        chosen = []
                        for _ in range(needed):
                            # چک کردن محدودیت روزانه (مهم)
                            eligible = [a for a in available if s_type not in st.session_state.staff[a]["day_prefs"].get(d, [])]
                            if eligible:
                                # انتخاب عادلانه‌تر (کسی که شیفت کمتری داشته)
                                eligible.sort(key=lambda x: st.session_state.staff[x]["total_shifts"])
                                pick = eligible[0]
                                sex = "خ" if st.session_state.staff[pick]["gender"] == "خانم" else "آ"
                                chosen.append(f"{pick} ({sex})")
                                available.remove(pick)
                                st.session_state.staff[pick]["total_shifts"] += 1
                                if s_type == "شب": today_nights.append(pick)
                            else:
                                chosen.append("⚠️ کمبود نیرو")
                        day_data[f"{ward}-{s_type}"] = " / ".join(chosen)
                
                final_rows.append(day_data)
                last_night_staff = today_nights

            st.session_state.final_df = pd.DataFrame(final_rows)
            st.balloons()

        if st.session_state.final_df is not None:
            st.data_editor(st.session_state.final_df, use_container_width=True)
            csv_data = st.session_state.final_df.to_csv(index=False).encode('utf-8-sig')
            st.download_button("📥 دانلود فایل اکسل برنامه", csv_data, "Bahar1_Schedule.csv", "text/csv")
