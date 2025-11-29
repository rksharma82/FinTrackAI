import React from 'react';
import { Settings } from 'lucide-react';

const CategoryManager = () => {
    return (
        <div className="bg-white rounded-xl shadow-sm border border-slate-100 p-6">
            <div className="flex items-center gap-2 mb-4 text-slate-800">
                <Settings size={20} className="text-slate-400" />
                <h3 className="font-semibold">Categories</h3>
            </div>
            <p className="text-sm text-slate-500">
                Category management will be available in the next update.
                For now, categories are automatically assigned by the AI.
            </p>
        </div>
    );
};

export default CategoryManager;
