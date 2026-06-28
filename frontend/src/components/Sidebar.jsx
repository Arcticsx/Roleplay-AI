import React, { useState, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';

function Sidebar({ activeView, onViewChange, onCreateClick }) {
  const [width, setWidth] = useState(224);
  const navigate = useNavigate();

  const handleMouseDown = useCallback((e) => {
    e.preventDefault();
    const startX = e.clientX;
    const startWidth = width;

    const onMouseMove = (e) => {
      const newWidth = Math.min(400, Math.max(160, startWidth + e.clientX - startX));
      setWidth(newWidth);
    };

    const onMouseUp = () => {
      document.removeEventListener('mousemove', onMouseMove);
      document.removeEventListener('mouseup', onMouseUp);
    };

    document.addEventListener('mousemove', onMouseMove);
    document.addEventListener('mouseup', onMouseUp);
  }, [width]);

  const items = [
    { key: 'create', label: 'Create', icon: <span className="material-symbols-outlined">add</span> },
    { key: 'discover', label: 'Discover', icon: <span className="material-symbols-outlined">explore</span> },
    { key: 'feed', label: 'Feed', icon: <span className="material-symbols-outlined">rss_feed</span> },
  ];

  return (
    <aside
      style={{ width: `${width}px` }}
      className="relative flex shrink-0 flex-col border-r border-border/70 bg-surface/80 px-0 py-5 backdrop-blur-xl"
    >
      {/* SARP logo*/}
      <div 
        onClick={() => navigate('/')}
        className="group relative px-10 pb-6 text-center cursor-pointer transition-all duration-300 hover:scale-105"
      >
        {/* background glow */}
        <div className="absolute inset-0 -z-10 opacity-0 group-hover:opacity-100 transition-opacity duration-500">
          <div className="absolute inset-0 bg-accent/20 blur-2xl rounded-full"></div>
        </div>
        
        <div className="relative inline-block">
          <span className="text-3xl font-bold tracking-tight text-text/90 hover:text-text transition-colors duration-300">
            SARP.
          </span>
          
          {/* dot */}
          <span className="absolute -bottom-1 -right-1 h-2 w-12 bg-accent rounded-full animate-pulse"></span>
          
        </div>
      </div>

      <nav className="flex flex-1 flex-col gap-1 px-3">
        {items.map((item) => {
          const isActive = activeView === item.key;
          return (
            <button
              key={item.key}
              className={`relative flex items-center gap-3 rounded-xl px-3 py-2.5 text-left text-sm font-medium transition-all duration-200 ${
                isActive 
                  ? 'bg-accent/10 text-accent shadow-[inset_0_1px_0_rgba(255,255,255,0.1)]' 
                  : 'text-muted hover:bg-white/5 hover:text-white'
              }`}
              onClick={item.key === 'create' ? onCreateClick : () => onViewChange(item.key)}
            >
              {/* Active indicator bar */}
              {isActive && (
                <div className="absolute left-0 top-1/2 -translate-y-1/2 h-6 w-0.5 bg-accent rounded-r-full shadow-[0_0_10px_rgba(99,102,241,0.5)]"></div>
              )}
              
              <span className={`flex h-5 w-5 items-center justify-center transition-transform duration-200 ${
                isActive ? 'scale-110' : ''
              }`}>
                {item.icon}
              </span>
              <span className="leading-none">{item.label}</span>
              
              {/* Hover effect */}
              <div className="absolute inset-0 rounded-xl overflow-hidden pointer-events-none">
                <div className="absolute inset-0 opacity-0 group-hover:opacity-100 bg-white/5 transition-opacity duration-300"></div>
              </div>
            </button>
          );
        })}
      </nav>

      {/* Drag handle*/}
      <div
        onMouseDown={handleMouseDown}
        className="absolute right-0 top-0 h-full w-1 cursor-col-resize group"
      >
        <div className="absolute inset-0 bg-transparent group-hover:bg-accent/30 transition-colors duration-300"></div>
        <div className="absolute inset-y-0 -left-1 w-3 bg-transparent"></div>
        
        {/* Drag handle dots */}
        <div className="absolute top-1/2 -translate-y-1/2 right-[-2px] flex flex-col gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-300">
          <div className="w-1 h-1 rounded-full bg-accent/60"></div>
          <div className="w-1 h-1 rounded-full bg-accent/60"></div>
          <div className="w-1 h-1 rounded-full bg-accent/60"></div>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;