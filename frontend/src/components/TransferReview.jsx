import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { ArrowRight, Link, Unlink } from 'lucide-react';

const TransferReview = () => {
    const [transfers, setTransfers] = useState([]);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchTransfers();
    }, []);

    const fetchTransfers = async () => {
        setLoading(true);
        try {
            // Fetch all transactions and filter for transfers client-side for now
            // Ideally backend should have a specific endpoint
            const response = await axios.get('/transactions');
            const allTxns = response.data;
            const transferTxns = allTxns.filter(t => t.is_transfer && t.linked_tx_id);

            // Group pairs
            const pairs = [];
            const processed = new Set();

            transferTxns.forEach(t => {
                if (processed.has(t._id)) return;

                const partner = transferTxns.find(p => p._id === t.linked_tx_id);
                if (partner) {
                    pairs.push({ source: t, target: partner });
                    processed.add(t._id);
                    processed.add(partner._id);
                }
            });

            setTransfers(pairs);
        } catch (error) {
            console.error("Error fetching transfers:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleUnlink = async (txId) => {
        try {
            await axios.post('/transfers/unlink', { tx_id: txId });
            fetchTransfers(); // Refresh
        } catch (error) {
            console.error("Error unlinking:", error);
            alert("Failed to unlink transactions");
        }
    };

    if (loading) return <div className="text-center py-4 text-gray-500">Loading transfers...</div>;

    return (
        <div className="bg-white rounded-xl shadow-sm border border-gray-100 p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Link className="w-5 h-5 text-blue-500" />
                Transfer Review
            </h2>

            {transfers.length === 0 ? (
                <p className="text-gray-500 text-sm">No linked transfers found.</p>
            ) : (
                <div className="space-y-4">
                    {transfers.map((pair, idx) => (
                        <div key={idx} className="flex items-center justify-between p-4 bg-gray-50 rounded-lg border border-gray-200">
                            {/* Source (Debit) */}
                            <div className="flex-1">
                                <div className="text-sm font-medium text-gray-900">{pair.source.account_name || "Unknown Account"}</div>
                                <div className="text-xs text-gray-500">{pair.source.date}</div>
                                <div className="text-sm text-red-600 font-mono">
                                    {pair.source.amount < 0 ? pair.source.amount : pair.target.amount}
                                </div>
                            </div>

                            {/* Visual Connector */}
                            <div className="flex flex-col items-center px-4">
                                <div className="text-xs text-gray-400 mb-1">Transfer</div>
                                <ArrowRight className="w-5 h-5 text-blue-400" />
                            </div>

                            {/* Target (Credit) */}
                            <div className="flex-1 text-right">
                                <div className="text-sm font-medium text-gray-900">{pair.target.account_name || "Unknown Account"}</div>
                                <div className="text-xs text-gray-500">{pair.target.date}</div>
                                <div className="text-sm text-green-600 font-mono">
                                    {pair.source.amount > 0 ? pair.source.amount : pair.target.amount}
                                </div>
                            </div>

                            {/* Action */}
                            <div className="ml-4 pl-4 border-l border-gray-200">
                                <button
                                    onClick={() => handleUnlink(pair.source._id)}
                                    className="p-2 text-gray-400 hover:text-red-500 transition-colors"
                                    title="Unlink"
                                >
                                    <Unlink className="w-4 h-4" />
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default TransferReview;
