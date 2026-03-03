import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import datetime
import io
from pillow_heif import register_heif_opener
from PIL.ExifTags import TAGS

register_heif_opener()
st.set_page_config(page_title="相册助手-终极稳健版", layout="centered")

# --- CSS 强力收紧间距 ---
st.markdown("""
    <style>
    div[data-testid="stVerticalBlock"] > div { margin-top: -20px !important; }
    .stImage { margin-bottom: -30px !important; }
    /* 让高清生成区更有仪式感 */
    .save-box { border: 3px solid #28a745; border-radius: 10px; padding: 5px; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load_and_fix_image(file):
    raw_img = Image.open(file)
    full_img = ImageOps.exif_transpose(raw_img)
    # 强制瘦身预览图：固定小尺寸确保任何手机秒开 [cite: 2026-03-03]
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

st.title("📸 相册助手 (稳如泰山版)")

uploaded_file = st.file_uploader("第一步：上传照片", type=["jpg", "jpeg", "png", "heic", "heif"])

# 1. 顶部预览占位符
image_placeholder = st.empty()

if uploaded_file:
    full_img, preview_img = load_and_fix_image(uploaded_file)
    w_full, h_full = full_img.size
    w_pre, h_pre = preview_img.size
    scale = w_full / w_pre

    # --- 设置区 ---
    st.subheader("⚙️ 调整文字信息")
    location = st.text_input("地点 (选填):", "")
    font_size_full = st.number_input("字的大小 (建议300-500):", 50, 2000, 200)
    final_date = st.date_input("日期确认:", get_accurate_date(full_img) or datetime.date.today())

    st.sidebar.header("🎨 位置调节")
    pos_x_pre = st.sidebar.slider("左右:", 0, w_pre, int(w_pre * 0.1))
    pos_y_pre = st.sidebar.slider("上下:", 0, h_pre, int(h_pre * 0.8))

    # --- 预览渲染 ---
    display_text = f"{final_date} {location}" if location.strip() else f"{final_date}"
    preview_draw = preview_img.copy()
    draw_p = ImageDraw.Draw(preview_draw)
    try:
        font_p = ImageFont.truetype("font.ttf", int(font_size_full / scale))
    except:
        font_p = ImageFont.load_default()
    draw_p.text((pos_x_pre, pos_y_pre), display_text, fill="#FFFF00", font=font_p)
    image_placeholder.image(preview_draw, use_container_width=True, caption="预览效果 (调好后点下方生成保存版)")

    st.write("---")
    
    # --- 2. 核心改进：回归 st.image 渲染高清图 (解决空白问题) ---
    if st.checkbox("✨ 调好了，点击生成高清保存图"):
        with st.spinner("正在生成高清原图..."):
            full_draw_img = full_img.copy()
            # 动态限高：为了防止原图太大导致手机浏览器崩溃，强制限高 3000px [cite: 2026-03-03]
            if full_draw_img.width > 3000:
                full_draw_img.thumbnail((3000, 3000))
                # 重新计算缩放比例
                scale_new = full_draw_img.width / w_pre
            else:
                scale_new = scale

            draw_f = ImageDraw.Draw(full_draw_img)
            try:
                font_f = ImageFont.truetype("font.ttf", int(font_size_full * (scale_new / scale)))
            except:
                font_f = ImageFont.load_default()
            
            # 绘制最终高清图
            draw_f.text((int(pos_x_pre * scale_new), int(pos_y_pre * scale_new)), display_text, fill="#FFFF00", font=font_f)
            
            # 使用原生 st.image 渲染，避开 Base64 的超长字符串限制 [cite: 2026-03-03]
            st.image(full_draw_img, caption="✅ 已生成高清图，请长按此图保存", use_container_width=True)
            st.success("好了！请‘长按’上方这张高清图选择保存。")

else:
    st.info("请先上传照片。")
