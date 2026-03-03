import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import datetime
import io
from pillow_heif import register_heif_opener
from PIL.ExifTags import TAGS

register_heif_opener()
st.set_page_config(page_title="父母相册助手", layout="centered")

# --- 1. 强力 CSS 注入：解决 0B 下载和间距问题 ---
st.markdown("""
    <style>
    /* 彻底消除图片和下方组件的间距 */
    div[data-testid="stImage"] > img { margin-bottom: -40px !important; }
    div[data-testid="stVerticalBlock"] > div { margin-top: -10px !important; }
    /* 紧凑化所有输入框 */
    .stNumberInput, .stTextInput, .stDateInput { margin-top: -15px !important; }
    /* 醒目的保存按钮 */
    .stDownloadButton button {
        width: 100%;
        background-color: #28a745 !important;
        color: white !important;
        height: 50px;
        font-size: 18px !important;
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load_and_fix_image(file):
    raw_img = Image.open(file)
    full_img = ImageOps.exif_transpose(raw_img)
    preview_img = full_img.copy()
    preview_img.thumbnail((800, 800)) # 降低预览图压力
    return full_img, preview_img

def get_accurate_date(image):
    try:
        exif = image.getexif()
        if exif:
            for tag_id, value in exif.items():
                tag_name = TAGS.get(tag_id, tag_id)
                if tag_name in ["DateTimeOriginal", "DateTime"]:
                    date_str = str(value)[:10].replace(":", "-")
                    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except:
        pass
    return None

st.title("📸 老人相册助手 (稳如泰山版)")

uploaded_file = st.file_uploader("第一步：上传照片", type=["jpg", "jpeg", "png", "heic", "heif", "dng"])

if uploaded_file:
    full_img, preview_base = load_and_fix_image(uploaded_file)
    w_full, h_full = full_img.size
    w_pre, h_pre = preview_base.size
    scale = w_full / w_pre

    # 侧边栏保持不变
    st.sidebar.header("🎨 样式与精确位置")
    color_options = {"亮黄色": "#FFFF00", "纯白色": "#FFFFFF", "大红色": "#FF0000", "黑色": "#000000"}
    selected_color = color_options[st.sidebar.selectbox("文字颜色:", list(color_options.keys()))]
    pos_x_pre = st.sidebar.slider("左右挪动位置:", 0, w_pre, int(w_pre * 0.1))
    pos_y_pre = st.sidebar.slider("上下挪动位置:", 0, h_pre, int(h_pre * 0.8))

    # --- 预览占位符 ---
    image_preview_placeholder = st.empty()

    # --- 基础设置区 (已极度紧凑) ---
    st.subheader("⚙️ 文字设置")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        location = st.text_input("地点 (选填):", "")
    with col2:
        font_size_full = st.number_input("字号:", 10, 2000, 300)
    with col3:
        detected_date = get_accurate_date(full_img)
        final_date = st.date_input("日期:", detected_date if detected_date else datetime.date.today())

    # --- 渲染逻辑 ---
    display_text = f"{final_date} {location}" if location.strip() else f"{final_date}"
    
    # 预览渲染
    preview_draw_img = preview_base.copy()
    draw_pre = ImageDraw.Draw(preview_draw_img)
    try:
        font_pre = ImageFont.truetype("font.ttf", int(font_size_full / scale))
    except:
        font_pre = ImageFont.load_default()
    draw_pre.text((pos_x_pre, pos_y_pre), display_text, fill=selected_color, font=font_pre)
    image_preview_placeholder.image(preview_draw_img, use_container_width=True)

    # --- 高清生成逻辑：使用锁定状态 ---
    if 'processed_bytes' not in st.session_state or st.sidebar.button("🪄 重新生成高清原图"):
        full_draw_img = full_img.copy()
        draw_full = ImageDraw.Draw(full_draw_img)
        try:
            font_full = ImageFont.truetype("font.ttf", font_size_full)
        except:
            font_full = ImageFont.load_default()
        draw_full.text((int(pos_x_pre * scale), int(pos_y_pre * scale)), display_text, fill=selected_color, font=font_full)
        
        buf = io.BytesIO()
        full_draw_img.save(buf, format="JPEG", quality=95)
        st.session_state.processed_bytes = buf.getvalue()

    # --- 保存/下载按钮 ---
    st.write("---")
    # 为文件名加入随机后缀，防止手机端缓存 0B 文件
    time_str = datetime.datetime.now().strftime('%H%M%S')
    st.download_button(
        label="💾 点击保存高清原图到相册",
        data=st.session_state.processed_bytes,
        file_name=f"photo_{time_str}.jpg",
        mime="image/jpeg"
    )
    
    st.warning("⚠️ 若无法保存，请长按上方预览图保存。")

else:
    st.info("请先上传照片。")
