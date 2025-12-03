# EudicSync (欧路词典生词本同步助手)
## ✍️ Introduction
> [!WARNING]
> 目前仅支持 Windows (64位)。插件内置了 NLP 库 (Spacy/Numpy) 的二进制文件，目前仅打包了 Windows 版本。Mac/Linux 用户直接安装可能会报错。

**语境填空**被公认为是第二语言习得的黄金法则，其又被通俗地归类为**句子挖掘**或者**语境填空**。\
其在应用层面的表现形式是，读者在阅读外语作品时，将生词与其所在句子截取，并将句子中的生词挖空，在后续复习中要求自己填写该生词。\
欧路词典提供了强大的词典、生词本和我的笔记功能，而anki则提供了对应的句子挖空和卡片制作功能。
本anki插件的作用就是将欧路词典的生词本和对应笔记同步至anki，并制作卡片。
## ✨ Features
### 1. 单个单词对应多个例句生成多张卡片
  在阅读过程中，单个单词往往出现在不同句子中会对应不同释义，而用户可通过欧路词典的我的笔记将对应例句和中文释义按简单的格式对应保存后，再同步到anki后，即可生成每个例句对应的卡片。
### 2. 单个例句中含多个生词在同一卡片中生成多个填空
  若同一个例句出现多个生词，用户在每个生词对应的笔记下都输入该例句和不同生词对应的中文释义，则anki卡片针对该例句只生成一张卡片，卡片中生成多个填空。
### 3. 跳过已有单词或已有例句
  用户在anki同步某一生词本后，之后在欧路词典的生词本添加新的单词，再同步至anki，会跳过已经同步的单词（若已有单词在欧路词典笔记下添加新的例句和释义，则该例句和释义仍旧会生成新的卡片）。
### 4. 智能挖空
  插件会自动识别单词和例句中对应的单词变形并挖空。
### 5. 卡片形式
  正面：英文例句，例句中单词对应的内容被挖空。提示，中文释义，点击出现。输入框，需要用户填入挖空内容。
  反面：挖空内容，单词原型，音标和书名号中的中文释义。

   <img width="300" height="350" alt="image" src="https://github.com/user-attachments/assets/a2904d9f-1810-4f52-af0b-cf25074b2949" />   <img width="300" height="350" alt="image" src="https://github.com/user-attachments/assets/e074f433-ffb4-41d1-ad23-2a2670b4791a" />

## 🚀 Usage
### 1. [获取欧路词典授权](https://my.eudic.net)
  登录后点击左栏获取授权，复制授权信息下的代码。
### 2. 启动插件
  在 Anki 菜单栏点击 工具 -> EudicSync。
### 3. 配置与同步：
  首次运行会要求输入授权信息下的代码（仅需输入一次）。\
  牌组：选择或输入一个新的牌组名称（例如: words_NYT）。\
  提取分组：点击按钮，插件会列出你欧路账号下的所有生词本 。\
  勾选并同步：勾选你想同步的生词本，点击“同步”。
### 4. 开始学习：
  同步完成后，就可以在 Anki 中开始背诵了！
> [!note]
> 欧路词典中我的笔记的格式为：英文例句 《中文释义》
> 
> 如单词account：\
> "What scenes of Grandeur and Beauty!" exclaimed Thomas Baldwin in his 1786 account, Airopaidia, of a balloon journey over Chester during which he created one of the earliest aerial drawings. 《描述，叙述》
> 
> 如含有多个例句：\
> "What scenes of Grandeur and Beauty!" exclaimed Thomas Baldwin in his 1786 account, Airopaidia, of a balloon journey over Chester during which he created one of the earliest aerial drawings. 《描述，叙述》  The agency has lost several of its most important accounts. 《老主顾》。

## 📥 Installation
### 1. 手动安装 (GitHub)
在右侧 Releases 页面下载最新的 .ankiaddon 文件。

双击该文件，Anki 将自动安装。

或者解压文件，将 EudicSync 文件夹放入 Anki 的插件目录 (AppData/Roaming/Anki2/addons21)。

重启 Anki。

### 2. ankiweb安装
anki暂不允许注册时间较短账号上传插件。

## 🛠️ Development
项目结构
```
EudicSync/
├── libs/                # 第三方库 (Vendor)
│   ├── spacy/
│   ├── requests/
│   └── en_core_web_sm/  # NLP 模型
├── api_client.py        # 欧路 API 封装
├── logic.py             # NLP 处理与数据清洗核心
├── anki_utils.py        # Anki 数据库交互
├── ui.py                # PyQt6 界面
└── __init__.py          # 入口
```
本地运行注意
由于 Anki 环境没有预装 Spacy，你需要将依赖安装到 libs 目录：
```
pip install requests spacy --target=libs --platform win_amd64 --python-version 3.13 --only-binary=:all:
```
此外，需手动下载 en_core_web_sm 模型解压至 libs 目录
## 📄 License & Disclaimer
MIT License: 本项目代码开源。

API 使用：本插件使用 欧路词典 OpenAPI，用户需遵守欧路词典的相关使用协议。插件仅作为数据同步工具，不提供任何词典内容数据，所有数据均来自用户个人的生词本 。

免责声明：使用本插件产生的 Anki 数据归用户所有。作者不对因使用插件导致的数据丢失负责（虽然我们做了详尽的错误捕获和测试）。

AI声明：部分代码由AI生成。

如果这个插件对你有帮助，欢迎点一个 ⭐ Star！


