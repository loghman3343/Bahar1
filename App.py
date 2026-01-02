
import streamlit as st
import pandas as pd
import random

# تنظیمات اصلی صفحه
st.set_page_config(page_title="مدیریت هوشمند بهار ۱", layout="wide")

# استایل اختصاصی برای ظاهر حرفه‌ای
st.markdown("""
<style>
.main { background-color: #f0f2f6; }
.stButton>button { width: 100%; border-radius: 8px; height: 3em; background-color: #1e3c72; color: white; font-weight: bold; }
.stExpander { border: 1px solid #1e3c72; border-radius: 10px; background-color: white; }
</style>
""", unsafe_allow_html=True)

# --- مدیریت حافظه (Session State) ---
if "login" not in st.session_state: st.session_state.login = False
if "staff" not in st.session_state: st.session_state.staff = {}
if "wards" not in st.session_state: 
    st.session_state.wards = {
        "تریاژ": {"morn": 2, "eve": 2, "night": 2},
        "سرم تراپی": {"morn": 1, "eve": 1, "night": 2}
    }
if "final_df" not in st.session_state: st.session_state.final_df = None

# ================== سیستم ورود ==================
if not st.session_state.login:
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.title("🔐 ورود به سامانه بهار ۱")
        u = st.text_input("نام کاربری")
        p = st.text_input("رمز عبور", type="password")
        if st.button("ورود به پنل مدیریت"):
            if u == "admin" and p == "1234":
                st.session_state.login = True
                st.rerun()
            else: st.error("اطلاعات ورود نادرست است.")
