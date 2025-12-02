import re
import sys
import os
import html
import traceback

# --- Spacy 加载逻辑 ---
nlp = None
spacy_error = None
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs'))

try:
    import spacy
    from spacy.matcher import Matcher  # 引入匹配器

    libs_dir = os.path.join(os.path.dirname(__file__), 'libs')
    model_folder_name = "en_core_web_sm"
    model_path = os.path.join(libs_dir, model_folder_name)

    if os.path.exists(os.path.join(model_path, "config.cfg")):
        nlp = spacy.load(model_path)
    else:
        raise FileNotFoundError(f"在 {model_path} 未找到 config.cfg")

except Exception as e:
    spacy_error = str(e)


# --- 简易备用逻辑 ---
def simple_lemmatize(word):
    # (保持原有备用逻辑不变，仅作兜底)
    IRREGULAR_MAP = {
        "geese": "goose", "mice": "mouse", "children": "child", "teeth": "tooth",
        "feet": "foot", "men": "man", "women": "woman", "went": "go", "gone": "go",
        "came": "come", "took": "take", "taken": "take", "saw": "see", "seen": "see",
        "ate": "eat", "eaten": "eat", "wrote": "write", "written": "write",
        "made": "make", "bought": "buy", "thought": "think", "caught": "catch",
        "ended": "end"
    }
    word = word.lower()
    if word in IRREGULAR_MAP: return IRREGULAR_MAP[word]
    if word.endswith("ing"): return [word[:-3], word[:-3] + "e"]
    if word.endswith("ed"): return [word[:-2], word[:-2] + "e"]
    if word.endswith("ies"): return [word[:-3] + "y"]
    if word.endswith("es"): return [word[:-2], word[:-1]]
    if word.endswith("s") and not word.endswith("ss"): return [word[:-1]]
    return [word]


def find_word_in_sentence(sentence, target_word, logger=None):
    """
    NLP 核心升级：支持短语 (end up) 和合成词 (bird's-eye)
    """
    if not sentence or not target_word: return None

    # 1. 优先使用 Spacy Matcher (处理短语神器)
    if nlp:
        try:
            matcher = Matcher(nlp.vocab)

            # 对目标词（可能是短语）进行分词，获取其 Lemma 序列
            # 例如 target="end up" -> lemmas=["end", "up"]
            target_doc = nlp(target_word)
            pattern = []

            for token in target_doc:
                # 构建匹配模式：基于词元匹配，且不区分大小写
                # 处理连字符：如果 token 是连字符，直接匹配原文
                if token.text in ["-", "—"]:
                    pattern.append({"TEXT": token.text})
                else:
                    pattern.append({"LEMMA": token.lemma_.lower()})

            matcher.add("TargetPhrase", [pattern])

            # 在句子中搜索
            doc = nlp(sentence)
            matches = matcher(doc)

            # 找到最长的匹配 (防止 text="ended up", target="end" 只匹配了 "ended")
            # 实际上我们希望精准匹配整个短语
            if matches:
                # 取第一个匹配项
                match_id, start, end = matches[0]
                span = doc[start:end]
                return span.text  # 返回句子中的原话 (如 "ended up")

        except Exception as e:
            if logger: logger(f"NLP Matcher Error: {e}")
            pass

    # 2. 备用逻辑 (增强版正则)
    # 处理 "bird's-eye" 这种直接包含的情况
    if target_word.lower() in sentence.lower():
        # 使用正则确保边界，防止 "end" 匹配到 "sender"
        # 允许中间有连字符或空格变化
        clean_target = re.escape(target_word).replace(r'\ ', r'[\s\-]')
        match = re.search(r'\b' + clean_target + r'\b', sentence, re.IGNORECASE)
        # 如果找不到带边界的，再试一次宽松匹配 (针对 symbol)
        if not match:
            match = re.search(re.escape(target_word), sentence, re.IGNORECASE)
        if match: return match.group(0)

    # 3. 逐词规则兜底 (针对单次变形)
    tokens = re.findall(r'\b[\w\-\']+\b', sentence)  # 允许连字符和撇号
    target_lower = target_word.lower()
    for token in tokens:
        token_lower = token.lower()
        if token_lower == target_lower: return token
        possible_bases = simple_lemmatize(token_lower)
        if isinstance(possible_bases, list):
            if target_lower in possible_bases: return token
        elif possible_bases == target_lower:
            return token

    return None


