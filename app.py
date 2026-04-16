import streamlit as st
import json
import os
import time
import uuid

# --- 1. 資料處理功能 ---
DATA_FILE = 'tasks.json'

def load_tasks():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            try:
                tasks = json.load(f)
                for t in tasks:
                    if 'id' not in t: t['id'] = str(uuid.uuid4())
                return tasks
            except:
                return []
    return []

def save_tasks(tasks):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(tasks, f, ensure_ascii=False, indent=4)

# --- 2. 網頁與樣式配置 ---
st.set_page_config(page_title="番茄鐘工作法", page_icon="🍅", layout="centered")

# 只保留必要的乾淨 CSS (隱藏預設選單與優化卡片)
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* 讓上方數據指標置中對齊，看起來更整齊 */
    div[data-testid="metric-container"] {
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- 3. 初始化資料 ---
if 'tasks' not in st.session_state:
    st.session_state.tasks = load_tasks()
if 'time_left' not in st.session_state:
    st.session_state.time_left = 25 * 60
if 'is_running' not in st.session_state:
    st.session_state.is_running = False

st.title("🍅 番茄鐘專注看板")

# ==========================================
# 卡片一：番茄鐘計時器
# ==========================================
with st.container(border=True):
    st.subheader("⏱️ 專注計時")
    
    col_ctrl, col_timer = st.columns([1, 2], vertical_alignment="center")
    
    with col_ctrl:
        input_mins = st.number_input("設定分鐘", min_value=1, value=25)
        if not st.session_state.is_running and st.session_state.time_left != input_mins * 60:
            st.session_state.time_left = input_mins * 60
        
        c1, c2 = st.columns(2)
        # 使用 type="primary" 讓開始按鈕自動凸顯
        if c1.button("▶️ 開始", type="primary", use_container_width=True): 
            st.session_state.is_running = True
        if c2.button("⏸️ 暫停", use_container_width=True): 
            st.session_state.is_running = False
        if st.button("🔄 重置時間", use_container_width=True):
            st.session_state.is_running = False
            st.session_state.time_left = input_mins * 60
            st.rerun()

    with col_timer:
        mm, ss = divmod(st.session_state.time_left, 60)
        st.markdown(f"<h1 style='text-align: center; font-size: 100px; margin: 0; color: #333;'>{mm:02d}:{ss:02d}</h1>", unsafe_allow_html=True)
        
    total_sec = input_mins * 60
    current_progress = 1.0 - (st.session_state.time_left / total_sec) if total_sec > 0 else 0.0
    st.progress(min(max(current_progress, 0.0), 1.0))

# 計時器運作邏輯
if st.session_state.is_running and st.session_state.time_left > 0:
    time.sleep(1)
    st.session_state.time_left -= 1
    st.rerun()
elif st.session_state.time_left == 0 and st.session_state.is_running:
    st.session_state.is_running = False
    st.balloons()
    st.success("🎉 時間到！休息一下吧！")

# ==========================================
# 卡片二：任務管理 (包含數據、輸入、列表、清除)
# ==========================================
with st.container(border=True):
    st.subheader("📝 任務管理")
    
    # 1. 任務數據 (移到任務管理最上方)
    done_count = sum(1 for t in st.session_state.tasks if t['done'])
    total_count = len(st.session_state.tasks)
    m1, m2, m3 = st.columns(3)
    m1.metric("今日任務", total_count)
    m2.metric("已完成", done_count)
    m3.metric("達成率", f"{int(done_count/total_count*100) if total_count>0 else 0}%")
    
    st.divider() # 加一條淡灰色的分隔線
    
    # 2. 任務輸入區
    col_in, col_btn = st.columns([4, 1], vertical_alignment="bottom")
    new_task = col_in.text_input("新增待辦事項", placeholder="輸入後點擊新增...", label_visibility="collapsed")
    if col_btn.button("➕ 新增", type="primary", use_container_width=True):
        if new_task:
            st.session_state.tasks.append({"id": str(uuid.uuid4()), "name": new_task, "done": False})
            save_tasks(st.session_state.tasks)
            st.rerun()

    st.write("") 
    
    # 3. 任務清單分欄
    col_pending, col_completed = st.columns(2)
    
    with col_pending:
        st.markdown("#### ⏳ 進行中")
        for i, task in enumerate(st.session_state.tasks):
            if not task['done']:
                ic1, ic2 = st.columns([0.2, 0.8], vertical_alignment="center")
                if ic1.checkbox("", value=False, key=f"chk_{task['id']}"):
                    st.session_state.tasks[i]['done'] = True
                    save_tasks(st.session_state.tasks)
                    st.rerun()
                ic2.write(task['name'])

    with col_completed:
        st.markdown("#### ✅ 已完成")
        for i, task in enumerate(st.session_state.tasks):
            if task['done']:
                ic1, ic2, ic3 = st.columns([0.15, 0.65, 0.2], vertical_alignment="center")
                if not ic1.checkbox("", value=True, key=f"chk_{task['id']}"):
                    st.session_state.tasks[i]['done'] = False
                    save_tasks(st.session_state.tasks)
                    st.rerun()
                ic2.write(f"<span style='color: #888;'>{task['name']}</span>", unsafe_allow_html=True)
                if ic3.button("🗑️", key=f"del_{task['id']}"):
                    st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                    save_tasks(st.session_state.tasks)
                    st.rerun()
                    
    st.write("") 
    
    # 4. 一鍵清除按鈕 
    if st.button("🧹 一鍵清除所有已完成任務", use_container_width=True):
        st.session_state.tasks = [t for t in st.session_state.tasks if not t['done']]
        save_tasks(st.session_state.tasks)
        st.rerun()
