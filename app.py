import streamlit as st
import base64
from PIL import Image, ImageDraw, ImageFont
import re
import io
import regex as re
from fpdf import FPDF

# Define constants
FONT_OPTIONS = {
    "姜浩":"姜浩.ttf",
    "田英章": "田英章楷书.ttf",
    "司马彦":"司马彦.ttf",
    "庞中华": "庞中华.ttf",
    "楷体":"楷体.ttf"
}
TITLE_FONT = "tian.ttf"
DPI = 300
SQUARE_SIZE_CM = 1.5
SQUARE_SIZE = int(SQUARE_SIZE_CM * 118.11)  # Convert cm to pixels at 300 DPI
FONT_SIZE = int(SQUARE_SIZE * 0.8)
FIRST_FONT_COLOR = (0, 0, 0)  # Black color for the first character
SECOND_FONT_COLOR = (205, 145, 148, 255)
BACK_COLOR = 'white'
LINE = 14
ROW = 10
TABLE_COLOR = (76, 173, 206, 255)
MODE = 'RGBA'
PIC_SCHEME = 'png'
TITLE_FONT_SIZE = int(35 * 300 / 72)  # Adjusted font size for high DPI
INFO_FONT_SIZE = int(13 * 300 / 72)  # Adjusted font size for high DPI


# Regular expression for matching Chinese characters
#CHINESE_PATTERN = re.compile(r'[\p{L}\u2e80-\u9fff]+')

CHINESE_PATTERN = re.compile(r'[\u2E80-\u2EFF\u31C0-\u31EF\u4E00-\u9FFF]')


# Example of loading fonts
fonts = {}
for key, font_filename in FONT_OPTIONS.items():
    font_path = os.path.join(os.path.dirname(__file__), font_filename)
    try:
        fonts[key] = ImageFont.truetype(font_path, size=12)  # Adjust size as needed
    except IOError:
        print(f"Error: Cannot load font file '{font_filename}'")

# Example of loading title font
title_font_path = os.path.join(os.path.dirname(__file__), TITLE_FONT)
try:
    title_font = ImageFont.truetype(title_font_path, size=18)  # Adjust size as needed
except IOError:
    print(f"Error: Cannot load title font file '{TITLE_FONT}'")
    
