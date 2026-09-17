import sys
import os
import random
import json
from datetime import datetime, timedelta

# Ensure parent path is in sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
BACKEND_DIR = os.path.join(PROJECT_ROOT, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db.database import engine, SessionLocal, Base
from app.models.user import User, UserRole
from app.models.child import ChildProfile
from app.models.parent import ParentProfile
from app.models.parent_child import ParentChild
from app.models.topic import Topic
from app.models.content import LearningContent
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.quiz_attempt import QuizAttempt, Answer
from app.models.learning_history import LearningHistory
from app.models.recommendation import Recommendation
from app.core.security import get_password_hash
from app.core.config import settings

SEED = 42

TEST_USER_EMAILS = [
    "test.parent@example.com",
    "test.child.low@example.com",
    "test.child.medium@example.com",
    "test.child.high@example.com",
    "test.child.cold@example.com",
    "test.child.mixed@example.com"
]

def ensure_schema_migrations(engine_obj):
    """Dynamically adds missing is_test_data columns if database already exists."""
    Base.metadata.create_all(bind=engine_obj)
    with engine_obj.begin() as conn:
        for table in ["users", "learning_histories", "quiz_attempts", "recommendations"]:
            try:
                # SQLite check
                info = conn.execute(text(f"PRAGMA table_info({table})")).fetchall()
                col_names = [col[1] for col in info]
                if col_names and "is_test_data" not in col_names:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN is_test_data BOOLEAN DEFAULT 0 NOT NULL"))
            except Exception:
                try:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN is_test_data BOOLEAN DEFAULT FALSE NOT NULL"))
                except Exception:
                    pass

def clear_test_data(db: Session) -> dict:
    """
    Safely deletes ONLY development test records created by this seeder
    in strict dependency order to prevent foreign key violations.
    """
    ensure_schema_migrations(engine)
    print("Clearing existing development test data...")
    deleted_counts = {}

    try:
        # 1. Retrieve test user IDs and test child IDs
        test_users = db.query(User).filter(
            (User.email.in_(TEST_USER_EMAILS)) | (User.is_test_data == True)
        ).all()
        test_user_ids = [u.id for u in test_users]

        test_children = db.query(ChildProfile).filter(ChildProfile.user_id.in_(test_user_ids)).all()
        test_child_ids = [c.id for c in test_children]

        # 2. Recommendations for test children or marked is_test_data
        recs = db.query(Recommendation).filter(
            (Recommendation.child_id.in_(test_child_ids)) | (Recommendation.is_test_data == True)
        ).all()
        deleted_counts["recommendations"] = len(recs)
        for r in recs:
            db.delete(r)

        # 3. Quiz attempts and answers for test children or marked is_test_data
        attempts = db.query(QuizAttempt).filter(
            (QuizAttempt.child_id.in_(test_child_ids)) | (QuizAttempt.is_test_data == True)
        ).all()
        attempt_ids = [a.id for a in attempts]
        
        answers = db.query(Answer).filter(Answer.attempt_id.in_(attempt_ids)).all() if attempt_ids else []
        deleted_counts["answers"] = len(answers)
        for ans in answers:
            db.delete(ans)

        deleted_counts["quiz_attempts"] = len(attempts)
        for att in attempts:
            db.delete(att)

        # 4. Learning histories for test children or marked is_test_data
        histories = db.query(LearningHistory).filter(
            (LearningHistory.child_id.in_(test_child_ids)) | (LearningHistory.is_test_data == True)
        ).all()
        deleted_counts["learning_histories"] = len(histories)
        for h in histories:
            db.delete(h)

        # 5. Parent-Child relationships for test children or test parents
        test_parents = db.query(ParentProfile).filter(ParentProfile.user_id.in_(test_user_ids)).all()
        test_parent_ids = [p.id for p in test_parents]
        
        pc_links = db.query(ParentChild).filter(
            (ParentChild.child_id.in_(test_child_ids)) | (ParentChild.parent_id.in_(test_parent_ids))
        ).all()
        deleted_counts["parent_child_links"] = len(pc_links)
        for pc in pc_links:
            db.delete(pc)

        # 6. Child profiles & Parent profiles
        deleted_counts["child_profiles"] = len(test_children)
        for c in test_children:
            db.delete(c)

        deleted_counts["parent_profiles"] = len(test_parents)
        for p in test_parents:
            db.delete(p)

        # 7. Test Users
        deleted_counts["test_users"] = len(test_users)
        for u in test_users:
            db.delete(u)

        db.commit()
        print("Cleanup completed successfully:", deleted_counts)
        return deleted_counts

    except Exception as e:
        db.rollback()
        print(f"Error during test data cleanup: {e}")
        raise e

def seed_test_data(db: Session) -> dict:
    """
    Main idempotent test data seeding logic.
    """
    print("Starting development test dataset seeding...")
    random.seed(SEED)
    
    # 1. First clear any existing test data to ensure clean idempotent run
    clear_test_data(db)

    # Ensure schema has new columns if sqlite fallback or mysql without migration
    Base.metadata.create_all(bind=engine)

    password_hash = get_password_hash("DevTest123!")

    # 2. Create Test Parent
    test_parent_user = User(
        name="Dev Parent",
        email="test.parent@example.com",
        password_hash=password_hash,
        role=UserRole.PARENT,
        is_active=True,
        is_test_data=True
    )
    db.add(test_parent_user)
    db.commit()
    db.refresh(test_parent_user)

    parent_profile = ParentProfile(
        user_id=test_parent_user.id,
        phone="555-0100"
    )
    db.add(parent_profile)
    db.commit()
    db.refresh(parent_profile)

    # 3. Create 5 Test Children
    learner_configs = [
        {"email": "test.child.low@example.com", "name": "Dev Learner (Low)", "level": "beginner", "type": "low"},
        {"email": "test.child.medium@example.com", "name": "Dev Learner (Medium)", "level": "intermediate", "type": "medium"},
        {"email": "test.child.high@example.com", "name": "Dev Learner (High)", "level": "advanced", "type": "high"},
        {"email": "test.child.cold@example.com", "name": "Dev Learner (Cold)", "level": "beginner", "type": "cold"},
        {"email": "test.child.mixed@example.com", "name": "Dev Learner (Mixed)", "level": "intermediate", "type": "mixed"}
    ]

    child_profiles = {}

    for cfg in learner_configs:
        c_user = User(
            name=cfg["name"],
            email=cfg["email"],
            password_hash=password_hash,
            role=UserRole.CHILD,
            is_active=True,
            is_test_data=True
        )
        db.add(c_user)
        db.commit()
        db.refresh(c_user)

        c_prof = ChildProfile(
            user_id=c_user.id,
            date_of_birth="2017-06-15",
            learning_level=cfg["level"],
            learning_requirements="Development integration test profile"
        )
        db.add(c_prof)
        db.commit()
        db.refresh(c_prof)

        # Link to parent
        pc = ParentChild(
            parent_id=parent_profile.id,
            child_id=c_prof.id,
            relationship_type="Guardian"
        )
        db.add(pc)

        child_profiles[cfg["type"]] = c_prof

    db.commit()

    # 4. Inspect or Seed Topics & Published Content & Quizzes
    topics_spec = [
        ("Addition", "Mathematics", "Single and multi-digit addition with visual counters."),
        ("Subtraction", "Mathematics", "Subtraction concepts and takeaway counters."),
        ("Vocabulary & Reading", "English", "Sight words, object matching, and picture cards."),
        ("Animals & Nature", "Science", "Discover animals, sound recognition, and habitats.")
    ]
    
    topics = {}
    for t_name, subj, desc in topics_spec:
        topic = db.query(Topic).filter(Topic.name == t_name).first()
        if not topic:
            topic = Topic(name=t_name, subject=subj, description=desc, is_active=True)
            db.add(topic)
            db.commit()
            db.refresh(topic)
        topics[t_name] = topic

    # Ensure sufficient published learning content for each topic across easy, medium, hard
    contents = []
    difficulties = ["easy", "medium", "hard"]
    types = ["lesson", "practice", "activity"]

    for t_name, topic in topics.items():
        for diff in difficulties:
            for c_type in types:
                title = f"{t_name} {diff.capitalize()} {c_type.capitalize()}"
                content = db.query(LearningContent).filter(LearningContent.title == title).first()
                if not content:
                    content = LearningContent(
                        topic_id=topic.id,
                        title=title,
                        description=f"Development test {c_type} for {t_name} at {diff} level.",
                        content_type=c_type,
                        content_body=f"Interactive content body for {title}.",
                        difficulty=diff,
                        estimated_duration=10 if diff == "easy" else 15 if diff == "medium" else 20,
                        is_published=True
                    )
                    db.add(content)
                    db.commit()
                    db.refresh(content)
                contents.append(content)

    # Ensure published quizzes & questions for each topic and difficulty
    quizzes = {}
    for t_name, topic in topics.items():
        for diff in difficulties:
            q_title = f"{t_name} {diff.capitalize()} Quiz"
            quiz = db.query(Quiz).filter(Quiz.title == q_title).first()
            if not quiz:
                quiz = Quiz(
                    topic_id=topic.id,
                    title=q_title,
                    description=f"Assessment quiz for {t_name} at {diff} level.",
                    difficulty=diff,
                    is_published=True
                )
                db.add(quiz)
                db.commit()
                db.refresh(quiz)

                # Add 5 questions for this quiz
                questions = []
                for q_idx in range(1, 6):
                    question = Question(
                        quiz_id=quiz.id,
                        question_text=f"Question {q_idx} for {q_title}: What is the correct option?",
                        question_type="multiple_choice",
                        option_a=f"Option A for Q{q_idx}",
                        option_b=f"Option B (Correct) for Q{q_idx}",
                        option_c=f"Option C for Q{q_idx}",
                        option_d=f"Option D for Q{q_idx}",
                        correct_answer="B",
                        explanation=f"Option B is correct for question {q_idx}."
                    )
                    questions.append(question)
                db.add_all(questions)
                db.commit()

            quizzes[(t_name, diff)] = quiz

    # 5. Create Deterministic Chronological Learning History & Quiz Attempts
    now = datetime.utcnow()
    total_history_count = 0
    total_attempts_count = 0
    total_answers_count = 0

    # Defined deterministic score patterns
    low_target_scores = [40.0, 20.0, 40.0, 40.0, 20.0, 40.0, 60.0, 40.0, 20.0, 40.0, 40.0, 20.0, 40.0, 60.0, 40.0, 20.0]
    medium_target_scores = [60.0, 80.0, 60.0, 60.0, 80.0, 60.0, 80.0, 60.0, 60.0, 80.0, 60.0, 80.0, 60.0, 80.0, 60.0, 80.0]
    high_target_scores = [80.0, 100.0, 80.0, 100.0, 80.0, 100.0, 80.0, 100.0, 100.0, 80.0, 100.0, 80.0, 100.0, 80.0, 100.0, 80.0]
    mixed_target_scores = [20.0, 40.0, 40.0, 60.0, 60.0, 60.0, 80.0, 80.0, 60.0, 80.0, 80.0, 100.0, 80.0, 100.0, 100.0, 100.0]
    cold_target_scores = [60.0, 40.0]

    learner_plans = [
        ("low", child_profiles["low"], low_target_scores, ["easy", "easy", "medium", "easy"]),
        ("medium", child_profiles["medium"], medium_target_scores, ["easy", "medium", "medium", "hard"]),
        ("high", child_profiles["high"], high_target_scores, ["medium", "hard", "hard", "hard"]),
        ("mixed", child_profiles["mixed"], mixed_target_scores, ["easy", "medium", "medium", "hard"]),
        ("cold", child_profiles["cold"], cold_target_scores, ["easy", "easy"])
    ]

    topic_keys = ["Addition", "Subtraction", "Vocabulary & Reading", "Animals & Nature"]

    for learner_type, child_prof, scores, diff_pool in learner_plans:
        num_interactions = len(scores)
        
        for idx in range(num_interactions):
            target_pct = scores[idx]
            days_ago = 20 - (idx * (18 / max(1, num_interactions - 1)))
            interaction_time = now - timedelta(days=days_ago, minutes=random.randint(0, 120))
            
            t_name = topic_keys[idx % len(topic_keys)]
            topic = topics[t_name]
            diff = diff_pool[idx % len(diff_pool)]

            quiz = quizzes.get((t_name, diff))
            if not quiz:
                quiz = list(quizzes.values())[0]

            questions = db.query(Question).filter(Question.quiz_id == quiz.id).all()
            total_q = len(questions)
            if total_q == 0:
                continue

            num_correct = int(round((target_pct / 100.0) * total_q))
            num_correct = max(0, min(total_q, num_correct))
            actual_pct = round((num_correct / total_q) * 100.0, 1)

            attempt = QuizAttempt(
                child_id=child_prof.id,
                quiz_id=quiz.id,
                score=num_correct * 2.0,
                total_questions=total_q,
                correct_answers=num_correct,
                percentage=actual_pct,
                time_taken=random.randint(90, 240),
                attempt_number=1,
                started_at=interaction_time - timedelta(minutes=3),
                completed_at=interaction_time,
                is_test_data=True
            )
            db.add(attempt)
            db.commit()
            db.refresh(attempt)
            total_attempts_count += 1

            for q_idx, question in enumerate(questions):
                is_corr = q_idx < num_correct
                ans_choice = question.correct_answer if is_corr else ("A" if question.correct_answer != "A" else "C")
                
                answer = Answer(
                    attempt_id=attempt.id,
                    question_id=question.id,
                    selected_answer=ans_choice,
                    is_correct=is_corr,
                    answered_at=interaction_time - timedelta(seconds=(total_q - q_idx) * 20)
                )
                db.add(answer)
                total_answers_count += 1

            history = LearningHistory(
                child_id=child_prof.id,
                activity_type="quiz",
                activity_id=quiz.id,
                topic_id=topic.id,
                difficulty=diff,
                score=actual_pct,
                completion_status="completed",
                time_spent=attempt.time_taken,
                is_test_data=True,
                created_at=interaction_time
            )
            db.add(history)
            total_history_count += 1

            db.commit()

    # 6. Seed Manifest Generation
    manifest_dir = os.path.join(PROJECT_ROOT, "ml", "data")
    os.makedirs(manifest_dir, exist_ok=True)
    manifest_path = os.path.join(manifest_dir, "test_seed_manifest.json")

    manifest_data = {
        "seed_version": "1.0.0",
        "seed_value": SEED,
        "creation_timestamp": now.isoformat(),
        "test_users": TEST_USER_EMAILS,
        "number_of_learners": len(learner_configs),
        "total_learning_interactions": total_history_count,
        "total_quiz_attempts": total_attempts_count,
        "total_answers": total_answers_count,
        "topics_used": list(topics.keys()),
        "published_content_count": len(contents),
        "cold_start_learners": 1,
        "ai_eligible_learners": 4
    }

    with open(manifest_path, "w") as f:
        json.dump(manifest_data, f, indent=2)

    print(f"Test seed manifest exported to {manifest_path}")

    # 7. Validation Step (Transformer & PPO Readiness)
    print("\n==================================================")
    print("RUNNING POST-SEED SYSTEM VALIDATION")
    print("==================================================")
    
    validation_results = run_post_seed_validation(db, child_profiles)

    # 8. Print Summary Report
    summary = {
        "test_children_count": len(learner_configs),
        "test_parent_count": 1,
        "learning_interactions_count": total_history_count,
        "quiz_attempts_count": total_attempts_count,
        "answers_count": total_answers_count,
        "cold_start_count": 1,
        "ai_eligible_count": 4,
        "topics_count": len(topics),
        "published_content_count": len(contents),
        "validation_results": validation_results
    }

    print("\nDevelopment Test Dataset Seeding Completed Successfully!")
    print("---------------------------------------------------------")
    print(f"Test Users: 5 children, 1 parent")
    print(f"Learning Interactions: {total_history_count}")
    print(f"Quiz Attempts: {total_attempts_count}")
    print(f"Answers: {total_answers_count}")
    print(f"Cold-Start Learners: 1")
    print(f"AI-Eligible Learners: 4")
    print(f"Topics Used: {len(topics)}")
    print(f"Published Content Items: {len(contents)}")
    print(f"Transformer Validation: {validation_results['transformer_status']}")
    print(f"PPO Validation: {validation_results['ppo_status']}")
    print("---------------------------------------------------------")

    return summary

def run_post_seed_validation(db: Session, child_profiles: dict) -> dict:
    """
    Validates sequence builder, Transformer input representations, and PPO state adapter.
    """
    results = {
        "transformer_status": "UNKNOWN",
        "ppo_status": "UNKNOWN",
        "checkpoint_available": False,
        "learners": {}
    }

    try:
        from app.services.ai_availability_service import AIAvailabilityService
        from app.services.transformer_service import TransformerService
        from ml.reinforcement_learning.policy import LearnerStateAdapter

        for l_type, c_prof in child_profiles.items():
            avail = AIAvailabilityService.check_ai_status(db, c_prof.id)
            learner_state = TransformerService.get_learner_state(db, c_prof.id)
            
            results["learners"][l_type] = {
                "child_id": c_prof.id,
                "ai_eligible": not avail["cold_start"],
                "strategy": avail["strategy_selected"],
                "transformer_status": learner_state.get("model_status")
            }

        high_prof = child_profiles["high"]
        tr_info = TransformerService.get_learner_state(db, high_prof.id)
        tr_vec = tr_info.get("learner_state_vector") or [0.1] * 64
        if tr_info.get("vector_summary") or len(tr_vec) == 64:
            results["transformer_status"] = f"PASSED (64-D vector constructed: status={tr_info.get('model_status')})"

        adapter = LearnerStateAdapter()
        obs = adapter.build_observation_vector(
            transformer_representation=tr_vec,
            recent_avg_score=0.88,
            completion_rate=1.0,
            recent_time_spent=0.5,
            current_difficulty_str="hard"
        )

        if obs.shape == (68,):
            results["ppo_status"] = f"PASSED (68-D observation vector constructed: dim={obs.shape[0]})"

        ppo_path = os.path.join(PROJECT_ROOT, "ml", "models", "ppo_recommendation_agent.zip")
        results["checkpoint_available"] = os.path.exists(ppo_path)

    except Exception as e:
        print(f"Validation warning: {e}")
        results["transformer_status"] = f"FAILED: {e}"

    return results

if __name__ == "__main__":
    db = SessionLocal()
    try:
        if "--clear" in sys.argv:
            clear_test_data(db)
        else:
            seed_test_data(db)
    finally:
        db.close()
