# 小児粉薬チェッカー — 起動手順

## 必要ファイル（同じフォルダに置く）
```
app.py
pediatric_master_full.json
```

## インストール
```bash
pip install streamlit
```

## 起動（PC / ローカル）
```bash
streamlit run app.py
```
ブラウザで http://localhost:8501 が開きます。

## スマホからアクセスする方法
PCとスマホが同じWi-Fiにつながっている場合:
```bash
streamlit run app.py --server.address=0.0.0.0
```
スマホブラウザで → http://[PCのIPアドレス]:8501

## クラウドへの展開（Streamlit Community Cloud）
1. GitHubリポジトリに app.py と pediatric_master_full.json をプッシュ
2. https://share.streamlit.io にアクセス
3. リポジトリを選択して「Deploy」→ URLが発行される
4. スマホのブラウザでそのURLにアクセス

## requirements.txt の内容
```
streamlit>=1.32.0
```
