import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const RiskChart = ({ data }) => {
    return (
        <div className="h-64 w-full bg-slate-900 p-4 rounded-lg border border-slate-700">
            <h3 className="text-slate-300 font-semibold mb-2">Risk Timeline</h3>
            <ResponsiveContainer width="100%" height="100%">
                <LineChart data={data}>
                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                    <XAxis dataKey="time" stroke="#94a3b8" />
                    <YAxis domain={[0, 100]} stroke="#94a3b8" />
                    <Tooltip
                        contentStyle={{ backgroundColor: '#1e293b', border: 'none' }}
                        itemStyle={{ color: '#f8fafc' }}
                    />
                    <Line type="monotone" dataKey="riskScore" stroke="#f43f5e" strokeWidth={2} dot={false} />
                </LineChart>
            </ResponsiveContainer>
        </div>
    );
};

export default RiskChart;
