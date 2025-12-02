import os
from aqt import mw

# 插件用户数据保存路径
user_files = os.path.join(os.path.dirname(__file__), "user_files")
if not os.path.exists(user_files):
    os.makedirs(user_files)

CONFIG_FILE = os.path.join(user_files, "config.json")
MODEL_NAME = "Eudic Type-in Cloze"

# 卡片正面：句子挖空 + 点击提示（只显示中文）
FRONT_TEMPLATE = """
<div class="sentence">{{cloze:Sentence}}</div>
<br>
<div class="hint-btn" onclick="this.style.display='none';document.getElementById('cn-hint').style.display='block';">
    [点击查看提示]
</div>
<div id="cn-hint" style="display:none; color: blue; font-weight: bold;">
    {{Hint}}
</div>

<br>
{{type:cloze:Sentence}}
"""

# 卡片背面：句子 + 详细排版信息 (BackDetails)
BACK_TEMPLATE = """
<div class="sentence">{{cloze:Sentence}}</div>
{{type:cloze:Sentence}}
<br>
<hr>
<div class="details">{{BackDetails}}</div>
"""

CSS = """
.card {
 font-family: arial;
 font-size: 20px;
 text-align: center;
 color: black;
 background-color: white;
}
.cloze {
 font-weight: bold;
 color: blue;
}
.nightMode .cloze {
 color: lightblue;
}
.details {
 text-align: left;
 margin: 0 auto;
 width: 80%;
 line-height: 1.6;
}
.word-row {
 margin-bottom: 15px;
}
.word-text {
 font-weight: bold;
 font-size: 22px;
 color: #2c3e50;
}
.phonetic {
 color: #7f8c8d;
 font-size: 16px;
 margin-left: 10px;
}
.meaning {
 display: block;
 color: #8e44ad;
 margin-top: 2px;
}
"""