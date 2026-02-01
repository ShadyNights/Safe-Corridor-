package com.safecorridor.tracker

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.location.Location
import android.os.Build
import android.os.IBinder
import androidx.core.app.NotificationCompat
import com.google.android.gms.location.*
import com.safecorridor.tracker.db.AppDatabase
import com.safecorridor.tracker.db.TelemetryPoint
import kotlinx.coroutines.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONObject

class TrackerService : Service() {

    private val CHANNEL_ID = "SafeCorridorChannel"
    private val NOTIF_ID = 1
    
    private lateinit var fusedLocationClient: FusedLocationProviderClient
    private lateinit var locationCallback: LocationCallback
    
    private lateinit var db: AppDatabase
    private val scope = CoroutineScope(Dispatchers.IO + Job())
    
    private val client = OkHttpClient()
    private val RIDE_SESSION_ID = "ride_pilot_001" 

    override fun onCreate() {
        super.onCreate()
        createNotificationChannel()
        fusedLocationClient = LocationServices.getFusedLocationProviderClient(this)
        db = AppDatabase.getDatabase(this)
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Safe Corridor Active")
            .setContentText("Monitoring ride safety silently...")
            .setSmallIcon(android.R.drawable.ic_menu_mylocation)
            .build()
            
        startForeground(NOTIF_ID, notification)
        
        startTracking()
        return START_STICKY
    }

    private fun startTracking() {
        val request = LocationRequest.Builder(Priority.PRIORITY_HIGH_ACCURACY, 5000)
            .setMinUpdateDistanceMeters(10.0f) 
            .build()

        locationCallback = object : LocationCallback() {
            override fun onLocationResult(result: LocationResult) {
                result.lastLocation?.let { location ->
                    if (location.latitude != 0.0 && location.longitude != 0.0) {
                         processLocation(location)
                    }
                }
            }
        }

        try {
            fusedLocationClient.requestLocationUpdates(request, locationCallback, null)
        } catch (e: SecurityException) {
        }
    }

    private fun processLocation(location: Location) {
        scope.launch {
             val point = TelemetryPoint(
                timestamp = System.currentTimeMillis(),
                lat = location.latitude,
                lng = location.longitude,
                speed = location.speed,
                isMock = location.isFromMockProvider
            )

            if (isNetworkAvailable()) {
                // Pass accuracy from location object
                if (sendTelemetry(point, location.accuracy)) {
                     flushBuffer() 
                } else {
                     db.telemetryDao().insert(point) 
                }
            } else {
                db.telemetryDao().insert(point) 
            }
        }
    }

    private fun sendTelemetry(point: TelemetryPoint, accuracy: Float = 0f): Boolean {
        val json = JSONObject().apply {
            put("sessionId", RIDE_SESSION_ID)
            put("location", JSONObject().put("lat", point.lat).put("lon", point.lng))
            put("speed", point.speed * 3.6) 
            put("deviation", 0)
            put("accuracy", accuracy)
            put("timestamp", point.timestamp)
            put("isMock", if (android.os.Build.VERSION.SDK_INT >= 31) point.isMock else false)
        }

        val request = Request.Builder()
            .url("http://10.0.2.2:3000/api/ride/telemetry")
            .post(json.toString().toRequestBody("application/json".toMediaType()))
            .addHeader("X-Ride-Secret", "hacknagpur_secret_123") 
            .build()

        return try {
            val response = client.newCall(request).execute()
            response.isSuccessful
        } catch (e: Exception) {
            false
        }
    }

    private suspend fun flushBuffer() {
        val unsent = db.telemetryDao().getUnsent()
        for (point in unsent) {
            if (sendTelemetry(point)) {
                db.telemetryDao().delete(point.id)
            } else {
                break 
            }
        }
    }

    private fun isNetworkAvailable(): Boolean {
        return true 
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(
                CHANNEL_ID,
                "Safe Corridor Service",
                NotificationManager.IMPORTANCE_LOW
            )
            val manager = getSystemService(NotificationManager::class.java)
            manager.createNotificationChannel(channel)
        }
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
