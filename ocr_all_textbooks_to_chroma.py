import os
from pathlib import Path
from pdf2image import convert_from_path
from google.cloud import vision
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "vision-ocr-key.json"
openai_key = os.getenv("OPENAI_API_KEY")

# Initialize Google Vision and ChromaDB
vision_client = vision.ImageAnnotatorClient()
client = chromadb.PersistentClient(path="chroma_store")
embedding_function = OpenAIEmbeddingFunction(api_key=openai_key)
collection = client.get_or_create_collection(name="student_notes", embedding_function=embedding_function)

# Root path for textbook PDFs
base_path = Path("Textbook_pages")

# Loop through all PDFs in all semester/grade/subject folders
for pdf_path in base_path.rglob("*.pdf"):
    try:
        parts = pdf_path.parts
        semester = next(p for p in parts if "semester" in p.lower())  # first_semester or second_semester
        grade_folder = next(p for p in parts if p.lower().startswith("grade_"))
        grade = grade_folder.replace("Grade_", "").replace("grade_", "").strip()
        subject = pdf_path.parent.name.strip()

        print(f"\n📘 OCR Processing: {pdf_path.name} [Semester: {semester}, Grade: {grade}, Subject: {subject}]")

        i = 0
        while True:
            try:
                page_number = i + 1
                images = convert_from_path(pdf_path, dpi=200, first_page=page_number, last_page=page_number)
                if not images:
                    break
                image = images[0]

                # Save page as temporary PNG
                temp_path = f"temp_page_{page_number}.png"
                image.save(temp_path)

                # OCR with Vision API
                with open(temp_path, "rb") as img_file:
                    content = img_file.read()
                    image_vision = vision.Image(content=content)
                    response = vision_client.document_text_detection(image=image_vision)
                    text = response.full_text_annotation.text.strip()

                os.remove(temp_path)

                # Upload to ChromaDB
                if text:
                    doc_id = f"{semester}_{grade}_{subject}_{pdf_path.stem}_page_{page_number}"
                    collection.add(
                        documents=[text],
                        ids=[doc_id],
                        metadatas=[{
                            "semester": semester,
                            "grade": grade,
                            "subject": subject
                        }]
                    )

                i += 1

            except Exception:
                break

        print(f"✅ OCR Completed for {pdf_path.name}")

    except Exception as e:
        print(f"❌ Error processing {pdf_path.name}: {e}")

print("\n🎉 All textbooks OCR-processed and added to ChromaDB.")
