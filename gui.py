# -*- coding: UTF-8 -*-  
"""
@author: Fang Yao
@file  : gui.py
@time  : 2023/05/06 10:59
@desc  : 字幕生成器图形化界面
"""
import os
import configparser
import PySimpleGUI as sg
from threading import Thread
import backend.config
from backend import main


class SubtitleGeneratorGUI:
    def _load_config(self):
        self.config_file = os.path.join(os.path.dirname(__file__), 'settings.ini')
        self.subtitle_config_file = os.path.join(os.path.dirname(__file__), 'subtitle.ini')
        self.config = configparser.ConfigParser()
        self.interface_config = configparser.ConfigParser()
        if not os.path.exists(self.config_file):
            # 如果没有配置文件，默认弹出语言选择界面
            LanguageModeGUI(self).run()
        self.INTERFACE_KEY_NAME_MAP = {
            '简体中文': 'ch',
            '繁體中文': 'chinese_cht',
            'English': 'en'
        }
        self.config.read(self.config_file, encoding='utf-8')
        self.interface_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', 'interface',
                                           f"{self.INTERFACE_KEY_NAME_MAP[self.config['DEFAULT']['Interface']]}.ini")
        self.interface_config.read(self.interface_file, encoding='utf-8')

    def __init__(self):
        self.font = 'Arial 10'
        self.theme = 'LightBrown12'
        sg.theme(self.theme)
        self.icon = os.path.join(os.path.dirname(__file__), 'design', 'vse.ico')
        self._load_config()
        self.screen_width, self.screen_height = sg.Window.get_screen_size()
        print(self.screen_width, self.screen_height)
        # 默认组件大小
        self.output_size = (100, 30)
        self.progressbar_size = (30, 20)
        # 分辨率低于1080
        if self.screen_width // 2 < 960:
            self.output_size = (58, 10)
            self.progressbar_size = (14, 20)
        # 字幕提取器布局
        self.layout = None
        # 字幕提取其窗口
        self.window = None
        # 视频路径
        self.file_path = None
        # 字幕提取器
        self.sg = None

    def run(self):
        # 创建布局
        self._create_layout()
        # 创建窗口
        self.window = sg.Window(title=self.interface_config['SubtitleGeneratorGUI']['Title'], layout=self.layout,
                                icon=self.icon)
        while True:
            # 循环读取事件
            event, values = self.window.read(timeout=10)
            # 处理【打开】事件
            self._file_event_handler(event, values)
            # 处理【识别语言】事件
            self._language_mode_event_handler(event)
            # 处理【运行】事件
            self._run_event_handler(event, values)
            # 如果关闭软件，退出
            if event == sg.WIN_CLOSED:
                break
            # 更新进度条
            if self.sg is not None:
                if self.sg.isFinished:
                    # 1) 打开【运行】、【打开】和【识别语言】按钮
                    self.window['-RUN-'].update(disabled=False)
                    self.window['-FILE-'].update(disabled=False)
                    self.window['-FILE_BTN-'].update(disabled=False)
                    self.window['-LANGUAGE-MODE-'].update(disabled=False)
                    self.sg = None
                if len(self.file_paths) >= 1:
                    # 2) 关闭【运行】、【打开】和【识别语言】按钮
                    self.window['-RUN-'].update(disabled=True)
                    self.window['-FILE-'].update(disabled=True)
                    self.window['-FILE_BTN-'].update(disabled=True)
                    self.window['-LANGUAGE-MODE-'].update(disabled=True)
                    print(f"{backend.config.interface_config['Main']['RecSubLang']}: {backend.config.REC_LANGUAGE_TYPE}")
                    print(f"{backend.config.interface_config['Main']['RecMode']}: {backend.config.settings_config['DEFAULT']['Mode']}")

    def update_interface_text(self):
        self._load_config()
        self.window.set_title(self.interface_config['SubtitleGeneratorGUI']['Title'])
        self.window['-FILE_BTN-'].Update(self.interface_config['SubtitleGeneratorGUI']['Open'])
        self.window['-RUN-'].Update(self.interface_config['SubtitleGeneratorGUI']['Run'])
        self.window['-LANGUAGE-MODE-'].Update(self.interface_config['SubtitleGeneratorGUI']['Setting'])

    def _create_layout(self):
        """
        创建字幕提取器布局
        """
        garbage = os.path.join(os.path.dirname(__file__), 'output')
        if os.path.exists(garbage):
            import shutil
            shutil.rmtree(garbage, True)
        self.layout = [
            # 打开按钮 + 快进快退条
            [sg.Input(key='-FILE-', visible=False, enable_events=True),
             sg.FilesBrowse(button_text=self.interface_config['SubtitleGeneratorGUI']['Open'], file_types=((
                            self.interface_config['SubtitleGeneratorGUI']['AllFile'], '*.*'), ('mp4', '*.mp4'),
                                                                                              ('mp3', '*.mp3'),
                                                                                              ('aac', '*.aac'),
                                                                                              ('wav', '*.wav'),
                                                                                              ('flv', '*.flv'),
                                                                                              ('wmv', '*.wmv'),
                                                                                              ('avi', '*.avi')),
                            key='-FILE_BTN-', size=(10, 1), font=self.font),
             ],
            # 输出区域
            [sg.Output(size=self.output_size, font=self.font)],

            # 运行按钮 + 进度条
            [sg.Button(button_text=self.interface_config['SubtitleGeneratorGUI']['Run'], key='-RUN-',
                       font=self.font, size=(20, 1)),
             sg.Button(button_text=self.interface_config['SubtitleGeneratorGUI']['Setting'], key='-LANGUAGE-MODE-',
                       font=self.font, size=(20, 1)),
             ],
        ]

    def _file_event_handler(self, event, values):
        """
        当点击打开按钮时：
        1）打开视频文件，将画布显示视频帧
        2）获取视频信息，初始化进度条滑块范围
        """
        if event == '-FILE-':
            self.file_paths = values['-FILE-'].split(';')
            self.file_path = self.file_paths[0]
            for file in self.file_paths:
                print(f"{self.interface_config['SubtitleGeneratorGUI']['OpenFileSuccess']}：{file}")


    def _language_mode_event_handler(self, event):
        if event != '-LANGUAGE-MODE-':
            return
        if 'OK' == LanguageModeGUI(self).run():
            # 重新加载config
            pass

    def _run_event_handler(self, event, values):
        """
        当点击运行按钮时：
        1) 禁止修改字幕滑块区域
        2) 禁止再次点击【运行】和【打开】按钮
        3) 设定字幕区域位置
        """
        if event == '-RUN-':
            if self.file_paths is None or self.file_paths == '':
                print(self.interface_config['SubtitleGeneratorGUI']['OpenVideoFirst'])
            else:
                # 2) 禁止再次点击【运行】、【打开】和【识别语言】按钮
                self.window['-RUN-'].update(disabled=True)
                self.window['-FILE-'].update(disabled=True)
                self.window['-FILE_BTN-'].update(disabled=True)
                self.window['-LANGUAGE-MODE-'].update(disabled=True)

                def task():
                    while self.file_paths:
                        print(self.file_paths)
                        file_path = self.file_paths.pop()
                        self.sg = main.SubtitleGenerator(file_path, backend.config.REC_LANGUAGE_TYPE)
                        self.sg.run()
                Thread(target=task, daemon=False).start()



