import streamlit as st

# ページ設定（これを最初に！）
st.set_page_config(
    page_title="Tech0 Web→スライド生成",
    page_icon="🎯",
    layout="wide"
)

from openai import OpenAI
import os
from duckduckgo_search import DDGS
import json

# OpenAI APIの設定
# Streamlit Cloud用とローカル用の両方に対応
try:
    # Streamlit Cloudの場合
    api_key = st.secrets["OPENAI_API_KEY"]
except (FileNotFoundError, KeyError):
    # ローカル環境の場合
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    st.error("❌ OPENAI_API_KEYが設定されていません。環境変数を確認してください。")
    st.info("""
    **Streamlit Cloudの場合:**
    Settings → Secrets で以下を設定してください:
```
    OPENAI_API_KEY = "your_key_here"
```
    
    **ローカルの場合:**
    .envファイルを作成してください:
```
    OPENAI_API_KEY=your_key_here
```
    """)
    st.stop()

client = OpenAI(api_key=api_key)

# カスタムCSS
st.markdown("""
<style>
    .main-title {
        font-size: 48px;
        font-weight: bold;
        text-align: center;
        color: #2196F3;
        margin-bottom: 10px;
    }
    .sub-title {
        font-size: 20px;
        text-align: center;
        color: #666;
        margin-bottom: 30px;
    }
    .stButton>button {
        width: 100%;
        background-color: #2196F3;
        color: white;
        font-size: 18px;
        padding: 15px;
        border-radius: 8px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# タイトル
st.markdown('<div class="main-title">🌐 Web検索→スライド自動生成</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">調べたいテーマを入力すると、Web検索結果からプレゼン資料を自動生成!</div>', unsafe_allow_html=True)

# Web検索関数(DuckDuckGo使用)
def search_web(query, max_results=5):
    """DuckDuckGoでWeb検索"""
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=max_results))
            
        search_text = f"「{query}」の検索結果:\n\n"
        for i, result in enumerate(results, 1):
            search_text += f"{i}. {result['title']}\n"
            search_text += f"   {result['body']}\n\n"
        
        return search_text
    except Exception as e:
        return f"検索エラー: {str(e)}\n\nデモモードで進めます。"

# OpenAI APIでスライド生成
def generate_slide_content(topic, search_results):
    """検索結果からスライドコンテンツを生成"""
    
    prompt = f"""以下のWeb検索結果をもとに、「{topic}」についてのプレゼンテーションスライド(1枚)のコンテンツを生成してください。

検索結果:
{search_results}

以下のJSON形式で出力してください:
{{
  "title": "スライドのタイトル(短く印象的に)",
  "subtitle": "サブタイトル(1行で)",
  "sections": [
    {{
      "heading": "セクション見出し1",
      "points": ["ポイント1", "ポイント2", "ポイント3"]
    }},
    {{
      "heading": "セクション見出し2",
      "points": ["ポイント1", "ポイント2", "ポイント3"]
    }}
  ],
  "footer": "出典や補足情報"
}}

重要:
- ビジネスプレゼンに適した内容に
- 各ポイントは簡潔に(20文字以内)
- セクションは2つまで
- 数字や具体例を含める
"""
    
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "あなたはプレゼンテーション資料作成のプロです。"},
            {"role": "user", "content": prompt}
        ],
        response_format={"type": "json_object"}
    )
    
    return json.loads(response.choices[0].message.content)

# HTMLスライド生成
def generate_html_slide(content):
    """HTMLスライドを生成"""
    
    sections_html = ""
    for section in content["sections"]:
        points_html = "".join([f'<li>{point}</li>' for point in section["points"]])
        sections_html += f"""
        <div class="content-section">
            <h2 class="section-heading">{section["heading"]}</h2>
            <ul class="points-list">
                {points_html}
            </ul>
        </div>
        """
    
    html = f"""<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{content["title"]} - Tech0</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        
        body {{
            font-family: 'Segoe UI', 'Hiragino Sans', 'Hiragino Kaku Gothic ProN', Meiryo, sans-serif;
            background: white;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
            padding: 20px;
        }}
        
        .slide {{
            width: 1200px;
            height: 675px;
            background: white;
            border-radius: 12px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            padding: 60px 80px;
            position: relative;
            overflow: hidden;
        }}
        
        .tech0-logo {{
            position: absolute;
            top: 40px;
            right: 80px;
            font-size: 36px;
            font-weight: bold;
            color: #2196F3;
            letter-spacing: 2px;
        }}
        
        .slide-title {{
            font-size: 56px;
            font-weight: bold;
            color: #1a1a1a;
            margin-bottom: 16px;
            line-height: 1.2;
        }}
        
        .slide-subtitle {{
            font-size: 22px;
            color: #666;
            margin-bottom: 50px;
            padding-bottom: 20px;
            border-bottom: 3px solid #2196F3;
        }}
        
        .content-section {{
            margin-bottom: 40px;
        }}
        
        .section-heading {{
            font-size: 28px;
            font-weight: bold;
            color: #2196F3;
            margin-bottom: 20px;
        }}
        
        .points-list {{
            list-style: none;
            padding-left: 0;
        }}
        
        .points-list li {{
            font-size: 24px;
            color: #333;
            margin-bottom: 16px;
            padding-left: 40px;
            position: relative;
            line-height: 1.4;
        }}
        
        .points-list li:before {{
            content: "▶";
            position: absolute;
            left: 0;
            color: #2196F3;
            font-size: 20px;
        }}
        
        .slide-footer {{
            position: absolute;
            bottom: 40px;
            left: 80px;
            right: 80px;
            font-size: 16px;
            color: #999;
            text-align: center;
        }}
    </style>
</head>
<body>
    <div class="slide">
        <div class="tech0-logo">Tech0</div>
        
        <h1 class="slide-title">{content["title"]}</h1>
        <p class="slide-subtitle">{content["subtitle"]}</p>
        
        {sections_html}
        
        <div class="slide-footer">{content["footer"]}</div>
    </div>
</body>
</html>"""
    
    return html

# メインUI
col1, col2 = st.columns([2, 1])

with col1:
    topic = st.text_input(
        "📝 調べたいテーマを入力",
        placeholder="例: 生成AIの活用事例",
        help="Web検索してスライドを自動生成します"
    )

with col2:
    st.write("")  # スペース調整
    st.write("")
    generate_button = st.button("🚀 スライド生成", type="primary")

# 生成処理
if generate_button and topic:
    with st.spinner('🔍 Web検索中...'):
        # Web検索
        search_results = search_web(topic)
        
        # 検索結果表示
        with st.expander("📊 検索結果を見る"):
            st.text(search_results)
    
    with st.spinner('✨ OpenAI APIでスライド生成中...'):
        # スライドコンテンツ生成
        slide_content = generate_slide_content(topic, search_results)
        
        # HTML生成
        html_slide = generate_html_slide(slide_content)
        
        # セッション状態に保存
        st.session_state.html_slide = html_slide
        st.session_state.topic = topic

# 生成されたスライドの表示
if 'html_slide' in st.session_state:
    st.markdown("---")
    st.markdown("### ✨ 生成されたスライド")
    
    col1, col2 = st.columns([3, 1])
    with col2:
        st.download_button(
            label="📥 HTMLダウンロード",
            data=st.session_state.html_slide,
            file_name=f"{st.session_state.topic.replace(' ', '_')}_slide.html",
            mime="text/html"
        )
    
    # iframeで表示
    st.components.v1.html(st.session_state.html_slide, height=700, scrolling=True)
    
    st.info("💡 ダウンロードしたHTMLファイルをブラウザで開くと、フルサイズで表示できます!")

# 使い方説明
if 'html_slide' not in st.session_state:
    st.markdown("---")
    st.markdown("### 🚀 使い方")
    st.markdown("""
    1. **調べたいテーマを入力** (例: "生成AIの活用事例")
    2. **「スライド生成」ボタンをクリック**
    3. **Web検索 → OpenAI APIで整理 → スライド自動生成!**
    4. **HTMLダウンロードして、そのままプレゼンに使える!**
    
    **Tech0のロゴ**が右上に青文字で入ります! 🎯
    """)