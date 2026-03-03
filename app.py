import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import datetime
import io
import base64
from pillow_heif import register_heif_opener
from PIL.ExifTags import TAGS

register_heif_opener()
st.set_page_config(page_title="父母相册助手", layout="centered")

# --- 1. 间距优化 CSS (基于用户反馈已解决) ---
st.markdown("""
    <style>
    div[data-testid="stImage"] > img { margin-bottom: -40px !important; }
    div[data-testid="stVerticalBlock"] > div { margin-top: -15px !important; }
    .stNumberInput, .stTextInput, .stDateInput { margin-top: -20px !important; }
    </style>
    """, unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load_and_fix_image(file):
    raw_img = Image.open(file)
    full_img = ImageOps.exif_transpose(raw_img)
    return full_img

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

# --- NEW: 将 PIL 图片转为 Base64 编码 (解决 0B 下载问题) [cite: 2026-02-26] ---
def get_image_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG", quality=95)
    return base64.b64encode(buffered.getvalue()).decode()

st.title("📸 老人相册助手 (稳如泰山版)")

uploaded_file = st.file_uploader("第一步：上传照片", type=["jpg", "jpeg", "png", "heic", "heif", "dng"])

if uploaded_file:
    full_img = load_and_fix_image(uploaded_file)
    w_full, h_full = full_img.size

    st.sidebar.header("🎨 样式与位置")
    color_options = {"亮黄色": "#FFFF00", "纯白色": "#FFFFFF", "大红色": "#FF0000", "黑色": "#000000"}
    selected_color = color_options[st.sidebar.selectbox("文字颜色:", list(color_options.keys()))]
    
    # 滑块范围：现在直接在主图坐标系上操作 [cite: 2026-02-26]
    pos_x = st.sidebar.slider("左右挪动位置:", 0, w_full, int(w_full * 0.1))
    pos_y = st.sidebar.slider("上下挪动位置:", 0, h_full, int(h_full * 0.8))

    # --- 设置区 ---
    st.subheader("⚙️ 文字设置")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        location = st.text_input("地点 (选填):", "")
    with col2:
        font_size = st.number_input("字号:", 10, 2000, 300)
    with col3:
        detected_date = get_accurate_date(full_img)
        final_date = st.date_input("日期:", detected_date if detected_date else datetime.date.today())

    # --- 渲染逻辑 ---
    display_text = f"{final_date} {location}" if location.strip() else f"{final_date}"
    
    # 在原图上绘制
    processed_img = full_img.copy()
    draw = ImageDraw.Draw(processed_img)
    try:
        font = ImageFont.truetype("font.ttf", font_size)
    except:
        font = ImageFont.load_default()
    draw.text((pos_x, pos_y), display_text, fill=selected_color, font=font)

    # --- 核心修复：微信保存逻辑 ---
    img_base64 = get_image_base64(processed_img)
    # 使用 HTML 标签显示图片，这样微信才会识别它是“一张真正的图片”，从而允许长按保存 [cite: 2026-02-26]
    st.markdown(f'<img src="data:image/jpeg;base64,{img_base64}" style="width:100%;">', unsafe_allow_html=True)
    
    st.success("✅ 处理完成！")
    st.info("直接长按保存即可获得高清画质。")

else:
    st.info("请先上传照片。")
