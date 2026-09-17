from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
from app.db.database import get_db
from app.models.user import User
from app.models.child import ChildProfile
from app.models.topic import Topic
from app.models.quiz import Quiz
from app.models.question import Question
from app.models.quiz_attempt import QuizAttempt, Answer
from app.models.learning_history import LearningHistory
from app.schemas.quiz import (
    QuizCreate, QuizUpdate, QuizResponse, QuizPublishToggle,
    QuestionCreate, QuestionUpdate, QuestionResponse,
    ChildQuizAttemptResponse, ChildQuestionResponse,
    QuizSubmissionRequest, QuizSubmissionResponse
)
from app.core.dependencies import get_current_user, require_role

router = APIRouter(prefix="", tags=["Quiz System"])

# --- ADMIN QUIZ ENDPOINTS ---

# GET /api/quizzes (Admin only)
@router.get("/quizzes", response_model=List[QuizResponse])
def get_all_quizzes(db: Session = Depends(get_db), current_user: User = Depends(require_role(["admin"]))):
    quizzes = db.query(Quiz).order_by(Quiz.id.desc()).all()
    res = []
    for q in quizzes:
        q_dict = QuizResponse.model_validate(q)
        q_dict.question_count = db.query(Question).filter(Question.quiz_id == q.id).count()
        res.append(q_dict)
    return res

# GET /api/quizzes/published (Child / Parent / Public)
@router.get("/quizzes/published", response_model=List[QuizResponse])
def get_published_quizzes(db: Session = Depends(get_db)):
    quizzes = db.query(Quiz).join(Topic).filter(
        Quiz.is_published == True,
        Topic.is_active == True
    ).order_by(Quiz.created_at.desc()).all()
    
    res = []
    for q in quizzes:
        q_dict = QuizResponse.model_validate(q)
        q_dict.question_count = db.query(Question).filter(Question.quiz_id == q.id).count()
        res.append(q_dict)
    return res

