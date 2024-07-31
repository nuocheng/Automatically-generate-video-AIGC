from django.shortcuts import render
import os
import time
import pandas as pd
from typing import Union
from datetime import datetime
from django.conf import settings
from django.http import JsonResponse

import asyncio
import aiohttp, aiofiles
import moviepy.editor as mpy

from . import make_image
from moviepy.video.compositing.concatenate import concatenate_videoclips
from moviepy.video.fx.all import fadein, fadeout, rotate, resize
from functools import wraps


def return_json_data(func):
    """

    :param func:
    :return:
    """

    @wraps(func)
    def wrapper(request):
        content = request.POST.get("content")
        json_str = func(content)
        return JsonResponse(json_str, safe=False)

    return wrapper


# Create your views here.

def make_dir(path):
    """
    创建目录
    :param path:
    :return:
    """
    if not os.path.exists(path):
        os.makedirs(path)


async def download_image(session, info, path):
    """

    :param url:
    :param save_path:
    :return:
    """
    name = ""
    if len(info['from_origin']) == 0:
        name += "other;"
    else:
        name += info['from_origin'] + ";"

    if len(info['image_title']) == 0:
        name += ";"
    else:
        name += info['image_title'] + ";"

    if len(info['page_title']) == 0:
        name += ";"
    else:
        name += info['page_title'] + ";"

    if info['image_url'] is None or len(info['image_url']) == "":
        return info
    async with session.get(info['image_url']) as resp:
        if resp.status == 200:
            # 确保保存路径的目录存在
            # os.makedirs(os.path.dirname(path), exist_ok=True)
            # 异步写入文件
            image_file_path = os.path.join(path, "{}.jpg".format(name))
            print(image_file_path)
            async with aiofiles.open(image_file_path, 'wb') as f:
                await f.write(await resp.read())
            print(f"saved to {path}")
            info['local_path'] = path
            return info
        else:
            print("失败：{}".format(info['image_url']))
            return info


async def download_images(image_info_urls):
    """

    :param image_info_urls:
    :return
    """
    now = datetime.now()
    formatted_date = now.strftime("%Y-%m-%d")
    file_name = str(int(time.time() * 10000))
    path = os.path.join(settings.BASE_DIR, 'static', formatted_date, file_name)
    make_dir(path)
    print("创建：{}".format(path))
    task = []
    async with aiohttp.ClientSession() as session:
        for item in image_info_urls:
            task.append(download_image(session, item, path))
        response = await asyncio.gather(*task)
    return response


def make_video(img_path: str) -> Union[str, None]:
    """
    创建相关视频文件
    :param img_path: 图片的路径
    :return:
    """
    now = datetime.now()
    formatted_date = now.strftime("%Y-%m-%d")
    image_files = []
    for item in os.listdir(img_path):
        if item.endswith("_edited.png"):
            image_files.append(item)
    if len(image_files) == 0:
        return None
    # 创建图片剪辑列表
    clips = []
    for img_file in image_files:
        # 创建图片剪辑
        img_file = os.path.join(img_path,img_file)
        clip = mpy.ImageClip(img_file).set_duration(3)  # 每张图片显示2秒
        # 添加特效
        clip = clip.fx(fadein, duration=1)  # 淡入效果，持续1秒
        clip = clip.fx(fadeout, duration=1)  # 淡出效果，持续1秒
        clips.append(clip)

    # 将所有剪辑拼接成一个视频
    final_clip = concatenate_videoclips(clips, method="compose")
    path = os.path.join(settings.BASE_DIR, 'static', "video", formatted_date)
    make_dir(path)
    name = str(int(time.time() * 10000))
    mp4_file = os.path.join(path, "{}.mp4".format(name))
    # 设置视频输出参数
    final_clip.write_videofile(mp4_file, fps=60)
    http_url = "/static/video/{}/{}.mp4".format(formatted_date, name)
    return http_url


@return_json_data
def get_relate_img(content):
    """

    :param content:
    :return:
    """
    decs = settings.db.get_relevant_documents(content)
    content_image_url_list = []

    for item in decs:
        print(item.metadata)
        row_index = item.metadata['row']
        filter_data = settings.demo_data.iloc[row_index]
        info = {
            "image_url": filter_data['img_url'] if not pd.isna(filter_data['img_url']) else "",
            "image_title": filter_data['img_title'].replace(" ","").replace(".","").replace("\u200b",",") if not pd.isna(filter_data['img_title']) else "",
            "from_origin": filter_data['from_origin'].replace(" ","").replace(".","").replace("\u200b",",") if not pd.isna(filter_data['from_origin']) else "",
            "page_title": filter_data['title'].replace(" ","").replace(".","").replace("\u200b",",") if not pd.isna(filter_data['title']) else "",
            "page_content": filter_data['content'].replace(" ","") if not pd.isna(filter_data['content']) else "",
            "date": filter_data['date'].replace(" ","") if not pd.isna(filter_data['date']) else "",
        }
        content_image_url_list.append(info)
    image_new_info = asyncio.run(download_images(content_image_url_list))
    img_path = ""     # image_new_info['local_path']
    for item in image_new_info:
        if "local_path" not in item:
            continue
        else:
            img_path = item["local_path"]
            break

    make_image.main(img_path)
    mp4_url = settings.ip_config+make_video(img_path)
    # return {"flag": 1, "message": "完成视频的创作","mp4_url": mp4_url,"info":content_image_url_list}
    return {"flag": 1, "message": "完成视频的创作","mp4_url": mp4_url}
