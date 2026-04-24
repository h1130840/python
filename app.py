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

def add_new_task():
    # 檢查輸入框裡有沒有字
    if st.session_state.task_input_box: 
        st.session_state.tasks.append({
            "id": str(uuid.uuid4()), 
            "name": st.session_state.task_input_box, 
            "done": False
        })
        save_tasks(st.session_state.tasks)
        # 在回調函數裡面清空輸入框
        st.session_state.task_input_box = "" 

# --- 2. 網頁與樣式配置 (注入科技感 CSS) ---
st.set_page_config(page_title="番茄鐘控制台", page_icon="⏱️", layout="centered")

st.markdown("""
<style>
    /* 隱藏預設選單與頁尾 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    div[data-testid="metric-container"] {
        text-align: center;
    }

    /* --- 科技感核心 CSS --- */
    
    /* 1. 讓卡片邊框有微發光感 */
    [data-testid="stVerticalBlockBorderWrapper"] {
        border: 1px solid rgba(0, 229, 255, 0.3) !important;
        box-shadow: 0 4px 20px rgba(0, 229, 255, 0.05);
        border-radius: 12px;
        background-color: rgba(21, 27, 43, 0.7); /* 微透明玻璃感 */
        backdrop-filter: blur(10px);
    }

    /* 2. 改造按鈕：預設狀態與 Hover 懸浮特效 */
    .stButton > button {
        background-color: transparent !important;
        border: 1px solid #00e5ff !important;
        color: #00e5ff !important;
        transition: all 0.3s ease-in-out;
    }
    
    .stButton > button:hover {
        box-shadow: 0 0 15px rgba(0, 229, 255, 0.6) !important;
        background-color: rgba(0, 229, 255, 0.1) !important;
        transform: translateY(-2px);
    }

    /* 3. 改造「主按鈕」(Primary Button) */
    .stButton > button[data-testid="baseButton-primary"] {
        background-color: #00e5ff !important;
        color: #0b0f19 !important;
        border: none !important;
        font-weight: bold;
    }
    .stButton > button[data-testid="baseButton-primary"]:hover {
        box-shadow: 0 0 20px rgba(0, 229, 255, 0.8) !important;
        background-color: #33eeff !important;
    }

    /* 4. 番茄鐘大數字特效 */
    h1 {
        text-shadow: 0 0 15px rgba(0, 229, 255, 0.5); /* 霓虹光暈 */
        letter-spacing: 2px;
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
if 'task_input_box' not in st.session_state:
    st.session_state.task_input_box = ""

st.title("⏱️ 專注控制台")

# ==========================================
# 卡片一：番茄鐘計時器
# ==========================================
with st.container(border=True):
    st.subheader("⚡ 核心計時")
    
    col_ctrl, col_timer = st.columns([1, 2], vertical_alignment="center")
    
    with col_ctrl:
        input_mins = st.number_input("設定分鐘", min_value=1, value=25)
        if not st.session_state.is_running and st.session_state.time_left != input_mins * 60:
            st.session_state.time_left = input_mins * 60
        
        c1, c2 = st.columns(2)
        if c1.button("▶️ 開始", type="primary", use_container_width=True): 
            st.session_state.is_running = True
        if c2.button("⏸️ 暫停", use_container_width=True): 
            st.session_state.is_running = False
        if st.button("🔄 重置", use_container_width=True):
            st.session_state.is_running = False
            st.session_state.time_left = input_mins * 60
            st.rerun()

    with col_timer:
        mm, ss = divmod(st.session_state.time_left, 60)
        # 移除了原本的 color: #333，讓它適應暗黑模式與 CSS 發光特效
        st.markdown(f"<h1 style='text-align: center; font-size: 100px; margin: 0;'>{mm:02d}:{ss:02d}</h1>", unsafe_allow_html=True)
        
    total_sec = input_mins * 60
    current_progress = 1.0 - (st.session_state.time_left / total_sec) if total_sec > 0 else 0.0
    st.progress(min(max(current_progress, 0.0), 1.0))

if st.session_state.is_running and st.session_state.time_left > 0:
    time.sleep(1)
    st.session_state.time_left -= 1
    st.rerun()
elif st.session_state.time_left == 0 and st.session_state.is_running:
    st.session_state.is_running = False
    st.balloons()
    st.success(f"時間到！已專注 {input_mins} 分鐘。")

# ==========================================
# 卡片二：任務管理 
# ==========================================
with st.container(border=True):
    st.subheader("📋 任務清單")
    
    done_count = sum(1 for t in st.session_state.tasks if t['done'])
    total_count = len(st.session_state.tasks)
    m1, m2, m3 = st.columns(3)
    m1.metric("今日任務", total_count)
    m2.metric("已完成", done_count)
    m3.metric("達成率", f"{int(done_count/total_count*100) if total_count>0 else 0}%")
    
    st.divider() 
    
    col_in, col_btn = st.columns([4, 1], vertical_alignment="bottom")
    col_in.text_input("新增待辦事項", placeholder="輸入後點擊新增或按 Enter", label_visibility="collapsed", key="task_input_box", on_change=add_new_task)
    col_btn.button("➕ 新增", type="primary", use_container_width=True, on_click=add_new_task)

    st.write("") 
    
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
                # 已完成任務改為稍暗的顏色 #64748b (Slate 500)，在暗黑模式下更好看
                ic2.write(f"<span style='color: #64748b;'>{task['name']}</span>", unsafe_allow_html=True)
                if ic3.button("🗑️", key=f"del_{task['id']}"):
                    st.session_state.tasks = [t for t in st.session_state.tasks if t['id'] != task['id']]
                    save_tasks(st.session_state.tasks)
                    st.rerun()
                    
    st.write("") 
    
    if st.button("🧹 一鍵清除所有已完成任務", use_container_width=True):
        st.session_state.tasks = [t for t in st.session_state.tasks if not t['done']]
        save_tasks(st.session_state.tasks)
        st.rerun()
