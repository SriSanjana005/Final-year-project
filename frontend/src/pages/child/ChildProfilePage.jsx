import React, { useState, useEffect } from 'react';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { useAuth } from '../../context/AuthContext';
import { userService } from '../../services/userService';
import { User as UserIcon, BookOpen, Heart, Calendar } from 'lucide-react';

export function ChildProfilePage() {
  const { user } = useAuth();
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const data = await userService.getChildProfile();
        setProfile(data);
      } catch (err) {
        console.error("Failed to fetch child profile:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchProfile();
  }, []);

  return (
    <AppLayout>
      <div className="max-w-2xl mx-auto space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Child Profile</h1>
          <p className="text-sm text-slate-500">Learner details and accommodation preferences.</p>
        </div>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-emerald-100 text-emerald-700 rounded-full flex items-center justify-center font-bold text-xl shadow-xs">
                {user?.name?.charAt(0) || 'C'}
              </div>
              <div>
                <CardTitle>{user?.name || 'Child Learner'}</CardTitle>
                <p className="text-xs text-slate-500">Role: Child Learner | Email: {user?.email}</p>
              </div>
            </div>
          </CardHeader>
          
          <CardContent className="space-y-6 pt-4 border-t border-slate-100 text-sm">
            {loading ? (
              <div className="p-4 text-center text-xs text-slate-400">Loading profile details...</div>
            ) : (
              <>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
                    <span className="text-xs text-slate-400 font-semibold flex items-center gap-1.5">
                      <BookOpen size={14} className="text-[#2563EB]" /> Learning Level
                    </span>
                    <span className="font-bold text-slate-800 capitalize">
                      {profile?.learning_level || 'Beginner'}
                    </span>
                  </div>

                  <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
                    <span className="text-xs text-slate-400 font-semibold flex items-center gap-1.5">
                      <Calendar size={14} className="text-[#14B8A6]" /> Date of Birth
                    </span>
                    <span className="font-bold text-slate-800">
                      {profile?.date_of_birth || 'Not specified'}
                    </span>
                  </div>
                </div>

                <div className="p-4 bg-blue-50/40 border border-blue-100 rounded-xl space-y-2">
                  <span className="text-xs font-semibold text-blue-900 flex items-center gap-1.5">
                    <Heart size={14} className="text-blue-600" /> Learning Requirements & Accommodations
                  </span>
                  <p className="text-xs text-slate-700 leading-relaxed">
                    {profile?.learning_requirements || 'Standard visual aids and tactile feedback.'}
                  </p>
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
