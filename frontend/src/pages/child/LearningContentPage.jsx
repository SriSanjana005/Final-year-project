import React, { useState } from 'react';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { BookOpen, CheckCircle, Clock } from 'lucide-react';

export function LearningContentPage() {
  const [selectedTopic, setSelectedTopic] = useState(1);

  const topics = [
    { id: 1, title: "Mathematics - Addition & Subtraction", difficulty: "Beginner", duration: "5 mins", desc: "Learn to add 2-digit numbers using visual blocks." },
    { id: 2, title: "Reading Comprehension & Sight Words", difficulty: "Intermediate", duration: "8 mins", desc: "Interactive story cards with clear visual icons." },
    { id: 3, title: "Visual Pattern Recognition", difficulty: "Beginner", duration: "6 mins", desc: "Identify shapes, colors, and repeating patterns." }
  ];

  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Learning Topics & Content</h1>
          <p className="text-sm text-slate-500">Explore approved learning modules designed for visual clarity.</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="space-y-3 lg:col-span-1">
            <p className="text-xs font-semibold text-slate-400 uppercase">Available Modules</p>
            {topics.map((t) => (
              <div 
                key={t.id}
                onClick={() => setSelectedTopic(t.id)}
                className={`p-4 rounded-xl border transition-all cursor-pointer ${
                  selectedTopic === t.id 
                    ? 'border-[#2563EB] bg-blue-50/50 shadow-sm' 
                    : 'border-slate-200 bg-white hover:border-slate-300'
                }`}
              >
                <div className="flex justify-between items-center mb-1">
                  <Badge variant="default">{t.difficulty}</Badge>
                  <span className="text-xs text-slate-400 flex items-center gap-1"><Clock size={12}/> {t.duration}</span>
                </div>
                <h3 className="font-bold text-slate-900 text-sm">{t.title}</h3>
                <p className="text-xs text-slate-500 mt-1 line-clamp-2">{t.desc}</p>
              </div>
            ))}
          </div>

          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <div className="flex items-center gap-2 text-xs font-semibold text-[#2563EB]">
                  <BookOpen size={16} /> Interactive Lesson View
                </div>
                <CardTitle>{topics.find(t => t.id === selectedTopic)?.title}</CardTitle>
                <CardDescription>Step-by-step visual lesson content</CardDescription>
              </CardHeader>
              <CardContent className="space-y-6">
                <div className="p-6 bg-slate-50 rounded-xl border border-slate-200 text-center space-y-4">
                  <div className="flex justify-center gap-4 text-4xl">
                    <span>🟦 🟦 🟦</span>
                    <span>+</span>
                    <span>🟦 🟦</span>
                  </div>
                  <p className="text-lg font-bold text-slate-800">3 Blocks + 2 Blocks = 5 Blocks</p>
                  <p className="text-sm text-slate-600 max-w-md mx-auto">
                    Count each block one by one to find the total sum. Use your hands to count along!
                  </p>
                </div>

                <div className="flex justify-between items-center pt-4">
                  <Button variant="outline">Previous Step</Button>
                  <Button variant="success" className="gap-2">
                    Mark Completed <CheckCircle size={16} />
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    </AppLayout>
  );
}
