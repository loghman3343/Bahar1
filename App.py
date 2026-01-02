
import streamlit as st
import pandas as pd
import random
import plotly.express as px

# تنظیمات استراتژیک صفحه
st.set_page_config(page_title="سامانه جامع هوشمند بهار ۱", layout="wide")

# طراحی رابط کاربری (UI) پیشرفته با CSS
st.markdown("""
    <style>
    .main { background: #f4f7f6; }
    .stMetric { background: white; padding: 20px; border-radius: 15px; box-shadow: 0 4px 12px rgba(0,0,0,0.05); }
    .shift-card { padding: 10px; border-radius: 8px; margin: 5px; color: white; font-weight: bold; text-align: center; }
    .morn { background: #FFD700; color: #333; }
    .eve { background: #FF8C00; }
    .night { background: #2F4F4F; }
    .stButton>button { border-radius: 10px; height: 3em; background: #1e3c72; color: white; border: none; }
    </style>
    """, unsafe_allow_html=True)

# --- مدیریت حافظه پایدار (Session State) ---
if "staff" not in st.session_state: st.session_state.staff = {}
if "wards" not in st.session_state: st.session_state.wards = {
    "تریاژ": {"morn": 2, "eve": 2, "night": 2, "color": "#1e3c72"},
    "سرم تراپی": {"morn": 1, "eve": 1, "night": 2, "color": "#2a5298"}
}
if "final_df" not in st.session_state: st.session_state.final_df = None

# --- سایدبار برای آمار سریع ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2764/2764442.png", width=80)
    st.title("پنل نظارتی")
    if st.session_state.staff:
        st.write("📊 وضعیت عدالت در شیفت:")
        names = list(st.session_state.staff.keys())
        shifts = [v['total_shifts'] for v in st.session_state.staff.values()]
        fig = px.bar(x=names, y=shifts, labels={'x':'پرسنل', 'y':'تعداد شیفت'}, height=200)
        st.plotly_chart(fig, use_container_width=True)

# --- بدنه اصلی برنامه ---
st.title("🏥 داشبورد عملیاتی بیمارستان (Bahar Enterprise)")

tabs = st.tabs(["🏛️ مرکز مدیریت", "🗓️ تقویم مرخصی و درخواست", "⚙️ مهندسی بخش‌ها", "💎 تولید هوشمند برنامه"])

with tabs[0]:
    col1, col2 = st.columns([2, 1])
    with col1:
        st.subheader("👥 ثبت و ویرایش پرسنل")
        with st.form("staff_form"):
            c1, c2 = st.columns(2)
            n = c1.text_input("نام و نام خانوادگی")
            g = c2.selectbox("جنسیت", ["خانم", "آقا"])
            if st.form_submit_button("افزودن به دیتابیس"):
                if n:
                    st.session_state.staff[n] = {"gender": g, "offs": [], "day_prefs": {}, "total_shifts": 0}
                    st.rerun()
        
        if st.session_state.staff:
            df_view = pd.DataFrame([{"نام": k, "جنسیت": v["gender"], "مجموع شیفت": v["total_shifts"]} for k, v in st.session_state.staff.items()])
            st.dataframe(df_view, use_container_width=True)

    with col2:
        st.subheader("⚠️ حذف و پاکسازی")
        del_target = st.selectbox("انتخاب فرد:", [""] + list(st.session_state.staff.keys()))
        if st.button("🗑️ حذف از سیستم"):
            if del_target: del st.session_state.staff[del_target]; st.rerun()
        st.divider()
        if st.button("🚨 ریست کامل ماهانه"):
            st.session_state.staff = {}; st.session_state.final_df = None; st.rerun()

