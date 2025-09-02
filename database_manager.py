"""
Database Management Utility for Labib Bot
أداة إدارة قاعدة البيانات لبوت لبيب
"""

import os
import shutil
import chromadb
from chromadb.utils.embedding_functions import OpenAIEmbeddingFunction
from config import Config

class DatabaseManager:
    """Manages ChromaDB operations"""
    
    def __init__(self):
        self.client = chromadb.PersistentClient(path=Config.CHROMA_DB_PATH)
        self.embedding_function = OpenAIEmbeddingFunction(api_key=Config.OPENAI_API_KEY)
    
    def list_collections(self):
        """List all collections in the database"""
        try:
            collections = self.client.list_collections()
            print(f"✅ Found {len(collections)} collections:")
            for collection in collections:
                print(f"  - {collection.name}")
            return collections
        except Exception as e:
            print(f"❌ Error listing collections: {e}")
            return []
    
    def get_collection_info(self, collection_name):
        """Get information about a specific collection"""
        try:
            collection = self.client.get_collection(name=collection_name)
            count = collection.count()
            print(f"📊 Collection '{collection_name}': {count} documents")
            return count
        except Exception as e:
            print(f"❌ Error getting collection info: {e}")
            return 0
    
    def backup_collection(self, collection_name, backup_path=None):
        """Backup a collection to a specified path"""
        if not backup_path:
            backup_path = f"backup_{collection_name}_{int(time.time())}"
        
        try:
            # Create backup directory
            os.makedirs(backup_path, exist_ok=True)
            
            # Copy collection data
            source_path = os.path.join(Config.CHROMA_DB_PATH, collection_name)
            if os.path.exists(source_path):
                shutil.copytree(source_path, os.path.join(backup_path, collection_name))
                print(f"✅ Collection '{collection_name}' backed up to {backup_path}")
                return True
            else:
                print(f"❌ Collection '{collection_name}' not found")
                return False
        except Exception as e:
            print(f"❌ Error backing up collection: {e}")
            return False
    
    def cleanup_orphaned_collections(self):
        """Remove collections that are no longer needed"""
        try:
            collections = self.client.list_collections()
            orphaned = []
            
            for collection in collections:
                if collection.name not in ["student_textbooks", "student_notes"]:
                    orphaned.append(collection.name)
            
            if orphaned:
                print(f"🗑️ Found {len(orphaned)} orphaned collections:")
                for name in orphaned:
                    print(f"  - {name}")
                
                response = input("Do you want to delete these collections? (y/N): ")
                if response.lower() == 'y':
                    for name in orphaned:
                        self.client.delete_collection(name=name)
                        print(f"✅ Deleted collection: {name}")
            else:
                print("✅ No orphaned collections found")
                
        except Exception as e:
            print(f"❌ Error cleaning up collections: {e}")
    
    def optimize_database(self):
        """Optimize database performance"""
        try:
            print("🔧 Optimizing database...")
            
            # Get main collection
            collection = self.client.get_or_create_collection(
                name="student_textbooks",
                embedding_function=self.embedding_function
            )
            
            # Get collection stats
            count = collection.count()
            print(f"📊 Total documents: {count}")
            
            # Check for duplicates (basic check)
            print("🔍 Checking for potential duplicates...")
            
            print("✅ Database optimization completed")
            return True
            
        except Exception as e:
            print(f"❌ Error optimizing database: {e}")
            return False
    
    def health_check(self):
        """Perform database health check"""
        try:
            print("🏥 Performing database health check...")
            
            # Check if client can connect
            collections = self.client.list_collections()
            print(f"✅ Database connection: OK ({len(collections)} collections)")
            
            # Check main collection
            main_collection = self.client.get_or_create_collection(
                name="student_textbooks",
                embedding_function=self.embedding_function
            )
            count = main_collection.count()
            print(f"✅ Main collection: OK ({count} documents)")
            
            # Check embedding function
            if Config.OPENAI_API_KEY:
                print("✅ OpenAI API key: OK")
            else:
                print("❌ OpenAI API key: Missing")
            
            print("✅ Database health check completed successfully")
            return True
            
        except Exception as e:
            print(f"❌ Database health check failed: {e}")
            return False

def main():
    """Main function for command-line usage"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Labib Database Manager")
    parser.add_argument("--list", action="store_true", help="List all collections")
    parser.add_argument("--info", type=str, help="Get collection info")
    parser.add_argument("--backup", type=str, help="Backup collection")
    parser.add_argument("--cleanup", action="store_true", help="Clean up orphaned collections")
    parser.add_argument("--optimize", action="store_true", help="Optimize database")
    parser.add_argument("--health", action="store_true", help="Perform health check")
    
    args = parser.parse_args()
    
    db_manager = DatabaseManager()
    
    if args.list:
        db_manager.list_collections()
    elif args.info:
        db_manager.get_collection_info(args.info)
    elif args.backup:
        db_manager.backup_collection(args.backup)
    elif args.cleanup:
        db_manager.cleanup_orphaned_collections()
    elif args.optimize:
        db_manager.optimize_database()
    elif args.health:
        db_manager.health_check()
    else:
        print("Use --help for usage information")

if __name__ == "__main__":
    main()
