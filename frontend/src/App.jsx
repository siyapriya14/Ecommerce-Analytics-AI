import React, { useEffect, useState } from 'react';
import { TrendingUp, ShoppingBag, DollarSign, Cpu, BarChart3, ShieldCheck, PlusCircle, CheckCircle2, Download, LogOut, Lock } from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';

export default function App() {
  const [token, setToken] = useState(localStorage.getItem('jwt_token') || null);
  const [isSignup, setIsSignup] = useState(false);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  
  const [analytics, setAnalytics] = useState(null);
  const [quantity, setQuantity] = useState('');
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);

  const [newCategory, setNewCategory] = useState('Electronics');
  const [newSales, setNewSales] = useState('');
  const [submittingOrder, setSubmittingOrder] = useState(false);
  const [successMsg, setSuccessMsg] = useState(false);

  const fetchAnalytics = async () => {
    try {
      const res = await fetch('/api/analytics');
      const data = await res.json();
      setAnalytics(data);
    } catch (err) {
      console.error("Error fetching analytics", err);
    }
  };

  useEffect(() => {
    if (token) fetchAnalytics();
  }, [token]);

  const handleAuth = async (e) => {
    e.preventDefault();
    const endpoint = isSignup ? '/api/signup' : '/api/login';
    const payload = isSignup ? { email: username, password } : { username, password };
    try {
      const res = await fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });
      const data = await res.json();
      if (!res.ok) {
        const msg = typeof data.detail === 'object' ? JSON.stringify(data.detail) : (data.detail || "Auth failed");
        throw new Error(msg);
      }
      
      if (!isSignup) {
        localStorage.setItem('jwt_token', data.token || data.access_token);
        setToken(data.token || data.access_token);
      } else {
        alert("Signup successful! Please login.");
        setIsSignup(false);
      }
    } catch (err) {
      alert(err.message);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('jwt_token');
    setToken(null);
  };

  const handlePredict = async (e) => {
    e.preventDefault();
    if (!quantity) return;
    setLoading(true);
    try {
      const res = await fetch(`/api/predict/${quantity}`);
      const data = await res.json();
      setPrediction(data.predicted_revenue);
    } finally {
      setLoading(false);
    }
  };

  const handleAddOrder = async (e) => {
    e.preventDefault();
    if (!newSales) return;
    setSubmittingOrder(true);

    try {
      const res = await fetch('/api/orders', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ category: newCategory, sales: Number(newSales) })
      });
      await res.json();
      setNewSales('');
      setSuccessMsg(true);
      setTimeout(() => setSuccessMsg(false), 3500);
      fetchAnalytics();
    } finally {
      setSubmittingOrder(false);
    }
  };

  if (!token) {
    return (
      <div className="min-h-screen bg-slate-950 flex items-center justify-center p-6 text-slate-100">
        <div className="bg-slate-900 border border-slate-800 p-8 rounded-2xl shadow-2xl w-full max-w-md">
          <div className="flex items-center gap-2 mb-6">
            <Lock className="w-6 h-6 text-indigo-500" />
            <h2 className="text-2xl font-bold">{isSignup ? "Enterprise Signup" : "Enterprise Login"}</h2>
          </div>
          <form onSubmit={handleAuth} className="space-y-4">
            <input 
              type="text" placeholder="Username / Email" value={username} onChange={e => setUsername(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-white focus:border-indigo-500 outline-none" required
            />
            <input 
              type="password" placeholder="Password" value={password} onChange={e => setPassword(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-3 text-white focus:border-indigo-500 outline-none" required
            />
            <button type="submit" className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-medium py-3 rounded-xl transition cursor-pointer">
              {isSignup ? "Create Account" : "Access BI Dashboard"}
            </button>
          </form>
          <button onClick={() => setIsSignup(!isSignup)} className="mt-4 text-xs text-slate-400 hover:text-indigo-400 w-full text-center">
            {isSignup ? "Already have an account? Login" : "Need an account? Signup"}
          </button>
        </div>
      </div>
    );
  }

  const categoryChartData = analytics && analytics.categories ? analytics.categories.map(cat => ({ name: cat.name, sales: cat.sales })) : [];

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans p-6 md:p-10">
      <header className="max-w-7xl mx-auto mb-10 flex flex-col md:flex-row justify-between items-center border-b border-slate-800 pb-5">
        <div>
          <div className="flex items-center gap-2">
            <span className="bg-indigo-600 text-white text-xs px-2.5 py-1 rounded-md font-semibold uppercase">Enterprise Suite</span>
            <span className="text-slate-400 text-xs">v3.0 Production Ready</span>
          </div>
          <h1 className="text-3xl font-extrabold tracking-tight mt-2 text-white">
            E-Commerce Business Intelligence & Predictive Analytics
          </h1>
          <p className="text-slate-400 text-sm mt-1">Powered by FastAPI, SQLite, Scikit-Learn Joblib & React</p>
        </div>
        <div className="flex items-center gap-3 mt-4 md:mt-0">
          <a href="/api/export" target="_blank" rel="noreferrer" className="bg-slate-900 hover:bg-slate-800 border border-slate-800 px-4 py-2 rounded-xl text-xs text-emerald-400 font-medium flex items-center gap-2 shadow-sm">
            <Download className="w-4 h-4" /> Export Report
          </a>
          <button onClick={handleLogout} className="bg-red-500/10 hover:bg-red-500/20 border border-red-500/30 px-3 py-2 rounded-xl text-xs text-red-400 font-medium flex items-center gap-2">
            <LogOut className="w-4 h-4" /> Logout
          </button>
        </div>
      </header>

      <main className="max-w-7xl mx-auto space-y-8">
        {analytics ? (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl shadow-xl">
              <span className="text-slate-400 text-sm font-medium">Total Revenue</span>
              <h2 className="text-3xl font-extrabold mt-3 text-white">₹{analytics.total_sales.toLocaleString()}</h2>
            </div>
            <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl shadow-xl">
              <span className="text-slate-400 text-sm font-medium">Monthly Growth</span>
              <h2 className="text-3xl font-extrabold mt-3 text-emerald-400">{analytics.monthly_growth}</h2>
            </div>
            <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl shadow-xl">
              <span className="text-slate-400 text-sm font-medium">Active Orders Tracked</span>
              <h2 className="text-3xl font-extrabold mt-3 text-white">{analytics.active_orders}</h2>
            </div>
          </div>
        ) : (
          <div className="text-center py-10 text-slate-400">Loading metrics...</div>
        )}

        {analytics && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
            <div className="bg-slate-900/80 border border-slate-800 p-6 rounded-2xl shadow-xl">
              <h3 className="text-lg font-semibold text-white mb-4">Category Revenue Distribution</h3>
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={categoryChartData}>
                    <XAxis dataKey="name" stroke="#64748b" />
                    <YAxis stroke="#64748b" />
                    <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155' }} />
                    <Bar dataKey="sales" fill="#6366f1" radius={[6, 6, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>
          </div>
        )}
      </main>
    </div>
  );
}