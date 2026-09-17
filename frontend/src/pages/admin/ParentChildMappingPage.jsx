import React from 'react';
import { AppLayout } from '../../components/layout/AppLayout';
import { Card, CardHeader, CardTitle, CardContent } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Link2 } from 'lucide-react';

export function ParentChildMappingPage() {
  return (
    <AppLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Parent-Child Mapping</h1>
            <p className="text-sm text-slate-500">Link parent accounts to their respective children.</p>
          </div>
          <Button variant="primary" className="gap-2"><Link2 size={16}/> Create New Mapping</Button>
        </div>

        <Card>
          <CardHeader><CardTitle className="text-base">Active Parent-Child Links</CardTitle></CardHeader>
          <CardContent>
            <div className="p-4 bg-slate-50 rounded-lg border border-slate-200 flex justify-between items-center text-sm">
              <div>
                <p className="font-bold text-slate-800">Parent: Sarah Smith</p>
                <p className="text-xs text-slate-500">Child: Leo Smith (Age 8)</p>
              </div>
              <Button variant="outline" size="sm">Remove Link</Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </AppLayout>
  );
}
