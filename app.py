import streamlit as st
import base64
from PIL import Image, ImageDraw, ImageFont
import regex as re
from fpdf import FPDF
import tempfile
import concurrent.futures

# Define constants
FONT_OPTIONS = {
    "姜浩":"./font/姜浩.ttf",
    "田英章": "./font/田英章楷书.ttf",
    "司马彦":"./font/司马彦.ttf",
    "庞中华": "./font/庞中华.ttf",
    "楷体":"./font/楷体.ttf"
}
TITLE_FONT = "./font/tian.ttf"
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
CHINESE_PATTERN = re.compile(r'[\u2E80-\u2EFF\u31C0-\u31EF\u4E00-\u9FFF]')

class ArticleProducer:
    def __init__(self, article, text, font_path, only_chinese=True):
        self.article = article
        self.text = text
        if only_chinese:
            self.text = ''.join(re.findall(CHINESE_PATTERN, text))
        self.offset = (SQUARE_SIZE - FONT_SIZE) / 2
        self.image = None
        self.draw = None
        self.font = ImageFont.truetype(font_path, FONT_SIZE)
        self.title_font = ImageFont.truetype(TITLE_FONT, TITLE_FONT_SIZE)
        self.info_font = ImageFont.truetype(TITLE_FONT, INFO_FONT_SIZE)
        self.current_color = FIRST_FONT_COLOR
        #self._init_painting()

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

    def write_line(self, char, y):
        for x in range(ROW):
            y_offset = y * 2 + 2  # Adjusted y-coordinate
            x_offset = (x * SQUARE_SIZE) + SQUARE_SIZE + self.offset
            if x_offset != 195:
                self.current_color = SECOND_FONT_COLOR
            else:
                self.current_color = FIRST_FONT_COLOR
            # Draw character
            self.draw.text((x_offset, SQUARE_SIZE * (y_offset + 1) + self.offset), char, font=self.font, fill=self.current_color, spacing=SQUARE_SIZE)

    def paint(self):
        image = Image.new(MODE, (SQUARE_SIZE * (ROW + 2), SQUARE_SIZE * (LINE + 5)), BACK_COLOR)  # Adjusted height for title and info line
        self.draw = ImageDraw.Draw(image)
        self.image = image
        self.create_table()
        # Draw the title
        title_width = self.draw.textlength(self.article, font=self.title_font)
        title_x = (self.image.width - title_width) / 2
        self.draw.text((title_x, SQUARE_SIZE), self.article, font=self.title_font, fill='black')
        # Draw the info line
        info_text = "姓名： ________    教师评价：坐姿 ☆☆☆☆☆    等级：________"
        info_width = self.draw.textlength(info_text, font=self.info_font)
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
    
    def create_table_2(self, start_x, start_y):
        skip = SQUARE_SIZE / 2
        for x in range(10 * 2 + 1):
            width, step = (4, 1) if x % 2 == 0 else (1, 8)
            self.draw_vertical_line(start_x + x * skip, start_y + SQUARE_SIZE * 3, start_y + (2 + 3) * SQUARE_SIZE, width, step)
        for y in range(2 * 2 + 1):
            width, step = (2, 1) if y % 2 == 0 else (1, 8)
            self.draw_level_line(SQUARE_SIZE, (10 + 1) * SQUARE_SIZE, start_y + SQUARE_SIZE * 3 + y * skip, width, step)
            
    def write_line_2(self, char, y, x):
        if x < 10:
            y_offset = y * 2 + 3  # Adjusted y-coordinate
            x_offset = (x * SQUARE_SIZE) + SQUARE_SIZE + self.offset
        else:
            y_offset = y * 2 + 2  # Adjusted y-coordinate
            x_offset = ((x - 10) * SQUARE_SIZE) + SQUARE_SIZE + self.offset
        # Draw character
        self.current_color = SECOND_FONT_COLOR
        print(f"x_offset: {x_offset}, y_offset: {y_offset}")
        self.draw.text((x_offset, SQUARE_SIZE * (y_offset + 1) + self.offset), char, font=self.font, fill=self.current_color, spacing=SQUARE_SIZE)

    def paint_2(self): 
        image = Image.new(MODE, (SQUARE_SIZE * (ROW + 2), SQUARE_SIZE * (LINE + 5)), BACK_COLOR)  # Adjusted height for title and info line
        self.draw = ImageDraw.Draw(image)
        self.image = image
        # Draw the title
        title_width = self.draw.textlength(self.article, font=self.title_font)
        title_x = (self.image.width - title_width) / 2
        self.draw.text((title_x, SQUARE_SIZE), self.article, font=self.title_font, fill='black')
        # Draw the info line
        info_text = "姓名：________        性别：________        年龄：________"
        info_width = self.draw.textlength(info_text, font=self.info_font)
        info_x = (self.image.width - info_width) / 2
        self.draw.text((info_x, SQUARE_SIZE * 2.5), info_text, font=self.info_font, fill='black')
        # Draw first two rows
        self.create_table_2(SQUARE_SIZE, SQUARE_SIZE * 1)
        # Draw the info
        text = "培训前书写："
        self.draw.text((SQUARE_SIZE, SQUARE_SIZE * 7), text, font=self.info_font, fill='black')
        # Draw second two rows
        self.create_table_2(SQUARE_SIZE, SQUARE_SIZE * 5)
        # Draw the info
        text = "------------------------------------------------------------------------------------------------------"
        self.draw.text((SQUARE_SIZE, SQUARE_SIZE * 11), text, font=self.info_font, fill='black')
        text = "培训后书写：  "
        self.draw.text((SQUARE_SIZE, SQUARE_SIZE * 12), text, font=self.info_font, fill='black')
        self.create_table_2(SQUARE_SIZE, SQUARE_SIZE * 10)
        
        # Iterate over characters and draw them
        char_index = 0
        for line in range(6):
            for index in range(10):
                if char_index < len(self.text):
                    print(f"len of text: {len(self.text)}, char index: {char_index}")
                    if char_index < 10:
                        char = self.text[char_index]
                        self.write_line_2(char, 0, char_index)
                    else:
                        char = self.text[char_index]
                        self.write_line_2(char, 1, char_index)
                    char_index += 1  # Move to the next character
        return self.image
        
    def img_to_pdf(self, images):
        pdf = FPDF()
        for image in images:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            image.save(temp_file.name, format='PNG')
            pdf.add_page()
            pdf.image(temp_file.name, x=10, y=10, w=190)
            temp_file.close()
        return pdf.output(dest='S').encode('latin1')

