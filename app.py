import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
from PIL.ExifTags import TAGS
import datetime
import os
from pillow_heif import register_heif_opener

# 启动全平台格式支持
register_heif_opener()

st.set_page_config(page_title="父母相册助手", layout="centered")

# --- 核心黑科技：CSS 注入，实现半透明毛玻璃侧边栏 ---
# 这样大爷大妈在手机上拉出设置时，还能隐约看到底下的照片位置
st.markdown("""
    <style>
    /* 侧边栏背景变半透明并加模糊 */
    section[data-testid="stSidebar"] {
        background-color: rgba(255, 255, 255, 0.6) !important;
        backdrop-filter: blur(15px);
    }
    /* 针对手机端滑块的宽度微调 */
    .stSlider {
        padding-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("📸 相册助手 (稳如泰山版)")

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

# --- 侧边栏设置 (现在的侧边栏是半透明的了！) ---
st.sidebar.header("⚙️ 文字设置")
location = st.sidebar.text_input("1. 输入地点 (不填则不显示):", "") 

color_options = {
    "亮黄色 (Yellow)": "#FFFF00", "纯白色 (White)": "#FFFFFF",
    "大红色 (Red)": "#FF0000", "黑色 (Black)": "#000000"
}
selected_color = color_options[st.sidebar.selectbox("2. 选择颜色:", list(color_options.keys()))]
font_size = st.sidebar.slider("3. 字的大小:", 50, 1000, 300)

uploaded_file = st.file_uploader(
    "上传照片 (支持所有手机格式)", 
    type=["jpg", "jpeg", "png", "heic", "heif", "dng", "JPG", "JPEG", "PNG", "HEIC", "HEIF", "DNG"]
)

if uploaded_file:
    try:
        raw_img = Image.open(uploaded_file)
        img = ImageOps.exif_transpose(raw_img)
        
        detected_date = get_accurate_date(img)
        final_date = st.sidebar.date_input("4. 确认日期:", detected_date if detected_date else datetime.date.today())

        draw = ImageDraw.Draw(img)
        w, h = img.size
        
        st.sidebar.header("📍 位置微调")
        # 左右/上下滑块：现在调的时候能看到底下的位置变化了！
        pos_x = st.sidebar.slider("左右位置:", 0, w, int(w * 0.1))
        pos_y = st.sidebar.slider("上下位置:", 0, h, int(h * 0.8))

        display_text = f"{final_date} {location}" if location.strip() else f"{final_date}"

        try:
            font = ImageFont.truetype("font.ttf", font_size)
        except:
            font = ImageFont.load_default()

        # 极简绘制
        draw.text((pos_x, pos_y), display_text, fill=selected_color, font=font)
        
        st.image(img, caption="预览效果 (满意后长按保存)", use_container_width=True)
        st.success("调整完成！快去分享给朋友们吧")
        
    except Exception as e:
        st.error(f"处理失败: {e}")
