import sys
import os

# Ensure ML package in project root is importable
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)



from sqlalchemy.orm import Session
from typing import Dict, Any
from app.models.child import ChildProfile
from ml.data.sequence_builder import SequenceBuilder
from ml.data.feature_encoder import FeatureEncoder
from ml.transformer.inference import LearnerStateExtractor

# Global singleton instance of Transformer extractor
_extractor_instance = None

def get_extractor():
    global _extractor_instance
    if _extractor_instance is None:
        _extractor_instance = LearnerStateExtractor()
    return _extractor_instance

class TransformerService:
    @staticmethod
    def get_learner_state(db: Session, child_id: int) -> Dict[str, Any]:
        """
        Retrieves recent learning sequence, encodes features, and executes Transformer forward pass
        to compute the 64-dimensional learner state representation.
        Handles cold-start safely.
        """
        # 1. Verify child exists
        child = db.query(ChildProfile).filter(ChildProfile.id == child_id).first()
        if not child:
            return {
                "child_id": child_id,
                "model_status": "error",
                "message": f"Child learner #{child_id} not found."
            }

        # 2. Build feature sequence
        seq_builder = SequenceBuilder(max_seq_len=20)
        raw_sequence, is_cold_start = seq_builder.build_sequence_from_db(db, child_id)

        # 3. Handle COLD-START safely if no history exists
        if is_cold_start or not raw_sequence:
            return {
                "child_id": child_id,
                "sequence_length": 0,
                "representation_dimension": 64,
                "model_status": "cold_start",
                "message": "Learner has insufficient interaction history. Cold-start baseline active."
            }

        # 4. Encode sequence features into PyTorch tensors
        encoder = FeatureEncoder(max_seq_len=20)
        batch_tensors = encoder.encode_sequence(raw_sequence)

        # 5. Execute Transformer forward pass inference
        extractor = get_extractor()
        result = extractor.extract_representation(batch_tensors)
        vec = result["learner_representation"]

        return {
            "child_id": child_id,
            "sequence_length": len(raw_sequence),
            "representation_dimension": 64,
            "model_status": "available",
            "predicted_performance_tier": result["predicted_performance_tier"],
            "vector_summary": {
                "mean": round(sum(vec) / len(vec), 4),
                "min": round(min(vec), 4),
                "max": round(max(vec), 4)
            }
        }
