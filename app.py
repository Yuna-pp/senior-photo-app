import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import datetime
import io
from pillow_heif import register_heif_opener
from PIL.ExifTags import TAGS

register_heif_opener()
st.set_page_config(page_title="父母相册助手", layout="centered")

# --- 1. CSS 紧凑布局优化 ---
st.markdown("""
    <style>
    .stImage { margin-bottom: -30px !important; }
    .stMarkdown h3 { margin-top: -10px !important; padding-bottom: 5px !important; }
    [data-testid="stVerticalBlock"] { gap: 0.5rem !important; }
    /* 下载按钮样式增强 */
    .stDownloadButton>button {
        width: 100%;
        background-color: #00c029;
        color: white;
        height: 3em;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 核心加载与缓存 ---
@st.cache_data(show_spinner=False)
def load_and_fix_image(file):
    raw_img = Image.open(file)
    full_img = ImageOps.exif_transpose(raw_img)
    # 生成轻量预览图提升滑动性能 [cite: 2026-02-26]
    preview_img = full_img.copy()
    preview_img.thumbnail((1000, 1000)) 
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
    except:
        pass
    return None

st.title("📸 父母相册助手 (V3.7 高清原图版)")

uploaded_file = st.file_uploader("第一步：上传照片", type=["jpg", "jpeg", "png", "heic", "heif", "dng"])

if uploaded_file:
    # 加载原图和预览底图
    full_img, preview_base = load_and_fix_image(uploaded_file)
    w_full, h_full = full_img.size
    w_pre, h_pre = preview_base.size
    scale = w_full / w_pre  # 计算原图与预览图的比例 [cite: 2026-02-26]

    # --- 侧边栏：高级选项 ---
    st.sidebar.header("🎨 样式与精确位置")
    color_options = {"亮黄色": "#FFFF00", "纯白色": "#FFFFFF", "大红色": "#FF0000", "黑色": "#000000"}
    selected_color = color_options[st.sidebar.selectbox("文字颜色:", list(color_options.keys()))]
    
    # 滑块：在预览图坐标系上操作
    pos_x_pre = st.sidebar.slider("左右挪动位置:", 0, w_pre, int(w_pre * 0.1))
    pos_y_pre = st.sidebar.slider("上下挪动位置:", 0, h_pre, int(h_pre * 0.8))

    # --- 图片预览占位符 ---
    image_preview_placeholder = st.empty()

    # --- 第三步：基础设置区 (位于图片下方) ---
    st.subheader("⚙️ 调整文字信息")
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        location = st.text_input("地点 (不填不显示):", "")
    with col2:
        # 这里的字号是针对“原图”设置的，方便下载后清晰
        font_size_full = st.number_input("字的大小 (原图尺寸):", 10, 2000, 100)
    with col3:
        detected_date = get_accurate_date(full_img)
        final_date = st.date_input("日期确认:", detected_date if detected_date else datetime.date.today())

    # --- 绘图逻辑：预览与高清同步 ---
    display_text = f"{final_date} {location}" if location.strip() else f"{final_date}"
    
    # 1. 在预览图上绘制 (用于实时观察)
    preview_draw_img = preview_base.copy()
    draw_pre = ImageDraw.Draw(preview_draw_img)
    try:
        # 预览图字号按比例缩小
        font_pre = ImageFont.truetype("font.ttf", int(font_size_full / scale))
    except:
        font_pre = ImageFont.load_default()
    draw_pre.text((pos_x_pre, pos_y_pre), display_text, fill=selected_color, font=font_pre)
    image_preview_placeholder.image(preview_draw_img, caption="预览效果 (调整下方参数)", use_container_width=True)

    # 2. 在原图上绘制 (用于下载)
    # 这步只有在准备下载或生成时才最关键
    full_draw_img = full_img.copy()
    draw_full = ImageDraw.Draw(full_draw_img)
    try:
        font_full = ImageFont.truetype("font.ttf", font_size_full)
    except:
        font_full = ImageFont.load_default()
    # 坐标按比例放大回原图坐标系 [cite: 2026-02-26]
    draw_full.text((int(pos_x_pre * scale), int(pos_y_pre * scale)), display_text, fill=selected_color, font=font_full)

    # --- 第四步：下载原图按钮 ---
    # 将 PIL 图片转化为二进制流 [cite: 2026-02-26]
    buf = io.BytesIO()
    full_draw_img.save(buf, format="JPEG", quality=95)
    byte_im = buf.getvalue()

    st.divider()
    st.download_button(
        label="💾 点击下载高清原图 (保存至相册)",
        data=byte_im,
        file_name=f"processed_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.jpg",
        mime="image/jpeg"
    )
    st.info("提示：长按图片只能保存缩略图，请点击上方绿色按钮下载原图画质。")

else:
    st.info("请先上传照片。")
