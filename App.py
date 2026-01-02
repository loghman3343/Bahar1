
import streamlit as st
import pandas as pd
import random

# تنظیمات اصلی صفحه
st.set_page_config(page_title="مدیریت هوشمند بهار ۱", layout="wide")

# استایل اختصاصی برای تمیز کردن ظاهر تنظیمات
st.markdown("""
<style>
.main { background-color: #f8f9fa; }
.stButton>button { border-radius: 8px; height: 3em; background-color: #1e3c72; color: white; font-weight: bold; }
.ward-card { border: 2px solid #1e3c72; border-radius: 15px; padding: 20px; background-color: white; margin-bottom: 25px; }
.shift-header { color: #1e3c72; border-bottom: 1px solid #ddd; padding-bottom: 5px; margin-bottom: 10px; font-weight: bold; }
.ward-header { background-color: #1e3c72; color: white; padding: 12px; border-radius: 8px; text-align: center; margin-top: 20px; }
</style>
""", unsafe_allow_html=True)

# --- مدیریت حافظه (Session State) ---
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
        if st.button("ورود"):
            if u == "admin" and p == "1234":
                st.session_state.login = True
                st.rerun()
else:
    h1, h2 = st.columns([4,1])
    h1.title("🏥 پنل مدیریت هوشمند شیفت‌بندی")
    if h2.button("خروج"):
        st.session_state.login = False
        st.rerun()

    t1, t2, t3, t4, t5 = st.tabs(["👥 پرسنل", "🏖️ مرخصی", "💡 محدودیت‌ها", "⚙️ تنظیمات بخش‌ها", "🚀 تولید برنامه"])

    # --- تب پرسنل ---
    with t1:
        st.subheader("افزودن همکار جدید")
        cn, cg, cb = st.columns([3, 2, 1])
        name = cn.text_input("نام و نام خانوادگی:")
        gender = cg.selectbox("جنسیت:", ["خانم", "آقا"])
        if cb.button("ثبت نام"):
            if name:
                st.session_state.staff[name] = {"gender": gender, "offs": [], "day_prefs": {}, "total_shifts": 0}
                st.rerun()
        if st.session_state.staff:
            st.table(pd.DataFrame([{"نام": k, "جنسیت": v["gender"]} for k, v in st.session_state.staff.items()]))

    # --- تب مرخصی ---
    with t2:
        if st.session_state.staff:
            p = st.selectbox("انتخاب فرد:", list(st.session_state.staff.keys()))
            offs = st.multiselect("روزهای مرخصی:", range(1, 32), default=st.session_state.staff[p]["offs"])
            if st.button("ذخیره مرخصی"):
                st.session_state.staff[p]["offs"] = offs
                st.success("ثبت شد")

    # --- تب محدودیت ---
    with t3:
        if st.session_state.staff:
            p = st.selectbox("نام همکار:", list(st.session_state.staff.keys()), key="pref_p")
            d = st.selectbox("روز:", range(1, 32))
            s = st.multiselect("در این شیفت نباشد:", ["صبح", "عصر", "شب"])
            if st.button("ثبت محدودیت"):
                st.session_state.staff[p]["day_prefs"][d] = s
                st.success("اعمال شد")

    # --- تب تنظیمات بخش‌ها (نسخه اصلاح شده و تمیز) ---
    with t4:
        st.subheader("🏢 مدیریت و پیکربندی بخش‌ها")
        cw1, cw2 = st.columns([3, 1])
        new_w = cw1.text_input("نام بخش جدید را وارد کنید:")
        if cw2.button("➕ ایجاد بخش"):
            if new_w and new_w not in st.session_state.wards:
                st.session_state.wards[new_w] = {
                    "morn_f": 0, "morn_m": 0, "eve_f": 0, "eve_m": 0, "night_f": 0, "night_m": 0
                }
                st.rerun()

        st.divider()

        for w, cfg in list(st.session_state.wards.items()):
            st.markdown(f"<div class='ward-card'>", unsafe_allow_html=True)
            st.subheader(f"📍 تنظیمات اختصاصی بخش: {w}")
            
            # ردیف صبح
            st.markdown("<div class='shift-header'>☀️ شیفت صبح</div>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            cfg["morn_f"] = c1.number_input(f"تعداد خانم (صبح) - {w}", 0, 10, cfg["morn_f"])
            cfg["morn_m"] = c2.number_input(f"تعداد آقا (صبح) - {w}", 0, 10, cfg["morn_m"])
            
            # ردیف عصر
            st.markdown("<div class='shift-header'>🌆 شیفت عصر</div>", unsafe_allow_html=True)
            c3, c4 = st.columns(2)
            cfg["eve_f"] = c3.number_input(f"تعداد خانم (عصر) - {w}", 0, 10, cfg["eve_f"])
            cfg["eve_m"] = c4.number_input(f"تعداد آقا (عصر) - {w}", 0, 10, cfg["eve_m"])
            
            # ردیف شب
            st.markdown("<div class='shift-header'>🌙 شیفت شب</div>", unsafe_allow_html=True)
            c5, c6 = st.columns(2)
            cfg["night_f"] = c5.number_input(f"تعداد خانم (شب) - {w}", 0, 10, cfg["night_f"])
            cfg["night_m"] = c6.number_input(f"تعداد آقا (شب) - {w}", 0, 10, cfg["night_m"])
            
            if st.button(f"🗑️ حذف کل بخش {w}", key=f"del_{w}"):
                del st.session_state.wards[w]
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    # --- تب تولید برنامه ---
    with t5:
        st.subheader("🚀 خروجی نهایی")
        days = st.number_input("تعداد روز:", 1, 31, 30)
        
        if st.button("🔥 شروع چیدمان"):
            for s in st.session_state.staff.values(): s["total_shifts"] = 0
            temp_schedules = {w: [] for w in st.session_state.wards}
            last_night = []

            for d in range(1, days + 1):
                avail = [n for n, v in st.session_state.staff.items() if d not in v["offs"] and n not in last_night]
                random.shuffle(avail)
                tonight = []

                for w, req in st.session_state.wards.items():
                    day_info = {"تاریخ": f"روز {d}"}
                    for s_type in ["صبح", "عصر", "شب"]:
                        s_key = 'morn' if s_type=='صبح' else 'eve' if s_type=='عصر' else 'night'
                        f_needed = req[f"{s_key}_f"]
                        m_needed = req[f"{s_key}_m"]
                        
                        chosen = []
                        for g_type, count in [("خانم", f_needed), ("آقا", m_needed)]:
                            for _ in range(count):
                                elig = [a for a in avail if st.session_state.staff[a]["gender"] == g_type and s_type not in st.session_state.staff[a]["day_prefs"].get(d, [])]
                                if elig:
                                    elig.sort(key=lambda x: st.session_state.staff[x]["total_shifts"])
                                    p = elig[0]; chosen.append(p); avail.remove(p); st.session_state.staff[p]["total_shifts"] += 1
                                    if s_type == "شب": tonight.append(p)
                                else: chosen.append("⚠️ کمبود")
                        day_info[s_type] = " / ".join(chosen)
                    temp_schedules[w].append(day_info)
                last_night = tonight

            st.session_state.final_schedules = {w: pd.DataFrame(data) for w, data in temp_schedules.items()}
            st.balloons()

        for w, df in st.session_state.final_schedules.items():
            st.markdown(f"<div class='ward-header'>📋 برنامه بخش: {w}</div>", unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True)
            st.download_button(f"📥 دانلود اکسل {w}", df.to_csv(index=False).encode('utf-8-sig'), f"Plan_{w}.csv")
