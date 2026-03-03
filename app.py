import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import datetime
from pillow_heif import register_heif_opener
from PIL.ExifTags import TAGS

register_heif_opener()
st.set_page_config(page_title="父母相册助手", layout="centered")

# --- 核心黑科技：缓存底图 (Cache the base image) ---
# 只要不换上传的文件，就不会重新执行读取和旋转逻辑 [cite: 2026-02-26]
@st.cache_data(show_spinner=False)
def load_and_fix_image(file):
    raw_img = Image.open(file)
    # 这一步最耗时，现在被缓存保护起来了 [cite: 2026-02-26]
    img = ImageOps.exif_transpose(raw_img)
    return img

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

st.title("📸 父母相册助手 (V3.4 丝滑版)")

# --- 第一步：上传 (最上方) ---
uploaded_file = st.file_uploader(
    "第一步：点击下方上传照片", 
    type=["jpg", "jpeg", "png", "heic", "heif", "dng"]
)

if uploaded_file:
    # 2. 从缓存读取底图 (Base Image)
    # 即使你动滑块，这一步也会因为缓存而秒开 [cite: 2026-02-26]
    base_img = load_and_fix_image(uploaded_file).copy()
    w, h = base_img.size
    
    # --- 第三步：高级功能 (放在侧边栏，保留伸缩，但不影响实时性) ---
    st.sidebar.header("🎨 高级美化选项")
    color_options = {"亮黄色": "#FFFF00", "纯白色": "#FFFFFF", "大红色": "#FF0000", "黑色": "#000000"}
    selected_color = color_options[st.sidebar.selectbox("文字颜色:", list(color_options.keys()))]
    
    st.sidebar.divider()
    # 坐标调节：现在是实时的，不会闪烁了！ [cite: 2026-02-26]
    pos_x = st.sidebar.slider("左右挪动位置:", 0, w, int(w * 0.1))
    pos_y = st.sidebar.slider("上下挪动位置:", 0, h, int(h * 0.8))

    # --- 第二步：基础设置 (图片下方) ---
    st.subheader("⚙️ 基础文字设置")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        location = st.text_input("地点:", "")
    with col2:
        font_size = st.number_input("字的大小:", 50, 1500, 300)
    with col3:
        detected_date = get_accurate_date(base_img)
        final_date = st.date_input("确认日期:", detected_date if detected_date else datetime.date.today())

    # --- 绘图逻辑 (只重绘文字，不重读照片) ---
    draw = ImageDraw.Draw(base_img)
    display_text = f"{final_date} {location}" if location.strip() else f"{final_date}"
    
    try:
        font = ImageFont.truetype("font.ttf", font_size)
    except:
        font = ImageFont.load_default()

    # 极简绘制
    draw.text((pos_x, pos_y), display_text, fill=selected_color, font=font)
    
    # 实时显示 [cite: 2026-02-26]
    st.image(base_img, caption="预览效果 (满意后长按保存)", use_container_width=True)
    st.success("现在调节滑块，字会实时跟着动了！")

else:
    st.info("请先上传一张照片。")
