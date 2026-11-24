# Antigravity CLI (`agy`) Python 連携クライアント

Windows 11（スマート アプリ コントロール有効環境）でも OS ブロックを受けず正規に動作する、Google 署名済み `agy.exe` ベースの Python ラッパー（外部パッケージ依存なし・Python 標準ライブラリのみ）です。

## 使い方

```python
import sys
sys.path.insert(0, ".agents/scripts")

from agy_client import AgyClient

client = AgyClient(cwd=".")
res = client.run("このリポジトリの概要を3行で要約して")
print(res.response)
print("conversation_id:", res.conversation_id)
print("usage:", res.usage)
```

### 非同期（`asyncio`）実行

```python
import asyncio
from agy_client import AgyClient

async def main():
    client = AgyClient(cwd=".")
    res = await client.arun("Reply with: OK")
    print(res.response)

asyncio.run(main())
```

### ストリーミング（`stream-json`）

```python
from agy_client import AgyClient

client = AgyClient(cwd=".")
for event in client.stream("README の改善点を1つ挙げて"):
    print(event)
```
