import sys
import os
import json
import time  # 引入时间库用于暂停
import traceback  # 用于打印错误详情

# 动态加载 libs 目录
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'libs'))
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry


class EudicClient:
    BASE_URL = "https://api.frdic.com/api/open/v1"

    def __init__(self, token):
        self.token = token
        self.headers = {
            'Authorization': token,
            'User-Agent': 'AnkiPlugin/1.0'
        }
        # 创建一个带有自动重试功能的 Session
        self.session = requests.Session()
        self.session.headers.update(self.headers)

        # 配置重试策略: 总共重试3次，遇到 500/502/503/504 错误或连接错误时重试
        retries = Retry(total=3, backoff_factor=1, status_forcelist=[500, 502, 503, 504])
        self.session.mount('https://', HTTPAdapter(max_retries=retries))

    def _safe_request(self, method, url, params=None):
        """
        封装一个安全的请求方法，处理超时和异常
        """
        try:
            # timeout=30 表示如果30秒没连上或没读到数据就超时，不再死等
            resp = self.session.request(method, url, params=params, timeout=30)
            resp.raise_for_status()  # 如果返回 4xx 或 5xx 错误，抛出异常
            # 每次请求后稍微休息一下，防止请求过快导致超时或封禁
            time.sleep(0.5)
            return resp
        except requests.exceptions.RequestException as e:
            # 这里打印错误但不让程序崩溃，交给调用层决定
            print(f"请求失败 [{url}]: {e}")
            raise e

    def check_auth(self):
        """验证 Token 是否有效"""
        url = f"{self.BASE_URL}/studylist/category?language=en"
        try:
            resp = self._safe_request("GET", url)
            if resp.status_code == 200:
                return True
        except:
            pass
        return False

    def get_categories(self):
        """获取生词本分类"""
        url = f"{self.BASE_URL}/studylist/category?language=en"
        try:
            resp = self._safe_request("GET", url)
            return resp.json().get('data', [])
        except:
            return []

    def get_words_in_category(self, category_id):
        """获取特定分类下的单词列表"""
        all_words = []
        page = 0
        page_size = 100

        while True:
            url = f"{self.BASE_URL}/studylist/words"
            params = {
                "language": "en",
                "category_id": category_id,
                "page": page,
                "page_size": page_size
            }

            try:
                resp = self._safe_request("GET", url, params=params)
                data = resp.json().get('data', [])

                if not data:
                    break

                all_words.extend(data)

                if len(data) < page_size:
                    break
                page += 1
            except Exception as e:
                # 如果某一页获取失败，记录错误并停止获取后续页，避免卡死
                print(f"获取单词列表第 {page} 页失败: {e}")
                break

        return all_words

    def get_all_notes(self):
        """【关键】获取所有笔记，处理分页 (增强版)"""
        all_notes = []
        page = 0
        page_size = 100

        retry_count = 0
        max_retries_per_page = 3

        while True:
            url = f"{self.BASE_URL}/studylist/notes"
            params = {
                "language": "en",
                "page": page,
                "page_size": page_size
            }

            try:
                # 发送请求
                resp = self._safe_request("GET", url, params=params)
                data = resp.json().get('data', [])

                if not data:
                    break

                all_notes.extend(data)

                # 如果数据量少于 page_size，说明是最后一页
                if len(data) < page_size:
                    break

                page += 1
                retry_count = 0  # 成功翻页，重置重试计数器

            except Exception as e:
                # 如果这一页失败了，尝试重试当前页，而不是直接退出
                retry_count += 1
                print(f"获取笔记第 {page} 页失败 ({retry_count}/{max_retries_per_page}): {e}")

                if retry_count >= max_retries_per_page:
                    print("重试次数过多，停止获取剩余笔记。")
                    break  # 放弃后续数据

                time.sleep(2)  # 失败后多休息几秒再试
                continue  # 重新执行循环，重试当前页

        return all_notes