def generate_page(article, text, font_path, zitie_type):
    if zitie_type == "普通":
        producer = ArticleProducer(article=article, text=text, font_path=font_path)
        return producer.paint()
    elif "测评表":
        producer = ArticleProducer(article=article, text=text, font_path=font_path)
        return producer.paint_2()

st.title("♡兰芳专属♡")
title = st.text_input("请输入标题:")
characters_input = st.text_area("请输入汉字 (以逗号分隔):", "")

font_option = st.selectbox("选择字体:", options=list(FONT_OPTIONS.keys()))

zitie_type = st.selectbox("选择格式:", options={"普通", "测评表"})

if st.button("生成 PDF"):
    characters = characters_input.split("，")
    
    if characters and title:
        FONT_PATH = FONT_OPTIONS.get(font_option)
        images = []
        page_characters = []
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for i, char in enumerate(characters):
                page_characters.append(char)
                if zitie_type == "普通":
                    if (i + 1) % 6 == 0 or i == len(characters) - 1:
                        futures.append(executor.submit(generate_page, title, ''.join(page_characters), FONT_PATH, zitie_type))
                        page_characters = []
                elif zitie_type == "测评表":
                    if (i + 1) % 20 == 0:
                        futures.append(executor.submit(generate_page, title, ''.join(page_characters), FONT_PATH, zitie_type))
                        page_characters = []

            for future in concurrent.futures.as_completed(futures):
                images.append(future.result())

        pdf_bytes = ArticleProducer(title, '', FONT_PATH).img_to_pdf(images)
        b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
        href = f'<a href="data:application/pdf;base64,{b64_pdf}" download="{title}.pdf">下载 PDF</a>'
        st.markdown(href, unsafe_allow_html=True)
    else:
       st.error("请输入标题和至少一个汉字。")

        
        