class ArticleProducer:
    def __init__(self, article, text, author='', only_chinese=True):
        self.article = article
        self.text = text
        if only_chinese:
            self.text = ''.join(re.findall(CHINESE_PATTERN, text))
        self.offset = (SQUARE_SIZE - FONT_SIZE) / 2
        self.image = None
        self.draw = None
        
        self.font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
        self.title_font = ImageFont.truetype(TITLE_FONT, TITLE_FONT_SIZE)
        self.info_font = ImageFont.truetype(TITLE_FONT, INFO_FONT_SIZE)
        self._init_painting()
        self.current_color = FIRST_FONT_COLOR

    def _init_painting(self):
        image = Image.new(MODE, (SQUARE_SIZE * (ROW + 2), SQUARE_SIZE * (LINE + 5)), BACK_COLOR)  # Adjusted height for title and info line
        self.draw = ImageDraw.Draw(image)
        self.image = image
        self.create_table()

    def create_table(self):
        skip = SQUARE_SIZE / 2
        for x in range(ROW * 2 + 1):
            width, step = (4, 1) if x % 2 == 0 else (1, 8)
            self.draw_vertical_line(SQUARE_SIZE + x * skip, SQUARE_SIZE * 3, (LINE + 3) * SQUARE_SIZE, width, step)  # Adjusted starting y-coordinate
        for y in range(LINE * 2 + 1):
            width, step = (2, 1) if y % 2 == 0 else (1, 8)
            self.draw_level_line(SQUARE_SIZE, (ROW + 1) * SQUARE_SIZE, SQUARE_SIZE * 3 + y * skip, width, step)  # Adjusted starting y-coordinate

    def draw_vertical_line(self, x, y1, y2, width, step=1):
        for y in range(y1, y2, step):
            self.draw.line([(x, y), (x, y + step / 2)], fill=TABLE_COLOR, width=width)

    def draw_level_line(self, x1, x2, y, width, step=1):
        for x in range(x1, x2, step):
            self.draw.line([(x, y), (x + step / 2, y)], fill=TABLE_COLOR, width=width)

    def paint(self):
        # Draw the title
        title_width, title_height = self.draw.textsize(self.article, font=self.title_font)
        title_x = (self.image.width - title_width) / 2
        self.draw.text((title_x, SQUARE_SIZE), self.article, font=self.title_font, fill='black')
        # Draw the info line
        info_text = "姓名: ________    教师评价：坐姿 ☆☆☆☆☆    等级：________"
        info_width, info_height = self.draw.textsize(info_text, font=self.info_font)
        info_x = (self.image.width - info_width) / 2
        self.draw.text((info_x, SQUARE_SIZE * 2), info_text, font=self.info_font, fill='black')

        # Iterate over characters and draw them
        char_index = 0
        for line in range(6):
            for index in range(ROW):
                if char_index < len(self.text):
                    char = self.text[char_index]
                    self.write_line(char, char_index)
                    char_index += 1  # Move to the next character
        return self.image
    
    def write_line(self, char, y):
        for x in range(ROW):
            y_offset = y * 2 + 2  # Adjusted y-coordinate
            x_offset = (x * SQUARE_SIZE) + SQUARE_SIZE + self.offset
            print(f"x_offset: {x_offset}, y_offset: {y_offset}")
            if x_offset != 195:
                self.current_color = SECOND_FONT_COLOR
            else:
                self.current_color = FIRST_FONT_COLOR
            # Draw character
            self.draw.text((x_offset, SQUARE_SIZE * (y_offset + 1) + self.offset), char, font=self.font, fill=self.current_color, spacing=SQUARE_SIZE)
            
def generate_pdf(title, characters):
    producer = ArticleProducer(article=title, text=characters)
    image = producer.paint()

    # Convert image to bytes
    img_bytes = image_to_bytes(image)

    # Generate and return download link
    href = f'<a href="data:application/octet-stream;base64,{img_bytes}" download="{title}.png">下载 PDF</a>'
    return href

def image_to_bytes(image):
    img_byte_array = io.BytesIO()
    image.save(img_byte_array, format='PNG')
    img_bytes = img_byte_array.getvalue()
    return base64.b64encode(img_bytes).decode()

def images_to_pdf(images):
    pdf = FPDF()
    for image in images:
        img_byte_array = io.BytesIO()
        image.save(img_byte_array, format='PNG')
        img_byte_array.seek(0)
        pdf.add_page()
        pdf.image(img_byte_array, 0, 0, 210, 297)  # A4 size in mm
    pdf_byte_array = io.BytesIO()
    pdf.output(pdf_byte_array, 'F')
    pdf_byte_array.seek(0)
    return pdf_byte_array

st.title("兰芳专属字帖生成网")
title = st.text_input("请输入标题:")
characters_input = st.text_area("请输入汉字 (以逗号分隔):", "")

font_option = st.selectbox("选择字体:", options=list(FONT_OPTIONS.keys()))

if st.button("生成 PDF"):
    characters = characters_input.split("，")

    if characters and title:
        FONT_PATH = FONT_OPTIONS.get(font_option)
        
        images = []
        page_characters = []
        for i, char in enumerate(characters):
            page_characters.append(char)
            if (i + 1) % 7 == 0 or i == len(characters) - 1:
                producer = ArticleProducer(article=title, text=''.join(page_characters))
                images.append(producer.paint())
                page_characters = []

        pdf_byte_array = images_to_pdf(images)
        b64_pdf = base64.b64encode(pdf_byte_array.getvalue()).decode()

        href = f'<a href="data:application/octet-stream;base64,{b64_pdf}" download="{title}.pdf">下载 PDF</a>'
        st.markdown(href, unsafe_allow_html=True)
    else:
        st.error("请输入标题和至少一个汉字。")
