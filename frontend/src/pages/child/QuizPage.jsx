import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';

export function QuizPage() {
  const navigate = useNavigate();
  const [selectedOption, setSelectedOption] = useState(null);

  const question = {
    title: "Mathematics Practice Quiz",
    questionText: "What is 4 + 3?",
    options: ["5 Blocks", "7 Blocks", "8 Blocks", "6 Blocks"],
    correctIndex: 1
  };

  const handleSubmit = () => {
    if (selectedOption !== null) {
      navigate('/child/quiz-result', { state: { score: selectedOption === question.correctIndex ? 100 : 50 } });
    }
  };

  return (
    <AppLayout>
      <div className="max-w-2xl mx-auto space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{question.title}</h1>
          <p className="text-sm text-slate-500">Question 1 of 1</p>
        </div>

        <Card className="p-8">
          <CardHeader className="px-0 pt-0">
            <CardTitle className="text-xl text-center text-slate-800">{question.questionText}</CardTitle>
          </CardHeader>
          <CardContent className="px-0 space-y-4">
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {question.options.map((opt, idx) => (
                <button
                  key={idx}
                  onClick={() => setSelectedOption(idx)}
                  className={`p-5 rounded-xl border-2 font-bold text-lg text-center transition-all ${
                    selectedOption === idx 
                      ? 'border-[#2563EB] bg-blue-50 text-[#2563EB] shadow-xs' 
                      : 'border-slate-200 bg-white text-slate-700 hover:border-slate-300'
                  }`}
                >
                  {opt}
                </button>
              ))}
            </div>

            <div className="pt-6 border-t border-slate-100 flex justify-end">
              <Button 
                variant="primary" 
                size="lg" 
                disabled={selectedOption === null}
                onClick={handleSubmit}
              >
                Submit Answer
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
