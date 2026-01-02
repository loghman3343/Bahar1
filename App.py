
import streamlit as st
import pandas as pd
import random

# تنظیمات اصلی صفحه
st.set_page_config(page_title="مدیریت هوشمند بهار ۱", layout="wide")

# استایل اختصاصی برای ظاهر حرفه‌ای و خوانا
st.markdown("""
<style>
.main { background-color: #f0f2f6; }
.stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #1e3c72; color: white; font-weight: bold; }
.ward-header { background-color: #1e3c72; color: white; padding: 12px; border-radius: 8px; margin-top: 25px; font-size: 20px; text-align: center; }
.stExpander { border: 1px solid #1e3c72; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# --- مدیریت حافظه (Session State) ---
if "login" not in st.session_state: st.session_state.login = False
if "staff" not in st.session_state: st.session_state.staff = {}
if "wards" not in st.session_state: st.session_state.wards = {}
if "final_schedules" not in st.session_state: st.session_state.final_schedules = {}

# ================== سیستم ورود ==================
if not st.session_state.login:
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.title("🔐 ورود به سامانه بهار ۱")
        u = st.text_input("نام کاربری")
        p = st.text_input("رمز عبور", type="password")
        if st.button("ورود به پنل"):
            if u == "admin" and p == "1234":
                st.session_state.login = True
                st.rerun()
            else: st.error("اطلاعات ورود اشتباه است.")
else:
    # هدر اصلی
    h1, h2 = st.columns([4,1])
    h1.title("🏥 سامانه مدیریت و چیدمان هوشمند")
    if h2.button("خروج از سیستم"):
        st.session_state.login = False
        st.rerun()

    # ایجاد تب‌های کاربردی
    t1, t2, t3, t4, t5 = st.tabs(["👥 پرسنل", "🏖️ مرخصی", "💡 محدودیت‌ها", "⚙️ تنظیمات بخش‌ها", "🚀 تولید برنامه"])

    with t1:
        st.subheader("👥 افزودن و مدیریت پرسنل")
        cn, cg, cb = st.columns([3, 2, 1])
        name = cn.text_input("نام و نام خانوادگی:")
        gender = cg.selectbox("جنسیت:", ["خانم", "آقا"])
        if cb.button("ثبت در سیستم"):
            if name:
                st.session_state.staff[name] = {"gender": gender, "offs": [], "day_prefs": {}, "total_shifts": 0}
                st.rerun()
        if st.session_state.staff:
            st.divider()
            df_staff = pd.DataFrame([{"نام": k, "جنسیت": v["gender"], "شیفت‌های ماه": v["total_shifts"]} for k, v in st.session_state.staff.items()])
            st.table(df_staff)
            
            del_target = st.selectbox("حذف فرد:", [""] + list(st.session_state.staff.keys()))
            if st.button("🗑️ حذف"):
                if del_target: del st.session_state.staff[del_target]; st.rerun()

    with t2:
        st.subheader("🏖️ ثبت مرخصی ماهانه")
        if st.session_state.staff:
            p_off = st.selectbox("انتخاب فرد:", list(st.session_state.staff.keys()), key="p_off")
            offs = st.multiselect("روزهای مرخصی (بدون شیفت):", range(1, 32), default=st.session_state.staff[p_off]["offs"])
            if st.button("ذخیره مرخصی"):
                st.session_state.staff[p_off]["offs"] = offs
                st.success(f"مرخصی {p_off} ثبت شد.")
        else: st.warning("ابتدا پرسنل را اضافه کنید.")

    with t3:
        st.subheader("💡 محدودیت‌های درخواستی (مثلاً: عصر نباشم)")
        if st.session_state.staff:
            p_pref = st.selectbox("نام فرد:", list(st.session_state.staff.keys()), key="p_pref")
            d_pref = st.selectbox("کدام روز؟", range(1, 32))
            s_pref = st.multiselect("در این شیفت نباشد:", ["صبح", "عصر", "شب"])
            if st.button("ثبت محدودیت"):
                st.session_state.staff[p_pref]["day_prefs"][d_pref] = s_pref
                st.success("محدودیت اعمال شد.")

    with t4:
        st.subheader("🏢 مدیریت بخش‌ها و نیاز جنسیتی")
        cw1, cw2 = st.columns([3, 1])
        new_ward = cw1.text_input("نام بخش جدید (مثلاً: اورژانس):")
        if cw2.button("➕ افزودن بخش"):
            if new_ward and new_ward not in st.session_state.wards:
                st.session_state.wards[new_ward] = {
                    "morn_f": 1, "morn_m": 1, 
                    "eve_f": 1, "eve_m": 1, 
                    "night_f": 1, "night_m": 1
                }
                st.rerun()
        
        for w, cfg in list(st.session_state.wards.items()):
            with st.expander(f"📍 تنظیمات ظرفیت بخش {w}", expanded=True):
                c1, c2, c3 = st.columns(3)
                with c1:
                    st.write("☀️ **صبح**")
                    cfg["morn_f"] = st.number_input(f"تعداد خانم (صبح) - {w}", 0, 10, cfg["morn_f"])
                    cfg["morn_m"] = st.number_input(f"تعداد آقا (صبح) - {w}", 0, 10, cfg["morn_m"])
                with c2:
                    st.write("🌆 **عصر**")
                    cfg["eve_f"] = st.number_input(f"تعداد خانم (عصر) - {w}", 0, 10, cfg["eve_f"])
                    cfg["eve_m"] = st.number_input(f"تعداد آقا (عصر) - {w}", 0, 10, cfg["eve_m"])
                with c3:
                    st.write("🌙 **شب**")
                    cfg["night_f"] = st.number_input(f"تعداد خانم (شب) - {w}", 0, 10, cfg["night_f"])
                    cfg["night_m"] = st.number_input(f"تعداد آقا (شب) - {w}", 0, 10, cfg["night_m"])
                if st.button(f"🗑️ حذف بخش {w}"):
                    del st.session_state.wards[w]
                    st.rerun()

    with t5:
        st.subheader("🚀 تولید برنامه تفکیکی")
        days_num = st.number_input("تعداد روزهای ماه:", 1, 31, 30)
        
        if st.button("🔥 شروع چیدمان هوشمند و عادلانه"):
            if not st.session_state.staff or not st.session_state.wards:
                st.error("لطفاً ابتدا پرسنل و بخش‌ها را تنظیم کنید.")
            else:
                for s in st.session_state.staff.values(): s["total_shifts"] = 0
                temp_results = {w: [] for w in st.session_state.wards}
                last_night_staff = []

                for d in range(1, days_num + 1):
                    # لیست افراد در دسترس (مرخصی نباشند و دیشب شبکار نباشند)
                    avail = [n for n, v in st.session_state.staff.items() if d not in v["offs"] and n not in last_night_staff]
                    random.shuffle(avail)
                    today_nights = []

                    for w, req in st.session_state.wards.items():
                        day_info = {"تاریخ": f"روز {d}"}
                        for s_type in ["صبح", "عصر", "شب"]:
                            # استخراج نیاز جنسیتی
                            s_key = 'morn' if s_type=='صبح' else 'eve' if s_type=='عصر' else 'night'
                            f_needed = req[f"{s_key}_f"]
                            m_needed = req[f"{s_key}_m"]
                            
                            chosen = []
                            # منطق انتخاب عادلانه: خانم‌ها و سپس آقایان
                            for g_type, count in [("خانم", f_needed), ("آقا", m_needed)]:
                                for _ in range(count):
                                    elig = [a for a in avail if st.session_state.staff[a]["gender"] == g_type and s_type not in st.session_state.staff[a]["day_prefs"].get(d, [])]
                                    if elig:
                                        elig.sort(key=lambda x: st.session_state.staff[x]["total_shifts"])
                                        pick = elig[0]
                                        chosen.append(pick)
                                        avail.remove(pick) # حذف از لیست برای جلوگیری از تداخل در بخش‌های دیگر
                                        st.session_state.staff[pick]["total_shifts"] += 1
                                        if s_type == "شب": today_nights.append(pick)
                                    else: chosen.append("⚠️ کمبود")
                            day_info[s_type] = " / ".join(chosen)
                        temp_results[w].append(day_info)
                    last_night_staff = today_nights

                st.session_state.final_schedules = {w: pd.DataFrame(data) for w, data in temp_results.items()}
                st.balloons()

        # نمایش و دانلود جداگانه برای هر بخش
        for w, df in st.session_state.final_schedules.items():
            st.markdown(f"<div class='ward-header'>📋 برنامه نهایی بخش: {w}</div>", unsafe_allow_html=True)
            st.data_editor(df, use_container_width=True, key=f"editor_{w}")
            st.download_button(f"📥 دانلود اکسل ({w})", df.to_csv(index=False).encode('utf-8-sig'), f"Schedule_{w}.csv")
