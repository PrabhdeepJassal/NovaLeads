// ============================================================
// NovaLeads — Register Page
// ============================================================

import { useState, useEffect, FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Target, User, Mail, Lock, Building2, Eye, EyeOff, Loader2 } from 'lucide-react';

export default function RegisterPage() {
  const { user, register, loading, error, clearError } = useAuth();
  const navigate = useNavigate();

  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [companyName, setCompanyName] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [formErrors, setFormErrors] = useState<Record<string, string>>({});

  // Redirect after successful registration
  useEffect(() => {
    if (user) {
      if (user.role === 'admin') {
        navigate('/admin', { replace: true });
      } else {
        navigate('/dashboard', { replace: true });
      }
    }
  }, [user, navigate]);

  const validate = () => {
    const errs: Record<string, string> = {};
    if (!name.trim()) errs.name = 'Name is required';
    if (!email.trim()) errs.email = 'Email is required';
    else if (!/\S+@\S+\.\S+/.test(email)) errs.email = 'Invalid email';
    if (!password) errs.password = 'Password is required';
    else if (password.length < 8) errs.password = 'Password must be at least 8 characters';
    if (!companyName.trim()) errs.company_name = 'Company name is required';
    setFormErrors(errs);
    return Object.keys(errs).length === 0;
  };

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    clearError();
    if (!validate()) return;

    try {
      await register({
        name: name.trim(),
        email: email.trim(),
        password,
        company_name: companyName.trim(),
      });
      // Auto-login: user state is set by AuthContext, useEffect will redirect
    } catch {
      // Error handled in context
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-primary-50 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Branding */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br from-primary-500 to-primary-700 shadow-lg shadow-primary-200 mb-4">
            <Target className="w-7 h-7 text-white" />
          </div>
          <h1 className="text-2xl font-bold text-gray-900">
            Nova<span className="text-primary-600">Leads</span>
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            AI-Powered Lead Conversion Prediction
          </p>
        </div>

        <div className="bg-white rounded-2xl shadow-xl border border-gray-100 p-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-1">Create your account</h2>
          <p className="text-sm text-gray-500 mb-6">Join NovaLeads and start tracking your leads.</p>

          {error && (
            <div className="mb-4 p-3 rounded-lg bg-cold-50 border border-cold-200 text-sm text-cold-700 animate-fade-in">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Name */}
            <div>
              <label className="input-label">
                <User className="w-3.5 h-3.5 inline mr-1.5 text-gray-400" />
                Full Name
              </label>
              <input
                className={`input-field ${formErrors.name ? 'border-cold-500' : ''}`}
                placeholder="John Doe"
                value={name}
                onChange={(e) => { setName(e.target.value); setFormErrors((p) => ({ ...p, name: '' })); }}
                autoFocus
              />
              {formErrors.name && <p className="input-error">{formErrors.name}</p>}
            </div>

            {/* Email */}
            <div>
              <label className="input-label">
                <Mail className="w-3.5 h-3.5 inline mr-1.5 text-gray-400" />
                Email Address
              </label>
              <input
                type="email"
                className={`input-field ${formErrors.email ? 'border-cold-500' : ''}`}
                placeholder="you@company.com"
                value={email}
                onChange={(e) => { setEmail(e.target.value); setFormErrors((p) => ({ ...p, email: '' })); }}
              />
              {formErrors.email && <p className="input-error">{formErrors.email}</p>}
            </div>

            {/* Password */}
            <div>
              <label className="input-label">
                <Lock className="w-3.5 h-3.5 inline mr-1.5 text-gray-400" />
                Password
              </label>
              <div className="relative">
                <input
                  type={showPassword ? 'text' : 'password'}
                  className={`input-field pr-10 ${formErrors.password ? 'border-cold-500' : ''}`}
                  placeholder="Minimum 8 characters"
                  value={password}
                  onChange={(e) => { setPassword(e.target.value); setFormErrors((p) => ({ ...p, password: '' })); }}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
              {formErrors.password && <p className="input-error">{formErrors.password}</p>}
            </div>

            {/* Company Name */}
            <div>
              <label className="input-label">
                <Building2 className="w-3.5 h-3.5 inline mr-1.5 text-gray-400" />
                Company Name
              </label>
              <input
                className={`input-field ${formErrors.company_name ? 'border-cold-500' : ''}`}
                placeholder="Acme Corp"
                value={companyName}
                onChange={(e) => { setCompanyName(e.target.value); setFormErrors((p) => ({ ...p, company_name: '' })); }}
              />
              {formErrors.company_name && <p className="input-error">{formErrors.company_name}</p>}
            </div>

            <button type="submit" className="btn-primary w-full" disabled={loading}>
              {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : null}
              {loading ? 'Creating account...' : 'Create Account'}
            </button>
          </form>

          <p className="text-center text-sm text-gray-500 mt-6">
            Already have an account?{' '}
            <Link to="/login" className="font-semibold text-primary-600 hover:text-primary-700 transition-colors">
              Sign in
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}
