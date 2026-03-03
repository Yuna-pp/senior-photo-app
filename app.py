import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import datetime
from pillow_heif import register_heif_opener
from PIL.ExifTags import TAGS

register_heif_opener()
st.set_page_config(page_title="父母相册助手", layout="centered")

# --- 核心缓存：确保大图处理不卡顿 ---
@st.cache_data(show_spinner=False)
def load_and_fix_image(file):
    raw_img = Image.open(file)
    return ImageOps.exif_transpose(raw_img)

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

st.title("📸 相册助手 (稳如泰山版)")

# --- 1. 上传区 ---
uploaded_file = st.file_uploader(
    "第一步：点击下方上传照片", 
    type=["jpg", "jpeg", "png", "heic", "heif", "dng"]
)

if uploaded_file:
    # 加载底图
    base_img = load_and_fix_image(uploaded_file).copy()
    w, h = base_img.size
    
    # --- 2. 侧边栏：高级选项 (保留伸缩) ---
    st.sidebar.header("🎨 样式与精确位置")
    color_options = {"亮黄色": "#FFFF00", "纯白色": "#FFFFFF", "大红色": "#FF0000", "黑色": "#000000"}
    selected_color = color_options[st.sidebar.selectbox("文字颜色:", list(color_options.keys()))]
    
    st.sidebar.divider()
    pos_x = st.sidebar.slider("左右挪动位置:", 0, w, int(w * 0.1))
    pos_y = st.sidebar.slider("上下挪动位置:", 0, h, int(h * 0.8))

    # --- 3. 核心布局修改：先挖坑，后填图 ---
    # 这个占位符会让图片显示在设置按钮的上方
    image_preview_placeholder = st.empty()

    st.divider() # 加一条分割线，视觉更整洁

    # --- 4. 基础设置区 (放在图片下方) ---
    st.subheader("⚙️ 调整文字信息")
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        location = st.text_input("地点 (不填不显示):", "")
    with col2:
        font_size = st.number_input("字的大小:", 50, 1500, 200)
    with col3:
        detected_date = get_accurate_date(base_img)
        # 默认显示检测到的日期，没检测到就显示 2026-03-03
        final_date = st.date_input("日期确认:", detected_date if detected_date else datetime.date.today())

    # --- 5. 绘图渲染 ---
    draw = ImageDraw.Draw(base_img)
    display_text = f"{final_date} {location}" if location.strip() else f"{final_date}"
    
    try:
        font = ImageFont.truetype("font.ttf", font_size)
    except:
        font = ImageFont.load_default()

    draw.text((pos_x, pos_y), display_text, fill=selected_color, font=font)
    
    # 把画好的图塞进刚才挖的“坑”里
    image_preview_placeholder.image(base_img, caption="预览效果 (满意后长按保存)", use_container_width=True)
    
    st.success("调整下方参数，上方的图片会实时变化。")

else:
    st.info("请先上传一张照片。")
