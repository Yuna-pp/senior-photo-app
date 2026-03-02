import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
from PIL.ExifTags import TAGS
import datetime
import os

# Set page title and layout
# 设置网页标题和布局
st.set_page_config(page_title="相册助手", layout="centered")
st.title("老人相册助手")

# --- Function: Get Original Date from Metadata ---
# --- 函数：从元数据中获取原始拍摄日期 ---
def get_original_date(image):
    """
    Tries to find the 'DateTimeOriginal' from EXIF.
    尝试从 EXIF 中寻找“原始拍摄日期”。
    """
    try:
        exif = image._getexif()
        if exif:
            for tag, value in exif.items():
                decoded = TAGS.get(tag, tag)
                if decoded == "DateTimeOriginal":
                    # Format: "2026:01:04 12:00:00" -> "2026-01-04"
                    return datetime.datetime.strptime(value.split(" ")[0], "%Y:%m:%d").date()
    except:
        pass
    return datetime.date.today()

# --- Sidebar: User Controls ---
# --- 侧边栏：用户控制面板 ---
st.sidebar.header("⚙️ 第一步：文字设置")

# 1. Location Input
location = st.sidebar.text_input("1. 输入地点 (Location):", "北京")

# 2. Color Selection (Dropdown)
# 颜色选择：提供大爷大妈最爱的几种高对比度颜色
color_options = {
    "亮黄色 (Yellow)": "#FFFF00",
    "纯白色 (White)": "#FFFFFF",
    "大红色 (Red)": "#FF0000",
    "草绿色 (Green)": "#00FF00",
    "紫色 (Purple)": "#800080",
    "深蓝色 (Blue)": "#0000FF",
    "黑色 (Black)": "#000000"
}
selected_color_name = st.sidebar.selectbox("2. 选择颜色 (Color):", list(color_options.keys()))
text_color = color_options[selected_color_name]

# 3. Font Size Slider (Increased range for high-res photos)
# 字号调整：针对高分辨率照片，上限调到 2000
font_size = st.sidebar.slider("3. 字的大小 (Size):", 50, 2000, 400)

# --- Main Area: File Upload ---
# --- 主区域：文件上传 ---
uploaded_file = st.file_uploader("第二步：请上传照片", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # A. Open and Fix Orientation (解决“照片躺平”问题)
    # 使用 exif_transpose 自动旋转照片到正确方向
    raw_img = Image.open(uploaded_file)
    img = ImageOps.exif_transpose(raw_img)
    
    # B. Extract Date (解决“日期不对”问题)
    # 自动获取 1月4日 这种原始时间
    detected_date = get_original_date(img)
    
    # Allow user to manually adjust date if detection is wrong
    # 允许用户在侧边栏手动微调日期（双重保险）
    final_date = st.sidebar.date_input("4. 确认日期 (Date):", detected_date)

    # C. Draw the Text (绘图逻辑)
    draw = ImageDraw.Draw(img)
    width, height = img.size
    
    # Position Sliders (位置调整)
    st.sidebar.header("📍 第二步：移动位置")
    pos_x = st.sidebar.slider("左右移动:", 0, width, int(width * 0.5))
    pos_y = st.sidebar.slider("上下移动:", 0, height, int(height * 0.8))

    display_text = f"{final_date} {location}"

    # Load Font (加载仓库里的字体文件)
    # Make sure 'ziti.ttf' is in your GitHub
