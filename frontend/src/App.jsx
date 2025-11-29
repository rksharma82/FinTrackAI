import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LayoutDashboard, PieChart, Wallet } from 'lucide-react';
import FileUpload from './components/FileUpload';
import TransactionTable from './components/TransactionTable';
import ChatInterface from './components/ChatInterface';
import CategoryManager from './components/CategoryManager';

// Configure axios base URL for development
// In production, this would be handled by Nginx or similar
axios.defaults.baseURL = 'http://localhost:8000';

function App() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchTransactions = async () => {
    try {
      const response = await axios.get('/transactions');
      setTransactions(response.data);
    } catch (error) {
      console.error("Error fetching transactions:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTransactions();
  }, []);

  return (
    <div className="min-h-screen bg-slate-50 font-sans text-slate-900">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="bg-blue-600 p-2 rounded-lg text-white">
              <Wallet size={24} />
            </div>
            <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600">
              FinTrackAI
            </h1>
          </div>
          <nav className="flex gap-6 text-sm font-medium text-slate-600">
            <a href="#" className="hover:text-blue-600 transition-colors">Dashboard</a>
            <a href="#" className="hover:text-blue-600 transition-colors">Transactions</a>
            <a href="#" className="hover:text-blue-600 transition-colors">Reports</a>
          </nav>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Left Column: Main Content */}
          <div className="lg:col-span-2 space-y-8">
            <section>
              <h2 className="text-lg font-semibold text-slate-800 mb-4">Upload Statement</h2>
              <FileUpload onUploadSuccess={fetchTransactions} />
            </section>

            <section>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-slate-800">Recent Transactions</h2>
                <button
                  onClick={fetchTransactions}
                  className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                >
                  Refresh
                </button>
              </div>
              {loading ? (
                <div className="text-center py-12 text-slate-500">Loading...</div>
              ) : (
                <TransactionTable transactions={transactions} />
              )}
            </section>
          </div>

          {/* Right Column: Sidebar */}
          <div className="space-y-8">
            <section>
              <ChatInterface />
            </section>

            <section>
              <CategoryManager />
            </section>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