# POST /api/quizzes (Admin only)
@router.post("/quizzes", response_model=QuizResponse, status_code=status.HTTP_201_CREATED)
def create_quiz(
    quiz_in: QuizCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    topic = db.query(Topic).filter(Topic.id == quiz_in.topic_id).first()
    if not topic:
        raise HTTPException(status_code=404, detail="Selected topic does not exist")

    new_quiz = Quiz(
        topic_id=quiz_in.topic_id,
        title=quiz_in.title,
        description=quiz_in.description,
        difficulty=quiz_in.difficulty,
        is_published=quiz_in.is_published,
        created_by=current_user.id
    )
    db.add(new_quiz)
    db.commit()
    db.refresh(new_quiz)
    
    res = QuizResponse.model_validate(new_quiz)
    res.question_count = 0
    return res

# GET /api/quizzes/{quiz_id}
@router.get("/quizzes/{quiz_id}", response_model=QuizResponse)
def get_quiz_by_id(quiz_id: int, db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    res = QuizResponse.model_validate(quiz)
    res.question_count = db.query(Question).filter(Question.quiz_id == quiz.id).count()
    return res

# PUT /api/quizzes/{quiz_id} (Admin only)
@router.put("/quizzes/{quiz_id}", response_model=QuizResponse)
def update_quiz(
    quiz_id: int,
    quiz_in: QuizUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    if quiz_in.topic_id is not None:
        topic = db.query(Topic).filter(Topic.id == quiz_in.topic_id).first()
        if not topic:
            raise HTTPException(status_code=404, detail="Selected topic does not exist")
        quiz.topic_id = quiz_in.topic_id

    if quiz_in.title is not None:
        quiz.title = quiz_in.title
    if quiz_in.description is not None:
        quiz.description = quiz_in.description
    if quiz_in.difficulty is not None:
        quiz.difficulty = quiz_in.difficulty
    if quiz_in.is_published is not None:
        quiz.is_published = quiz_in.is_published

    db.commit()
    db.refresh(quiz)
    res = QuizResponse.model_validate(quiz)
    res.question_count = db.query(Question).filter(Question.quiz_id == quiz.id).count()
    return res

# PATCH /api/quizzes/{quiz_id}/publish (Admin only)
@router.patch("/quizzes/{quiz_id}/publish", response_model=QuizResponse)
def toggle_quiz_publish(
    quiz_id: int,
    status_in: QuizPublishToggle,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    quiz.is_published = status_in.is_published
    db.commit()
    db.refresh(quiz)
    res = QuizResponse.model_validate(quiz)
    res.question_count = db.query(Question).filter(Question.quiz_id == quiz.id).count()
    return res

# DELETE /api/quizzes/{quiz_id} (Admin only)
@router.delete("/quizzes/{quiz_id}", status_code=status.HTTP_200_OK)
def delete_quiz(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    db.delete(quiz)
    db.commit()
    return {"message": "Quiz deleted successfully"}

# --- ADMIN QUESTION ENDPOINTS ---

# GET /api/quizzes/{quiz_id}/questions (Admin only)
@router.get("/quizzes/{quiz_id}/questions", response_model=List[QuestionResponse])
def get_quiz_questions(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return db.query(Question).filter(Question.quiz_id == quiz_id).all()

# POST /api/quizzes/{quiz_id}/questions (Admin only)
@router.post("/quizzes/{quiz_id}/questions", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
def create_quiz_question(
    quiz_id: int,
    q_in: QuestionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    new_q = Question(
        quiz_id=quiz_id,
        question_text=q_in.question_text,
        question_type=q_in.question_type,
        option_a=q_in.option_a,
        option_b=q_in.option_b,
        option_c=q_in.option_c,
        option_d=q_in.option_d,
        correct_answer=q_in.correct_answer.upper().strip(),
        explanation=q_in.explanation
    )
    db.add(new_q)
    db.commit()
    db.refresh(new_q)
    return new_q

# PUT /api/questions/{question_id} (Admin only)
@router.put("/questions/{question_id}", response_model=QuestionResponse)
def update_question(
    question_id: int,
    q_in: QuestionUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    if q_in.question_text is not None:
        q.question_text = q_in.question_text
    if q_in.question_type is not None:
        q.question_type = q_in.question_type
    if q_in.option_a is not None:
        q.option_a = q_in.option_a
    if q_in.option_b is not None:
        q.option_b = q_in.option_b
    if q_in.option_c is not None:
        q.option_c = q_in.option_c
    if q_in.option_d is not None:
        q.option_d = q_in.option_d
    if q_in.correct_answer is not None:
        q.correct_answer = q_in.correct_answer.upper().strip()
    if q_in.explanation is not None:
        q.explanation = q_in.explanation

    db.commit()
    db.refresh(q)
    return q

# DELETE /api/questions/{question_id} (Admin only)
@router.delete("/questions/{question_id}", status_code=status.HTTP_200_OK)
def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    q = db.query(Question).filter(Question.id == question_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Question not found")

    db.delete(q)
    db.commit()
    return {"message": "Question deleted successfully"}

# --- CHILD QUIZ DELIVERY & SUBMISSION ---

# GET /api/quizzes/{quiz_id}/attempt (Child delivery)
# CRITICAL SECURITY: STRIPS correct_answer AND explanation
@router.get("/quizzes/{quiz_id}/attempt", response_model=ChildQuizAttemptResponse)
def get_quiz_for_attempt(
    quiz_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    quiz = db.query(Quiz).join(Topic).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")

    user_role_val = current_user.role.value if hasattr(current_user.role, "value") else str(current_user.role)
    if user_role_val in ["child", "parent"]:
        if not quiz.is_published or (quiz.topic and not quiz.topic.is_active):
            raise HTTPException(status_code=403, detail="Access denied to unpublished quiz")

    questions = db.query(Question).filter(Question.quiz_id == quiz_id).all()
    if not questions:
        raise HTTPException(status_code=400, detail="This quiz has no configured questions yet")

    child_questions = [
        ChildQuestionResponse(
            id=q.id,
            quiz_id=q.quiz_id,
            question_text=q.question_text,
            question_type=q.question_type,
            option_a=q.option_a,
            option_b=q.option_b,
            option_c=q.option_c,
            option_d=q.option_d
        )
        for q in questions
    ]

    return ChildQuizAttemptResponse(
        id=quiz.id,
        title=quiz.title,
        description=quiz.description,
        difficulty=quiz.difficulty,
        topic_name=quiz.topic.name if quiz.topic else "General",
        questions=child_questions
    )

# POST /api/quizzes/{quiz_id}/submit (Child submission & backend score calculation)
@router.post("/quizzes/{quiz_id}/submit", response_model=QuizSubmissionResponse)
def submit_quiz_attempt(
    quiz_id: int,
    submission: QuizSubmissionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["child"]))
):
    child_profile = db.query(ChildProfile).filter(ChildProfile.user_id == current_user.id).first()
    if not child_profile:
        raise HTTPException(status_code=404, detail="Child profile not found for authenticated user")

    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz or not quiz.is_published:
        raise HTTPException(status_code=404, detail="Quiz not found or not published")

    questions = db.query(Question).filter(Question.quiz_id == quiz_id).all()
    if not questions:
        raise HTTPException(status_code=400, detail="Quiz has no questions")

    questions_map = {q.id: q for q in questions}
    total_q = len(questions)
    correct_count = 0

    # Map submitted answers
    sub_answers_map = {sa.question_id: sa.selected_answer.upper().strip() for sa in submission.answers}

    # Calculate correctness on backend
    ans_records = []
    for q_id, q in questions_map.items():
        user_choice = sub_answers_map.get(q_id, "")
        is_corr = (user_choice == q.correct_answer.upper().strip())
        if is_corr:
            correct_count += 1
        ans_records.append({
            "question_id": q_id,
            "selected_answer": user_choice,
            "is_correct": is_corr
        })

    pct = round((correct_count / total_q) * 100.0, 2)
    score_val = float(correct_count)

    # Determine performance tier
    if pct >= 85.0:
        perf = "excellent"
    elif pct >= 70.0:
        perf = "good"
    else:
        perf = "needs_practice"

    # Calculate attempt_number for this child & quiz
    previous_attempts_count = db.query(QuizAttempt).filter(
        QuizAttempt.child_id == child_profile.id,
        QuizAttempt.quiz_id == quiz_id
    ).count()
    attempt_num = previous_attempts_count + 1

    # Create QuizAttempt record
    now = datetime.utcnow()
    attempt = QuizAttempt(
        quiz_id=quiz_id,
        child_id=child_profile.id,
        score=score_val,
        total_questions=total_q,
        correct_answers=correct_count,
        percentage=pct,
        time_taken=submission.time_taken,
        attempt_number=attempt_num,
        started_at=now,
        completed_at=now
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)

    # Create Answer records
    for a_rec in ans_records:
        ans_obj = Answer(
            attempt_id=attempt.id,
            question_id=a_rec["question_id"],
            selected_answer=a_rec["selected_answer"],
            is_correct=a_rec["is_correct"]
        )
        db.add(ans_obj)

    # Create LearningHistory record for future Transformer / AI training
    history = LearningHistory(
        child_id=child_profile.id,
        activity_type="quiz",
        activity_id=quiz_id,
        topic_id=quiz.topic_id,
        difficulty=quiz.difficulty,
        score=pct,
        completion_status="completed",
        time_spent=submission.time_taken
    )
    db.add(history)
    db.commit()

    return QuizSubmissionResponse(
        attempt_id=attempt.id,
        quiz_id=quiz_id,
        score=score_val,
        total_questions=total_q,
        correct_answers=correct_count,
        percentage=pct,
        time_taken=submission.time_taken,
        completed_at=attempt.completed_at,
        performance=perf
    )
