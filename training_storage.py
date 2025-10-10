#!/usr/bin/env python
"""
Persistent Training Data Storage
Stores all training data in files instead of memory
"""
import os
import json
import uuid
from datetime import datetime
from typing import List, Dict, Any

class TrainingStorage:
    def __init__(self, storage_dir: str = "training_data"):
        self.storage_dir = storage_dir
        self.documents_file = os.path.join(storage_dir, "documents.json")
        self.training_samples_file = os.path.join(storage_dir, "training_samples.json")
        self.training_stats_file = os.path.join(storage_dir, "training_stats.json")
        
        # Create storage directory if it doesn't exist
        os.makedirs(storage_dir, exist_ok=True)
        
        # Initialize files if they don't exist
        self._init_files()
    
    def _init_files(self):
        """Initialize storage files if they don't exist"""
        if not os.path.exists(self.documents_file):
            self._save_json(self.documents_file, {})
        
        if not os.path.exists(self.training_samples_file):
            self._save_json(self.training_samples_file, [])
        
        if not os.path.exists(self.training_stats_file):
            self._save_json(self.training_stats_file, {
                "total_samples": 0,
                "last_training": None,
                "document_count": 0
            })
    
    def _load_json(self, filepath: str) -> Any:
        """Load JSON data from file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            return {} if 'documents' in filepath else []
    
    def _save_json(self, filepath: str, data: Any):
        """Save JSON data to file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def save_document(self, doc_id: str, document_data: Dict[str, Any]) -> bool:
        """Save document data to persistent storage"""
        try:
            documents = self._load_json(self.documents_file)
            documents[doc_id] = {
                **document_data,
                "saved_at": datetime.now().isoformat(),
                "doc_id": doc_id
            }
            self._save_json(self.documents_file, documents)
            
            # Update stats
            stats = self._load_json(self.training_stats_file)
            stats["document_count"] = len(documents)
            self._save_json(self.training_stats_file, stats)
            
            print(f"Document {doc_id} saved to persistent storage")
            return True
        except Exception as e:
            print(f"Error saving document {doc_id}: {e}")
            return False
    
    def load_document(self, doc_id: str) -> Dict[str, Any]:
        """Load document data from persistent storage"""
        try:
            documents = self._load_json(self.documents_file)
            return documents.get(doc_id, {})
        except Exception as e:
            print(f"Error loading document {doc_id}: {e}")
            return {}
    
    def get_all_documents(self) -> Dict[str, Dict[str, Any]]:
        """Get all stored documents"""
        return self._load_json(self.documents_file)
    
    def add_training_samples(self, samples: List[Dict[str, Any]]) -> bool:
        """Add training samples to persistent storage"""
        try:
            existing_samples = self._load_json(self.training_samples_file)
            existing_samples.extend(samples)
            self._save_json(self.training_samples_file, existing_samples)
            
            # Update stats
            stats = self._load_json(self.training_stats_file)
            stats["total_samples"] = len(existing_samples)
            stats["last_training"] = datetime.now().isoformat()
            self._save_json(self.training_stats_file, stats)
            
            print(f"Added {len(samples)} training samples. Total: {len(existing_samples)}")
            return True
        except Exception as e:
            print(f"Error adding training samples: {e}")
            return False
    
    def get_training_samples(self) -> List[Dict[str, Any]]:
        """Get all training samples"""
        return self._load_json(self.training_samples_file)
    
    def get_training_stats(self) -> Dict[str, Any]:
        """Get training statistics"""
        stats = self._load_json(self.training_stats_file)
        documents = self._load_json(self.documents_file)
        samples = self._load_json(self.training_samples_file)
        
        return {
            **stats,
            "documents_in_storage": len(documents),
            "document_ids": list(documents.keys()),
            "training_samples": len(samples)
        }
    
    def clear_all_data(self):
        """Clear all stored data"""
        try:
            self._save_json(self.documents_file, {})
            self._save_json(self.training_samples_file, [])
            self._save_json(self.training_stats_file, {
                "total_samples": 0,
                "last_training": None,
                "document_count": 0
            })
            print("All training data cleared")
        except Exception as e:
            print(f"Error clearing data: {e}")

# Global instance
training_storage = TrainingStorage()

