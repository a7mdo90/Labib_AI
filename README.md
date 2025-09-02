# Labib Telegram Bot - Educational AI Assistant

## English Description

**Labib** is an intelligent Telegram bot designed to help Kuwaiti students with their textbook questions. The bot uses AI-powered OCR (Optical Character Recognition) and natural language processing to provide accurate answers based on official Kuwaiti Ministry of Education textbooks.

### 🎯 Main Features

- **Smart Textbook Search**: Searches through digitized textbook content using ChromaDB vector database
- **OCR Processing**: Extracts text from textbook images and PDFs using Google Vision API
- **AI-Powered Answers**: Uses OpenAI GPT to provide accurate, curriculum-based responses
- **Multi-Grade Support**: Covers grades 1-12 with subject-specific assistance
- **Arabic Language Support**: Fully supports Arabic text and Kuwaiti curriculum
- **Image Upload**: Students can send photos of textbook pages for instant help

### 🏗️ Architecture

- **Frontend**: Telegram Bot API
- **Backend**: Python with async/await support
- **Database**: ChromaDB for vector storage and semantic search
- **AI Services**: OpenAI GPT-3.5-turbo for intelligent responses
- **OCR**: Google Cloud Vision API for text extraction
- **Deployment**: Docker containerization with persistent storage

### 📚 Supported Subjects

**Grades 1-5**: Arabic, English, Mathematics, Science, Islamic Education, Social Studies
**Grades 6-9**: Arabic, English, Mathematics, Science, Islamic Education, Social Studies  
**Grade 10**: Arabic, English, Mathematics, Islamic Education, Social Studies, Chemistry, Physics, Biology
**Grade 11**: Arabic, English, Mathematics (Scientific/Literary), Islamic Education, Social Studies, Chemistry, Physics, Biology, History, Geography, Psychology, French, Geology
**Grade 12**: Arabic, English, Mathematics (Scientific/Statistical Literary), Islamic Education, History, Geography, Philosophy, French, Constitution, Chemistry, Physics, Biology

---

## الوصف بالعربية

**لبيب** هو بوت تيليجرام ذكي مصمم لمساعدة الطلاب الكويتيين في أسئلة الكتب المدرسية. يستخدم البوت تقنية الذكاء الاصطناعي للتعرف على النصوص (OCR) ومعالجة اللغة الطبيعية لتقديم إجابات دقيقة بناءً على الكتب المدرسية الرسمية لوزارة التربية الكويتية.

### 🎯 الميزات الرئيسية

- **البحث الذكي في الكتب**: يبحث في محتوى الكتب المدرسية الرقمية باستخدام قاعدة بيانات ChromaDB المتجهية
- **معالجة النصوص**: يستخرج النصوص من صور الكتب المدرسية وملفات PDF باستخدام Google Vision API
- **إجابات ذكية**: يستخدم OpenAI GPT لتقديم استجابات دقيقة ومبنية على المنهج الدراسي
- **دعم متعدد الصفوف**: يغطي الصفوف من الأول إلى الثاني عشر مع مساعدة خاصة بكل مادة
- **دعم اللغة العربية**: يدعم النصوص العربية والمنهج الكويتي بالكامل
- **رفع الصور**: يمكن للطلاب إرسال صور من صفحات الكتب المدرسية للحصول على مساعدة فورية

### 🏗️ البنية التقنية

- **الواجهة الأمامية**: Telegram Bot API
- **الخلفية**: Python مع دعم async/await
- **قاعدة البيانات**: ChromaDB للتخزين المتجهي والبحث الدلالي
- **خدمات الذكاء الاصطناعي**: OpenAI GPT-3.5-turbo للاستجابات الذكية
- **التعرف على النصوص**: Google Cloud Vision API لاستخراج النصوص
- **النشر**: حاويات Docker مع تخزين دائم

---

## 🚀 Getting Started / البدء

### Prerequisites / المتطلبات

- Python 3.11+
- Docker and Docker Compose
- Google Cloud Vision API credentials
- OpenAI API key
- Telegram Bot Token

### Installation / التثبيت

1. Clone the repository
```bash
git clone <repository-url>
cd Labib_telegram_bot
```

2. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Run with Docker
```bash
docker-compose up -d
```

---

## 📋 Project Status & Tasks / حالة المشروع والمهام

### ✅ Completed / مكتمل
- [x] Core Telegram bot functionality
- [x] OCR processing for textbooks
- [x] ChromaDB integration
- [x] Multi-grade and subject support
- [x] Docker containerization
- [x] Arabic language support

