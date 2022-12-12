### 项目介绍

- 支持中文、英文、韩文、日文、越南语、俄语、西班牙语、葡萄语等语言的字幕生成
- large 模型错词率（WER）如下：

<img src="https://github.com/YaoFANGUK/video-subtitle-generator/blob/main/design/language-breakdown.svg?raw=true" alt="demo">

### DEMO

<img src="https://github.com/YaoFANGUK/video-subtitle-generator/blob/main/design/demo.gif?raw=true" alt="demo">


### 使用方法

安装依赖：
```shell
pip install -r requirements.txt
```

使用方法：

```shell
    # 1.指定音视频文件路径
    wav_path = './test/test.flv'
    # 2. 新建字幕提取器
    sg = SubtitleGenerator(wav_path)
    # 3. 运行字幕生成
    ret = sg.run()
```

- 设置模型文件

修改settings.ini中的Mode，取值为：base, medium, large，即可使用对应的识别模型

|  Mode  |  要求显存  |  速度  |
|:------:|:------:|:----:|
|  base  | ~1 GB  | ~16x |
| medium | ~5 GB  | ~2x  |
| large  | ~10 GB |  1x  |


- CLI运行：
```SHELL
python backend/main.py
```
