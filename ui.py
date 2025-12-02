from aqt.qt import *
from aqt import mw
from aqt.operations import QueryOp
from .config import CONFIG_FILE
from .api_client import EudicClient
from .logic import process_data, generate_cloze_sentence
from .anki_utils import sync_to_anki
import json
import datetime


class EudicSyncDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("欧路词典同步 (Eudic Sync)")
        self.resize(500, 600)
        self.client = None
        self.categories = []

        self.setup_ui()
        self.load_config()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        # 1. 牌组选择
        deck_layout = QHBoxLayout()
        deck_layout.addWidget(QLabel("牌组:"))
        self.deck_combo = QComboBox()
        self.deck_combo.setEditable(True)  # 允许输入新牌组
        # 填充现有牌组
        self.deck_combo.addItems(mw.col.decks.all_names())
        deck_layout.addWidget(self.deck_combo)
        layout.addLayout(deck_layout)

        # 2. 中部框 (Category List)
        group_box = QGroupBox("生词本分组")
        group_layout = QVBoxLayout()

        # 提取按钮
        self.btn_fetch = QPushButton("提取分组")
        self.btn_fetch.clicked.connect(self.on_fetch_categories)
        group_layout.addWidget(self.btn_fetch)

        # 列表
        self.cat_list = QListWidget()
        group_layout.addWidget(self.cat_list)

        # 同步按钮
        self.btn_sync = QPushButton("同步")
        self.btn_sync.clicked.connect(self.on_sync)
        group_layout.addWidget(self.btn_sync)

        group_box.setLayout(group_layout)
        layout.addWidget(group_box)

        # 3. 运行框 (Log)
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)

    def log(self, message):
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        # 强制刷新 UI
        QApplication.processEvents()

    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                conf = json.load(f)
                self.token = conf.get('token', '')
                last_deck = conf.get('last_deck', '')
                if last_deck:
                    self.deck_combo.setCurrentText(last_deck)
        else:
            self.token = ""

        if not self.token:
            self.ask_for_token()
        else:
            self.client = EudicClient(self.token)
            # 验证一下 token
            # 放在后台验证比较好，这里简化直接用
            self.log("API Token 已加载。请点击“提取分组”。")

    def ask_for_token(self):
        token, ok = QInputDialog.getText(self, "授权", "请输入欧路词典 API Authorization:")
        if ok and token:
            self.token = token
            # 保存
            with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump({'token': token}, f)
            self.client = EudicClient(token)
            self.log("Token 已保存。")
        else:
            self.log("未输入 Token，插件无法工作。")

    def on_fetch_categories(self):
        if not self.client:
            self.ask_for_token()
            return

        self.log("正在获取分组...")
        self.btn_fetch.setEnabled(False)

        # 使用 QueryOp 避免卡死 UI (Anki Background Ops)
        op = QueryOp(
            parent=self,
            op=lambda col: self.client.get_categories(),
            success=self.on_fetch_success
        )
        op.with_progress().run_in_background()

    def on_fetch_success(self, data):
        self.btn_fetch.setEnabled(True)
        self.cat_list.clear()
        self.categories = data
        for cat in data:
            item = QListWidgetItem(cat['name'])
            item.setFlags(item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
            item.setCheckState(Qt.CheckState.Unchecked)
            item.setData(Qt.ItemDataRole.UserRole, cat['id'])
            self.cat_list.addItem(item)
        self.log(f"成功获取 {len(data)} 个分组。")

    def on_sync(self):
        # 获取选中的 Category IDs
        selected_ids = []
        for i in range(self.cat_list.count()):
            item = self.cat_list.item(i)
            if item.checkState() == Qt.CheckState.Checked:
                selected_ids.append(item.data(Qt.ItemDataRole.UserRole))

        if not selected_ids:
            self.log("请至少选择一个分组。")
            return

        deck_name = self.deck_combo.currentText()
        if not deck_name:
            self.log("请输入牌组名称。")
            return

        # 保存上次使用的牌组
        with open(CONFIG_FILE, 'r+', encoding='utf-8') as f:
            d = json.load(f)
            d['last_deck'] = deck_name
            f.seek(0)
            json.dump(d, f)

        self.log("开始同步任务...")
        self.btn_sync.setEnabled(False)

        # 启动后台任务
        op = QueryOp(
            parent=self,
            op=lambda col: self.execute_sync_logic(col, selected_ids, deck_name),
            success=self.on_sync_finish
        )
        op.with_progress().run_in_background()

    def execute_sync_logic(self, col, cat_ids, deck_name):
        # 此函数在后台线程运行
        # 1. 获取所有分组单词
        all_target_words = []
        for cid in cat_ids:
            # 需要跨线程更新 log 比较麻烦，这里简化，只在结束报告
            # 或者使用 mw.taskman.run_on_main 发送信号
            words = self.client.get_words_in_category(cid)
            all_target_words.extend(words)

        # 2. 获取所有笔记 (分页已在 api_client 处理)
        all_notes = self.client.get_all_notes()

        # 3. 处理数据 (NLP + Merge)
        # 这里的 logger 需要特殊处理，暂时定义一个简单的 lambda
        # 实际上应该用 taskman.run_on_main 更新 UI
        def worker_log(msg):
            mw.taskman.run_on_main(lambda: self.log(msg))

        processed_data = process_data(all_target_words, all_notes, worker_log)

        # 4. 生成 Cloze 字符串
        for key, val in processed_data.items():
            val['cloze_sentence'] = generate_cloze_sentence(val)

        # 5. 写入 Anki (必须在主线程写 DB? QueryOp 自动传递了 col，但是在后台线程)
        # Anki 的 CollectionOp 是为了写入。这里我们用的 QueryOp。
        # 安全起见，写入操作最好放回主线程，或者使用 col.db.execute 的锁。
        # 但 Anki 2.1.50+ 允许后台读，主线程写。
        # 我们将 processed_data 返回给 success 回调，在主线程写入。
        return (processed_data, deck_name)

    def on_sync_finish(self, result):
        self.btn_sync.setEnabled(True)
        data, deck_name = result
        self.log("数据处理完成，正在写入 Anki 数据库...")

        # 写入 Anki (主线程)
        count = sync_to_anki(data, deck_name, self.log)