### 🔄 In Progress / قيد التنفيذ
- [ ] Database optimization
- [ ] Error handling improvements
- [ ] Performance monitoring

### 📝 TODO / المهام المطلوبة
- [ ] **High Priority**
  - [ ] Clean up redundant OCR scripts
  - [ ] Consolidate database collections
  - [ ] Improve error handling and logging
  - [ ] Add rate limiting and user management
  - [ ] Implement proper environment variable management

- [ ] **Medium Priority**
  - [ ] Add analytics and usage tracking
  - [ ] Implement caching for common queries
  - [ ] Add admin panel for content management
  - [ ] Improve response quality with better prompts

- [ ] **Low Priority**
  - [ ] Add multi-language support (English interface)
  - [ ] Implement user feedback system
  - [ ] Add progress tracking for students
  - [ ] Create backup and recovery systems

### 🗑️ Redundant/Unused Files / الملفات الزائدة أو غير المستخدمة
- `instagram_poster.py` - Instagram automation (not needed for core functionality)
- `topic_bot.py` - Topic management bot (can be simplified)
- `bulk_metadata_ocr.py` - Duplicate OCR functionality
- `create_chroma_db.py` - Hardcoded API keys, needs cleanup
- Multiple OCR scripts with overlapping functionality

---

## 🛠️ Development / التطوير

### File Structure / هيكل الملفات
```
Labib_telegram_bot/
├── telegram_bot.py          # Main bot application
├── qa_engine.py             # Question-answer engine
├── requirements.txt          # Python dependencies
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker services
├── chroma_store/            # Vector database storage
├── Textbook_pages/          # Textbook PDFs organized by grade/subject
└── ocr_textspdf_uploads/    # OCR processed content
```

### Key Components / المكونات الرئيسية
1. **telegram_bot.py**: Main bot logic with conversation handling
2. **qa_engine.py**: AI-powered question answering system
3. **ChromaDB**: Vector database for semantic search
4. **Google Vision API**: OCR processing for images and PDFs
5. **OpenAI GPT**: Natural language understanding and response generation

---

## 🔧 Configuration / الإعداد

### Environment Variables / متغيرات البيئة
```bash
TELEGRAM_TOKEN=your_telegram_bot_token
OPENAI_API_KEY=your_openai_api_key
GOOGLE_APPLICATION_CREDENTIALS=path_to_vision_key.json
```

### Database Collections / مجموعات قاعدة البيانات
- `student_textbooks`: Main collection for textbook content
- `student_notes`: Additional notes and supplementary content

---

## 📊 Monitoring & Logs / المراقبة والسجلات

### Log Files / ملفات السجلات
- `student_logs.csv`: Student interaction logs
- `feedback_logs.csv`: User feedback and ratings

### Key Metrics / المقاييس الرئيسية
- Daily active users
- Questions answered per day
- OCR processing success rate
- Response quality ratings

---

## 🚀 Deployment / النشر

### Production Deployment / النشر الإنتاجي
```bash
# Build and deploy
docker-compose -f docker-compose.prod.yml up -d

# Monitor logs
docker-compose logs -f labib_bot

# Update and restart
docker-compose pull && docker-compose up -d
```

### Health Checks / فحوصات الصحة
- Bot responsiveness
- Database connectivity
- API service availability
- OCR processing pipeline

---

## 🤝 Contributing / المساهمة

### Development Guidelines / إرشادات التطوير
1. Follow PEP 8 Python style guide
2. Add comprehensive error handling
3. Include Arabic language support
4. Test with real textbook content
5. Document all API changes

### Code Review Process / عملية مراجعة الكود
1. Create feature branch
2. Implement changes with tests
3. Submit pull request
4. Code review and approval
5. Merge to main branch

---

## 📞 Support / الدعم

### Contact Information / معلومات الاتصال
- **Project Maintainer**: Labib Team
- **Telegram Bot**: @LabibBot
- **Issues**: GitHub Issues page

### Common Issues / المشاكل الشائعة
1. **OCR Processing Failures**: Check Google Vision API credentials
2. **Database Connection Issues**: Verify ChromaDB storage permissions
3. **Bot Not Responding**: Check Telegram token and network connectivity
4. **Memory Issues**: Monitor Docker container resource usage

---

## 📄 License / الترخيص

This project is proprietary software developed for educational purposes in Kuwait.

هذا المشروع برمجيات خاصة تم تطويرها لأغراض تعليمية في الكويت.

---

*Last Updated: December 2024*
*آخر تحديث: ديسمبر 2024*
