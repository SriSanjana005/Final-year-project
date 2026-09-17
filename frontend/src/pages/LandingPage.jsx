import React from 'react';
import { useNavigate } from 'react-router-dom';
import { Sparkles, Shield, Brain, Heart, ArrowRight } from 'lucide-react';
import { Button } from '../components/ui/button';

export function LandingPage() {
  const navigate = useNavigate();

  return (
    <div className="min-h-screen bg-[#F8FAFC] text-[#0F172A]">
      {/* Header */}
      <header className="max-w-7xl mx-auto px-6 h-20 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 bg-[#2563EB] rounded-xl flex items-center justify-center text-white font-bold text-xl shadow-md">
            A
          </div>
          <span className="font-bold text-xl tracking-tight text-slate-900">AdaptLearn</span>
        </div>
        <div className="flex items-center gap-4">
          <Button variant="outline" onClick={() => navigate('/login')}>Sign In</Button>
          <Button variant="primary" onClick={() => navigate('/login')}>Get Started</Button>
        </div>
      </header>

      {/* Hero Section */}
      <section className="max-w-5xl mx-auto px-6 py-20 text-center space-y-8">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-blue-50 border border-blue-200 text-[#2563EB] text-sm font-semibold">
          <Sparkles size={16} /> Transformer & Deep Reinforcement Learning Powered
        </div>
        
        <h1 className="text-4xl md:text-6xl font-extrabold text-[#0F172A] leading-tight tracking-tight">
          Personalized Learning Experiences for Children with Special Needs
        </h1>

        <p className="text-lg md:text-xl text-slate-600 max-w-3xl mx-auto leading-relaxed">
          An intelligent adaptive learning platform designed to support unique learning styles, deliver tailored educational content, and track real progress with care and precision.
        </p>

        <div className="flex flex-col sm:flex-row justify-center gap-4 pt-4">
          <Button size="lg" variant="primary" onClick={() => navigate('/login')} className="gap-2">
            Access Portal <ArrowRight size={18} />
          </Button>
        </div>
      </section>

      {/* Features Grid */}
      <section className="max-w-6xl mx-auto px-6 py-12">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <div className="w-12 h-12 bg-blue-50 text-[#2563EB] rounded-xl flex items-center justify-center">
              <Brain size={24} />
            </div>
            <h3 className="text-xl font-bold text-slate-900">Adaptive AI Guidance</h3>
            <p className="text-slate-600 text-sm leading-relaxed">
              Leverages Transformer sequence modeling and DRL to understand historical learning patterns and recommend ideal next actions.
            </p>
          </div>

          <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <div className="w-12 h-12 bg-teal-50 text-[#14B8A6] rounded-xl flex items-center justify-center">
              <Heart size={24} />
            </div>
            <h3 className="text-xl font-bold text-slate-900">Accessible & Uncluttered</h3>
            <p className="text-slate-600 text-sm leading-relaxed">
              Designed explicitly with high contrast, readable typography, and calm layouts suitable for children with sensory sensitivities.
            </p>
          </div>

          <div className="bg-white p-8 rounded-2xl border border-slate-200 shadow-sm space-y-4">
            <div className="w-12 h-12 bg-purple-50 text-purple-600 rounded-xl flex items-center justify-center">
              <Shield size={24} />
            </div>
            <h3 className="text-xl font-bold text-slate-900">Parent & Admin Control</h3>
            <p className="text-slate-600 text-sm leading-relaxed">
              Curated, admin-approved educational content library with real-time parent progress monitoring dashboards.
            </p>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-slate-200 py-8 text-center text-sm text-slate-500">
        <p>© 2026 AdaptLearn. Transformer-Based Personalized Learning FYP Project.</p>
      </footer>
    </div>
  );
}
