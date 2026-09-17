import React, { useState, useEffect } from 'react';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../../components/ui/card';
import { Badge } from '../../components/ui/badge';
import { userService } from '../../services/userService';
import { progressService } from '../../services/progressService';
import { Loader2, Calendar, Clock, CheckCircle } from 'lucide-react';

export function ChildLearningHistoryPage() {
  const [children, setChildren] = useState([]);
  const [selectedChildId, setSelectedChildId] = useState("");
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [fetchingHistory, setFetchingHistory] = useState(false);

  useEffect(() => {
    const fetchChildren = async () => {
      try {
        const data = await userService.getParentChildren();
        setChildren(data);
        if (data.length > 0) {
          setSelectedChildId(data[0].id.toString());
        }
      } catch (err) {
        console.error("Failed to load children:", err);
      } finally {
        setLoading(false);
      }
    };
    fetchChildren();
  }, []);

  useEffect(() => {
    if (!selectedChildId) return;
    const fetchHistoryData = async () => {
      setFetchingHistory(true);
      try {
        const data = await progressService.getChildHistory(selectedChildId);
        setHistory(data);
      } catch (err) {
        console.error("Failed to load child history:", err);
      } finally {
        setFetchingHistory(false);
      }
    };
    fetchHistoryData();
  }, [selectedChildId]);

  const selectedChildObj = children.find(c => c.id.toString() === selectedChildId);

  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 bg-white p-6 rounded-xl border border-slate-200 shadow-2xs">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Child Learning Activity History</h1>
            <p className="text-sm text-slate-500">Timeline of recorded learning interactions and recommendations.</p>
          </div>

          <div className="flex items-center gap-3">
            <span className="text-xs font-semibold text-slate-500">Select Child:</span>
            {loading ? (
              <span className="text-xs text-slate-400">Loading...</span>
            ) : children.length === 0 ? (
              <span className="text-xs text-amber-600 font-semibold bg-amber-50 px-2 py-1 rounded">No linked children</span>
            ) : (
              <select 
                value={selectedChildId} 
                onChange={(e) => setSelectedChildId(e.target.value)}
                className="h-10 px-3 bg-slate-50 border border-slate-300 rounded-lg text-sm font-semibold text-slate-800 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                {children.map(c => (
                  <option key={c.id} value={c.id}>
                    {c.user?.name || `Child #${c.id}`} ({c.learning_level})
                  </option>
                ))}
              </select>
            )}
          </div>
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-base">Interaction Sequence Timeline</CardTitle>
            <CardDescription>Chronological sequence for {selectedChildObj?.user?.name || 'Selected Child'}</CardDescription>
          </CardHeader>
          <CardContent>
            {fetchingHistory ? (
              <div className="flex justify-center items-center py-12">
                <Loader2 className="animate-spin text-blue-600" size={32} />
              </div>
            ) : history.length === 0 ? (
              <div className="text-center py-12 text-slate-500 text-sm">
                No activity history logged for this child yet.
              </div>
            ) : (
              <div className="space-y-3">
                {history.map((item) => (
                  <div key={item.id} className="p-4 bg-slate-50 border border-slate-200 rounded-xl flex items-center justify-between text-sm">
                    <div className="space-y-1">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-slate-900 capitalize">{item.activity_type}</span>
                        {item.topic_name && (
                          <span className="text-xs font-semibold bg-blue-100 text-blue-800 px-2 py-0.5 rounded">
                            {item.topic_name}
                          </span>
                        )}
                        <span className="text-xs text-slate-500 capitalize">({item.difficulty || 'beginner'})</span>
                      </div>
                      <div className="flex items-center gap-4 text-xs text-slate-500">
                        <span className="flex items-center gap-1">
                          <Calendar size={12} /> {new Date(item.timestamp).toLocaleString()}
                        </span>
                        {item.time_spent && (
                          <span className="flex items-center gap-1">
                            <Clock size={12} /> {Math.round(item.time_spent / 60)} mins
                          </span>
                        )}
                      </div>
                    </div>
                    <div>
                      {item.score !== null && item.score !== undefined ? (
                        <Badge variant="success" className="text-sm font-bold px-3 py-1">
                          Score: {Math.round(item.score)}%
                        </Badge>
                      ) : (
                        <Badge variant="default">{item.completion_status}</Badge>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}

