import os
import sys
import json

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from ml.config.training_config import config

def generate_experiment_plots():
    """
    Generates training and evaluation plots from actual recorded metrics JSON files.
    Exports figure images to docs/results/ and ml/results/.
    """
    t_meta_path = os.path.join(config.TRANSFORMER_MODEL_DIR, "metadata.json")
    t_eval_path = os.path.join(config.TRANSFORMER_MODEL_DIR, "evaluation_results.json")
    ppo_eval_path = os.path.join(config.PPO_MODEL_DIR, "ppo_evaluation_results.json")

    os.makedirs(config.RESULTS_DIR, exist_ok=True)
    os.makedirs(config.DOCS_RESULTS_DIR, exist_ok=True)

    try:
        import matplotlib
        matplotlib.use("Agg") # Non-gui backend
        import matplotlib.pyplot as plt
    except ImportError:
        print("Notice: matplotlib not installed. Skipping PNG image rendering.")
        return False

    # 1. Transformer Loss & Accuracy Curves
    if os.path.exists(t_meta_path):
        with open(t_meta_path, "r", encoding="utf-8") as f:
            t_meta = json.load(f)

        history = t_meta.get("history", {})
        epochs = list(range(1, len(history.get("train_loss", [])) + 1))

        if epochs:
            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.5))

            # Loss Plot
            ax1.plot(epochs, history.get("train_loss", []), label="Train Loss", marker="o", color="#2563EB")
            ax1.plot(epochs, history.get("val_loss", []), label="Val Loss", marker="s", color="#DC2626")
            ax1.set_title("Transformer Encoder Loss vs Epoch")
            ax1.set_xlabel("Epoch")
            ax1.set_ylabel("CrossEntropy Loss")
            ax1.grid(True, linestyle="--", alpha=0.5)
            ax1.legend()

            # Accuracy Plot
            ax2.plot(epochs, history.get("train_acc", []), label="Train Acc", marker="o", color="#14B8A6")
            ax2.plot(epochs, history.get("val_acc", []), label="Val Acc", marker="s", color="#7C3AED")
            ax2.set_title("Transformer Accuracy vs Epoch")
            ax2.set_xlabel("Epoch")
            ax2.set_ylabel("Accuracy")
            ax2.set_ylim(0, 1.05)
            ax2.grid(True, linestyle="--", alpha=0.5)
            ax2.legend()

            plt.tight_layout()
            plt.savefig(os.path.join(config.RESULTS_DIR, "transformer_learning_curves.png"), dpi=150)
            plt.savefig(os.path.join(config.DOCS_RESULTS_DIR, "transformer_learning_curves.png"), dpi=150)
            plt.close()
            print("Generated transformer_learning_curves.png")

    # 2. Confusion Matrix Heatmap
    if os.path.exists(t_eval_path):
        with open(t_eval_path, "r", encoding="utf-8") as f:
            t_eval = json.load(f)

        cm = t_eval.get("metrics", {}).get("confusion_matrix", [])
        if cm:
            fig, ax = plt.subplots(figsize=(6, 5))
            cax = ax.matshow(cm, cmap="Blues")
            fig.colorbar(cax)

            labels = ["LOW (<50%)", "MEDIUM (50-80%)", "HIGH (>=80%)"]
            ax.set_xticks(range(3))
            ax.set_yticks(range(3))
            ax.set_xticklabels(labels, rotation=15)
            ax.set_yticklabels(labels)
            ax.set_xlabel("Predicted Performance Tier")
            ax.set_ylabel("Actual Performance Tier")
            ax.set_title("Transformer Test Confusion Matrix")

            for i in range(len(cm)):
                for j in range(len(cm[i])):
                    ax.text(j, i, str(cm[i][j]), ha="center", va="center", color="black" if cm[i][j] < (max(map(max, cm))/2) else "white", fontweight="bold")

            plt.tight_layout()
            plt.savefig(os.path.join(config.RESULTS_DIR, "transformer_confusion_matrix.png"), dpi=150)
            plt.savefig(os.path.join(config.DOCS_RESULTS_DIR, "transformer_confusion_matrix.png"), dpi=150)
            plt.close()
            print("Generated transformer_confusion_matrix.png")

    # 3. PPO Action Distribution
    if os.path.exists(ppo_eval_path):
        with open(ppo_eval_path, "r", encoding="utf-8") as f:
            ppo_eval = json.load(f)

        act_dist = ppo_eval.get("action_distribution", {})
        if act_dist:
            fig, ax = plt.subplots(figsize=(8, 4.5))
            actions = list(act_dist.keys())
            frequencies = [act_dist[k] * 100.0 for k in actions]

            bars = ax.bar(actions, frequencies, color="#2563EB", edgecolor="#1D4ED8")
            ax.set_ylabel("Selection Percentage (%)")
            ax.set_title("PPO Agent Discrete Action Selection Distribution")
            ax.set_ylim(0, 100)
            ax.grid(axis="y", linestyle="--", alpha=0.5)

            for bar in bars:
                height = bar.get_height()
                ax.annotate(f"{height:.1f}%",
                            xy=(bar.get_x() + bar.get_width() / 2, height),
                            xytext=(0, 3),
                            textcoords="offset points",
                            ha="center", va="bottom", fontsize=9, fontweight="bold")

            plt.xticks(rotation=15)
            plt.tight_layout()
            plt.savefig(os.path.join(config.RESULTS_DIR, "ppo_action_distribution.png"), dpi=150)
            plt.savefig(os.path.join(config.DOCS_RESULTS_DIR, "ppo_action_distribution.png"), dpi=150)
            plt.close()
            print("Generated ppo_action_distribution.png")

    return True

if __name__ == "__main__":
    generate_experiment_plots()
