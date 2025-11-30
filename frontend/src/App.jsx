import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { LayoutDashboard, Settings, Upload, CreditCard, RefreshCw, MessageSquare } from 'lucide-react';
import FileUpload from './components/FileUpload';
import TransactionTable from './components/TransactionTable';
import ChatInterface from './components/ChatInterface';
import CategoryManager from './components/CategoryManager';
import TransferReview from './components/TransferReview';

// Configure axios base URL for development
// In production, this would be handled by Nginx or similar
axios.defaults.baseURL = 'http://localhost:8000';

function App() {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(false);
  const [llmMode, setLlmMode] = useState("LOADING...");

  // Filter State
  const [startDate, setStartDate] = useState("");
  const [endDate, setEndDate] = useState("");
  const [vendorFilter, setVendorFilter] = useState("");
  const [categoryFilter, setCategoryFilter] = useState("");

  const categories = [
    "Food", "Transport", "Utilities", "Salary", "Entertainment", "Shopping", "Health", "Other"
  ];

  useEffect(() => {
    fetchConfig();
    fetchTransactions();
  }, []);

  const fetchConfig = async () => {
    try {
      const response = await axios.get('/config');
      setLlmMode(response.data.llm_type);
    } catch (error) {
      console.error("Error fetching config:", error);
      setLlmMode("UNKNOWN");
    }
  };

  const fetchTransactions = async () => {
    setLoading(true);
    try {
      const params = {};
      if (startDate) params.start_date = startDate;
      if (endDate) params.end_date = endDate;
      if (vendorFilter) params.vendor = vendorFilter;
      if (categoryFilter) params.category = categoryFilter;

      const response = await axios.get('/transactions', { params });
      setTransactions(response.data);
    } catch (error) {
      console.error("Error fetching transactions:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleUploadSuccess = () => {
    fetchTransactions();
  };

  const handleApplyFilters = () => {
    fetchTransactions();
  };

  const handleClearData = async () => {
    if (window.confirm("Are you sure you want to delete ALL transactions? This action cannot be undone.")) {
      try {
        await axios.delete('/transactions');
        fetchTransactions();
      } catch (error) {
        console.error("Error clearing data:", error);
        alert("Failed to clear data.");
      }
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 text-gray-900 font-sans">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <div className="bg-blue-600 p-2 rounded-lg">
              <LayoutDashboard className="w-6 h-6 text-white" />
            </div>
            <h1 className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-indigo-600">
              FinTrackAI
            </h1>
          </div>
          <div className="flex items-center gap-4">
            <div className="px-3 py-1 bg-gray-100 rounded-full text-xs font-medium text-gray-600 border border-gray-200">
              Running on: <span className="text-blue-600">{llmMode}</span>
            </div>
            <button
              onClick={handleClearData}
              className="px-3 py-1 bg-red-50 hover:bg-red-100 text-red-600 rounded-full text-xs font-medium border border-red-200 transition-colors"
              title="Clear All Data"
            >
              Clear Data
            </button>
            <button className="p-2 hover:bg-gray-100 rounded-full transition-colors">
              <Settings className="w-5 h-5 text-gray-500" />
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">

          {/* Left Column: Upload & Transactions */}
          <div className="lg:col-span-2 space-y-8">

            {/* Upload Section */}
            <section>
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Upload className="w-5 h-5 text-blue-500" />
                Import Data
              </h2>
              <FileUpload onUploadSuccess={handleUploadSuccess} />
            </section>

            {/* Transactions Section */}
            <section>
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold flex items-center gap-2">
                  <CreditCard className="w-5 h-5 text-green-500" />
                  Recent Transactions
                </h2>
                <button
                  onClick={fetchTransactions}
                  className="p-2 hover:bg-gray-200 rounded-full transition-colors"
                  title="Refresh"
                >
                  <RefreshCw className={`w-4 h-4 text-gray-500 ${loading ? 'animate-spin' : ''}`} />
                </button>
              </div>

              {/* Filter Bar */}
              <div className="bg-white p-4 rounded-xl shadow-sm border border-gray-100 mb-4 grid grid-cols-1 md:grid-cols-5 gap-4 items-end">
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">Start Date</label>
                  <input
                    type="date"
                    className="w-full text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">End Date</label>
                  <input
                    type="date"
                    className="w-full text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">Vendor</label>
                  <input
                    type="text"
                    placeholder="e.g. Uber"
                    className="w-full text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    value={vendorFilter}
                    onChange={(e) => setVendorFilter(e.target.value)}
                  />
                </div>
                <div>
                  <label className="block text-xs font-medium text-gray-500 mb-1">Category</label>
                  <select
                    className="w-full text-sm border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                    value={categoryFilter}
                    onChange={(e) => setCategoryFilter(e.target.value)}
                  >
                    <option value="">All Categories</option>
                    {categories.map(cat => (
                      <option key={cat} value={cat}>{cat}</option>
                    ))}
                  </select>
                </div>
                <button
                  onClick={handleApplyFilters}
                  className="bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium py-2 px-4 rounded-md transition-colors"
                >
                  Apply Filters
                </button>
              </div>

              <TransactionTable transactions={transactions} loading={loading} />
            </section>
          </div>

          {/* Right Column: Chat & Insights */}
          <div className="lg:col-span-1 space-y-8">
            <section className="sticky top-24">
              <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <MessageSquare className="w-5 h-5 text-purple-500" />
                AI Assistant
              </h2>
              <ChatInterface />

              <div className="mt-8">
                <CategoryManager />
              </div>

              <div className="mt-8">
                <TransferReview />
              </div>
            </section>
          </div>

        </div>
      </main>
    </div>
  );
}

export default App;
