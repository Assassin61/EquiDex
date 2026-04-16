import firebase_admin
from firebase_admin import credentials, firestore
import json
from datetime import datetime

class FirebaseAdapter:
    def __init__(self, config: dict):
        self.project_id = config["database"].get("project_id", "YOUR_PROJECT_ID")
        
        # Initialize Firebase App
        if not firebase_admin._apps:
            try:
                # If running locally with service account
                cred = credentials.ApplicationDefault()
                firebase_admin.initialize_app(cred, {
                    'projectId': self.project_id,
                })
            except Exception:
                # Fallback or pure GCP environment
                firebase_admin.initialize_app(options={'projectId': self.project_id})
                
        self.db = firestore.client()

    def save(self, collection: str, record: dict):
        """Saves a record to a specified Firestore collection."""
        self.db.collection(collection).add(record)

    def update(self, collection: str, updates: dict, audit_id: str):
        """Updates fields in records matching audit_id."""
        docs = self.db.collection(collection).where("audit_id", "==", audit_id).stream()
        batch = self.db.batch()
        count = 0
        
        for doc in docs:
            batch.update(doc.reference, updates)
            count += 1
            
        if count > 0:
            batch.commit()

    def get_all(self, collection: str, audit_id: str = None) -> list:
        """Fetches all records from a Firestore collection."""
        col_ref = self.db.collection(collection)
        if audit_id:
            docs = col_ref.where("audit_id", "==", audit_id).stream()
        else:
            docs = col_ref.stream()
            
        return [doc.to_dict() for doc in docs]

    def get_latest_audit_id(self) -> str:
        """Returns the most recent audit_id from audit_logs collection."""
        docs = self.db.collection("audit_logs").order_by(
            "timestamp", direction=firestore.Query.DESCENDING
        ).limit(1).stream()
        
        for doc in docs:
            return doc.to_dict().get("audit_id")
            
        return None
