### 项目介绍

Video-subtitle-generator (vsg) 是一款基于语音识别，将音频/视频生成外挂字幕文件(srt格式)的软件。 

- 支持中文、英文、韩文、日文、越南语、俄语、西班牙语、葡萄语等语言的字幕生成

<img src="https://github.com/YaoFANGUK/video-subtitle-generator/blob/main/design/gui.png?raw=true" alt="gui" border="1px" >

### DEMO

<img src="https://github.com/YaoFANGUK/video-subtitle-generator/blob/main/design/demo.gif?raw=true" alt="demo">

## 源码使用说明

> 运行要求：需要Nvidia GPU显卡（显存大于1G可使用base模型，大于5G可使用medium模型，大于10G可使用large模型）

#### 1. 下载安装Miniconda 

- Windows: <a href="https://repo.anaconda.com/miniconda/Miniconda3-py38_4.11.0-Windows-x86_64.exe">Miniconda3-py38_4.11.0-Windows-x86_64.exe</a>


- MacOS：<a href="https://repo.anaconda.com/miniconda/Miniconda3-py38_4.11.0-MacOSX-x86_64.pkg">Miniconda3-py38_4.11.0-MacOSX-x86_64.pkg</a>


- Linux: <a href="https://repo.anaconda.com/miniconda/Miniconda3-py38_4.11.0-Linux-x86_64.sh">Miniconda3-py38_4.11.0-Linux-x86_64.sh</a>

#### 2. 创建并激活虚机环境

（1）切换到源码所在目录：
```shell
cd <源码所在目录>
```
> 例如：如果你的源代码放在D盘的tools文件下，并且源代码的文件夹名为video-subtitle-generator，就输入 ```cd D:/tools/video-subtitle-generator-main```

（2）创建激活conda环境
```shell
conda create -n vsgEnv python=3.8
```

```shell
conda activate vsgEnv
```

#### 3. 安装依赖文件

请确保你已经安装 python 3.8+，使用conda创建项目虚拟环境并激活环境 (建议创建虚拟环境运行，以免后续出现问题)

安装依赖：
```shell
pip install -r requirements.txt
```

#### 4. 运行程序

- 运行图形化界面版本(GUI)

```SHELL
python gui.py
```

- 运行命令行版本(CLI)

```SHELL
python backend/main.py
```


- 代码调用：

```shell
    # 1.指定音视频文件路径
    wav_path = './test/test.flv'
    # 2. 新建字幕生成对象，指定语言
    sg = SubtitleGenerator(video_path, language='zh-cn')
    # 3. 运行字幕生成
    ret = sg.run()
```

#### 5. 程序配置

- 设置模型文件

修改settings.ini中的Mode，取值为：base, medium, large，即可使用对应的识别模型

|  Mode  |  要求显存  |  速度  |
|:------:|:------:|:----:|
|  base  | 大于1 GB  | ~16x |
| medium | 大于5 GB  | ~2x  |
| large  | 大于10 GB |  1x  |
