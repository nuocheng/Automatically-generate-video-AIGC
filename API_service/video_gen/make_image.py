#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
    Module Documentation 
    here
"""

# Created by  : Zhang Chengdong
# Create Date : 2024/7/24 20:15
# Version = v0.1.0

__author__ = "Zhang Chengdong And Sun Maokang"
__copyright__ = "Copyright 2024. Large scale model"
__credits__ = ['Zhang Chengdong']

__liscence__ = "MIT"
__version__ = "1.0.1"
__maintainer__ = "Zhang Chengdong And Sun Maokang"
__status__ = "Production"

import os
import math
import numpy as np
import cv2
from time import time
from tqdm import tqdm
from PIL import Image, ImageDraw, ImageFont
from django.conf import settings


def calculate_font_size(image_width, image_height, base_font_size, base_image_width, base_image_height):
    base_area = base_image_width * base_image_height
    target_area = image_width * image_height
    area_ratio = target_area / base_area
    suggested_font_size = base_font_size * math.sqrt(area_ratio)
    return round(suggested_font_size)


def get_all_files(parent_folder):
    all_files = []
    for root, dirs, files in os.walk(parent_folder):
        for file in files:
            file_path = os.path.join(root, file)
            all_files.append(file_path)
    return all_files


def draw_trapezoid(draw, coords, fill_color):
    draw.polygon(coords, fill=fill_color)


def draw_text(draw, text, position, font, fill_color):
    draw.text(position, text, fill=fill_color, font=font)


def create_gradient(width, height, color):
    gradient = Image.new('RGBA', (width, height), color=0)
    for x in range(gradient.width):
        for y in range(gradient.height):
            alpha = 255 if x < 4 * gradient.width / 5 else int(
                255 * (1 - (x - 4 * gradient.width / 5) / (gradient.width / 5)))
            gradient.putpixel((x, y), (color[0], color[1], color[2], alpha))
    return gradient


def process_image(input_image_path, font_path):
    """

    :param input_image_path:
    :param font_path:
    :return:
    """
    file_name = os.path.basename(input_image_path)
    parent_directory = os.path.dirname(input_image_path)
    info_desc = file_name.split('.')[0].split(";")
    part1_text = str(info_desc[0])
    part2_text = str(info_desc[1])
    part3_text = str(info_desc[2])
    image_xy = cv2.imdecode(np.fromfile(input_image_path, dtype=np.uint8), cv2.IMREAD_COLOR)
    height_xy, width_xy = image_xy.shape[:2]
    max_x = width_xy - 1
    max_y = height_xy - 1

    image = Image.open(input_image_path)
    draw = ImageDraw.Draw(image)

    title_bar_color = (40, 91, 160)
    text_color = (255, 255, 255)
    image_name_color = (187, 31, 36)
    gray_bar_color = (169, 169, 169)
    gray_text_color = (0, 0, 0)

    font_size_title = calculate_font_size(max_x, max_y, 13, 552, 310)
    font_size_image_title = calculate_font_size(max_x, max_y, 12, 552, 310)
    font_size_text = calculate_font_size(max_x, max_y, 15, 552, 310)

    font_title = ImageFont.truetype(font_path, int(font_size_title))
    font_image_title = ImageFont.truetype(font_path, int(font_size_image_title))
    font_text = ImageFont.truetype(font_path, int(font_size_text))

    text_padding = 7
    title_text = part1_text
    title_bbox = draw.textbbox((0, 0), title_text, font=font_title)
    title_width = title_bbox[2] - title_bbox[0]
    title_height = title_bbox[3] - title_bbox[1]

    title_bar_x = int(max_x * 35 / 552)
    title_bar_y = int(max_y * 250 / 310)

    title_bar_left = title_bar_x
    title_bar_top = title_bar_y
    title_bar_right = title_bar_left + title_width + 1 * text_padding
    title_bar_bottom = title_bar_top + title_height + 1 * text_padding

    trapezoid_top_width = title_width + 1 * text_padding
    trapezoid_bottom_width = trapezoid_top_width - 20

    trapezoid_coords = [
        (title_bar_left, title_bar_top),
        (title_bar_left + trapezoid_top_width + 5, title_bar_top),
        (title_bar_left + int((trapezoid_top_width - trapezoid_bottom_width) / 2) + trapezoid_bottom_width + 5,
         title_bar_bottom),
        (title_bar_left, title_bar_bottom)
    ]

    draw_trapezoid(draw, trapezoid_coords, title_bar_color)

    title_text_x = title_bar_left + int((trapezoid_top_width - title_width) / 2)
    title_text_y = title_bar_top + int((title_bar_bottom - title_bar_top - title_height) / 7)

    draw_text(draw, title_text, (title_text_x, title_text_y), font_title, text_color)

    gray_bar_text = part2_text
    gray_bar_bbox = draw.textbbox((0, 0), gray_bar_text, font=font_image_title)
    gray_bar_width = gray_bar_bbox[2] - gray_bar_bbox[0]
    gray_bar_height = gray_bar_bbox[3] - gray_bar_bbox[1]

    gray_trapezoid_top_width = gray_bar_width + 1 * text_padding
    gray_trapezoid_bottom_width = gray_trapezoid_top_width + 20

    gray_trapezoid_coords = [
        (title_bar_right + 5, title_bar_top),
        (title_bar_right + gray_trapezoid_top_width, title_bar_top),
        (title_bar_right + int(
            (gray_trapezoid_top_width - gray_trapezoid_bottom_width) / 2) + gray_trapezoid_bottom_width,
         title_bar_bottom),
        (title_bar_right + int((gray_trapezoid_top_width - gray_trapezoid_bottom_width) / 2) + 5, title_bar_bottom)
    ]

    draw_trapezoid(draw, gray_trapezoid_coords, gray_bar_color)

    gray_text_x = title_bar_right + int((gray_trapezoid_top_width - gray_bar_width) / 2)
    gray_text_y = title_bar_top + int((title_bar_bottom - title_bar_top - gray_bar_height) / 2.6)

    draw_text(draw, gray_bar_text, (gray_text_x, gray_text_y), font_image_title, gray_text_color)

    subtitle_text = part3_text
    subtitle_bbox = draw.textbbox((0, 0), subtitle_text, font=font_text)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    subtitle_height = subtitle_bbox[3] - subtitle_bbox[1]

    red_bar_left = title_bar_left
    red_bar_top = title_bar_bottom
    red_bar_right = red_bar_left + subtitle_width + 1 * text_padding
    red_bar_bottom = red_bar_top + subtitle_height + 1 * text_padding

    gradient = create_gradient(red_bar_right - red_bar_left, red_bar_bottom - red_bar_top, image_name_color)
    image.paste(gradient, (red_bar_left, red_bar_top), gradient)

    subtitle_text_x = red_bar_left + int((red_bar_right - red_bar_left - subtitle_width) / 2)
    subtitle_text_y = red_bar_top + int((red_bar_bottom - red_bar_top - subtitle_height) / 2.6)

    draw_text(draw, subtitle_text, (subtitle_text_x, subtitle_text_y), font_text, text_color)

    new_name = str(int(time()*10000))
    edited_image_path = os.path.join(parent_directory, f"{new_name}_edited.png")
    image.save(edited_image_path)



def main(img_path):
    """

    :param img_path:
    :return:
    """
    parent_folder = img_path  # Path to a parent folder
    font_path = settings.font_path  # Path to a suitable font file
    all_files = get_all_files(parent_folder)
    print("完成检索图片")
    for input_image_path in tqdm(all_files):
        process_image(input_image_path, font_path)
