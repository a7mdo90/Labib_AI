#!/usr/bin/env python3
"""
Labib Telegram Bot - All-in-One Script
=====================================

This is the main script that combines all functionality:
- Telegram bot operations
- Textbook processing and OCR
- Database management
- Health monitoring
- File organization
- Deployment utilities

Author: Labib AI Team
Date: September 18, 2025
"""

import os
import sys
import time
import json
import logging
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import asyncio

# Third-party imports
from pdf2image import convert_from_path
from google.cloud import vision
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from dotenv import load_dotenv
import telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('labib_bot.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class LabibBot:
    """Main Labib Bot class with all functionality."""
    
    def __init__(self):
        """Initialize the bot with all components."""
        self.setup_environment()
        self.setup_clients()
        self.setup_collection()
        self.user_states = {}
        self.stats = {
            'total_files': 0,
            'processed_files': 0,
            'failed_files': 0,
            'total_pages': 0,
            'processed_pages': 0,
            'interactions': 0,
            'questions_answered': 0
        }
        
    def setup_environment(self):
        """Load environment variables and validate configuration."""
        load_dotenv()
        
        # Set Google Cloud credentials
        if not os.path.exists("vision-ocr-key.json"):
            raise FileNotFoundError("Google Cloud Vision API key file not found: vision-ocr-key.json")
        
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "vision-ocr-key.json"
        
        # Set OpenAI API key directly
        self.openai_key = "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"
        os.environ["OPENAI_API_KEY"] = self.openai_key
        
        # Telegram token
        self.telegram_token = "8139033915:AAFZrysdKan225y4G3HnQ08aYxrFk3uTMQM"
        
        logger.info("Environment configuration loaded successfully")
    
    def setup_clients(self):
        """Initialize all external clients."""
        try:
            # Google Vision client
            self.vision_client = vision.ImageAnnotatorClient()
            
            # ChromaDB client
            self.chroma_client = chromadb.PersistentClient(path="chroma_store")
            self.embedding_function = OpenAIEmbeddingFunction(api_key=self.openai_key)
            
            logger.info("All clients initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize clients: {e}")
            raise
    
    def setup_collection(self):
        """Setup ChromaDB collection."""
        try:
            self.collection = self.chroma_client.get_or_create_collection(
                name="student_notes",
                embedding_function=self.embedding_function
            )
            logger.info("ChromaDB collection 'student_notes' ready")
        except Exception as e:
            logger.error(f"Failed to setup collection: {e}")
            raise
    
    # ==================== TEXTBOOK PROCESSING ====================
    
    def extract_metadata(self, pdf_path: Path) -> Dict[str, str]:
        """Extract metadata from PDF file path."""
        parts = pdf_path.parts
        
        metadata = {
            'file_name': pdf_path.name,
            'file_path': str(pdf_path),
            'semester': 'unknown',
            'grade': 'unknown',
            'subject': 'unknown',
            'processed_date': datetime.now().isoformat()
        }
        
        try:
            # Extract semester
            for part in parts:
                if 'semester' in part.lower():
                    metadata['semester'] = part
                    break
                elif 'فصل' in part or 'اول' in part or 'ثاني' in part:
                    metadata['semester'] = part
                    break
            
            # Extract grade
            for part in parts:
                if part.lower().startswith('grade_'):
                    metadata['grade'] = part.replace('Grade_', '').replace('grade_', '').strip()
                    break
                elif any(grade in part for grade in ['اول', 'ثاني', 'ثالث', 'رابع', 'خامس', 'سادس', 'سابع', 'ثامن', 'تاسع', 'عاشر', 'حادي', 'ثاني عشر']):
                    metadata['grade'] = part
                    break
            
            # Extract subject
            metadata['subject'] = pdf_path.parent.name.strip()
            
        except Exception as e:
            logger.warning(f"Could not extract metadata from {pdf_path}: {e}")
        
        return metadata
    
    def process_pdf_page(self, pdf_path: Path, page_number: int) -> Optional[str]:
        """Process a single PDF page and return OCR text."""
        try:
            # Set poppler path
            poppler_path = str(Path("poppler-24.08.0/Library/bin").absolute())
            
            # Convert PDF page to image
            images = convert_from_path(
                pdf_path, 
                dpi=200, 
                first_page=page_number, 
                last_page=page_number,
                poppler_path=poppler_path
            )
            
            if not images:
                return None
            
            image = images[0]
            
            # Save temporary image
            temp_path = f"temp_page_{page_number}_{int(time.time())}.png"
            image.save(temp_path)
            
            try:
                # Perform OCR
                with open(temp_path, "rb") as img_file:
                    content = img_file.read()
                    image_vision = vision.Image(content=content)
                    response = self.vision_client.document_text_detection(image=image_vision)
                    
                    if response.error.message:
                        logger.error(f"Vision API error: {response.error.message}")
                        return None
                    
                    text = response.full_text_annotation.text.strip()
                    return text if text else None
                    
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
        except Exception as e:
            logger.error(f"Error processing page {page_number} of {pdf_path.name}: {e}")
            return None
    
    def add_to_database(self, text: str, metadata: Dict[str, str], page_number: int) -> bool:
        """Add processed text to ChromaDB."""
        try:
            doc_id = f"{metadata['semester']}_{metadata['grade']}_{metadata['subject']}_{metadata['file_name']}_page_{page_number}"
            
            db_metadata = {
                'semester': metadata['semester'],
                'grade': metadata['grade'],
                'subject': metadata['subject'],
                'file_name': metadata['file_name'],
                'page_number': str(page_number),
                'processed_date': metadata['processed_date']
            }
            
            self.collection.add(
                documents=[text],
                ids=[doc_id],
                metadatas=[db_metadata]
            )
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to add to database: {e}")
            return False
    
    def process_single_pdf(self, pdf_path: Path) -> bool:
        """Process a single PDF file completely."""
        logger.info(f"Processing: {pdf_path.name}")
        
        metadata = self.extract_metadata(pdf_path)
        logger.info(f"Metadata: Semester={metadata['semester']}, Grade={metadata['grade']}, Subject={metadata['subject']}")
        
        page_count = 0
        processed_pages = 0
        
        try:
            page_number = 1
            while True:
                text = self.process_pdf_page(pdf_path, page_number)
                
                if text is None:
                    break
                
                page_count += 1
                
                # Add to database if text is meaningful
                if len(text.strip()) > 50:
                    if self.add_to_database(text, metadata, page_number):
                        processed_pages += 1
                        logger.info(f"Page {page_number} processed ({len(text)} characters)")
                    else:
                        logger.error(f"Failed to add page {page_number} to database")
                else:
                    logger.warning(f"Page {page_number} has insufficient text ({len(text)} characters)")
                
                page_number += 1
                
                # Safety limit
                if page_number > 1000:
                    logger.warning(f"Reached safety limit of 1000 pages for {pdf_path.name}")
                    break
            
            logger.info(f"Completed {pdf_path.name}: {processed_pages}/{page_count} pages processed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to process {pdf_path.name}: {e}")
            return False
    
    def process_all_textbooks(self, base_path: str = "Textbook_pages") -> bool:
        """Process all textbook PDFs."""
        logger.info("Starting textbook processing...")
        
        base_path = Path(base_path)
        
        if not base_path.exists():
            logger.error(f"Textbook directory not found: {base_path}")
            return False
        
        pdf_files = list(base_path.rglob("*.pdf"))
        self.stats['total_files'] = len(pdf_files)
        logger.info(f"Found {len(pdf_files)} PDF files")
        
        if not pdf_files:
            logger.error("No PDF files found to process")
            return False
        
        # Process each PDF
        for i, pdf_path in enumerate(pdf_files, 1):
            logger.info(f"Processing file {i}/{len(pdf_files)}: {pdf_path.name}")
            
            try:
                if self.process_single_pdf(pdf_path):
                    self.stats['processed_files'] += 1
                else:
                    self.stats['failed_files'] += 1
                    
            except KeyboardInterrupt:
                logger.info("Processing interrupted by user")
                break
            except Exception as e:
                logger.error(f"Unexpected error processing {pdf_path.name}: {e}")
                self.stats['failed_files'] += 1
        
        # Print statistics
        logger.info("PROCESSING STATISTICS:")
        logger.info(f"Total PDF files found: {self.stats['total_files']}")
        logger.info(f"Successfully processed: {self.stats['processed_files']}")
        logger.info(f"Failed files: {self.stats['failed_files']}")
        logger.info(f"Total pages processed: {self.stats['processed_pages']}")
        
        try:
            collection_count = self.collection.count()
            logger.info(f"Database documents: {collection_count}")
        except Exception as e:
            logger.error(f"Failed to get database count: {e}")
        
        logger.info("Textbook processing completed!")
        return True
    
    # ==================== TELEGRAM BOT FUNCTIONALITY ====================
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        user_id = update.effective_user.id
        self.user_states[user_id] = {'state': 'started'}
        self.stats['interactions'] += 1
        
        welcome_message = """
مرحباً! أنا مساعدك الذكي لبيب 🤖

يمكنني مساعدتك في:
📚 الإجابة على أسئلة المناهج الدراسية
🔍 البحث في الكتب المدرسية
📖 تحليل الصور والنصوص
💬 الدردشة والمساعدة التعليمية

أرسل لي سؤالاً أو صورة وسأقوم بمساعدتك!
        """
        
        await update.message.reply_text(welcome_message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_text = """
أوامر البوت:
/start - بدء المحادثة
/help - عرض هذه المساعدة
/status - حالة البوت والإحصائيات
/process - معالجة الكتب المدرسية
/health - فحص صحة النظام

يمكنك أيضاً:
- إرسال أسئلة نصية
- إرسال صور للتحليل
- إرسال ملفات PDF
        """
        
        await update.message.reply_text(help_text)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command."""
        try:
            collection_count = self.collection.count()
            status_text = f"""
حالة البوت:
📊 إجمالي التفاعلات: {self.stats['interactions']}
❓ الأسئلة المجابة: {self.stats['questions_answered']}
📚 الملفات المعالجة: {self.stats['processed_files']}
🗄️ مستندات قاعدة البيانات: {collection_count}
⏰ آخر تحديث: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            await update.message.reply_text(status_text)
        except Exception as e:
            await update.message.reply_text(f"خطأ في الحصول على الحالة: {e}")
    
    async def process_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /process command."""
        await update.message.reply_text("بدء معالجة الكتب المدرسية...")
        
        try:
            success = self.process_all_textbooks()
            if success:
                await update.message.reply_text("✅ تمت معالجة الكتب بنجاح!")
            else:
                await update.message.reply_text("❌ فشلت معالجة الكتب")
        except Exception as e:
            await update.message.reply_text(f"خطأ في المعالجة: {e}")
    
    async def health_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /health command."""
        try:
            # Check Google Vision API
            test_image = vision.Image(content=b"test")
            response = self.vision_client.document_text_detection(image=test_image)
            vision_status = "✅ OK" if not response.error.message else "❌ Error"
            
            # Check ChromaDB
            count = self.collection.count()
            chroma_status = f"✅ OK ({count} documents)"
            
            # Check OpenAI API
            test_embedding = self.embedding_function(["test"])
            openai_status = "✅ OK"
            
            health_text = f"""
فحص صحة النظام:
🔍 Google Vision API: {vision_status}
🗄️ ChromaDB: {chroma_status}
🤖 OpenAI API: {openai_status}
⏰ وقت الفحص: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
            """
            
            await update.message.reply_text(health_text)
        except Exception as e:
            await update.message.reply_text(f"خطأ في فحص الصحة: {e}")
    
    async def handle_text_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages."""
        user_id = update.effective_user.id
        text = update.message.text
        
        self.stats['interactions'] += 1
        
        try:
            # Search for relevant content in database
            results = self.collection.query(
                query_texts=[text],
                n_results=5
            )
            
            if results['documents'] and results['documents'][0]:
                # Combine relevant content
                context_text = "\n".join(results['documents'][0])
                
                # Generate response using OpenAI (simplified)
                response = f"بناءً على البحث في الكتب المدرسية:\n\n{context_text[:1000]}..."
                
                await update.message.reply_text(response)
                self.stats['questions_answered'] += 1
            else:
                await update.message.reply_text("لم أجد معلومات ذات صلة في قاعدة البيانات. حاول إرسال صورة أو سؤال أكثر تحديداً.")
                
        except Exception as e:
            logger.error(f"Error handling text message: {e}")
            await update.message.reply_text("عذراً، حدث خطأ في معالجة رسالتك.")
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle photo messages."""
        user_id = update.effective_user.id
        self.stats['interactions'] += 1
        
        try:
            # Get the photo file
            photo = update.message.photo[-1]  # Get highest resolution
            file = await context.bot.get_file(photo.file_id)
            
            # Download photo
            temp_path = f"temp_photo_{int(time.time())}.jpg"
            await file.download_to_drive(temp_path)
            
            try:
                # Perform OCR on the photo
                with open(temp_path, "rb") as img_file:
                    content = img_file.read()
                    image_vision = vision.Image(content=content)
                    response = self.vision_client.document_text_detection(image=image_vision)
                    
                    if response.error.message:
                        await update.message.reply_text(f"خطأ في تحليل الصورة: {response.error.message}")
                        return
                    
                    text = response.full_text_annotation.text.strip()
                    
                    if text:
                        await update.message.reply_text(f"النص المستخرج من الصورة:\n\n{text}")
                        
                        # Search for relevant content
                        results = self.collection.query(
                            query_texts=[text],
                            n_results=3
                        )
                        
                        if results['documents'] and results['documents'][0]:
                            context_text = "\n".join(results['documents'][0])
                            await update.message.reply_text(f"معلومات ذات صلة:\n\n{context_text[:1000]}...")
                            self.stats['questions_answered'] += 1
                    else:
                        await update.message.reply_text("لم أتمكن من استخراج نص من الصورة.")
                        
            finally:
                # Clean up temporary file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
                    
        except Exception as e:
            logger.error(f"Error handling photo: {e}")
            await update.message.reply_text("عذراً، حدث خطأ في معالجة الصورة.")
    
    # ==================== UTILITY FUNCTIONS ====================
    
    def health_check(self) -> bool:
        """Perform comprehensive health check."""
        logger.info("Performing health check...")
        
        try:
            # Check Google Vision API
            test_image = vision.Image(content=b"test")
            response = self.vision_client.document_text_detection(image=test_image)
            logger.info("Google Vision API: OK")
            
            # Check ChromaDB
            count = self.collection.count()
            logger.info(f"ChromaDB: OK ({count} documents)")
            
            # Check OpenAI API
            test_embedding = self.embedding_function(["test"])
            logger.info("OpenAI API: OK")
            
            logger.info("All health checks passed!")
            return True
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False
    
    def cleanup_files(self):
        """Clean up temporary files."""
        logger.info("Cleaning up temporary files...")
        
        temp_patterns = [
            "temp_*.png",
            "temp_*.jpg",
            "temp_*.ogg",
            "temp_*.wav",
            "temp_page_*.png"
        ]
        
        cleaned_count = 0
        for pattern in temp_patterns:
            for file_path in Path(".").glob(pattern):
                try:
                    file_path.unlink()
                    cleaned_count += 1
                except Exception as e:
                    logger.warning(f"Could not remove {file_path}: {e}")
        
        logger.info(f"Cleaned up {cleaned_count} temporary files")
    
    def get_stats(self) -> Dict:
        """Get current statistics."""
        try:
            collection_count = self.collection.count()
            return {
                **self.stats,
                'database_documents': collection_count
            }
        except Exception as e:
            logger.error(f"Failed to get stats: {e}")
            return self.stats
    
    # ==================== MAIN FUNCTIONS ====================
    
    async def run_bot(self):
        """Run the Telegram bot."""
        logger.info("Starting Labib Telegram Bot...")
        
        # Create application
        application = Application.builder().token(self.telegram_token).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("status", self.status_command))
        application.add_handler(CommandHandler("process", self.process_command))
        application.add_handler(CommandHandler("health", self.health_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text_message))
        application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        
        # Start bot
        await application.run_polling()
    
    def run_textbook_processing(self, base_path: str = "Textbook_pages") -> bool:
        """Run textbook processing."""
        logger.info("Starting textbook processing...")
        
        # Run health check first
        if not self.health_check():
            logger.error("Health check failed, aborting textbook processing")
            return False
        
        # Process textbooks
        success = self.process_all_textbooks(base_path)
        
        if success:
            logger.info("Textbook processing completed successfully!")
            return True
        else:
            logger.error("Textbook processing failed!")
            return False

def main():
    """Main function with command line interface."""
    parser = argparse.ArgumentParser(description="Labib Telegram Bot - All-in-One Script")
    parser.add_argument("--mode", choices=["bot", "process", "health", "cleanup"], default="bot", 
                       help="Mode to run: bot (Telegram bot), process (textbook processing), health (health check), cleanup (cleanup files)")
    parser.add_argument("--textbook-path", default="Textbook_pages", help="Path to textbook directory")
    
    args = parser.parse_args()
    
    try:
        bot = LabibBot()
        
        if args.mode == "bot":
            # Run Telegram bot
            asyncio.run(bot.run_bot())
        elif args.mode == "process":
            # Process textbooks
            success = bot.run_textbook_processing(args.textbook_path)
            sys.exit(0 if success else 1)
        elif args.mode == "health":
            # Health check
            success = bot.health_check()
            sys.exit(0 if success else 1)
        elif args.mode == "cleanup":
            # Cleanup files
            bot.cleanup_files()
            sys.exit(0)
        
    except KeyboardInterrupt:
        logger.info("Process interrupted by user")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
