import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
from PIL.ExifTags import TAGS
import datetime
import os

st.set_page_config(page_title="相册助手", layout="centered")
st.title("老人相册助手")

# --- Function: Get Original Date (Jan 4, 2026) ---
# --- 函数：精准获取 1月4日 拍摄日期 ---
def get_safe_date(image):
    try:
        exif = image._getexif()
        if exif:
            for tag_id, value in exif.items():
                tag_name = TAGS.get(tag_id, tag_id)
                if tag_name == "DateTimeOriginal":
                    # Correctly parsing the Jan 4 date from your Fujifilm camera
                    date_str = str(value)[:10].replace(":", "-")
                    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except:
        pass
    return datetime.date(2026, 1, 4) # Default fallback based on your photo

# --- Sidebar: User Controls ---
st.sidebar.header("⚙️ 第一步：文字内容设置")
location = st.sidebar.text_input("1. 输入地点 (Location):", "澳门")

# Seniors' favorite high-contrast colors
color_options = {
    "亮黄色 (Yellow)": "#FFFF00", "纯白色 (White)": "#FFFFFF",
    "大红色 (Red)": "#FF0000", "草绿色 (Green)": "#00FF00",
    "紫色 (Purple)": "#800080", "深蓝色 (Blue)": "#0000FF", "黑色 (Black)": "#000000"
}
selected_color = color_options[st.sidebar.selectbox("2. 选择颜色:", list(color_options.keys()))]
font_size = st.sidebar.slider("3. 字的大小 (Size):", 50, 1000, 300)

uploaded_file = st.file_uploader("第二步：请上传照片 (Upload Photo)", type=["jpg", "png", "jpeg"])

if uploaded_file:
    try:
        # 1. Open and fix orientation (Ensure it's vertical) [cite: 2026-02-26]
        raw_img = Image.open(uploaded_file)
        img = ImageOps.exif_transpose(raw_img)
        
        # 2. Get the correct Jan 4th date
        detected_date = get_safe_date(img)
        final_date = st.sidebar.date_input("4. 确认日期:", detected_date)

        # 3. Preparation for Drawing
        draw = ImageDraw.Draw(img)
        w, h = img.size # Current rotated dimensions
        
        # --- NEW: Dynamic Sliders limited to actual image size ---
        # --- 新增：动态滑块，严格限制在图片尺寸内，防止字“跑丢” ---
        st.sidebar.header("📍 第二步：文字位置微调")
        pos_x = st.sidebar.slider("左右移动 (Left-Right):", 0, w, int(w * 0.1))
        pos_y = st.sidebar.slider("上下移动 (Up-Down):", 0, h, int(h * 0.8))

        display_text = f"{final_date} {location}"
        
        # Debug info for user reassurance
        st.sidebar.write(f"当前准备写入: {display_text}")

        # 4. Load Font
        try:
            font = ImageFont.truetype("font.ttf", font_size)
        except:
            st.warning("未找到字体文件，使用默认字体 (字会很小)")
            font = ImageFont.load_default()

        # 5. DRAW WITH STROKE (The Secret to Visibility!)
        # 使用“描边”功能，确保在任何背景下都清晰可见
        # In Java: g2d.setStroke(new BasicStroke(5));
        draw.text(
            (pos_x, pos_y), 
            display_text, 
            fill=selected_color, 
            font=font,
            stroke_width=int(font_size/15), # Automatic stroke thickness
            stroke_fill="#000000"           # Black outline
        )
        
        # 6. Final Display
        st.image(img, caption=f"预览效果 - 照片尺寸: {w}x{h}", use_container_width=True)
        st.success("这回一定能看到了！满意后长按保存。")
        
    except Exception as e:
        st.error(f"运行出错了: {e}")
