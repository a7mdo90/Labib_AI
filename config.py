"""
Labib Telegram Bot Configuration
إعدادات بوت تيليجرام لبيب
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Application configuration class"""
    
    # Bot Configuration
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
    TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    
    # Google Cloud Vision Configuration
    GOOGLE_APPLICATION_CREDENTIALS = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    
    # Database Configuration
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "./chroma_store")
    
    # Application Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
    
    # Instagram Configuration (Optional)
    IG_USER_ID = os.getenv("IG_USER_ID")
    IG_ACCESS_TOKEN = os.getenv("IG_ACCESS_TOKEN")
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required_vars = [
            "TELEGRAM_TOKEN",
            "OPENAI_API_KEY",
            "GOOGLE_APPLICATION_CREDENTIALS"
        ]
        
        missing_vars = []
        for var in required_vars:
            if not getattr(cls, var):
                missing_vars.append(var)
        
        if missing_vars:
            raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
        
        return True
    
    @classmethod
    def is_production(cls):
        """Check if running in production"""
        return cls.ENVIRONMENT.lower() == "production"
    
    @classmethod
    def is_development(cls):
        """Check if running in development"""
        return cls.ENVIRONMENT.lower() == "development"

# Grade and subject mapping
GRADE_SUBJECTS = {
    "1": ["عربي", "انجليزي", "رياضيات", "علوم", "تربية اسلامية"],
    "2": ["عربي", "انجليزي", "رياضيات", "علوم", "تربية اسلامية"],
    "3": ["عربي", "انجليزي", "رياضيات", "علوم", "تربية اسلامية"],
    "4": ["عربي", "انجليزي", "رياضيات", "علوم", "تربية اسلامية", "اجتماعيات"],
    "5": ["عربي", "انجليزي", "رياضيات", "علوم", "تربية اسلامية", "اجتماعيات"],
    "6": ["عربي", "انجليزي", "رياضيات", "علوم", "تربية اسلامية", "اجتماعيات"],
    "7": ["عربي", "انجليزي", "رياضيات", "علوم", "تربية اسلامية", "اجتماعيات"],
    "8": ["عربي", "انجليزي", "رياضيات", "علوم", "تربية اسلامية", "اجتماعيات"],
    "9": ["عربي", "انجليزي", "رياضيات", "علوم", "تربية اسلامية", "اجتماعيات"],
    "10": ["عربي", "انجليزي", "رياضيات", "تربية اسلامية", "اجتماعيات", "كيمياء", "فيزياء", "احياء"],
    "11": ["عربي", "انجليزي", "رياضيات علمي", "رياضيات ادبي", "تربية اسلامية", "اجتماعيات",
           "كيمياء", "فيزياء", "احياء", "تاريخ", "جغرافيا", "علم نفس", "اللغة الفرنسية", "جيولوجيا"],
    "12": ["عربي", "انجليزي", "رياضيات احصاء ادبي", "تربية اسلامية", "تاريخ", "جغرافيا",
           "فلسفة", "اللغة الفرنسية", "دستور", "رياضيات علمي", "كيمياء", "فيزياء", "احياء"],
}

# System prompts
SYSTEM_PROMPT = (
    "أنت معلم كويتي محترف وذو خبرة في تدريس جميع المواد من الصف الأول إلى الصف الثاني عشر "
    "وفقًا لمنهج وزارة التربية في الكويت.\n\n"
    "لقد تم تزويدك بنسخة رقمية من محتوى الكتاب المدرسي الرسمي، لذلك يجب أن تعتمد فقط على هذا "
    "المحتوى في إجاباتك.\n\n"
    "مهمتك هي مساعدة الطلاب في فهم وإجابة أسئلة نهاية الدروس بشكل دقيق، وبأسلوب بسيط وواضح. "
    "لا تضف أي معلومة من خارج الكتاب. يمكنك إعادة صياغة الإجابات لتسهيل الفهم، لكن بدون تغيير "
    "المعنى.\n\n"
    "إذا لم تجد الإجابة في السياق المقدم، اجب على السؤال بشكل مختصر جداً بدون أي شرح مطول."
)

# Conversation states
ASK_PHONE, GRADE, SUBJECT, QUESTION, RATING, COMMENT = range(6)

# File paths
INTERACTIONS_LOG = "student_logs.csv"
FEEDBACK_LOG = "feedback_logs.csv"