def extract_items_from_note(note_text):
    """解析笔记 (保持不变)"""
    if not note_text: return []
    clean_text = html.unescape(note_text)
    clean_text = re.sub(r'', '', clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'<[^>]+>', '', clean_text)
    results = []
    matches = re.finditer(r'([^《]+)《([^》]+)》', clean_text)
    found_any = False
    for match in matches:
        found_any = True
        sent_part = match.group(1).strip()
        hint_part = match.group(2).strip()
        sent_part = re.sub(r'\s+', ' ', sent_part).strip()
        if sent_part: results.append((sent_part, hint_part))
    if not found_any and clean_text.strip():
        cleaned = re.sub(r'\s+', ' ', clean_text).strip()
        results.append((cleaned, ""))
    return results


def process_data(category_words, all_notes, logger):
    logger("正在匹配单词与笔记 (NLP Enhanced)...")
    if not nlp:
        logger(f"提示: Spacy 未加载，部分短语匹配可能不准确。")

    word_note_map = {}
    for note in all_notes:
        w = note['word']
        if w not in word_note_map: word_note_map[w] = []
        word_note_map[w].append(note)

    processed_cards = {}

    for word_item in category_words:
        word_text = word_item['word']
        phonetic = word_item.get('phon', '')

        notes = word_note_map.get(word_text, [])

        for note in notes:
            raw_note = note['note']
            items = extract_items_from_note(raw_note)

            for sentence, chinese_hint in items:
                sent_key = sentence.strip()

                if sent_key not in processed_cards:
                    processed_cards[sent_key] = {
                        "original_sentence": sentence,
                        "words_to_cloze": set(),
                        "hints_list": [],  # 只存中文提示，用于卡片正面
                        "details_list": [],  # 【新】存完整信息 (word, phon, meaning) 用于卡片背面
                        "base_words": []
                    }

                # 查找单词/短语
                actual_word = find_word_in_sentence(sentence, word_text, logger)

                if actual_word:
                    processed_cards[sent_key]["words_to_cloze"].add(actual_word)

                    # 1. 处理正面提示 (只显示中文)
                    if chinese_hint and chinese_hint not in processed_cards[sent_key]["hints_list"]:
                        processed_cards[sent_key]["hints_list"].append(chinese_hint)

                    # 2. 处理背面详细 (单词 + 音标 + 中文)
                    # 检查是否已经添加过这个组合，防止重复
                    detail_entry = {
                        "word": word_text,
                        "phon": phonetic,
                        "mean": chinese_hint
                    }
                    if detail_entry not in processed_cards[sent_key]["details_list"]:
                        processed_cards[sent_key]["details_list"].append(detail_entry)

                    if word_text not in processed_cards[sent_key]["base_words"]:
                        processed_cards[sent_key]["base_words"].append(word_text)
                else:
                    pass

    logger(f"数据处理完成，共生成 {len(processed_cards)} 张聚合卡片数据。")
    return processed_cards


def generate_cloze_sentence(card_data):
    sentence = card_data["original_sentence"]
    # 按长度倒序，防止短词替换了长词的一部分
    words = sorted(list(card_data["words_to_cloze"]), key=len, reverse=True)
    for w in words:
        # 使用正则进行全词匹配替换，避免替换掉单词内部
        pattern = re.compile(r'\b' + re.escape(w) + r'\b')
        # 如果单词包含特殊符号（如 bird's-eye），正则边界可能失效，直接替换文本
        if not re.search(r'^\w+$', w):
            sentence = sentence.replace(w, f"{{{{c1::{w}}}}}")
        else:
            sentence = pattern.sub(f"{{{{c1::{w}}}}}", sentence)
    return sentence