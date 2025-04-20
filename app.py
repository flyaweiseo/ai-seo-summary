import streamlit as st
import openai
import trafilatura
from newspaper import Article

# 頁面設定
st.set_page_config(page_title="AI SEO 顧問摘要工具", page_icon="📌")

# 設定 OpenAI 金鑰
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ✅ 優先使用 trafilatura，失敗時改用 newspaper3k
def fetch_article(url):
    downloaded = trafilatura.fetch_url(url)
    if downloaded:
        extracted = trafilatura.extract(downloaded, with_metadata=True)
        if extracted and extracted.get("text"):
            return {
                "content": extracted["text"],
                "title": extracted.get("title", "無標題文章（由 trafilatura 擷取）")
            }

    # ➕ 備援方案：使用 newspaper3k
    try:
        article = Article(url, language='zh')
        article.download()
        article.parse()
        if article.text:
            return {
                "content": article.text,
                "title": article.title or "無標題文章（由 newspaper 擷取）"
            }
    except:
        return None

    return None

# ✅ 用 GPT-4 生成繁體摘要
def summarize_article(content, title="（無標題）"):
    prompt = f"""
你是一位有15年經驗的資深SEO顧問，擅長快速理解中英文內容、統整資訊並提煉重點。

請將下方內容不論是中文或英文，皆以「繁體中文」輸出條列摘要與結語總結。

【輸出格式】
- 請於開頭加上文章標題，格式為：# 文章標題：{title}
1. 條列式摘要：請依照內容邏輯，加入重點段落標題（使用 H2 或 H3 標記），每個段落下用條列式寫出重點（使用 - 開頭），資訊分層清楚、乾淨有條理。
2. 結語總結：請以不超過 500 字的方式，以繁體中文寫出這篇文章的精隨，讓未閱讀原文者也能快速掌握重點。

【文章內容】：
{content}
"""
    client = openai.OpenAI(api_key=openai.api_key)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.4,
        max_tokens=2000
    )
    return response.choices[0].message.content.strip()

# ✅ Streamlit 主畫面
st.title("🔍 網頁內容重點摘要工具")

url = st.text_input("請輸入網頁連結：")

if url:
    with st.spinner("正在擷取與分析文章..."):
        data = fetch_article(url)
        if data and "content" in data and data["content"]:
            content = data["content"]
            title = data["title"]
            summary = summarize_article(content, title)

            st.subheader("📌 條列式摘要 + 精華總結")
            st.markdown(summary)

            with st.expander("📄 查看原始文章內容"):
                st.markdown(f"**原始文章標題：** {title}")
                st.write(content)

        else:
            st.error("❌ 無法擷取內容，請確認網址是否正確，或該網站是否支援文字擷取。")
