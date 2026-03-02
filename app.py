import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import datetime

# 1. 设置网页标题 (Web Page Title)
st.set_page_config(page_title="相册助手", layout="centered")
st.title("📸 父母专属相册加字助手")
st.write("给照片加上时间、地点，留下美好回忆。")

# 2. 侧边栏设置 (Sidebar Settings)
st.sidebar.header("⚙️ 调整文字设置")

# 用户手动输入地点 (Manual Location Input)
location = st.sidebar.text_input("在这里输入地点 (Location):", "北京")

# 用户选择日期 (Date Picker)
date_choice = st.sidebar.date_input("选择日期 (Date):", datetime.date.today())

# 字号调整 (Font Size Slider)
font_size = st.sidebar.slider("字的大小 (Font Size):", 10, 500, 100)

# 颜色选择 (Color Picker)
text_color = st.sidebar.color_picker("字的颜色 (Text Color):", "#FFFF00")

# 3. 文件上传 (File Uploader)
uploaded_file = st.file_uploader("请上传照片 (Upload Photo):", type=["jpg", "png", "jpeg"])

if uploaded_file:
    # 加载图片
    img = Image.open(uploaded_file)
    draw = ImageDraw.Draw(img)
    width, height = img.size

    # 4. 动态位置调整 (Position Sliders)
    # 根据图片的实际宽高来设置滑动条范围
    pos_x = st.sidebar.slider("左右位置 (Left-Right):", 0, width, int(width * 0.7))
    pos_y = st.sidebar.slider("上下位置 (Up-Down):", 0, height, int(height * 0.9))

    # 准备显示的文字
    display_text = f"{date_choice}  {location}"

    # 加载字体 (针对 Colab 或 Linux 云端环境，尝试加载默认字体)
    try:
        # 这个路径是云端服务器常用的字体路径
        font = ImageFont.truetype("/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf", font_size)
    except:
        font = ImageFont.load_default()

    # 画字
    draw.text((pos_x, pos_y), display_text, fill=text_color, font=font)

    # 显示结果
    st.image(img, caption="预览效果 (Preview)", use_column_width=True)

    # 注意：在手机 H5 上，大爷大妈可以直接长按图片保存
    st.success("满意的话，长按上方图片【保存到手机】即可！")