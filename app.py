import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
from PIL.ExifTags import TAGS
import datetime
import os
from pillow_heif import register_heif_opener

# 启动苹果 HEIC 格式支持
register_heif_opener()

st.set_page_config(page_title="相册助手", layout="centered")
st.title("📸 父母相册助手")

def get_accurate_date(image):
    """
    地毯式搜索：尝试从所有可能的元数据槽位中抓取拍摄日期
    """
    try:
        # 1. 尝试标准 EXIF (适用于绝大多数情况)
        exif = image.getexif()
        if exif:
            for tag_id, value in exif.items():
                tag_name = TAGS.get(tag_id, tag_id)
                if tag_name in ["DateTimeOriginal", "DateTime"]:
                    date_str = str(value)[:10].replace(":", "-")
                    return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()

        # 2. 深度扫描（针对某些 HEIC 的特殊存储位）
        info = image.info
        if 'exif' in info:
            # 再次尝试从 info 字典里捞数据
            exif_raw = image._getexif()
            if exif_raw:
                for tag_id, value in exif_raw.items():
                    tag_name = TAGS.get(tag_id, tag_id)
                    if tag_name == "DateTimeOriginal":
                        date_str = str(value)[:10].replace(":", "-")
                        return datetime.datetime.strptime(date_str, "%Y-%m-%d").date()
    except Exception as e:
        print(f"扫描异常: {e}")
    
    # 3. 如果实在找不到，返回 None，让用户在界面上自己选，而不是给个错的
    return None

# --- 侧边栏设置 ---
st.sidebar.header("⚙️ 第一步：文字设置")
location = st.sidebar.text_input("1. 手动输入地点:", "俄罗斯堪察加") # 根据你的新照片改了默认值

color_options = {
    "亮黄色 (Yellow)": "#FFFF00", "纯白色 (White)": "#FFFFFF",
    "大红色 (Red)": "#FF0000", "草绿色 (Green)": "#00FF00",
    "紫色 (Purple)": "#800080", "深蓝色 (Blue)": "#0000FF", "黑色 (Black)": "#000000"
}
selected_color = color_options[st.sidebar.selectbox("2. 选择颜色:", list(color_options.keys()))]
font_size = st.sidebar.slider("3. 字的大小:", 50, 1000, 300)

uploaded_file = st.file_uploader("第二步：上传照片", type=["jpg", "png", "jpeg", "heic", "HEIC"])

if uploaded_file:
    try:
        raw_img = Image.open(uploaded_file)
        img = ImageOps.exif_transpose(raw_img) # 扶正照片
        
        # 抓取日期
        detected_date = get_accurate_date(img)
        
        # 逻辑判断：如果抓到了就用抓到的，没抓到就用今天，并在界面提示
        if detected_date:
            final_date = st.sidebar.date_input("4. 自动检测到日期:", detected_date)
            st.sidebar.success(f"✅ 已成功读取拍摄时间：{detected_date}")
        else:
            final_date = st.sidebar.date_input("4. 未检测到日期，请手动选择:", datetime.date.today())
            st.sidebar.warning("🔎 照片里没翻到时间，请手动在上面改一下。")

        # 画图逻辑
        draw = ImageDraw.Draw(img)
        w, h = img.size
        
        st.sidebar.header("📍 第二步：位置微调")
        pos_x = st.sidebar.slider("左右位置:", 0, w, int(w * 0.1))
        pos_y = st.sidebar.slider("上下移动:", 0, h, int(h * 0.8))

        display_text = f"{final_date} {location}"

        try:
            font = ImageFont.truetype("font.ttf", font_size)
        except:
            font = ImageFont.load_default()

        # 增加描边宽度，增强大爷大妈的视觉体验 [cite: 2026-02-26]
        draw.text(
            (pos_x, pos_y), 
            display_text, 
            fill=selected_color, 
            font=font,
            stroke_width=int(font_size/12),
            stroke_fill="#000000"
        )
        
        st.image(img, caption=f"预览效果 - 拍摄日期: {final_date}", use_container_width=True)
        st.success("这回日期如果还不对，我就去新西兰帮你修电脑！")
        
    except Exception as e:
        st.error(f"运行崩了: {e}")
