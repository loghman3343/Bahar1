
import streamlit as st
import pandas as pd
import random

# تنظیمات اصلی صفحه
st.set_page_config(page_title="مدیریت بهار ۱", layout="wide")

# استایل اختصاصی برای زیباسازی کارت‌های تنظیمات
st.markdown("""
<style>
.main { background-color: #f4f7f9; }
.stButton>button { border-radius: 8px; background-color: #1e3c72; color: white; font-weight: bold; }
.setup-card { 
    background-color: white; 
    padding: 20px; 
    border-radius: 15px; 
    border-right: 8px solid #1e3c72;
    box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}
.shift-label { color: #1e3c72; font-weight: bold; font-size: 16px; margin-bottom: 5px; }
.ward-title { color: #1e3c72; font-size: 22px; font-weight: bold; margin-bottom: 15px; border-bottom: 2px solid #eee; }
</style>
""", unsafe_allow_html=True)

# --- مدیریت حافظه ---
if "login" not in st.session_state: st.session_state.login = False
if "staff" not in st.session_state: st.session_state.staff = {}
if "wards" not in st.session_state: st.session_state.wards = {}
if "final_schedules" not in st.session_state: st.session_state.final_schedules = {}

# ================== ورود ==================
if not st.session_state.login:
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.title("🏥 ورود به سامانه بهار ۱")
        u = st.text_input("نام کاربری")
        p = st.text_input("رمز عبور", type="password")
        if st.button("ورود به پنل"):
            if u == "admin" and p == "1234":
                st.session_state.login = True
                st.rerun()
