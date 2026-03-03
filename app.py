import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import datetime
import io
import base64
from pillow_heif import register_heif_opener
from PIL.ExifTags import TAGS

register_heif_opener()
st.set_page_config(page_title="相册助手-稳如泰山版", layout="centered")

# --- 强力 CSS：收紧间距 ---
st.markdown("""
    <style>
    div[data-testid="stVerticalBlock"] > div { margin-top: -20px !important; }
    .stImage { margin-bottom: -30px !important; }
    </style>
    """, unsafe_allow_html=True)

# 核心优化：加载时强制生成一个超小的预览图 [cite: 2026-03-03]
@st.cache_data(show_spinner=False)
def load_and_fix_image(file):
    raw_img = Image.open(file)
    full_img = ImageOps.exif_transpose(raw_img)
    
    # 强制给预览图“瘦身”：宽度固定为 600 像素，确保华为手机秒开 [cite: 2026-03-03]
    preview_img = full_img.copy()
    preview_img.thumbnail((600, 600)) 
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
    except: pass
    return None

def get_image_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG", quality=85) # 适当降低质量确保 Base64 不溢出
    return base64.b64encode(buffered.getvalue()).decode()

st.title("📸 相册助手（稳如泰山版）")

uploaded_file = st.file_uploader("第一步：上传照片", type=["jpg", "jpeg", "png", "heic", "heif"])

# 1. 顶部预览占位符
image_placeholder = st.empty()

if uploaded_file:
    # 加载两个版本的图
    full_img, preview_img = load_and_fix_image(uploaded_file)
    w_full, h_full = full_img.size
    w_pre, h_pre = preview_img.size
    scale = w_full / w_pre

    # --- 基础设置 (图片下方) ---
    st.subheader("⚙️ 调整文字信息")
    location = st.text_input("地点 (选填):", "")
    font_size_full = st.number_input("字的大小:", 50, 2000, 400)
    final_date = st.date_input("日期:", get_accurate_date(full_img) or datetime.date.today())

    # 侧边栏调位置
    st.sidebar.header("🎨 位置调节")
    pos_x_pre = st.sidebar.slider("左右:", 0, w_pre, int(w_pre * 0.1))
    pos_y_pre = st.sidebar.slider("上下:", 0, h_pre, int(h_pre * 0.8))

    # --- 渲染预览图 (这一步现在非常轻量了！) ---
    display_text = f"{final_date} {location}" if location.strip() else f"{final_date}"
    preview_draw = preview_img.copy()
    draw_p = ImageDraw.Draw(preview_draw)
    try:
        font_p = ImageFont.truetype("font.ttf", int(font_size_full / scale))
    except:
        font_p = ImageFont.load_default()
    draw_p.text((pos_x_pre, pos_y_pre), display_text, fill="#FFFF00", font=font_p)
    
    # 强制让手机先看到这张瘦身后的预览图 [cite: 2026-03-03]
    image_placeholder.image(preview_draw, use_container_width=True, caption="预览区 (满意后再点下方生成)")

    st.write("---")
    
    # --- 微信保存逻辑 ---
    if st.checkbox("✨ 调好了，生成可长按保存的高清图"):
        with st.spinner("正在生成高清原图..."):
            full_draw_img = full_img.copy()
            draw_f = ImageDraw.Draw(full_draw_img)
            try:
                font_f = ImageFont.truetype("font.ttf", font_size_full)
            except:
                font_f = ImageFont.load_default()
            draw_f.text((int(pos_x_pre * scale), int(pos_y_pre * scale)), display_text, fill="#FFFF00", font=font_f)
            
            img_base64 = get_image_base64(full_draw_img)
            st.markdown(
                f'<img src="data:image/jpeg;base64,{img_base64}" style="width:100%; border: 3px solid #28a745;">',
                unsafe_allow_html=True
            )
            st.success("✅ 好了！请长按上方‘带绿色框’的图保存。")
