import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { Progress } from '../../components/ui/progress';
import { quizService } from '../../services/quizService';
import { HelpCircle, Clock, Play, ArrowLeft, ArrowRight, CheckCircle, AlertCircle } from 'lucide-react';

export function QuizPage() {
  const { quizId } = useParams();
  const navigate = useNavigate();

  // Mode 1: Listing published quizzes
  const [quizzes, setQuizzes] = useState([]);
  const [loadingListing, setLoadingListing] = useState(true);

  // Mode 2: Quiz Take Interface
  const [quizAttemptData, setQuizAttemptData] = useState(null);
  const [currentQIndex, setCurrentQIndex] = useState(0);
  const [userAnswers, setUserAnswers] = useState({}); // { question_id: "A" | "B" | "C" | "D" }
  const [startTime, setStartTime] = useState(null);
  const [loadingAttempt, setLoadingAttempt] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");

  useEffect(() => {
    if (!quizId) {
      // Load published quizzes list
      const fetchList = async () => {
        try {
          setLoadingListing(true);
          const data = await quizService.getPublishedQuizzes();
          setQuizzes(data);
        } catch (err) {
          console.error("Failed to load published quizzes:", err);
        } finally {
          setLoadingListing(false);
        }
      };
      fetchList();
    } else {
      // Load quiz questions for attempt
      const fetchAttempt = async () => {
        try {
          setLoadingAttempt(true);
          setErrorMsg("");
          const data = await quizService.getQuizForAttempt(quizId);
          setQuizAttemptData(data);
          setStartTime(Date.now());
        } catch (err) {
          setErrorMsg(err.response?.data?.detail || "Unable to start quiz assessment.");
        } finally {
          setLoadingAttempt(false);
        }
      };
      fetchAttempt();
    }
  }, [quizId]);

  const handleSelectOption = (questionId, optionKey) => {
    setUserAnswers(prev => ({
      ...prev,
      [questionId]: optionKey
    }));
  };

  const handleSubmitQuiz = async () => {
    if (!quizAttemptData) return;

    const questions = quizAttemptData.questions;
    const answeredCount = Object.keys(userAnswers).length;
    
    if (answeredCount < questions.length) {
      if (!window.confirm(`You have answered ${answeredCount} of ${questions.length} questions. Are you sure you want to submit?`)) {
        return;
      }
    }

    const elapsedSeconds = startTime ? Math.max(1, Math.floor((Date.now() - startTime) / 1000)) : 10;

    const answersPayload = questions.map(q => ({
      question_id: q.id,
      selected_answer: userAnswers[q.id] || ""
    }));

    setSubmitting(true);
    try {
      const res = await quizService.submitQuiz(quizId, {
        time_taken: elapsedSeconds,
        answers: answersPayload
      });

      navigate(`/child/quiz/${quizId}/result/${res.attempt_id}`, { state: { result: res, quiz: quizAttemptData } });
    } catch (err) {
      alert("Failed to submit quiz: " + (err.response?.data?.detail || err.message));
    } finally {
      setSubmitting(false);
    }
  };

  const getDifficultyBadge = (diff) => {
    switch (diff) {
      case 'easy':
        return <Badge variant="success">Easy</Badge>;
      case 'medium':
        return <Badge variant="warning">Medium</Badge>;
      case 'hard':
        return <Badge variant="danger">Hard</Badge>;
      default:
        return <Badge variant="neutral">{diff}</Badge>;
    }
  };

  // --- MODE 2: INTERACTIVE QUIZ TAKE INTERFACE ---
  if (quizId) {
    if (loadingAttempt) {
      return (
        <AppLayout>
          <div className="p-12 text-center text-xs text-slate-400">Loading quiz assessment questions...</div>
        </AppLayout>
      );
    }

    if (errorMsg || !quizAttemptData) {
      return (
        <AppLayout>
          <div className="max-w-md mx-auto space-y-4">
            <Card className="p-8 text-center text-red-600 space-y-3">
              <AlertCircle size={36} className="mx-auto" />
              <h3 className="font-bold text-base">Quiz Not Available</h3>
              <p className="text-xs text-slate-500">{errorMsg || "This quiz does not exist or has no questions."}</p>
              <Button variant="outline" size="sm" onClick={() => navigate('/child/quiz')}>
                Return to Quizzes
              </Button>
            </Card>
          </div>
        </AppLayout>
      );
    }

    const questions = quizAttemptData.questions;
    const currentQ = questions[currentQIndex];
    const progressPct = Math.round(((currentQIndex + 1) / questions.length) * 100);

    return (
      <AppLayout>
        <div className="max-w-2xl mx-auto space-y-6">
          {/* Header */}
          <div className="flex justify-between items-center border-b border-slate-200 pb-4">
            <div>
              <button 
                onClick={() => navigate('/child/quiz')} 
                className="text-xs text-slate-500 hover:text-blue-600 flex items-center gap-1 cursor-pointer mb-1"
              >
                <ArrowLeft size={14} /> Back to Quizzes
              </button>
              <h1 className="text-xl font-bold text-slate-900">{quizAttemptData.title}</h1>
              <span className="text-xs text-slate-500">Topic: {quizAttemptData.topic_name}</span>
            </div>
            {getDifficultyBadge(quizAttemptData.difficulty)}
          </div>

          {/* Progress Indicator */}
          <div className="space-y-1">
            <div className="flex justify-between text-xs font-semibold text-slate-600">
              <span>Question {currentQIndex + 1} of {questions.length}</span>
              <span>{progressPct}% Completed</span>
            </div>
            <Progress value={progressPct} color="bg-[#2563EB]" />
          </div>

          {/* Question Card */}
          <Card className="p-6 md:p-8 shadow-md border border-slate-200 space-y-6">
            <div className="space-y-2">
              <span className="text-xs font-bold text-[#2563EB] uppercase tracking-wider">
                Question #{currentQIndex + 1}
              </span>
              <h2 className="text-xl md:text-2xl font-bold text-slate-900 leading-snug">
                {currentQ.question_text}
              </h2>
            </div>

            {/* Answer Options */}
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 pt-2">
              {[
                { key: 'A', text: currentQ.option_a },
                { key: 'B', text: currentQ.option_b },
                { key: 'C', text: currentQ.option_c },
                { key: 'D', text: currentQ.option_d },
              ].map(opt => {
                const isSelected = userAnswers[currentQ.id] === opt.key;
                return (
                  <button
                    key={opt.key}
                    onClick={() => handleSelectOption(currentQ.id, opt.key)}
                    className={`p-4 rounded-xl border-2 font-bold text-left transition-all cursor-pointer flex items-center gap-3 ${
                      isSelected
                        ? 'border-[#2563EB] bg-blue-50 text-[#2563EB] shadow-xs'
                        : 'border-slate-200 bg-white text-slate-700 hover:border-slate-300 hover:bg-slate-50'
                    }`}
                  >
                    <span className={`w-8 h-8 rounded-lg flex items-center justify-center font-bold text-sm shrink-0 ${
                      isSelected ? 'bg-[#2563EB] text-white' : 'bg-slate-100 text-slate-700'
                    }`}>
                      {opt.key}
                    </span>
                    <span className="text-base">{opt.text}</span>
                  </button>
                );
              })}
            </div>

            {/* Question Navigation Controls */}
            <div className="flex justify-between items-center pt-6 border-t border-slate-100">
              <Button 
                variant="outline" 
                size="md" 
                disabled={currentQIndex === 0}
                onClick={() => setCurrentQIndex(prev => prev - 1)}
              >
                Previous
              </Button>

              {currentQIndex < questions.length - 1 ? (
                <Button 
                  variant="primary" 
                  size="md"
                  onClick={() => setCurrentQIndex(prev => prev + 1)}
                >
                  Next Question <ArrowRight size={16} />
                </Button>
              ) : (
                <Button 
                  variant="success" 
                  size="lg"
                  disabled={submitting}
                  onClick={handleSubmitQuiz}
                  className="gap-2 font-semibold"
                >
                  {submitting ? "Calculating Result..." : "Submit Assessment"} <CheckCircle size={18} />
                </Button>
              )}
            </div>
          </Card>
        </div>
      </AppLayout>
    );
  }

  // --- MODE 1: PUBLISHED QUIZZES LISTING ---
  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <HelpCircle className="text-[#2563EB]" /> Interactive Quiz Assessments
          </h1>
          <p className="text-sm text-slate-500">Test your learning progress with approved practice quizzes.</p>
        </div>

        {loadingListing ? (
          <div className="p-12 text-center text-xs text-slate-400">Loading published quizzes...</div>
        ) : quizzes.length === 0 ? (
          <Card className="p-12 text-center text-slate-500 space-y-2">
            <HelpCircle size={36} className="mx-auto text-slate-300" />
            <h3 className="font-bold text-slate-800 text-base">No quizzes available yet</h3>
            <p className="text-xs text-slate-500 max-w-sm mx-auto">
              No published practice quizzes are currently available. Check back soon!
            </p>
          </Card>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {quizzes.map((q) => (
              <Card key={q.id} className="border border-slate-200 hover:border-blue-300 transition-all flex flex-col justify-between">
                <CardHeader>
                  <div className="flex justify-between items-center mb-1">
                    <Badge variant="default">{q.topic?.subject || 'General'}</Badge>
                    {getDifficultyBadge(q.difficulty)}
                  </div>
                  <CardTitle className="text-base pt-1">{q.title}</CardTitle>
                  <CardDescription className="line-clamp-2">{q.description || 'Topic quiz assessment'}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <div className="flex items-center justify-between text-xs text-slate-500">
                    <span>Topic: <strong>{q.topic?.name}</strong></span>
                    <span><strong>{q.question_count}</strong> Questions</span>
                  </div>

                  <Button 
                    variant="primary" 
                    size="md" 
                    className="w-full gap-2 text-xs font-semibold"
                    onClick={() => navigate(`/child/quiz/${q.id}`)}
                  >
                    <Play size={16} /> Start Quiz
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        )}
      </div>
    </AppLayout>
  );
}