else:
    # هدر اصلی
    h_col1, h_col2 = st.columns([4,1])
    h_col1.title("🏥 سامانه برنامه‌ریزی هوشمند")
    if h_col2.button("خروج از سیستم 🚪"):
        st.session_state.login = False
        st.rerun()

    # ایجاد تب‌های مدیریتی
    t1, t2, t3, t4, t5 = st.tabs(["👥 پرسنل", "🏖️ مرخصی", "💡 محدودیت‌ها", "⚙️ تنظیمات بخش‌ها", "🚀 تولید برنامه"])

    with t1:
        st.subheader("➕ مدیریت بانک اطلاعاتی پرسنل")
        col_n, col_g, col_b = st.columns([3, 2, 1])
        new_name = col_n.text_input("نام همکار:")
        new_gen = col_g.selectbox("جنسیت:", ["خانم", "آقا"])
        if col_b.button("ثبت نام"):
            if new_name and new_name not in st.session_state.staff:
                st.session_state.staff[new_name] = {"gender": new_gen, "offs": [], "day_prefs": {}, "total_shifts": 0}
                st.rerun()
        
        if st.session_state.staff:
            df_staff = pd.DataFrame([{"نام": k, "جنسیت": v["gender"], "شیفت‌های ماه": v["total_shifts"]} for k, v in st.session_state.staff.items()])
            st.table(df_staff)
            
            del_target = st.selectbox("حذف همکار:", [""] + list(st.session_state.staff.keys()))
            if st.button("🗑️ حذف از لیست"):
                if del_target:
                    del st.session_state.staff[del_target]
                    st.rerun()

    with t2:
        st.subheader("🏖️ مدیریت ایام مرخصی")
        if st.session_state.staff:
            p_off = st.selectbox("انتخاب همکار:", list(st.session_state.staff.keys()), key="p_off")
            current_offs = st.session_state.staff[p_off]["offs"]
            offs = st.multiselect("روزهایی که حضور ندارد:", range(1, 32), default=current_offs)
            if st.button("تایید مرخصی"):
                st.session_state.staff[p_off]["offs"] = offs
                st.success("مرخصی با موفقیت ثبت شد.")
        else: st.info("لطفاً ابتدا پرسنل را تعریف کنید.")

    with t3:
        st.subheader("💡 محدودیت‌های شیفت (درخواستی)")
        if st.session_state.staff:
            p_pref = st.selectbox("انتخاب همکار:", list(st.session_state.staff.keys()), key="p_pref")
            d_pref = st.selectbox("انتخاب روز:", range(1, 32))
            s_pref = st.multiselect("عدم حضور در شیفت‌های:", ["صبح", "عصر", "شب"])
            if st.button("ثبت محدودیت خاص"):
                st.session_state.staff[p_pref]["day_prefs"][d_pref] = s_pref
                st.success(f"محدودیت برای {p_pref} در روز {d_pref} ثبت شد.")
        else: st.info("لیستی برای نمایش وجود ندارد.")

    with t4:
        st.subheader("🏢 مهندسی ساختار بخش‌ها")
        c_add1, c_add2 = st.columns([3, 1])
        new_ward_name = c_add1.text_input("نام بخش جدید (مثلاً: ICU):")
        if c_add2.button("➕ افزودن بخش"):
            if new_ward_name and new_ward_name not in st.session_state.wards:
                st.session_state.wards[new_ward_name] = {"morn": 0, "eve": 0, "night": 0}
                st.rerun()

        st.divider()
        if st.session_state.wards:
            for w_name in list(st.session_state.wards.keys()):
                with st.expander(f"📍 تنظیم ظرفیت بخش: {w_name}", expanded=True):
                    col_w1, col_w2, col_w3, col_w4 = st.columns([2, 2, 2, 1])
                    st.session_state.wards[w_name]["morn"] = col_w1.number_input(f"تعداد صبح", 0, 10, st.session_state.wards[w_name]["morn"], key=f"m_{w_name}")
                    st.session_state.wards[w_name]["eve"] = col_w2.number_input(f"تعداد عصر", 0, 10, st.session_state.wards[w_name]["eve"], key=f"e_{w_name}")
                    st.session_state.wards[w_name]["night"] = col_w3.number_input(f"تعداد شب", 0, 10, st.session_state.wards[w_name]["night"], key=f"n_{w_name}")
                    if col_w4.button("🗑️ حذف", key=f"del_w_{w_name}"):
                        del st.session_state.wards[w_name]
                        st.rerun()

    with t5:
        st.subheader("🚀 موتور تولید چیدمان خودکار")
        days_num = st.number_input("تعداد روزهای بازه برنامه:", 1, 31, 30)
        
        if st.button("🔥 شروع فرآیند چیدمان"):
            if not st.session_state.staff:
                st.error("بانک اطلاعات پرسنل خالی است.")
            elif not st.session_state.wards:
                st.error("هیچ بخشی تعریف نشده است.")
            else:
                for s in st.session_state.staff.values(): s["total_shifts"] = 0
                all_days = []
                last_night_staff = []

                for d in range(1, days_num + 1):
                    day_row = {"تاریخ": f"روز {d}"}
                    # فیلتر در دسترس بودن و قانون استراحت پس از شب‌کاری
                    avail = [n for n, v in st.session_state.staff.items() if d not in v["offs"] and n not in last_night_staff]
                    random.shuffle(avail)
                    
                    tonight_staff = []
                    for ward, req in st.session_state.wards.items():
                        for s_type in ["صبح", "عصر", "شب"]:
                            needed = req[{"صبح": "morn", "عصر": "eve", "شب": "night"}[s_type]]
                            chosen = []
                            for _ in range(needed):
                                # چک کردن محدودیت‌های درخواستی
                                eligible = [a for a in avail if s_type not in st.session_state.staff[a]["day_prefs"].get(d, [])]
                                if eligible:
                                    # اولویت با کسانی که شیفت کمتری داشته‌اند (عدالت)
                                    eligible.sort(key=lambda x: st.session_state.staff[x]["total_shifts"])
                                    pick = eligible[0]
                                    sex = "خ" if st.session_state.staff[pick]["gender"] == "خانم" else "آ"
                                    chosen.append(f"{pick} ({sex})")
                                    avail.remove(pick)
                                    st.session_state.staff[pick]["total_shifts"] += 1
                                    if s_type == "شب": tonight_staff.append(pick)
                                else:
                                    chosen.append("⚠️ کمبود نیرو")
                            day_row[f"{ward} ({s_type})"] = " / ".join(chosen)
                    
                    all_days.append(day_row)
                    last_night_staff = tonight_staff

                st.session_state.final_df = pd.DataFrame(all_days)
                st.balloons()

        if st.session_state.final_df is not None:
            st.data_editor(st.session_state.final_df, use_container_width=True)
            st.download_button("📥 دانلود اکسل برنامه (Excel)", st.session_state.final_df.to_csv(index=False).encode('utf-8-sig'), "Bahar_Hospital_Plan.csv")
