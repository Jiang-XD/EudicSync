from aqt import mw
from anki.notes import Note
import traceback
from .config import MODEL_NAME, FRONT_TEMPLATE, BACK_TEMPLATE, CSS


def ensure_model_exists():
    """创建或修复 Note Type"""
    col = mw.col
    mm = col.models
    model = mm.by_name(MODEL_NAME)

    should_create = False
    required_fields = ["Sentence", "Hint", "BackDetails", "Word", "Phonetic", "OriginalNote"]

    if not model:
        should_create = True
    else:
        field_names = mm.field_names(model)
        # 如果缺少字段 (比如缺了新加的 BackDetails)，则需要重建或升级
        if len(field_names) < len(required_fields):
            should_create = True

    if should_create:
        if model:
            # 备份旧模板（防止报错）
            model['name'] = MODEL_NAME + "_OLD_v1"
            mm.save(model)

        model = mm.new(MODEL_NAME)
        model['type'] = 1  # Cloze

        for field in required_fields:
            mm.add_field(model, mm.new_field(field))

        t = mm.new_template("ClozeCard")
        t['qfmt'] = FRONT_TEMPLATE
        t['afmt'] = BACK_TEMPLATE
        mm.add_template(model, t)
        model['css'] = CSS
        mm.add(model)
        mm.save(model)
    return model


def get_deck_id(deck_name):
    return mw.col.decks.id(deck_name)


def get_existing_fingerprints(deck_name):
    fingerprints = set()
    try:
        did = mw.col.decks.id_if_exists(deck_name)
    except AttributeError:
        d = mw.col.decks.by_name(deck_name)
        did = d['id'] if d else None

    if not did: return fingerprints

    query = f'"deck:{deck_name}" "note:{MODEL_NAME}"'
    note_ids = mw.col.find_notes(query)
    import re
    for nid in note_ids:
        try:
            note = mw.col.get_note(nid)
            sent = note['Sentence']
            clean_sent = re.sub(r'\{\{c\d+::(.*?)(::.*?)?\}\}', r'\1', sent)
            fingerprints.add(clean_sent.strip())
        except:
            continue
    return fingerprints


def format_back_details(details_list):
    """
    将详情列表转换为 HTML 格式 (解决排版杂乱问题)
    Word 1, Phonetic 1, Meaning 1
    (Empty Line)
    Word 2...
    """
    html_parts = []
    for item in details_list:
        word = item['word']
        phon = item['phon']
        mean = item['mean']

        # 构建单行 HTML
        row_html = f"""
        <div class="word-row">
            <span class="word-text">{word}</span>
            <span class="phonetic">{phon}</span>
            <span class="meaning">{mean}</span>
        </div>
        """
        html_parts.append(row_html)

    # 用空行连接
    return "<br>".join(html_parts)


def sync_to_anki(processed_data, deck_name, logger):
    logger("正在初始化 Anki 写入流程...")
    try:
        col = mw.col
        model = ensure_model_exists()
        deck_id = get_deck_id(deck_name)
    except Exception as e:
        logger(f"初始化环境失败: {traceback.format_exc()}")
        return 0

    try:
        existing_fingerprints = get_existing_fingerprints(deck_name)
    except Exception as e:
        logger(f"读取旧卡片失败: {str(e)}")
        existing_fingerprints = set()

    added_count = 0
    skipped_count = 0
    errors = []

    for sent_key, data in processed_data.items():
        try:
            original_sent = data["original_sentence"].strip()

            if original_sent in existing_fingerprints:
                skipped_count += 1
                continue

            note = col.new_note(model)
            note.note_type()['did'] = deck_id

            # 填入字段
            note['Sentence'] = data['cloze_sentence']
            # 正面提示：只显示中文
            note['Hint'] = " ； ".join(data['hints_list'])

            # 背面详情：生成 HTML 块
            note['BackDetails'] = format_back_details(data['details_list'])

            # 保留原始数据以备查
            note['Word'] = ", ".join(data['base_words'])
            note['Phonetic'] = ""  # 已整合进 BackDetails
            note['OriginalNote'] = str(data)

            col.add_note(note, deck_id)
            added_count += 1

        except Exception as e:
            errors.append(f"写入失败: {str(e)}")
            if len(errors) == 1: print(traceback.format_exc())

    if errors:
        logger(f"警告: {len(errors)} 条写入失败。")

    logger(f"同步结束。新增: {added_count}, 跳过: {skipped_count}")
    return added_count