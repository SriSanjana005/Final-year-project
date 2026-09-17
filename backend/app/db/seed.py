import sys
import os

# Add parent directory to path to allow importing app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

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
from app.services.recommendation_service import RecommendationService

def run_seed():
    print("Re-creating all database tables cleanly...")
    try:
        Base.metadata.drop_all(bind=engine)
    except Exception as e:
        print(f"Drop tables warning: {e}")
    Base.metadata.create_all(bind=engine)


    db = SessionLocal()
    try:
        print("Seeding database data...")

        # 1. Seed Users if not present
        demo_password_hash = get_password_hash("Password123!")

        admin_user = db.query(User).filter(User.email == "admin@example.com").first()
        if not admin_user:
            admin_user = User(
                name="System Admin",
                email="admin@example.com",
                password_hash=demo_password_hash,
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin_user)

        parent_user = db.query(User).filter(User.email == "parent@example.com").first()
        if not parent_user:
            parent_user = User(
                name="Priya Smith (Parent)",
                email="parent@example.com",
                password_hash=demo_password_hash,
                role=UserRole.PARENT,
                is_active=True
            )
            db.add(parent_user)

        child_user = db.query(User).filter(User.email == "child@example.com").first()
        if not child_user:
            child_user = User(
                name="Aishwarya Smith (Child)",
                email="child@example.com",
                password_hash=demo_password_hash,
                role=UserRole.CHILD,
                is_active=True
            )
            db.add(child_user)

        db.commit()
        db.refresh(admin_user)
        db.refresh(parent_user)
        db.refresh(child_user)

        # 2. Profiles
        parent_prof = db.query(ParentProfile).filter(ParentProfile.user_id == parent_user.id).first()
        if not parent_prof:
            parent_prof = ParentProfile(user_id=parent_user.id, phone="555-0199")
            db.add(parent_prof)
            db.commit()
            db.refresh(parent_prof)

        child_prof = db.query(ChildProfile).filter(ChildProfile.user_id == child_user.id).first()
        if not child_prof:
            child_prof = ChildProfile(
                user_id=child_user.id,
                date_of_birth="2018-05-12",
                learning_level="beginner",
                learning_requirements="Visual counters and auditory cues for tactile learning"
            )
            db.add(child_prof)
            db.commit()
            db.refresh(child_prof)

        # 3. ParentChild Mapping
        link = db.query(ParentChild).filter(
            ParentChild.parent_id == parent_prof.id,
            ParentChild.child_id == child_prof.id
        ).first()
        if not link:
            link = ParentChild(
                parent_id=parent_prof.id,
                child_id=child_prof.id,
                relationship_type="Mother"
            )
            db.add(link)
            db.commit()

        # 4. Topics
        topics_data = [
            ("Addition", "Mathematics", "Learn single and double digit addition with visual blocks."),
            ("Subtraction", "Mathematics", "Basic subtraction concepts and visual takeaway counters."),
            ("Vocabulary & Reading", "English", "Sight words, object matching, and picture cards."),
            ("Animals & Nature", "Science", "Discover animals, their sounds, and natural habitats.")
        ]
        created_topics = {}
        for name, subject, desc in topics_data:
            topic = db.query(Topic).filter(Topic.name == name).first()
            if not topic:
                topic = Topic(name=name, subject=subject, description=desc, is_active=True)
                db.add(topic)
                db.commit()
                db.refresh(topic)
            created_topics[name] = topic

        t_addition = created_topics["Addition"]
        t_subtraction = created_topics["Subtraction"]
        t_vocab = created_topics["Vocabulary & Reading"]
        t_animals = created_topics["Animals & Nature"]

        # 5. Educational Content
        contents_data = [
            (t_addition.id, "Introduction to Addition", "Learn how to combine groups of objects using visual counters.", "lesson",
             "Welcome to Addition! Addition means putting groups together. When you have 3 blocks and add 2 more blocks, you get 5 blocks in total.\n🟦 🟦 🟦 + 🟦 🟦 = 🟦 🟦 🟦 🟦 🟦.\nPractice counting out loud!", "easy", 10),
            
            (t_addition.id, "Addition Practice with Visual Blocks", "Interactive exercise combining 2-digit numbers.", "practice",
             "Count the visual groups carefully:\nGroup A has 4 green circles 🟢 🟢 🟢 🟢.\nGroup B has 3 yellow circles 🟡 🟡 🟡.\nHow many circles are there altogether? Answer: 7!", "medium", 15),

            (t_addition.id, "Advanced Addition Challenge", "Challenging multi-group block addition problems.", "activity",
             "Try adding three groups together:\nGroup 1: 5 blocks 🟦 🟦 🟦 🟦 🟦\nGroup 2: 4 blocks 🟩 🟩 🟩 🟩\nGroup 3: 2 blocks 🟨 🟨\nTotal = 11 blocks!", "hard", 20),

            (t_vocab.id, "Sight Words & Object Matching", "Match words with tactile visual pictures.", "lesson",
             "Look at the word: CAT 🐱\nLook at the word: DOG 🐶\nLook at the word: SUN ☀️\nPoint to each word as you say it out loud.", "easy", 8),

            (t_animals.id, "Animal Sounds & Sight Words", "Discover domestic animals and learn their names.", "activity",
             "Learn animal names and sounds:\n1. Dog 🐶 says 'Woof!'\n2. Cat 🐱 says 'Meow!'\n3. Cow 🐮 says 'Moo!'\nRepeat after each animal sound!", "easy", 12)
        ]

        created_contents = []
        for topic_id, title, desc, c_type, body, diff, duration in contents_data:
            content = db.query(LearningContent).filter(LearningContent.title == title).first()
            if not content:
                content = LearningContent(
                    topic_id=topic_id,
                    title=title,
                    description=desc,
                    content_type=c_type,
                    content_body=body,
                    difficulty=diff,
                    estimated_duration=duration,
                    is_published=True,
                    created_by=admin_user.id
                )

                db.add(content)
                db.commit()
                db.refresh(content)
            created_contents.append(content)

        # 6. Quizzes
        q_math = db.query(Quiz).filter(Quiz.title == "Basic Addition Quiz").first()
        if not q_math:
            q_math = Quiz(
                topic_id=t_addition.id,
                title="Basic Addition Quiz",
                description="Practice single-digit visual addition problems.",
                difficulty="easy",
                is_published=True,
                created_by=admin_user.id
            )
            db.add(q_math)
            db.commit()
            db.refresh(q_math)

        q_english = db.query(Quiz).filter(Quiz.title == "Vocabulary & Sight Words Quiz").first()
        if not q_english:
            q_english = Quiz(
                topic_id=t_vocab.id,
                title="Vocabulary & Sight Words Quiz",
                description="Match sight words and animal pictures.",
                difficulty="easy",
                is_published=True,
                created_by=admin_user.id
            )
            db.add(q_english)
            db.commit()
            db.refresh(q_english)

        # 7. Questions
        if db.query(Question).filter(Question.quiz_id == q_math.id).count() == 0:
            math_questions = [
                Question(quiz_id=q_math.id, question_text="What is 2 + 2?", question_type="multiple_choice", option_a="3", option_b="4", option_c="5", option_d="6", correct_answer="B", explanation="2 blocks + 2 blocks = 4 blocks."),
                Question(quiz_id=q_math.id, question_text="What is 5 + 3?", question_type="multiple_choice", option_a="6", option_b="7", option_c="8", option_d="9", correct_answer="C", explanation="Count forward 3 steps from 5: 6, 7, 8."),
                Question(quiz_id=q_math.id, question_text="If you have 4 blocks and add 1 block, how many do you have?", question_type="multiple_choice", option_a="5", option_b="4", option_c="6", option_d="3", correct_answer="A", explanation="4 + 1 = 5."),
                Question(quiz_id=q_math.id, question_text="What is 6 + 2?", question_type="multiple_choice", option_a="7", option_b="9", option_c="8", option_d="10", correct_answer="C", explanation="6 + 2 = 8."),
                Question(quiz_id=q_math.id, question_text="What is 3 + 3?", question_type="multiple_choice", option_a="5", option_b="6", option_c="7", option_d="4", correct_answer="B", explanation="3 + 3 = 6.")
            ]
            db.add_all(math_questions)
            db.commit()

        if db.query(Question).filter(Question.quiz_id == q_english.id).count() == 0:
            english_questions = [
                Question(quiz_id=q_english.id, question_text="Which word matches the animal 🐱?", question_type="multiple_choice", option_a="Dog", option_b="Cat", option_c="Fish", option_d="Bird", correct_answer="B", explanation="🐱 is a Cat."),
                Question(quiz_id=q_english.id, question_text="Which word matches the animal 🐶?", question_type="multiple_choice", option_a="Cat", option_b="Rabbit", option_c="Dog", option_d="Bear", correct_answer="C", explanation="🐶 is a Dog."),
                Question(quiz_id=q_english.id, question_text="Which word names a bright yellow star in the sky ☀️?", question_type="multiple_choice", option_a="Moon", option_b="Star", option_c="Sun", option_d="Cloud", correct_answer="C", explanation="☀️ is the Sun."),
                Question(quiz_id=q_english.id, question_text="Which word names something you read 📖?", question_type="multiple_choice", option_a="Book", option_b="Pen", option_c="Desk", option_d="Chair", correct_answer="A", explanation="📖 is a Book."),
                Question(quiz_id=q_english.id, question_text="Which word is an apple 🍎?", question_type="multiple_choice", option_a="Fruit", option_b="Toy", option_c="Car", option_d="Shoe", correct_answer="A", explanation="🍎 Apple is a Fruit.")
            ]
            db.add_all(english_questions)
            db.commit()

        # 8. Sample Quiz Attempt & Learning History
        if db.query(QuizAttempt).filter(QuizAttempt.child_id == child_prof.id).count() == 0:
            attempt = QuizAttempt(
                child_id=child_prof.id,
                quiz_id=q_math.id,
                score=4.0,
                total_questions=5,
                correct_answers=4,
                percentage=80.0,
                time_taken=120
            )
            db.add(attempt)
            db.commit()
            db.refresh(attempt)


            # Record learning history
            history = LearningHistory(
                child_id=child_prof.id,
                activity_type="quiz",
                activity_id=q_math.id,
                topic_id=t_addition.id,
                difficulty="easy",
                score=80.0,
                completion_status="completed",
                time_spent=120
            )
            db.add(history)
            db.commit()

        # 9. Generate Rule-Based Baseline Recommendation
        if db.query(Recommendation).filter(Recommendation.child_id == child_prof.id).count() == 0:
            RecommendationService.generate_recommendation(db, child_prof.id)

        print("Database seeded successfully with users, profiles, topics, content, quizzes, questions, history, and baseline recommendations!")

    except Exception as e:
        print(f"Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run_seed()
