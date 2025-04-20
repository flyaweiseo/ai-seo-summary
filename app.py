import streamlit as st
import openai
import trafilatura

st.set_page_config(page_title="AI SEO 顧問摘要工具", page_icon="📌")

openai.api_key = st.secrets["OPENAI_API_KEY"]

def fetch_article(url):
    downloaded = trafilatura.fetch_url(url)
    if downloaded:
        return trafilatura.extract(downloaded)
    return None

def summarize_article(content):
    prompt = f"""
你是一位有15年經驗的資深SEO顧問，善於快速理解中英文內容、擅長梳理文章架構、提煉重點與總結精華。

**請將下方內容不論是中文或英文，皆以「繁體中文」輸出條列摘要與結語總結。**

【輸出格式】
- 請於開頭加上文章標題，格式為：# 文章標題：{title}
1. 條列式摘要：請依照內容邏輯，加入重點段落標題（使用 H2 或 H3 標記），每個段落下用條列式寫出重點（使用 - 開頭），資訊分層清楚、乾淨有條理。
2. 結語總結：請以不超過 500 字的方式，寫出這篇文章的精隨，彷彿要讓沒看過文章的人快速理解核心觀點。

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

st.title("🔍 網頁內容重點摘要工具")

url = st.text_input("請輸入網頁連結：")

if url:
    with st.spinner("正在分析中..."):
        data = fetch_article(url)
        if data:
            content = data["content"]
            title = data["title"]
            summary = summarize_article(content, title)
            st.subheader("📌 條列式摘要 + 精華總結")
            st.markdown(summary)
        else:
            st.error("❌ 無法擷取內容，請確認網址是否正確。")
