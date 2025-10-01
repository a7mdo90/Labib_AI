# qa_engine.py

import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction

def search_notes(question, grade, subject, openai_client):
    client = chromadb.PersistentClient(path="chroma_store")
    embedding_function = OpenAIEmbeddingFunction(api_key=openai_client.api_key)
    collection = client.get_or_create_collection(name="student_notes", embedding_function=embedding_function)

    # Query
    results = collection.query(
        query_texts=[question],
        n_results=5,
        where={"$and": [{"grade": {"$eq": grade}}, {"subject": {"$eq": subject}}]}
    )

    if not results["documents"] or not results["documents"][0]:
        return "❌ عذرًا، لم أتمكن من العثور على إجابة في الكتاب. جرب صياغة مختلفة أو أرسل صورة أو اختر مادة مختلفة."

    # Prepare context
    chunks = results["documents"][0]
    context = "\n\n".join(chunks)

    # Prompt
    system_prompt = (
        "أنت معلم كويتي محترف وذو خبرة في تدريس جميع المواد من الصف الأول إلى الصف الثاني عشر وفقًا لمنهج وزارة التربية في الكويت. "
        "لقد تم تزويدك بنسخة رقمية من محتوى الكتاب المدرسي الرسمي، لذلك يجب أن تعتمد فقط على هذا المحتوى في إجاباتك. "
        "مهمتك هي مساعدة الطلاب في فهم وإجابة أسئلة نهاية الدروس بشكل دقيق، وبأسلوب بسيط وواضح. "
        "لا تضف أي معلومة من خارج الكتاب. يمكنك إعادة صياغة الإجابات لتسهيل الفهم، لكن بدون تغيير المعنى. "
        "إذا لم تجد الإجابة في السياق المقدم، اجب على السؤال بشكل مختصر جدا بدون اي شرح مطول."
    )

    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"السؤال:\n{question}\n\nالسياق:\n{context}"}
        ]
    )

    return response.choices[0].message.content.strip()
