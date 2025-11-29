import React from 'react';

const TransactionTable = ({ transactions }) => {
    if (!transactions || transactions.length === 0) {
        return (
            <div className="text-center py-12 text-slate-500 bg-white rounded-xl shadow-sm border border-slate-100">
                <p>No transactions found. Upload a statement to get started.</p>
            </div>
        );
    }

    return (
        <div className="bg-white rounded-xl shadow-sm border border-slate-100 overflow-hidden">
            <div className="overflow-x-auto">
                <table className="w-full text-left text-sm">
                    <thead className="bg-slate-50 text-slate-600 font-medium border-b border-slate-100">
                        <tr>
                            <th className="px-6 py-4">Date</th>
                            <th className="px-6 py-4">Description</th>
                            <th className="px-6 py-4">Category</th>
                            <th className="px-6 py-4 text-right">Amount</th>
                        </tr>
                    </thead>
                    <tbody className="divide-y divide-slate-100">
                        {transactions.map((txn, index) => (
                            <tr key={txn._id || index} className="hover:bg-slate-50 transition-colors">
                                <td className="px-6 py-4 text-slate-600 whitespace-nowrap">{txn.date}</td>
                                <td className="px-6 py-4 text-slate-900 font-medium">{txn.description}</td>
                                <td className="px-6 py-4">
                                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-50 text-blue-700">
                                        {txn.category}
                                    </span>
                                </td>
                                <td className={`px-6 py-4 text-right font-medium ${txn.type === 'income' || txn.amount > 0 ? 'text-green-600' : 'text-slate-900'
                                    }`}>
                                    {txn.amount < 0 ? '-' : ''}${Math.abs(txn.amount).toFixed(2)}
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
};

export default TransactionTable;
