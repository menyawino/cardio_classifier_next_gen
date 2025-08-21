import React, { useState } from 'react';
import { login, register } from '../lib/auth';

interface Props {
  onAuth: (token: string) => void;
}

export const AuthPanel: React.FC<Props> = ({ onAuth }) => {
  const [mode, setMode] = useState<'login' | 'register'>('login');
  const [email, setEmail] = useState('tester@example.com');
  const [password, setPassword] = useState('secret123');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const submit = async () => {
    setLoading(true); setError(null);
    try {
      const fn = mode === 'login' ? login : register;
      const res = await fn(email, password);
      onAuth(res.access_token);
    } catch (e: any) {
      setError(e?.response?.data?.detail || 'Auth failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="border rounded p-4 space-y-3">
      <div className="flex justify-between items-center">
        <h2 className="font-semibold text-lg">{mode === 'login' ? 'Login' : 'Register'}</h2>
        <button className="text-sm text-blue-600" onClick={()=>setMode(mode==='login'?'register':'login')}>
          {mode === 'login' ? 'Need an account?' : 'Have an account?'}
        </button>
      </div>
      <input className="border rounded px-3 py-2 w-full" placeholder="Email" value={email} onChange={e=>setEmail(e.target.value)} />
      <input className="border rounded px-3 py-2 w-full" placeholder="Password" type="password" value={password} onChange={e=>setPassword(e.target.value)} />
      <button disabled={loading} onClick={submit} className="bg-blue-600 text-white px-4 py-2 rounded w-full disabled:opacity-50">{loading? '...' : (mode==='login'?'Login':'Register')}</button>
      {error && <p className="text-red-600 text-sm">{error}</p>}
    </div>
  );
};