class LanguageModeGUI:
    def __init__(self, subtitle_extractor_gui):
        self.subtitle_extractor_gui = subtitle_extractor_gui
        self.icon = os.path.join(os.path.dirname(__file__), 'design', 'vsg.ico')
        self.config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.ini')
        # 设置界面
        self.INTERFACE_DEF = '简体中文'
        if not os.path.exists(self.config_file):
            self.interface_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', 'interface',
                                               "ch.ini")
        self.interface_config = configparser.ConfigParser()
        # 设置语言
        self.INTERFACE_KEY_NAME_MAP = {
            '简体中文': 'ch',
            '繁體中文': 'chinese_cht',
            'English': 'en'
        }
        # 设置语言
        self.LANGUAGE_DEF = 'ch'
        self.LANGUAGE_NAME_KEY_MAP = None
        self.LANGUAGE_KEY_NAME_MAP = None
        self.MODE_DEF = 'medium'
        self.MODE_NAME_KEY_MAP = None
        self.MODE_KEY_NAME_MAP = None
        # 语言选择布局
        self.layout = None
        # 语言选择窗口
        self.window = None

    def run(self):
        # 创建布局
        title = self._create_layout()
        # 创建窗口
        self.window = sg.Window(title=title, layout=self.layout, icon=self.icon)
        while True:
            # 循环读取事件
            event, values = self.window.read(timeout=10)
            # 处理【OK】事件
            self._ok_event_handler(event, values)
            # 处理【切换界面语言】事件
            self._interface_event_handler(event, values)
            # 如果关闭软件，退出
            if event == sg.WIN_CLOSED:
                if os.path.exists(self.config_file):
                    break
                else:
                    exit(0)
            if event == 'Cancel':
                if os.path.exists(self.config_file):
                    self.window.close()
                    break
                else:
                    exit(0)

    def _create_layout(self):
        interface_def, language_def, mode_def = self.parse_config(self.config_file)
        # 加载界面文本
        self._load_interface_text()
        choose_language_text = self.interface_config["LanguageModeGUI"]["InterfaceLanguage"]
        choose_sub_lang_text = self.interface_config["LanguageModeGUI"]["SubtitleLanguage"]
        choose_mode_text = self.interface_config["LanguageModeGUI"]["Mode"]
        self.layout = [
            # 显示选择界面语言
            [sg.Text(choose_language_text),
             sg.DropDown(values=list(self.INTERFACE_KEY_NAME_MAP.keys()), size=(30, 20),
                         pad=(0, 20),
                         key='-INTERFACE-', readonly=True,
                         default_value=interface_def),
             sg.OK(key='-INTERFACE-OK-')],
            # 显示选择字幕语言
            [sg.Text(choose_sub_lang_text),
             sg.DropDown(values=list(self.LANGUAGE_NAME_KEY_MAP.keys()), size=(30, 20),
                         pad=(0, 20),
                         key='-LANGUAGE-', readonly=True, default_value=language_def)],
            # 显示识别模式
            [sg.Text(choose_mode_text),
             sg.DropDown(values=list(self.MODE_NAME_KEY_MAP.keys()), size=(30, 20), pad=(0, 20),
                         key='-MODE-', readonly=True, default_value=mode_def)],
            # 显示确认关闭按钮
            [sg.OK(), sg.Cancel()]
        ]
        return self.interface_config["LanguageModeGUI"]["Title"]

    def _ok_event_handler(self, event, values):
        if event == 'OK':
            # 设置模型语言配置
            interface = None
            language = None
            mode = None
            # 设置界面语言
            interface_str = values['-INTERFACE-']
            if interface_str in self.INTERFACE_KEY_NAME_MAP:
                interface = interface_str
            language_str = values['-LANGUAGE-']
            # 设置字幕语言
            print(self.interface_config["LanguageModeGUI"]["SubtitleLanguage"], language_str)
            if language_str in self.LANGUAGE_NAME_KEY_MAP:
                language = self.LANGUAGE_NAME_KEY_MAP[language_str]
            # 设置模型语言配置
            mode_str = values['-MODE-']
            print(self.interface_config["LanguageModeGUI"]["Mode"], mode_str)
            if mode_str in self.MODE_NAME_KEY_MAP:
                mode = self.MODE_NAME_KEY_MAP[mode_str]
            self.set_config(self.config_file, interface, language, mode)
            if self.subtitle_extractor_gui is not None:
                self.subtitle_extractor_gui.update_interface_text()
            self.window.close()

    def _interface_event_handler(self, event, values):
        if event == '-INTERFACE-OK-':
            self.interface_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', 'interface',
                                               f"{self.INTERFACE_KEY_NAME_MAP[values['-INTERFACE-']]}.ini")
            self.interface_config.read(self.interface_file, encoding='utf-8')
            config = configparser.ConfigParser()
            if os.path.exists(self.config_file):
                config.read(self.config_file, encoding='utf-8')
                self.set_config(self.config_file, values['-INTERFACE-'], config['DEFAULT']['Language'],
                                config['DEFAULT']['Mode'])
            self.window.close()
            title = self._create_layout()
            self.window = sg.Window(title=title, layout=self.layout, icon=self.icon)

    @staticmethod
    def set_config(config_file, interface, language_code, mode):
        # 写入配置文件
        with open(config_file, mode='w', encoding='utf-8') as f:
            f.write('[DEFAULT]\n')
            f.write(f'Interface = {interface}\n')
            f.write(f'Language = {language_code}\n')
            f.write(f'Mode = {mode}\n')

    def _load_interface_text(self):
        self.interface_config.read(self.interface_file, encoding='utf-8')
        config_language_mode_gui = self.interface_config["LanguageModeGUI"]
        # 设置界面
        self.INTERFACE_DEF = config_language_mode_gui["InterfaceDefault"]

        self.LANGUAGE_DEF = config_language_mode_gui["LanguageZH-CN"]
        self.LANGUAGE_NAME_KEY_MAP = {}
        for lang in backend.config.LANGUAGE_LIST:
            self.LANGUAGE_NAME_KEY_MAP[config_language_mode_gui[f"Language{lang.upper()}"]] = lang
        self.LANGUAGE_NAME_KEY_MAP = dict(sorted(self.LANGUAGE_NAME_KEY_MAP.items(), key=lambda item: item[1]))
        self.LANGUAGE_KEY_NAME_MAP = {v: k for k, v in self.LANGUAGE_NAME_KEY_MAP.items()}
        self.MODE_DEF = config_language_mode_gui['ModeMedium']
        self.MODE_NAME_KEY_MAP = {
            config_language_mode_gui['ModeBase']: 'base',
            config_language_mode_gui['ModeMedium']: 'medium',
            config_language_mode_gui['ModeLarge']: 'large',
        }
        self.MODE_KEY_NAME_MAP = {v: k for k, v in self.MODE_NAME_KEY_MAP.items()}

    def parse_config(self, config_file):
        if not os.path.exists(config_file):
            self.interface_config.read(self.interface_file, encoding='utf-8')
            interface_def = self.interface_config['LanguageModeGUI']['InterfaceDefault']
            language_def = self.interface_config['LanguageModeGUI']['InterfaceDefault']
            mode_def = self.interface_config['LanguageModeGUI']['ModeFast']
            return interface_def, language_def, mode_def
        config = configparser.ConfigParser()
        config.read(config_file, encoding='utf-8')
        interface = config['DEFAULT']['Interface']
        language = config['DEFAULT']['Language']
        mode = config['DEFAULT']['Mode']
        self.interface_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend', 'interface',
                                           f"{self.INTERFACE_KEY_NAME_MAP[interface]}.ini")
        self._load_interface_text()
        interface_def = interface if interface in self.INTERFACE_KEY_NAME_MAP else \
            self.INTERFACE_DEF
        language_def = self.LANGUAGE_KEY_NAME_MAP[language] if language in self.LANGUAGE_KEY_NAME_MAP else \
            self.LANGUAGE_DEF
        mode_def = self.MODE_KEY_NAME_MAP[mode] if mode in self.MODE_KEY_NAME_MAP else self.MODE_DEF
        return interface_def, language_def, mode_def


if __name__ == '__main__':
    sgs = SubtitleGeneratorGUI()
    sgs.run()
