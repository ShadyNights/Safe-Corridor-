import React from 'react';

const LogStream = ({ logs }) => {
    return (
        <div className="h-full bg-slate-900 rounded-lg border border-slate-700 flex flex-col">
            <div className="p-3 border-b border-slate-700">
                <h3 className="text-slate-300 font-semibold">Activity Log</h3>
            </div>
            <div className="flex-1 overflow-y-auto p-3 space-y-2">
                {logs.length === 0 && (
                    <p className="text-slate-500 text-sm text-center italic">No activity yet...</p>
                )}
                {logs.map((log, i) => (
                    <div key={i} className="text-sm border-l-2 border-slate-600 pl-2 py-1">
                        <span className="text-xs text-slate-500 block">{log.time}</span>
                        <span className={`font-medium ${log.type === 'RISK_UP' ? 'text-red-400' : 'text-slate-300'}`}>
                            {log.message}
                        </span>
                    </div>
                ))}
            </div>
        </div>
    );
};

export default LogStream;
