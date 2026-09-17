from dataclasses import dataclass

@dataclass
class TransformerConfig:
    embedding_dim: int = 64
    num_layers: int = 2
    num_heads: int = 4
    feedforward_dim: int = 128
    dropout: float = 0.1
    max_seq_length: int = 20
    
    # Categorical Vocabulary Sizes
    num_topics: int = 100
    num_difficulties: int = 10
    num_activity_types: int = 10
    num_completion_statuses: int = 10

    # Prediction Head
    num_classes: int = 3 # low, medium, high performance tier prediction
