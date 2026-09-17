import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { quizService } from '../../services/quizService';
import { HelpCircle, Plus, Edit2, Trash2, X, Check, AlertCircle } from 'lucide-react';

export function QuestionManagementPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialQuizId = searchParams.get("quiz_id") || "";

  const [quizzes, setQuizzes] = useState([]);
  const [selectedQuizId, setSelectedQuizId] = useState(initialQuizId);
  const [questions, setQuestions] = useState([]);
  const [loading, setLoading] = useState(false);

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingQuestion, setEditingQuestion] = useState(null);

  // Form State
  const [questionText, setQuestionText] = useState("");
  const [optionA, setOptionA] = useState("");
  const [optionB, setOptionB] = useState("");
  const [optionC, setOptionC] = useState("");
  const [optionD, setOptionD] = useState("");
  const [correctAnswer, setCorrectAnswer] = useState("A");
  const [explanation, setExplanation] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);

  const loadQuizzes = async () => {
    try {
      const data = await quizService.getQuizzes();
      setQuizzes(data);
      if (!selectedQuizId && data.length > 0) {
        setSelectedQuizId(data[0].id.toString());
      }
    } catch (err) {
      console.error("Failed to load quizzes:", err);
    }
  };

  const loadQuestions = async (quizId) => {
    if (!quizId) {
      setQuestions([]);
      return;
    }
    try {
      setLoading(true);
      const data = await quizService.getQuestions(quizId);
      setQuestions(data);
    } catch (err) {
      console.error("Failed to load questions:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadQuizzes();
  }, []);

  useEffect(() => {
    if (selectedQuizId) {
      loadQuestions(selectedQuizId);
    }
  }, [selectedQuizId]);

  const openAddModal = () => {
    if (!selectedQuizId) {
      alert("Please select a quiz first.");
      return;
    }
    setEditingQuestion(null);
    setQuestionText("");
    setOptionA("");
    setOptionB("");
    setOptionC("");
    setOptionD("");
    setCorrectAnswer("A");
    setExplanation("");
    setIsModalOpen(true);
  };

  const openEditModal = (q) => {
    setEditingQuestion(q);
    setQuestionText(q.question_text);
    setOptionA(q.option_a);
    setOptionB(q.option_b);
    setOptionC(q.option_c);
    setOptionD(q.option_d);
    setCorrectAnswer(q.correct_answer);
    setExplanation(q.explanation || "");
    setIsModalOpen(true);
  };

  const handleSaveQuestion = async (e) => {
    e.preventDefault();
    if (!questionText.trim() || !optionA || !optionB || !optionC || !optionD) {
      alert("Question text and all four options are required.");
      return;
    }

    setIsSubmitting(true);
    try {
      const payload = {
        question_text: questionText,
        question_type: "multiple_choice",
        option_a: optionA,
        option_b: optionB,
        option_c: optionC,
        option_d: optionD,
        correct_answer: correctAnswer,
        explanation
      };

      if (editingQuestion) {
        await quizService.updateQuestion(editingQuestion.id, payload);
      } else {
        await quizService.createQuestion(parseInt(selectedQuizId), payload);
      }

      setIsModalOpen(false);
      loadQuestions(selectedQuizId);
    } catch (err) {
      alert("Failed to save question: " + (err.response?.data?.detail || err.message));
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleDeleteQuestion = async (qId) => {
    if (!window.confirm("Are you sure you want to delete this question?")) {
      return;
    }
    try {
      await quizService.deleteQuestion(qId);
      loadQuestions(selectedQuizId);
    } catch (err) {
      alert("Failed to delete question");
    }
  };

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
          <div>
            <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
              <HelpCircle className="text-[#2563EB]" /> Question Bank Management
            </h1>
            <p className="text-sm text-slate-500">Configure multiple choice questions and answer keys for assessments.</p>
          </div>
          <Button variant="primary" className="gap-2 text-xs" onClick={openAddModal} disabled={!selectedQuizId}>
            <Plus size={16} /> Add Question
          </Button>
        </div>

        {/* Quiz Selector Filter */}
        <Card className="p-4 bg-slate-50 border border-slate-200">
          <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
            <span className="text-xs font-semibold text-slate-700">Select Quiz Assessment:</span>
            <select 
              value={selectedQuizId}
              onChange={(e) => {
                setSelectedQuizId(e.target.value);
                setSearchParams({ quiz_id: e.target.value });
              }}
              className="h-10 px-3 border border-slate-300 rounded-lg text-xs bg-white font-semibold text-slate-800 focus:ring-2 focus:ring-blue-500 w-full sm:w-auto min-w-[280px]"
            >
              <option value="">-- Select Quiz --</option>
              {quizzes.map(q => (
                <option key={q.id} value={q.id}>
                  {q.topic?.subject} - {q.title} ({q.question_count} questions)
                </option>
              ))}
            </select>
          </div>
        </Card>

        {/* Question Bank Table */}
        <Card>
          <CardHeader><CardTitle className="text-base">Quiz Questions ({questions.length})</CardTitle></CardHeader>
          <CardContent>
            {!selectedQuizId ? (
              <div className="p-8 text-center text-xs text-slate-500">Please select a quiz assessment from the dropdown above.</div>
            ) : loading ? (
              <div className="p-8 text-center text-xs text-slate-400">Loading question items...</div>
            ) : questions.length === 0 ? (
              <div className="p-8 text-center text-xs text-slate-500">No questions added to this quiz yet. Click "Add Question" to build the question bank.</div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-200 text-slate-500 font-semibold">
                      <th className="pb-3 px-2">#</th>
                      <th className="pb-3 px-2">Question Text</th>
                      <th className="pb-3 px-2">Options</th>
                      <th className="pb-3 px-2">Correct Answer</th>
                      <th className="pb-3 px-2">Explanation</th>
                      <th className="pb-3 px-2 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {questions.map((q, idx) => (
                      <tr key={q.id} className="hover:bg-slate-50">
                        <td className="py-3 px-2 font-bold text-slate-400">{idx + 1}</td>
                        <td className="py-3 px-2 font-bold text-slate-800 max-w-xs">{q.question_text}</td>
                        <td className="py-3 px-2 text-slate-600">
                          <div className="grid grid-cols-2 gap-x-2 gap-y-0.5 text-[11px]">
                            <span className={q.correct_answer === 'A' ? 'font-bold text-teal-700' : ''}>A: {q.option_a}</span>
                            <span className={q.correct_answer === 'B' ? 'font-bold text-teal-700' : ''}>B: {q.option_b}</span>
                            <span className={q.correct_answer === 'C' ? 'font-bold text-teal-700' : ''}>C: {q.option_c}</span>
                            <span className={q.correct_answer === 'D' ? 'font-bold text-teal-700' : ''}>D: {q.option_d}</span>
                          </div>
                        </td>
                        <td className="py-3 px-2">
                          <Badge variant="success">Option {q.correct_answer}</Badge>
                        </td>
                        <td className="py-3 px-2 text-slate-500 max-w-xs truncate">{q.explanation || 'None'}</td>
                        <td className="py-3 px-2 text-right space-x-1">
                          <Button variant="outline" size="sm" className="h-8 px-2" onClick={() => openEditModal(q)}>
                            <Edit2 size={14} />
                          </Button>
                          <Button variant="danger" size="sm" className="h-8 px-2" onClick={() => handleDeleteQuestion(q.id)}>
                            <Trash2 size={14} />
                          </Button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </CardContent>
        </Card>
      </div>

      {/* Add / Edit Question Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 bg-slate-900/40 backdrop-blur-xs flex items-center justify-center p-4">
          <div className="bg-white rounded-xl border border-slate-200 shadow-xl max-w-lg w-full max-h-[90vh] overflow-y-auto p-6 space-y-4">
            <div className="flex justify-between items-center border-b border-slate-100 pb-3">
              <h3 className="font-bold text-slate-900 text-base">
                {editingQuestion ? "Edit Question Item" : "Add Multiple Choice Question"}
              </h3>
              <button onClick={() => setIsModalOpen(false)} className="text-slate-400 hover:text-slate-600">
                <X size={18} />
              </button>
            </div>

            <form onSubmit={handleSaveQuestion} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Question Text</label>
                <textarea 
                  value={questionText}
                  onChange={(e) => setQuestionText(e.target.value)}
                  placeholder="e.g. What is 4 + 3?"
                  className="w-full p-3 border border-slate-300 rounded-lg text-xs h-20 focus:ring-2 focus:ring-blue-500"
                  required
                />
              </div>

              <div className="space-y-2">
                <label className="block text-xs font-semibold text-slate-700">Answer Options & Correct Answer Selection</label>
                
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
                  <div className={`p-2.5 rounded-lg border flex items-center gap-2 ${correctAnswer === 'A' ? 'border-teal-500 bg-teal-50/50' : 'border-slate-200'}`}>
                    <input 
                      type="radio"
                      name="correctRadio"
                      checked={correctAnswer === 'A'}
                      onChange={() => setCorrectAnswer('A')}
                      className="w-4 h-4 text-teal-600"
                    />
                    <span className="font-bold text-slate-700">A:</span>
                    <input 
                      type="text"
                      value={optionA}
                      onChange={(e) => setOptionA(e.target.value)}
                      placeholder="Option A text"
                      className="w-full bg-white border border-slate-200 px-2 py-1 rounded text-xs"
                      required
                    />
                  </div>

                  <div className={`p-2.5 rounded-lg border flex items-center gap-2 ${correctAnswer === 'B' ? 'border-teal-500 bg-teal-50/50' : 'border-slate-200'}`}>
                    <input 
                      type="radio"
                      name="correctRadio"
                      checked={correctAnswer === 'B'}
                      onChange={() => setCorrectAnswer('B')}
                      className="w-4 h-4 text-teal-600"
                    />
                    <span className="font-bold text-slate-700">B:</span>
                    <input 
                      type="text"
                      value={optionB}
                      onChange={(e) => setOptionB(e.target.value)}
                      placeholder="Option B text"
                      className="w-full bg-white border border-slate-200 px-2 py-1 rounded text-xs"
                      required
                    />
                  </div>

                  <div className={`p-2.5 rounded-lg border flex items-center gap-2 ${correctAnswer === 'C' ? 'border-teal-500 bg-teal-50/50' : 'border-slate-200'}`}>
                    <input 
                      type="radio"
                      name="correctRadio"
                      checked={correctAnswer === 'C'}
                      onChange={() => setCorrectAnswer('C')}
                      className="w-4 h-4 text-teal-600"
                    />
                    <span className="font-bold text-slate-700">C:</span>
                    <input 
                      type="text"
                      value={optionC}
                      onChange={(e) => setOptionC(e.target.value)}
                      placeholder="Option C text"
                      className="w-full bg-white border border-slate-200 px-2 py-1 rounded text-xs"
                      required
                    />
                  </div>

                  <div className={`p-2.5 rounded-lg border flex items-center gap-2 ${correctAnswer === 'D' ? 'border-teal-500 bg-teal-50/50' : 'border-slate-200'}`}>
                    <input 
                      type="radio"
                      name="correctRadio"
                      checked={correctAnswer === 'D'}
                      onChange={() => setCorrectAnswer('D')}
                      className="w-4 h-4 text-teal-600"
                    />
                    <span className="font-bold text-slate-700">D:</span>
                    <input 
                      type="text"
                      value={optionD}
                      onChange={(e) => setOptionD(e.target.value)}
                      placeholder="Option D text"
                      className="w-full bg-white border border-slate-200 px-2 py-1 rounded text-xs"
                      required
                    />
                  </div>
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Explanation (Optional)</label>
                <input 
                  type="text"
                  value={explanation}
                  onChange={(e) => setExplanation(e.target.value)}
                  placeholder="Explain why this option is correct..."
                  className="w-full h-10 px-3 border border-slate-300 rounded-lg text-xs focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div className="flex justify-end gap-3 pt-3 border-t border-slate-100">
                <Button type="button" variant="outline" size="sm" onClick={() => setIsModalOpen(false)}>Cancel</Button>
                <Button type="submit" variant="primary" size="sm" disabled={isSubmitting}>
                  {isSubmitting ? "Saving..." : "Save Question"}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}
    </AppLayout>
  );
}
