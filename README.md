Eudic to Anki Sync (欧路词典生词同步助手)
Eudic to Anki Sync 是一款强大的 Anki 插件，能够将你在 欧路词典 (Eudic) 中积累的生词、例句和详细笔记，智能转化为高质量的 Anki 拼写填空卡片 (Type-in Cloze)。

本插件专为深度英语学习者设计，通过 NLP（自然语言处理）技术自动识别句子中的单词变形，支持多例句切分与智能去重。

✨ 核心功能 (Features)
用户将生词保存到欧路词典生词本中，并为每一个单词添加笔记。笔记的形式是该单词所在语境的英文例句和用书名号标注的对应中文释义。

如针对单词account，笔记通常为：

"What scenes of Grandeur and Beauty!" exclaimed Thomas Baldwin in his 1786 account, Airopaidia, of a balloon journey over Chester during which he created one of the earliest aerial drawings. 《描述，叙述》。

若同一单词对应不同的例中组合，如单词account，笔记为： "What scenes of Grandeur and Beauty!" exclaimed Thomas Baldwin in his 1786 account, Airopaidia, of a balloon journey over Chester during which he created one of the earliest aerial drawings. 《描述，叙述》  The agency has lost several of its most important accounts. 《老主顾》。

该插件将单词和笔记同步至anki后，卡片形式为：

卡组为填空形式。正面为笔记中的英文例句，例句中单词对应的内容被挖空，且不含原笔记中书名号内的中文。正面还含有单词对应的书名号内的中文作为提示，提示不含有该单词。提示点击后才出现。用户需要将挖空内容正确拼写到正面的填空中。反面依次为挖空内容，单词原型，音标和书名号中的中文释义。

b. 如某个单词含有多条例句，同一个单词的每一个例句应该对应不同的卡片。

c. 如果不同单词的某一例句相同，该例句只对应一张卡片。

用户生词本中间断地加入新的生词和之前生词的不同的例句，若有相同单词则跳过，但若是某一单词的新的例句，那该例句不被跳过，对应一张新的卡片。

🔗 无缝同步：直接调用欧路词典官方 API，获取你的生词本分类、单词、音标及笔记 。



🧠 智能挖空 (NLP Powered)：内置 Spacy 自然语言处理模型。

即使笔记中的单词是 ended，而生词本单词是 end，也能精准识别并挖空。

支持短语（如 end up）和合成词（如 bird's-eye）的完整匹配与挖空。

📚 自动切分与合并：

多例句支持：一条笔记包含 5 个例句？插件会自动生成 5 张不同的卡片。

智能合并：如果不同单词对应了同一个例句（例如 jump 和 excitement 都在同一句话中），插件会将其合并为一张卡片，挖掉两个空，避免重复背诵。

✍️ 拼写检查 (Type-in)：生成的卡片要求你手动拼写答案，强化记忆。

🎨 精美排版：

正面：仅显示句子挖空和书名号内的中文提示（点击查看）。

背面：包含句子原句、单词、音标及完整释义，排版整洁。

⚠️ 兼容性说明 (Compatibility)
操作系统：目前仅支持 Windows (64位)。

原因：插件内置了高性能 NLP 库 (Spacy/Numpy) 的二进制文件，目前仅打包了 Windows 版本。Mac/Linux 用户直接安装可能会报错。

Anki 版本：建议 Anki 23.10 或更高版本（最低支持 Python 3.9+ 环境）。

📥 安装指南 (Installation)
方法一：通过 AnkiWeb 安装（推荐）

方法二：手动安装 (GitHub)
在右侧 Releases 页面下载最新的 .ankiaddon 文件。

双击该文件，Anki 将自动安装。

或者解压文件，将 EudicSync 文件夹放入 Anki 的插件目录 (AppData/Roaming/Anki2/addons21)。

重启 Anki。

🚀 使用教程 (Usage)
获取授权：

登录 欧路词典开放平台。

获取你的 Authorization (Token) 。请在https://my.eudic.net 登录获取。

启动插件：

在 Anki 菜单栏点击 工具 -> 欧路词典同步。

配置与同步：

首次运行会要求输入 API Token（仅需输入一次）。

牌组：选择或输入一个新的牌组名称（例如 English::Eudic）。

提取分组：点击按钮，插件会列出你欧路账号下的所有生词本 。

勾选并同步：勾选你想同步的生词本，点击“同步”。

开始学习：

同步完成后，就可以在 Anki 中开始背诵了！

🛠️ 开发与构建 (Development)
如果你想自行构建或为项目贡献代码：

依赖环境
Python 3.13 (与最新 Anki 保持一致)

依赖库：requests, spacy, numpy

项目结构
Plaintext

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
本地运行注意
由于 Anki 环境没有预装 Spacy，你需要将依赖安装到 libs 目录：

Bash

pip install requests spacy --target=libs --platform win_amd64 --python-version 3.13 --only-binary=:all:
# 此外，需手动下载 en_core_web_sm 模型解压至 libs 目录
📄 版权与声明 (License & Disclaimer)
MIT License: 本项目代码开源。


API 使用：本插件使用 欧路词典 OpenAPI，用户需遵守欧路词典的相关使用协议。插件仅作为数据同步工具，不提供任何词典内容数据，所有数据均来自用户个人的生词本 。

免责声明：使用本插件产生的 Anki 数据归用户所有。作者不对因使用插件导致的数据丢失负责（虽然我们做了详尽的错误捕获和测试）。

如果这个插件对你有帮助，欢迎点一个 ⭐ Star！
