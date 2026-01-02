
import streamlit as st
import pandas as pd
import random

# تنظیمات اصلی صفحه به صورت عریض (Wide Mode)
st.set_page_config(page_title="مدیریت بهار ۱", layout="wide", initial_sidebar_state="collapsed")

# تزریق استایل CSS برای تبدیل محیط ساده به یک سایت حرفه‌ای
st.markdown("""
<style>
    /* استایل کلی پس‌زمینه */
    .stApp { background-color: #f0f2f6; }
    
    /* استایل کارت‌ها */
    .main-card {
        background-color: #ffffff;
        padding: 25px;
        border-radius: 15px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        border-top: 5px solid #1e3c72;
    }
    
    /* استایل هدرها */
    h1, h2, h3 { color: #1e3c72; font-family: 'Tahoma'; }
    
    /* دکمه‌های اصلی */
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3.5em;
        background-image: linear-gradient(to right, #1e3c72, #2a5298);
        color: white;
        font-weight: bold;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(30,60,114,0.3); }
    
    /* استایل ورودی‌ها */
    .stNumberInput, .stTextInput { border-radius: 10px; }
    
    /* جداکننده بخش‌ها */
    .section-header {
        background-color: #1e3c72;
        color: white;
        padding: 10px 20px;
        border-radius: 8px;
        margin: 20px 0;
    }
</style>
""", unsafe_allow_html=True)

# --- مدیریت حافظه (Session State) ---
if "wards" not in st.session_state: st.session_state.wards = {}
if "staff" not in st.session_state: st.session_state.staff = {}

# ==================== صفحه اصلی سایت ====================
st.markdown("<h1 style='text-align: center;'>🏥 پنل هوشمند برنامه‌ریزی بیمارستان (بهار ۱)</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666;'>مدیریت یکپارچه بخش‌ها، پرسنل و شیفت‌بندی جنسیتی</p>", unsafe_allow_html=True)

# --- قدم اول: تعریف ساختار بخش‌ها ---
st.markdown("<div class='section-header'>Step 1: تنظیمات بخش‌ها و نیاز جنسیتی</div>", unsafe_allow_html=True)

with st.container():
    col_w1, col_w2 = st.columns([3, 1])
    with col_w1:
        new_ward = st.text_input("➕ نام بخش جدید را وارد کنید (مثلاً: ICU، اورژانس، جراحی):", placeholder="نام بخش...")
    with col_w2:
        st.write(" ")
        st.write(" ")
        if st.button("ثبت بخش جدید"):
            if new_ward and new_ward not in st.session_state.wards:
                st.session_state.wards[new_ward] = {
                    "morning": {"f": 0, "m": 0},
                    "evening": {"f": 0, "m": 0},
                    "night": {"f": 0, "m": 0}
                }
                st.rerun()

# نمایش کارت‌های تنظیمات برای هر بخش به صورت شبکه‌ای
if st.session_state.wards:
    for w_name, shifts in list(st.session_state.wards.items()):
        st.markdown(f"<div class='main-card'>", unsafe_allow_html=True)
        c_head, c_del = st.columns([5, 1])
        c_head.subheader(f"📍 پیکربندی بخش: {w_name}")
        if c_del.button("❌ حذف بخش", key=f"del_{w_name}"):
            del st.session_state.wards[w_name]
            st.rerun()

        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("<p class='shift-label'>☀️ <b>شیفت صبح</b></p>", unsafe_allow_html=True)
            shifts["morning"]["f"] = st.number_input(f"تعداد خانم (صبح)", 0, 10, key=f"mf_{w_name}")
            shifts["morning"]["m"] = st.number_input(f"تعداد آقا (صبح)", 0, 10, key=f"mm_{w_name}")
        
        with col2:
            st.markdown("<p class='shift-label'>🌆 <b>شیفت عصر</b></p>", unsafe_allow_html=True)
            shifts["evening"]["f"] = st.number_input(f"تعداد خانم (عصر)", 0, 10, key=f"ef_{w_name}")
            shifts["evening"]["m"] = st.number_input(f"تعداد آقا (عصر)", 0, 10, key=f"em_{w_name}")
            
        with col3:
            st.markdown("<p class='shift-label'>🌙 <b>شیفت شب</b></p>", unsafe_allow_html=True)
            shifts["night"]["f"] = st.number_input(f"تعداد خانم (شب)", 0, 10, key=f"nf_{w_name}")
            shifts["night"]["m"] = st.number_input(f"تعداد آقا (شب)", 0, 10, key=f"nm_{w_name}")
        st.markdown("</div>", unsafe_allow_html=True)

