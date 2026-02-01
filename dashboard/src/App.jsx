import { useState, useEffect, useRef } from 'react'

const IS_PROD = false;

import io from 'socket.io-client';
import MapView from './components/MapView';
import RiskChart from './components/RiskChart';
import LogStream from './components/LogStream';
import { AlertTriangle, ShieldCheck, Activity } from 'lucide-react';

const SOCKET_URL = 'http://localhost:3000';
const API_URL = 'http://localhost:3000/api';

function App() {
    const [socket, setSocket] = useState(null);
    const [status, setStatus] = useState('Disconnected');
    const [rideState, setRideState] = useState(null);
    const [path, setPath] = useState([]);
    const [riskData, setRiskData] = useState([]);
    const [logs, setLogs] = useState([]);
    const [simInterval, setSimInterval] = useState(null);

    const simPos = useRef({ lat: 21.1458, lon: 79.0882 });
    const simStep = useRef(0);

    useEffect(() => {
        const newSocket = io(SOCKET_URL);
        setSocket(newSocket);

        newSocket.on('connect', () => {
            setStatus('Connected');
            addLog('Connected to Backend', 'INFO');
        });
        newSocket.on('disconnect', () => setStatus('Disconnected'));

        newSocket.on('ride_started', (data) => {
            addLog(`Ride Started: ${data.sessionId}`, 'INFO');
            setRideState({ ...data, riskScore: 0, severity: 'NORMAL' });
            setPath([data.startLocation]);
            simPos.current = { ...data.startLocation };
            setRiskData([]);
        });

        newSocket.on('ride_update', (data) => {
            setRideState(prev => ({ ...prev, ...data }));
            setPath(prev => [...prev, data.location]);

            setRiskData(prev => [...prev, {
                time: new Date().toLocaleTimeString(),
                riskScore: data.riskScore
            }]);

            if (data.reasons && data.reasons.length > 0) {
                data.reasons.forEach(r => addLog(`Risk Increase: ${r}`, 'RISK_UP'));
            }
        });

        newSocket.on('ride_ended', () => {
            addLog('Ride Ended', 'INFO');
            if (simInterval) clearInterval(simInterval);
        });

        return () => newSocket.close();
    }, []);

    const addLog = (message, type = 'INFO') => {
        setLogs(prev => [{ time: new Date().toLocaleTimeString(), message, type }, ...prev]);
    };

    const startRide = async () => {
        const start = { lat: 21.1458, lon: 79.0882 };
        const end = { lat: 21.1600, lon: 79.0900 };

        try {
            await fetch(`${API_URL}/ride/start`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ startLocation: start, endLocation: end })
            });
        } catch (e) {
            console.error(e);
            addLog('Failed to start ride', 'ERROR');
        }
    };

    const endRide = async () => {
        if (!rideState?.sessionId) return;
        await fetch(`${API_URL}/ride/end`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ sessionId: rideState.sessionId })
        });
        stopSimulation();
    };

    const startSimulation = (type) => {
        if (!rideState?.sessionId) return;
        if (simInterval) clearInterval(simInterval);

        addLog(`Starting ${type} Simulation...`, 'INFO');

        const id = setInterval(() => {
            let speed = 40;
            let deviation = 0;

            if (type === 'BAD') {
                if (Math.random() > 0.7) speed = 0;
                if (Math.random() > 0.5) {
                    simPos.current.lat += 0.0002;
                    deviation = 0.6;
                } else {
                    simPos.current.lat += 0.0001;
                }
            } else {
                simPos.current.lat += 0.0001;
                simPos.current.lon += 0.0001;
            }

            fetch(`${API_URL}/ride/telemetry`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    sessionId: rideState.sessionId,
                    location: simPos.current,
                    speed: speed,
                    deviation: deviation
                })
            });

        }, 1000);
        setSimInterval(id);
    };

    const stopSimulation = () => {
        if (simInterval) clearInterval(simInterval);
        setSimInterval(null);
        addLog('Simulation Stopped', 'INFO');
    };

    return (
        <div className="flex h-screen bg-slate-950 text-slate-100 overflow-hidden">
            <div className="w-64 bg-slate-900 border-r border-slate-700 p-4 flex flex-col gap-4">
                <h1 className="text-xl font-bold flex items-center gap-2">
                    <ShieldCheck className="text-emerald-400" /> SafeCorridor
                </h1>

                <div className="p-3 bg-slate-800 rounded-lg">
                    <h2 className="text-xs uppercase text-slate-500 font-bold mb-2">Ride Controls</h2>
                    <div className="flex gap-2 mb-2">
                        <button onClick={startRide} className="bg-emerald-600 hover:bg-emerald-500 text-white text-xs px-3 py-2 rounded flex-1">
                            New Ride
                        </button>
                        <button onClick={endRide} className="bg-slate-600 hover:bg-slate-500 text-white text-xs px-3 py-2 rounded flex-1">
                            End
                        </button>
                    </div>
                    {!IS_PROD && (
                        <>
                            <h2 className="text-xs uppercase text-slate-500 font-bold mb-2 mt-4">Simulate Scenario</h2>
                            <div className="flex flex-col gap-2">
                                <button onClick={() => startSimulation('NORMAL')} className="bg-blue-900/50 hover:bg-blue-800 text-blue-200 text-xs px-3 py-2 rounded border border-blue-800">
                                    ▶ Play Normal Ride
                                </button>
                                <button onClick={() => startSimulation('BAD')} className="bg-red-900/50 hover:bg-red-800 text-red-200 text-xs px-3 py-2 rounded border border-red-800">
                                    ▶ Play Risky Ride
                                </button>
                                <button onClick={stopSimulation} className="bg-slate-700 hover:bg-slate-600 text-white text-xs px-3 py-2 rounded">
                                    ⏹ Stop Sim
                                </button>
                            </div>
                        </>
                    )}
                </div>

                <div className="mt-auto">
                    <div className="flex items-center gap-2 text-xs text-slate-500">
                        <div className={`w-2 h-2 rounded-full ${status === 'Connected' ? 'bg-emerald-500' : 'bg-red-500'}`}></div>
                        {status}
                    </div>
                </div>
            </div>

            <div className="flex-1 flex flex-col p-4 gap-4">

                <div className="grid grid-cols-3 gap-4 h-32">
                    <div className="bg-slate-900 p-4 rounded-lg border border-slate-700 flex items-center justify-between">
                        <div>
                            <p className="text-slate-400 text-sm">Risk Score</p>
                            <p className={`text-4xl font-bold ${(rideState?.riskScore || 0) > 50 ? 'text-red-500' : 'text-emerald-400'
                                }`}>
                                {Math.round(rideState?.riskScore || 0)}
                            </p>
                        </div>
                        <Activity className="text-slate-700 w-12 h-12" />
                    </div>
                    <div className="bg-slate-900 p-4 rounded-lg border border-slate-700 flex items-center justify-between">
                        <div>
                            <p className="text-slate-400 text-sm">Status</p>
                            <p className="text-2xl font-bold text-white">
                                {rideState?.severity || 'IDLE'}
                            </p>
                        </div>
                        <AlertTriangle className={`w-12 h-12 ${rideState?.severity === 'WARNING' ? 'text-orange-500' :
                            rideState?.severity === 'CRITICAL' ? 'text-red-500' : 'text-slate-700'
                            }`} />
                    </div>
                    <div className="bg-slate-900 p-4 rounded-lg border border-slate-700">
                        <p className="text-slate-400 text-sm mb-2">Details</p>
                        <div className="text-sm">
                            <p>Session: <span className="text-slate-200">{rideState?.sessionId?.slice(-6) || '-'}</span></p>
                            <p>Speed: <span className="text-slate-200">{rideState?.speed || 0} km/h</span></p>
                        </div>
                    </div>
                </div>

                <div className="flex-1 grid grid-cols-3 gap-4 min-h-0">
                    <div className="col-span-2 flex flex-col gap-4">
                        <div className="flex-1 min-h-0 bg-slate-900 rounded-lg border border-slate-700 overflow-hidden">
                            <MapView path={path} currentPos={rideState?.location} startPos={rideState?.startLocation} endPos={rideState?.endLocation} />
                        </div>
                        <div className="h-48 shrink-0">
                            <RiskChart data={riskData} />
                        </div>
                    </div>
                    <div className="col-span-1 min-h-0">
                        <LogStream logs={logs} />
                    </div>
                </div>
            </div>
        </div>
    )
}

export default App