with tabs[1]:
    st.subheader("📅 مدیریت تقویم درخواست‌ها")
    if st.session_state.staff:
        p_sel = st.selectbox("انتخاب همکار:", list(st.session_state.staff.keys()))
        col_a, col_b = st.columns(2)
        with col_a:
            st.info("مرخصی کامل (Full Day Off)")
            current_offs = st.multiselect("روزهای مرخصی:", list(range(1, 32)), default=st.session_state.staff[p_sel]["offs"])
            if st.button("ذخیره مرخصی"):
                st.session_state.staff[p_sel]["offs"] = current_offs
                st.toast("مرخصی‌ها ثبت شد")
        with col_b:
            st.info("محدودیت شیفت (Shift Constraint)")
            day_target = st.selectbox("روز خاص:", list(range(1, 32)))
            limit = st.multiselect("نباید باشد در:", ["صبح", "عصر", "شب"])
            if st.button("ثبت محدودیت"):
                st.session_state.staff[p_sel]["day_prefs"][day_target] = limit
                st.toast("محدودیت روزانه اعمال شد")
    else: st.warning("لیست پرسنل خالی است.")

with tabs[2]:
    st.subheader("🏢 مهندسی منابع انسانی بخش‌ها")
    for w_name in list(st.session_state.wards.keys()):
        with st.expander(f"⚙️ پیکربندی {w_name}"):
            c1, c2, c3 = st.columns(3)
            st.session_state.wards[w_name]["morn"] = c1.number_input(f"نیاز صبح {w_name}", 0, 10, st.session_state.wards[w_name]["morn"], key=f"m_{w_name}")
            st.session_state.wards[w_name]["eve"] = c2.number_input(f"نیاز عصر {w_name}", 0, 10, st.session_state.wards[w_name]["eve"], key=f"e_{w_name}")
            st.session_state.wards[w_name]["night"] = c3.number_input(f"نیاز شب {w_name}", 0, 10, st.session_state.wards[w_name]["night"], key=f"n_{w_name}")

with tabs[3]:
    st.subheader("💎 هوش مصنوعی چیدمان")
    days_count = st.number_input("بازه برنامه (روز):", 1, 31, 30)
    
    if st.button("🚀 اجرای چیدمان بهینه و عادلانه"):
        # الگوریتم عدالتی: صفر کردن آمار
        for s in st.session_state.staff: st.session_state.staff[s]["total_shifts"] = 0
        
        all_days = []
        last_night_shift = []
        
        for d in range(1, days_count + 1):
            # اولویت‌دهی به کسانی که شیفت کمتری داشته‌اند (الگوریتم عادلانه)
            sorted_staff = sorted(st.session_state.staff.items(), key=lambda x: x[1]['total_shifts'])
            avail = [n for n, v in sorted_staff if d not in v["offs"] and n not in last_night_shift]
            
            day_data = {"تاریخ": f"روز {d}"}
            today_nights = []

            for ward, req in st.session_state.wards.items():
                for s_type in ["صبح", "عصر", "شب"]:
                    needed = req[{"صبح": "morn", "عصر": "eve", "شب": "night"}[s_type]]
                    chosen_list = []
                    for _ in range(needed):
                        eligible = [a for a in avail if s_type not in st.session_state.staff[a]["day_prefs"].get(d, [])]
                        if eligible:
                            pick = eligible[0]
                            sex = "خ" if st.session_state.staff[pick]['gender'] == "خانم" else "آ"
                            chosen_list.append(f"{pick} ({sex})")
                            avail.remove(pick)
                            st.session_state.staff[pick]["total_shifts"] += 1
                            if s_type == "شب": today_nights.append(pick)
                        else: chosen_list.append("⚠️ کمبود")
                    day_data[f"{ward}-{s_type}"] = " / ".join(chosen_list)
            
            all_days.append(day_data)
            last_night_shift = today_nights

        st.session_state.final_df = pd.DataFrame(all_days)
        st.success("برنامه با رعایت سقف عدالت و محدودیت‌ها تولید شد!")

    if st.session_state.final_df is not None:
        st.data_editor(st.session_state.final_df, use_container_width=True)
        # دکمه دانلود اکسل با یونیکد مناسب ایران
        csv = st.session_state.final_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button("📥 دریافت فایل چاپی (Excel)", csv, "Bahar_Schedule.csv", "text/csv")
