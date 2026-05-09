import React from 'react';
import { Terminal, Command } from 'lucide-react';

function SearchBar({ onSearch, query }) {
  return (
    <div className="relative group w-full font-mono">
      <div className="absolute inset-y-0 left-4 flex items-center pointer-events-none">
        <Terminal className="h-4 w-4 text-indigo-500/70 group-focus-within:text-indigo-400 transition-colors" />
        <span className="ml-2 text-indigo-500/50 group-focus-within:text-indigo-400/80 text-xs font-bold select-none">SEARCH_SIG_&gt;</span>
      </div>
      <input
        type="text"
        placeholder="ENTER_QUERY..."
        value={query}
        onChange={(e) => onSearch(e.target.value)}
        className="block w-full pl-36 pr-12 py-2.5 bg-black/40 border border-slate-800 rounded text-[11px] text-indigo-100 placeholder-slate-700 focus:outline-none focus:ring-1 focus:ring-indigo-500/30 focus:border-indigo-500/40 focus:bg-black/60 transition-all uppercase tracking-widest"
      />
      <div className="absolute inset-y-0 right-3 flex items-center pointer-events-none">
        <div className="flex items-center gap-1.5 px-2 py-1 rounded border border-slate-800 bg-slate-900 text-[9px] text-slate-500 font-bold uppercase tracking-tighter shadow-inner">
          <Command className="w-2.5 h-2.5" />
          <span>K</span>
        </div>
      </div>
      {/* Decorative focus glow */}
      <div className="absolute inset-0 -z-10 bg-indigo-500/5 blur-xl opacity-0 group-focus-within:opacity-100 transition-opacity rounded-full" />
    </div>
  );
}

export default SearchBar;
