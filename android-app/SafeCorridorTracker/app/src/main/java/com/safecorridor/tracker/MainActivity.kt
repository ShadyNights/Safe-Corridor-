package com.safecorridor.tracker

import android.content.Intent
import android.os.Bundle
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Auto-start service on app launch for MVP
        val intent = Intent(this, TrackerService::class.java)
        startForegroundService(intent)
    }
}
