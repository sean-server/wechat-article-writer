#!/usr/bin/env python3
import urllib.request, urllib.parse, json, os, sys

# Read article content
article_path = '/Users/xiaoan/.workbuddy/skills/wechat-article-writer/outputs/2026-03-21/大模型越来越强-我们还需要学习吗/article.md'
with open(article_path, encoding='utf-8') as f:
    content = f.read()

client_id = os.environ.get('IMA_OPENAPI_CLIENTID', 'a457db5d35a635c9d8abcbbd32b4d5a0')
doc_id = '7440917942268450'

url = f"https://ima.woa.com/openapi/notes/documents/{doc_id}/content"
payload = json.dumps({"content": content, "append": True}, ensure_ascii=False).encode('utf-8')

req = urllib.request.Request(url, data=payload, method='POST', headers={
    'Content-Type': 'application/json',
    'X-OpenAPI-ClientID': client_id,
    'X-OpenAPI-Version': '2024-11-01'
})

try:
    resp = urllib.request.urlopen(req, timeout=20)
    result = resp.read().decode()
    print("Success:", result)
except urllib.error.HTTPError as e:
    print("HTTP Error:", e.code, e.read().decode())
except Exception as e:
    print("Error:", e)
