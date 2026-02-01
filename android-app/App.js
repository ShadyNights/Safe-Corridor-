import React, { useState, useEffect } from 'react';
import { StyleSheet, Text, View, Button } from 'react-native';
import * as Location from 'expo-location';

const BACKEND_URL = "http://YOUR_IP_ADDRESS:3000/api";

export default function App() {
    const [location, setLocation] = useState(null);
    const [errorMsg, setErrorMsg] = useState(null);
    const [sessionId, setSessionId] = useState(null);

    useEffect(() => {
        (async () => {
            let { status } = await Location.requestForegroundPermissionsAsync();
            if (status !== 'granted') {
                setErrorMsg('Permission to access location was denied');
                return;
            }
        })();
    }, []);

    const startRide = async () => {
        let { coords } = await Location.getCurrentPositionAsync({});
        // Start Ride API
        const response = await fetch(`${BACKEND_URL}/ride/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                startLocation: { lat: coords.latitude, lon: coords.longitude },
                endLocation: { lat: 21.1600, lon: 79.0900 } // Mock Destination
            })
        });
        const data = await response.json();
        setSessionId(data.sessionId);

        // Start Interval
        // In real app, use BackgroundLocation
    };

    return (
        <View style={styles.container}>
            <Text style={styles.title}>SafeCorridor Mobile</Text>
            {sessionId ? (
                <Text style={styles.status}>Ride Active: {sessionId.slice(0, 5)}</Text>
            ) : (
                <Button title="Start Ride" onPress={startRide} />
            )}
            <Text>{errorMsg}</Text>
        </View>
    );
}

const styles = StyleSheet.create({
    container: {
        flex: 1,
        backgroundColor: '#fff',
        alignItems: 'center',
        justifyContent: 'center',
    },
    title: {
        fontSize: 24,
        fontWeight: 'bold',
        marginBottom: 20
    },
    status: {
        fontSize: 18,
        color: 'green'
    }
});
