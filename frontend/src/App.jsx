import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';

// Common Pages
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/LoginPage';
import { NotFoundPage } from './pages/NotFoundPage';

// Child Pages
import { ChildDashboard } from './pages/child/ChildDashboard';
import { LearningContentPage } from './pages/child/LearningContentPage';
import { QuizPage } from './pages/child/QuizPage';
import { QuizResultPage } from './pages/child/QuizResultPage';
import { ProgressPage } from './pages/child/ProgressPage';
import { RecommendationsPage } from './pages/child/RecommendationsPage';
import { LearningHistoryPage } from './pages/child/LearningHistoryPage';
import { ChildProfilePage } from './pages/child/ChildProfilePage';

// Parent Pages
import { ParentDashboard } from './pages/parent/ParentDashboard';
import { ChildProgressPage } from './pages/parent/ChildProgressPage';
import { ChildPerformancePage } from './pages/parent/ChildPerformancePage';
import { ChildLearningHistoryPage } from './pages/parent/ChildLearningHistoryPage';
import { ParentProfilePage } from './pages/parent/ParentProfilePage';

// Admin Pages
import { AdminDashboard } from './pages/admin/AdminDashboard';
import { UserManagementPage } from './pages/admin/UserManagementPage';
import { ParentChildMappingPage } from './pages/admin/ParentChildMappingPage';
import { TopicManagementPage } from './pages/admin/TopicManagementPage';
import { ContentManagementPage } from './pages/admin/ContentManagementPage';
import { QuizManagementPage } from './pages/admin/QuizManagementPage';
import { QuestionManagementPage } from './pages/admin/QuestionManagementPage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Common Routes */}
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />

        {/* Child Routes */}
        <Route path="/child/dashboard" element={<ChildDashboard />} />
        <Route path="/child/content" element={<LearningContentPage />} />
        <Route path="/child/quiz" element={<QuizPage />} />
        <Route path="/child/quiz-result" element={<QuizResultPage />} />
        <Route path="/child/progress" element={<ProgressPage />} />
        <Route path="/child/recommendations" element={<RecommendationsPage />} />
        <Route path="/child/history" element={<LearningHistoryPage />} />
        <Route path="/child/profile" element={<ChildProfilePage />} />

        {/* Parent Routes */}
        <Route path="/parent/dashboard" element={<ParentDashboard />} />
        <Route path="/parent/child-progress" element={<ChildProgressPage />} />
        <Route path="/parent/child-performance" element={<ChildPerformancePage />} />
        <Route path="/parent/child-history" element={<ChildLearningHistoryPage />} />
        <Route path="/parent/profile" element={<ParentProfilePage />} />

        {/* Admin Routes */}
        <Route path="/admin/dashboard" element={<AdminDashboard />} />
        <Route path="/admin/users" element={<UserManagementPage />} />
        <Route path="/admin/mapping" element={<ParentChildMappingPage />} />
        <Route path="/admin/topics" element={<TopicManagementPage />} />
        <Route path="/admin/content" element={<ContentManagementPage />} />
        <Route path="/admin/quizzes" element={<QuizManagementPage />} />
        <Route path="/admin/questions" element={<QuestionManagementPage />} />

        {/* Catch-all 404 */}
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </BrowserRouter>
  );
}
