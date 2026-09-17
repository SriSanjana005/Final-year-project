import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

class TrainingConfig:
    # 1. Reproducibility
    RANDOM_SEED: int = 42

    # 2. Sequence Preprocessing
    MAX_SEQUENCE_LENGTH: int = 20

    # 3. Target Definition Thresholds (Next Performance Tier)
    PERFORMANCE_LOW_THRESHOLD: float = 50.0
    PERFORMANCE_MEDIUM_THRESHOLD: float = 80.0
    TARGET_CLASSES = {0: "LOW", 1: "MEDIUM", 2: "HIGH"}

    # 4. Data Split Configuration
    TRAIN_RATIO: float = 0.70
    VALIDATION_RATIO: float = 0.15
    TEST_RATIO: float = 0.15

    # 5. PyTorch Transformer Architecture
    D_MODEL: int = 64
    NHEAD: int = 4
    NUM_LAYERS: int = 2
    DIM_FEEDFORWARD: int = 128
    DROPOUT: float = 0.1
    NUM_CLASSES: int = 3

    # 6. Transformer Training Hyperparameters
    BATCH_SIZE: int = 8
    LEARNING_RATE: float = 1e-3
    EPOCHS: int = 20
    WEIGHT_DECAY: float = 1e-4
    EARLY_STOPPING_PATIENCE: int = 5

    # 7. Stable-Baselines3 PPO Hyperparameters
    PPO_LEARNING_RATE: float = 3e-4
    PPO_N_STEPS: int = 2048
    PPO_BATCH_SIZE: int = 64
    PPO_GAMMA: float = 0.99
    PPO_GAE_LAMBDA: float = 0.95
    PPO_CLIP_RANGE: float = 0.2
    PPO_ENT_COEF: float = 0.01
    PPO_SEED: int = 42
    PPO_TOTAL_TIMESTEPS: int = 10000

    # 8. Directories & Artifact Paths
    PROCESSED_DATA_DIR = os.path.join(PROJECT_ROOT, "ml", "data", "processed")
    TRANSFORMER_MODEL_DIR = os.path.join(PROJECT_ROOT, "ml", "models", "transformer")
    PPO_MODEL_DIR = os.path.join(PROJECT_ROOT, "ml", "models", "ppo")
    RESULTS_DIR = os.path.join(PROJECT_ROOT, "ml", "results")
    DOCS_RESULTS_DIR = os.path.join(PROJECT_ROOT, "docs", "results")

config = TrainingConfig()
