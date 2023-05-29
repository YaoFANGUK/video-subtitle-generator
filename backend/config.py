# -*- coding: UTF-8 -*-  
"""
@author: Fang Yao
@file  : config.py
@time  : 2022/04/27 22:55
@desc  : 配置文件
"""
import os
from pathlib import Path
from fsplit.filesplit import Filesplit
import configparser
import platform
import stat


def merge_large_file(file_name, file_dir):
    """
    切分的大文件合并
    """
    fs = Filesplit()
    if file_name not in (os.listdir(file_dir)):
        fs.merge(input_dir=file_dir, cleanup=CLEAN_UP)


def split_large_file(file, output_dir):
    """
    将大文件切分
    """
    fs = Filesplit()
    fs.split(file=file, split_size=50000000, output_dir=output_dir)


def get_settings_config():
    # 读取settings.ini配置
    settings_config = configparser.ConfigParser()
    settings_config.read(SETTINGS_PATH, encoding='utf-8')
    return settings_config


def get_model_path():
    model_dir = os.path.join(BASE_DIR, 'models', f'{get_settings_config()["DEFAULT"]["Mode"]}_asr')
    model_path = os.path.join(model_dir, 'infer_model')
    return model_path


def get_interface_config():
    # 读取interface下的语言配置,e.g. ch.ini
    interface_config = configparser.ConfigParser()
    interface_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'interface',
                                  f"{INTERFACE_KEY_NAME_MAP[get_settings_config()['DEFAULT']['Interface']]}.ini")
    interface_config.read(interface_file, encoding='utf-8')
    return interface_config


def init_settings_config():
    if not os.path.exists(SETTINGS_PATH):
        # 如果没有配置文件，默认使用中文
        with open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'settings.ini'), mode='w', encoding='utf-8') as f:
            f.write('[DEFAULT]\n')
            f.write('Interface = 简体中文\n')
            f.write('Language = auto\n')
            f.write('Mode = medium')


# --------------------- 请你不要改 start-----------------------------
# 项目的base目录
BASE_DIR = str(Path(os.path.abspath(__file__)).parent)
# 设置文件保存路径
SETTINGS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'settings.ini')
# 识别语言
LANGUAGE_LIST = (
    "auto", "en", 'zh-cn', 'zh-tw', 'zh-hk', 'zh-sg', 'zh-hans', 'zh-hant', "de", "es", "ru", "ko",
    "fr", "ja", "pt", "tr", "pl", "ca", "nl", "ar", "sv", "it", "id", "hi", "fi", "vi", "he", "uk", "el",
    "ms", "cs", "ro", "da", "hu", "ta", "no", "th", "ur", "hr", "bg", "lt", "la", "ml", "cy", "sk",
    "te", "fa", "lv", "bn", "sr", "az", "sl", "kn", "et", "mk", "br", "eu", "is", "hy", "ne", "mn", "bs",
    "kk", "sq", "sw", "gl", "mr", "pa", "si", "km", "sn", "yo", "so", "af", "oc", "ka", "be", "tg", "sd"
)
INTERFACE_KEY_NAME_MAP = {
    '简体中文': 'ch',
    '繁體中文': 'chinese_cht',
    'English': 'en'
}
CLEAN_UP = False   # cleanup改成True会删除合并前的文件
init_settings_config()
# 查看该路径下是否有语音模型识别完整文件，没有的话合并小文件生成完整文件
merge_large_file('infer_model', os.path.join(BASE_DIR, 'models', 'base_asr'))
merge_large_file('infer_model', os.path.join(BASE_DIR, 'models', 'medium_asr'))
merge_large_file('infer_model', os.path.join(BASE_DIR, 'models', 'large_asr'))
merge_large_file('ffmpeg.exe', os.path.join(BASE_DIR, 'ffmpeg', 'win_x64'))


# 指定ffmpeg可执行程序路径
sys_str = platform.system()
if sys_str == "Windows":
    ffmpeg_bin = os.path.join('win_x64', 'ffmpeg.exe')
elif sys_str == "Linux":
    ffmpeg_bin = os.path.join('linux_x64', 'ffmpeg')
else:
    ffmpeg_bin = os.path.join('macos', 'ffmpeg')
FFMPEG_PATH = os.path.join(BASE_DIR, '', 'ffmpeg', ffmpeg_bin)
# 将ffmpeg添加可执行权限
os.chmod(FFMPEG_PATH, stat.S_IRWXU+stat.S_IRWXG+stat.S_IRWXO)
# --------------------- 请你不要改 end-----------------------------


# --------------------- 请根据自己的实际情况改 start-----------------
# 设置识别语言
REC_LANGUAGE_TYPE = get_settings_config()["DEFAULT"]["Language"]

# 音频设置
SILENCE_THRESH = -70           # 小于 -70dBFS以下的为静默
MIN_SILENCE_LEN = 700          # 静默超过700毫秒则拆分
LENGTH_LIMIT = 60 * 1000       # 拆分后每段不得超过1分钟
ABANDON_CHUNK_LEN = 500        # 丢弃小于500毫秒的段

# 字幕设置
DEFAULT_SUBTITLE_FORMAT = 'srt'
DEFAULT_CONCURRENCY = 10
