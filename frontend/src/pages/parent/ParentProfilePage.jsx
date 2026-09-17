import React, { useState, useEffect } from 'react';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { useAuth } from '../../context/AuthContext';
import { userService } from '../../services/userService';
import { Phone, Mail, Users, Sparkles } from 'lucide-react';

export function ParentProfilePage() {
  const { user } = useAuth();
  const [parentProfile, setParentProfile] = useState(null);
  const [childrenList, setChildrenList] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const [profData, childData] = await Promise.all([
          userService.getParentProfile(),
          userService.getParentChildren()
        ]);
        setParentProfile(profData);
        setChildrenList(childData);
      } catch (err) {
        console.error("Failed to fetch parent profile data:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, []);

  return (
    <AppLayout>
      <div className="max-w-2xl mx-auto space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Parent Profile</h1>
          <p className="text-sm text-slate-500">Account settings and authorized child relationships.</p>
        </div>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-4">
              <div className="w-14 h-14 bg-blue-100 text-[#2563EB] rounded-full flex items-center justify-center font-bold text-xl shadow-xs">
                {user?.name?.charAt(0) || 'P'}
              </div>
              <div>
                <CardTitle>{user?.name || 'Parent User'}</CardTitle>
                <p className="text-xs text-slate-500">Role: Parent | Email: {user?.email}</p>
              </div>
            </div>
          </CardHeader>

          <CardContent className="space-y-6 pt-4 border-t border-slate-100 text-sm">
            {loading ? (
              <div className="p-4 text-center text-xs text-slate-400">Loading parent details...</div>
            ) : (
              <>
                <div className="p-4 bg-slate-50 border border-slate-200 rounded-xl space-y-1">
                  <span className="text-xs text-slate-400 font-semibold flex items-center gap-1.5">
                    <Phone size={14} className="text-[#2563EB]" /> Phone Number
                  </span>
                  <span className="font-bold text-slate-800">
                    {parentProfile?.phone || 'Not provided'}
                  </span>
                </div>

                <div className="space-y-3">
                  <span className="text-xs font-bold text-slate-700 uppercase tracking-wider flex items-center gap-1.5">
                    <Users size={16} className="text-[#2563EB]" /> Linked Children ({childrenList.length})
                  </span>

                  {childrenList.length === 0 ? (
                    <p className="text-xs text-slate-500 italic p-3 bg-slate-50 rounded-lg border">
                      No linked children mapped to this account yet.
                    </p>
                  ) : (
                    <div className="space-y-2">
                      {childrenList.map((ch) => (
                        <div key={ch.id} className="p-4 bg-white border border-slate-200 rounded-xl flex items-center justify-between shadow-2xs">
                          <div>
                            <p className="font-bold text-slate-800 text-sm">{ch.user?.name || 'Child Learner'}</p>
                            <p className="text-xs text-slate-500">Level: <span className="capitalize font-semibold text-teal-700">{ch.learning_level}</span> | DOB: {ch.date_of_birth || 'N/A'}</p>
                          </div>
                          <span className="px-2.5 py-1 bg-emerald-50 text-emerald-700 border border-emerald-200 rounded-full text-xs font-semibold">
                            Authorized
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </>
            )}
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
