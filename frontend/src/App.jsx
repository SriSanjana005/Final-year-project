import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import { ProtectedRoute } from './components/ProtectedRoute';

// Common Pages
import { LandingPage } from './pages/LandingPage';
import { LoginPage } from './pages/auth/LoginPage';
import { NotFoundPage } from './pages/NotFoundPage';

// Child Pages
import { ChildDashboard } from './pages/child/ChildDashboard';
import { LearningContentPage } from './pages/child/LearningContentPage';
import { ContentDetailPage } from './pages/child/ContentDetailPage';
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
import { RecommendationMonitoringPage } from './pages/admin/RecommendationMonitoringPage';
import { EvaluationDashboardPage } from './pages/admin/EvaluationDashboardPage';

export default function App() {
  return (
    <AuthProvider>
      <BrowserRouter>
        <Routes>
          {/* Public Routes */}
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<LoginPage />} />

          {/* Child Protected Routes */}
          <Route path="/child/dashboard" element={<ProtectedRoute allowedRoles={['child']}><ChildDashboard /></ProtectedRoute>} />
          <Route path="/child/content" element={<ProtectedRoute allowedRoles={['child']}><LearningContentPage /></ProtectedRoute>} />
          <Route path="/child/learning" element={<ProtectedRoute allowedRoles={['child']}><LearningContentPage /></ProtectedRoute>} />
          <Route path="/child/learning/:contentId" element={<ProtectedRoute allowedRoles={['child']}><ContentDetailPage /></ProtectedRoute>} />
          <Route path="/child/quiz" element={<ProtectedRoute allowedRoles={['child']}><QuizPage /></ProtectedRoute>} />
          <Route path="/child/quiz/:quizId" element={<ProtectedRoute allowedRoles={['child']}><QuizPage /></ProtectedRoute>} />
          <Route path="/child/quiz/:quizId/result/:attemptId" element={<ProtectedRoute allowedRoles={['child']}><QuizResultPage /></ProtectedRoute>} />
          <Route path="/child/quiz-result" element={<ProtectedRoute allowedRoles={['child']}><QuizResultPage /></ProtectedRoute>} />
          <Route path="/child/result" element={<ProtectedRoute allowedRoles={['child']}><QuizResultPage /></ProtectedRoute>} />
          <Route path="/child/progress" element={<ProtectedRoute allowedRoles={['child']}><ProgressPage /></ProtectedRoute>} />
          <Route path="/child/recommendations" element={<ProtectedRoute allowedRoles={['child']}><RecommendationsPage /></ProtectedRoute>} />
          <Route path="/child/history" element={<ProtectedRoute allowedRoles={['child']}><LearningHistoryPage /></ProtectedRoute>} />
          <Route path="/child/profile" element={<ProtectedRoute allowedRoles={['child']}><ChildProfilePage /></ProtectedRoute>} />

          {/* Parent Protected Routes */}
          <Route path="/parent/dashboard" element={<ProtectedRoute allowedRoles={['parent']}><ParentDashboard /></ProtectedRoute>} />
          <Route path="/parent/child-progress" element={<ProtectedRoute allowedRoles={['parent']}><ChildProgressPage /></ProtectedRoute>} />
          <Route path="/parent/progress" element={<ProtectedRoute allowedRoles={['parent']}><ChildProgressPage /></ProtectedRoute>} />
          <Route path="/parent/child-performance" element={<ProtectedRoute allowedRoles={['parent']}><ChildPerformancePage /></ProtectedRoute>} />
          <Route path="/parent/performance" element={<ProtectedRoute allowedRoles={['parent']}><ChildPerformancePage /></ProtectedRoute>} />
          <Route path="/parent/child-history" element={<ProtectedRoute allowedRoles={['parent']}><ChildLearningHistoryPage /></ProtectedRoute>} />
          <Route path="/parent/history" element={<ProtectedRoute allowedRoles={['parent']}><ChildLearningHistoryPage /></ProtectedRoute>} />
          <Route path="/parent/profile" element={<ProtectedRoute allowedRoles={['parent']}><ParentProfilePage /></ProtectedRoute>} />

          {/* Admin Protected Routes */}
          <Route path="/admin/dashboard" element={<ProtectedRoute allowedRoles={['admin']}><AdminDashboard /></ProtectedRoute>} />
          <Route path="/admin/users" element={<ProtectedRoute allowedRoles={['admin']}><UserManagementPage /></ProtectedRoute>} />
          <Route path="/admin/mapping" element={<ProtectedRoute allowedRoles={['admin']}><ParentChildMappingPage /></ProtectedRoute>} />
          <Route path="/admin/mappings" element={<ProtectedRoute allowedRoles={['admin']}><ParentChildMappingPage /></ProtectedRoute>} />
          <Route path="/admin/topics" element={<ProtectedRoute allowedRoles={['admin']}><TopicManagementPage /></ProtectedRoute>} />
          <Route path="/admin/content" element={<ProtectedRoute allowedRoles={['admin']}><ContentManagementPage /></ProtectedRoute>} />
          <Route path="/admin/quizzes" element={<ProtectedRoute allowedRoles={['admin']}><QuizManagementPage /></ProtectedRoute>} />
          <Route path="/admin/questions" element={<ProtectedRoute allowedRoles={['admin']}><QuestionManagementPage /></ProtectedRoute>} />
          <Route path="/admin/recommendations" element={<ProtectedRoute allowedRoles={['admin']}><RecommendationMonitoringPage /></ProtectedRoute>} />
          <Route path="/admin/evaluation" element={<ProtectedRoute allowedRoles={['admin']}><EvaluationDashboardPage /></ProtectedRoute>} />


          {/* Catch-all 404 Route */}
          <Route path="*" element={<NotFoundPage />} />
        </Routes>
      </BrowserRouter>
    </AuthProvider>
  );
}