else:
    # هدر اصلی
    st.title("🏥 داشبورد هوشمند چیدمان شیفت")
    if st.sidebar.button("خروج از سیستم 🚪"):
        st.session_state.login = False
        st.rerun()

    # ایجاد تب‌ها - تب اول دقیقاً همان چیزی است که خواستید
    tabs = st.tabs(["🏗️ تنظیمات بخش و پرسنل", "👥 مدیریت اعضا", "📅 تولید و خروجی برنامه"])

    # ---------------------------------------------------------
    # تب اول: انتخاب بخش و تعداد پرسنل و جنسیت (هسته اصلی خواسته شما)
    # ---------------------------------------------------------
    with tabs[0]:
        st.subheader("۱. تعریف بخش و نیازهای شیفت")
        
        with st.container():
            col_add1, col_add2 = st.columns([3, 1])
            new_w = col_add1.text_input("نام بخش جدید (مثلاً: اورژانس، CCU...)", placeholder="نام را اینجا بنویسید...")
            if col_add2.button("➕ افزودن بخش به لیست"):
                if new_w and new_w not in st.session_state.wards:
                    st.session_state.wards[new_w] = {
                        "morn_f": 0, "morn_m": 0, 
                        "eve_f": 0, "eve_m": 0, 
                        "night_f": 0, "night_m": 0
                    }
                    st.rerun()

        st.divider()

        # نمایش کارت‌های تنظیمات برای هر بخش
        if st.session_state.wards:
            for w, cfg in list(st.session_state.wards.items()):
                st.markdown(f"""<div class="setup-card">
                    <div class="ward-title">📍 تنظیمات بخش: {w}</div>
                </div>""", unsafe_allow_html=True)
                
                # طراحی ۳ ردیف برای ۳ شیفت
                # شیفت صبح
                st.markdown("<div class='shift-label'>☀️ شیفت صبح</div>", unsafe_allow_html=True)
                c1, c2 = st.columns(2)
                cfg["morn_f"] = c1.number_input(f"تعداد خانم - صبح ({w})", 0, 20, cfg["morn_f"], key=f"mf_{w}")
                cfg["morn_m"] = c2.number_input(f"تعداد آقا - صبح ({w})", 0, 20, cfg["morn_m"], key=f"mm_{w}")
                
                # شیفت عصر
                st.markdown("<div class='shift-label'>🌆 شیفت عصر</div>", unsafe_allow_html=True)
                c3, c4 = st.columns(2)
                cfg["eve_f"] = c3.number_input(f"تعداد خانم - عصر ({w})", 0, 20, cfg["eve_f"], key=f"ef_{w}")
                cfg["eve_m"] = c4.number_input(f"تعداد آقا - عصر ({w})", 0, 20, cfg["eve_m"], key=f"em_{w}")
                
                # شیفت شب
                st.markdown("<div class='shift-label'>🌙 شیفت شب</div>", unsafe_allow_html=True)
                c5, c6 = st.columns(2)
                cfg["night_f"] = c5.number_input(f"تعداد خانم - شب ({w})", 0, 20, cfg["night_f"], key=f"nf_{w}")
                cfg["night_m"] = c6.number_input(f"تعداد آقا - شب ({w})", 0, 20, cfg["night_m"], key=f"nm_{w}")
                
                if st.button(f"🗑️ حذف بخش {w}", key=f"del_{w}"):
                    del st.session_state.wards[w]
                    st.rerun()
                st.markdown("---")
        else:
            st.info("هنوز بخشی اضافه نکرده‌اید. از کادر بالا نام بخش را وارد کنید.")

    # ---------------------------------------------------------
    # تب دوم: مدیریت پرسنل (نام‌ها و مرخصی‌ها)
    # ---------------------------------------------------------
    with tabs[1]:
        st.subheader("۲. ثبت اطلاعات همکاران")
        col_n, col_g, col_b = st.columns([3, 2, 1])
        n = col_n.text_input("نام و نام خانوادگی:")
        g = col_g.selectbox("جنسیت:", ["خانم", "آقا"])
        if col_b.button("ثبت عضو"):
            if n:
                st.session_state.staff[n] = {"gender": g, "offs": [], "total_shifts": 0}
                st.rerun()
        
        if st.session_state.staff:
            st.divider()
            p_name = st.selectbox("انتخاب فرد برای ثبت مرخصی:", list(st.session_state.staff.keys()))
            offs = st.multiselect("روزهای مرخصی:", range(1, 32), default=st.session_state.staff[p_name]["offs"])
            if st.button("ذخیره مرخصی"):
                st.session_state.staff[p_name]["offs"] = offs
                st.success("انجام شد.")

    # ---------------------------------------------------------
    # تب سوم: تولید و خروجی (تفکیک شده)
    # ---------------------------------------------------------
    with tabs[2]:
        st.subheader("۳. تولید برنامه نهایی بر اساس نیاز هر بخش")
        days = st.number_input("تعداد روز ماه:", 1, 31, 30)
        
        if st.button("🚀 شروع چیدمان هوشمند"):
            if not st.session_state.staff or not st.session_state.wards:
                st.error("ابتدا بخش‌ها و پرسنل را تعریف کنید.")
            else:
                for s in st.session_state.staff.values(): s["total_shifts"] = 0
                temp_scheds = {w: [] for w in st.session_state.wards}
                last_night = []

                for d in range(1, days + 1):
                    avail = [n for n, v in st.session_state.staff.items() if d not in v["offs"] and n not in last_night]
                    random.shuffle(avail)
                    tonight = []

                    for w, req in st.session_state.wards.items():
                        day_data = {"تاریخ": f"روز {d}"}
                        for s_type in ["صبح", "عصر", "شب"]:
                            s_key = 'morn' if s_type=='صبح' else 'eve' if s_type=='عصر' else 'night'
                            f_needed = req[f"{s_key}_f"]
                            m_needed = req[f"{s_key}_m"]
                            
                            chosen = []
                            for g_type, count in [("خانم", f_needed), ("آقا", m_needed)]:
                                for _ in range(count):
                                    elig = [a for a in avail if st.session_state.staff[a]["gender"] == g_type]
                                    if elig:
                                        elig.sort(key=lambda x: st.session_state.staff[x]["total_shifts"])
                                        p = elig[0]; chosen.append(p); avail.remove(p)
                                        st.session_state.staff[p]["total_shifts"] += 1
                                        if s_type == "شب": tonight.append(p)
                                    else: chosen.append("⚠️ کمبود")
                            day_data[s_type] = " / ".join(chosen)
                        temp_scheds[w].append(day_data)
                    last_night = tonight
                
                st.session_state.final_schedules = {w: pd.DataFrame(data) for w, data in temp_scheds.items()}
                st.balloons()

        for w, df in st.session_state.final_schedules.items():
            st.markdown(f"<div class='ward-title'>📋 برنامه نهایی: {w}</div>", unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True)
            st.download_button(f"📥 دانلود فایل اکسل {w}", df.to_csv(index=False).encode('utf-8-sig'), f"Schedule_{w}.csv")
