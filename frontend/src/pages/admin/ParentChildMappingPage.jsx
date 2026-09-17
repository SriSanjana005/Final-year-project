import React, { useState, useEffect } from 'react';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Badge } from '../../components/ui/badge';
import { userService } from '../../services/userService';
import { Link2, Trash2, Plus, AlertCircle, Check } from 'lucide-react';

export function ParentChildMappingPage() {
  const [mappings, setMappings] = useState([]);
  const [parents, setParents] = useState([]);
  const [children, setChildren] = useState([]);
  const [loading, setLoading] = useState(true);

  // New mapping form state
  const [selectedParentId, setSelectedParentId] = useState("");
  const [selectedChildId, setSelectedChildId] = useState("");
  const [relationshipType, setRelationshipType] = useState("Parent");
  const [formError, setFormError] = useState("");
  const [successMsg, setSuccessMsg] = useState("");
  const [submitting, setSubmitting] = useState(false);

  const loadData = async () => {
    try {
      setLoading(true);
      const [mapData, parData, chData] = await Promise.all([
        userService.getMappings(),
        userService.getParents(),
        userService.getChildren()
      ]);
      setMappings(mapData);
      setParents(parData);
      setChildren(chData);
    } catch (err) {
      console.error("Failed to fetch mappings data:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleCreateMapping = async (e) => {
    e.preventDefault();
    setFormError("");
    setSuccessMsg("");

    if (!selectedParentId || !selectedChildId) {
      setFormError("Please select both a parent and a child.");
      return;
    }

    setSubmitting(true);
    try {
      await userService.createMapping(selectedParentId, selectedChildId, relationshipType);
      setSuccessMsg("Parent-Child relationship mapped successfully!");
      setSelectedParentId("");
      setSelectedChildId("");
      loadData();
    } catch (err) {
      const msg = err.response?.data?.detail || "Failed to create mapping.";
      setFormError(msg);
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteMapping = async (mappingId) => {
    if (!window.confirm("Are you sure you want to remove this parent-child relationship mapping?")) {
      return;
    }
    try {
      await userService.deleteMapping(mappingId);
      loadData();
    } catch (err) {
      alert("Failed to delete mapping: " + (err.response?.data?.detail || err.message));
    }
  };

  return (
    <AppLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-2">
            <Link2 className="text-[#2563EB]" /> Parent-Child Relationship Mappings
          </h1>
          <p className="text-sm text-slate-500">Create and manage authorized relationships between parents and children.</p>
        </div>

        {/* Create Mapping Form Card */}
        <Card className="border border-blue-200 bg-blue-50/20">
          <CardHeader>
            <CardTitle className="text-base flex items-center gap-2">
              <Plus size={18} className="text-[#2563EB]" /> Add New Parent-Child Relationship
            </CardTitle>
          </CardHeader>
          <CardContent>
            {formError && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-lg flex items-center gap-2">
                <AlertCircle size={16} /> {formError}
              </div>
            )}
            {successMsg && (
              <div className="mb-4 p-3 bg-teal-50 border border-teal-200 text-teal-700 text-xs rounded-lg flex items-center gap-2">
                <Check size={16} /> {successMsg}
              </div>
            )}

            <form onSubmit={handleCreateMapping} className="grid grid-cols-1 md:grid-cols-4 gap-4 items-end">
              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Select Parent Profile</label>
                <select 
                  value={selectedParentId}
                  onChange={(e) => setSelectedParentId(e.target.value)}
                  className="w-full h-10 px-3 border border-slate-300 rounded-lg text-xs bg-white focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">-- Choose Parent --</option>
                  {parents.map(p => (
                    <option key={p.id} value={p.id}>
                      {p.user?.name || `Parent #${p.id}`} ({p.user?.email})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Select Child Profile</label>
                <select 
                  value={selectedChildId}
                  onChange={(e) => setSelectedChildId(e.target.value)}
                  className="w-full h-10 px-3 border border-slate-300 rounded-lg text-xs bg-white focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">-- Choose Child --</option>
                  {children.map(c => (
                    <option key={c.id} value={c.id}>
                      {c.user?.name || `Child #${c.id}`} ({c.user?.email})
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-700 mb-1">Relationship Type</label>
                <input 
                  type="text"
                  value={relationshipType}
                  onChange={(e) => setRelationshipType(e.target.value)}
                  placeholder="e.g. Mother, Father, Guardian"
                  className="w-full h-10 px-3 border border-slate-300 rounded-lg text-xs bg-white focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <Button type="submit" variant="primary" className="h-10 text-xs font-semibold" disabled={submitting}>
                {submitting ? "Mapping..." : "Create Mapping"}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Existing Mappings List */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Active Parent-Child Mappings ({mappings.length})</CardTitle>
          </CardHeader>
          <CardContent>
            {loading ? (
              <div className="p-4 text-center text-xs text-slate-400">Loading mappings...</div>
            ) : mappings.length === 0 ? (
              <p className="text-xs text-slate-500 p-4 text-center">No active parent-child mappings found.</p>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead>
                    <tr className="border-b border-slate-200 text-slate-500 font-semibold">
                      <th className="pb-3 px-2">ID</th>
                      <th className="pb-3 px-2">Parent Name & Email</th>
                      <th className="pb-3 px-2">Child Name & Email</th>
                      <th className="pb-3 px-2">Relationship</th>
                      <th className="pb-3 px-2">Mapping Date</th>
                      <th className="pb-3 px-2 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {mappings.map((m) => (
                      <tr key={m.id} className="hover:bg-slate-50">
                        <td className="py-3 px-2 text-slate-400">#{m.id}</td>
                        <td className="py-3 px-2">
                          <p className="font-semibold text-slate-800">{m.parent?.user?.name || `Parent #${m.parent_id}`}</p>
                          <p className="text-[11px] text-slate-400">{m.parent?.user?.email}</p>
                        </td>
                        <td className="py-3 px-2">
                          <p className="font-semibold text-slate-800">{m.child?.user?.name || `Child #${m.child_id}`}</p>
                          <p className="text-[11px] text-slate-400">{m.child?.user?.email}</p>
                        </td>
                        <td className="py-3 px-2"><Badge variant="default">{m.relationship_type}</Badge></td>
                        <td className="py-3 px-2 text-slate-500">
                          {m.created_at ? new Date(m.created_at).toLocaleDateString() : 'N/A'}
                        </td>
                        <td className="py-3 px-2 text-right">
                          <Button 
                            variant="danger" 
                            size="sm" 
                            className="h-8 px-2 text-xs" 
                            onClick={() => handleDeleteMapping(m.id)}
                          >
                            <Trash2 size={14} /> Remove
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
    </AppLayout>
  );
}
