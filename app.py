import streamlit as st
import openai
import trafilatura
from newspaper import Article

# 頁面設定
st.set_page_config(page_title="AI SEO 顧問摘要工具", page_icon="📌")
openai.api_key = st.secrets["OPENAI_API_KEY"]

# ✅ 正確版本 fetch_article（處理 trafilatura 回傳 str、不使用 .get()）
def fetch_article(url):
    downloaded = trafilatura.fetch_url(url)
    if downloaded:
        text = trafilatura.extract(downloaded)
        if text:
            metadata = trafilatura.metadata.extract_metadata(downloaded)
            title = metadata.title if metadata and metadata.title else "無標題文章（trafilatura）"
            return {
                "content": text,
                "title": title
            }

    # ➕ 備援方案：newspaper3k
    try:
        article = Article(url)
        article.download()
        article.parse()
        if article.text:
            return {
                "content": article.text,
                "title": article.title or "無標題文章（newspaper）"
            }
    except:
        return None

    return None

# ✅ GPT 繁體中文摘要邏輯
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

# ✅ Streamlit 主介面
st.title("🔍 AI SEO 顧問：網頁或貼文摘要工具（中英文輸入，繁中輸出）")

tab1, tab2 = st.tabs(["🌐 貼網址分析", "✍️ 貼上原文"])

# 👉 Tab 1：網址擷取分析
with tab1:
    url = st.text_input("請輸入網頁連結：")
    if url:
        with st.spinner("擷取與分析中..."):
            data = fetch_article(url)
            if data and "content" in data and data["content"]:
                content = data["content"]
                title = data["title"]
                summary = summarize_article(content, title)

                st.subheader("📌 條列式摘要 + 精華總結")
                st.markdown(summary)

                with st.expander("📄 原始文章內容"):
                    st.markdown(f"**原始文章標題：** {title}")
                    st.write(content)
            else:
                st.warning("⚠️ 擷取失敗，可能該網站使用防爬蟲，請改用下方【✍️ 貼上原文】分析")

# 👉 Tab 2：手動貼文分析
with tab2:
    title_input = st.text_input("文章標題（可空白）")
    content_input = st.text_area("請貼上你要分析的文章內容：", height=300)
    if st.button("生成摘要", key="manual"):
        if content_input.strip():
            summary = summarize_article(content_input, title_input or "手動輸入文章")
            st.subheader("📌 條列式摘要 + 精華總結")
            st.markdown(summary)
        else:
            st.error("❌ 內容不能為空")