# --- قدم دوم: مدیریت پرسنل ---
st.markdown("<div class='section-header'>Step 2: ورود اطلاعات همکاران</div>", unsafe_allow_html=True)
with st.container():
    c_p1, c_p2, c_p3 = st.columns([3, 2, 1])
    with c_p1: p_name = st.text_input("نام و نام خانوادگی همکار:")
    with c_p2: p_gen = st.selectbox("جنسیت:", ["خانم", "آقا"])
    with c_p3:
        st.write(" ")
        st.write(" ")
        if st.button("ثبت همکار"):
            if p_name:
                st.session_state.staff[p_name] = {"gender": p_gen, "shifts": 0}
                st.rerun()

if st.session_state.staff:
    with st.expander("👥 مشاهده لیست پرسنل ثبت شده"):
        df_staff = pd.DataFrame([{"نام": k, "جنسیت": v["gender"]} for k, v in st.session_state.staff.items()])
        st.dataframe(df_staff, use_container_width=True)

# --- قدم سوم: تولید خروجی نهایی ---
st.markdown("<div class='section-header'>Step 3: تولید و دریافت برنامه</div>", unsafe_allow_html=True)
col_gen1, col_gen2 = st.columns([1, 2])
with col_gen1:
    days = st.number_input("تعداد روزهای ماه:", 1, 31, 30)
    generate = st.button("🚀 تولید برنامه هوشمند")

if generate:
    if not st.session_state.wards or not st.session_state.staff:
        st.error("❌ خطا: ابتدا بخش‌ها و پرسنل را وارد کنید.")
    else:
        # صفر کردن آمار شیفت‌ها
        for s in st.session_state.staff.values(): s["shifts"] = 0
        
        for w_name, w_req in st.session_state.wards.items():
            st.markdown(f"<div class='main-card'><h3>📋 خروجی برنامه بخش: {w_name}</h3>", unsafe_allow_html=True)
            ward_data = []
            last_night_staff = []

            for d in range(1, days + 1):
                row = {"تاریخ": f"روز {d}"}
                # افراد در دسترس (امروز مرخصی نباشند و دیشب شبکار نباشند - ساده شده برای این نسخه)
                avail = list(st.session_state.staff.keys())
                random.shuffle(avail)
                
                for s_name, s_label in [("morning", "صبح"), ("evening", "عصر"), ("night", "شب")]:
                    f_needed = w_req[s_name]["f"]
                    m_needed = w_req[s_name]["m"]
                    chosen = []
                    
                    # انتخاب خانم‌ها
                    f_pool = [n for n in avail if st.session_state.staff[n]["gender"] == "خانم"]
                    for _ in range(f_needed):
                        if f_pool:
                            p = f_pool.pop(0); chosen.append(p); avail.remove(p)
                    
                    # انتخاب آقایان
                    m_pool = [n for n in avail if st.session_state.staff[n]["gender"] == "آقا"]
                    for _ in range(m_needed):
                        if m_pool:
                            p = m_pool.pop(0); chosen.append(p); avail.remove(p)
                    
                    row[s_label] = " / ".join(chosen) if chosen else "---"
                ward_data.append(row)
            
            df_final = pd.DataFrame(ward_data)
            st.dataframe(df_final, use_container_width=True)
            st.download_button(f"📥 دانلود اکسل بخش {w_name}", df_final.to_csv(index=False).encode('utf-8-sig'), f"Plan_{w_name}.csv")
            st.markdown("</div>", unsafe_allow_html=True)
