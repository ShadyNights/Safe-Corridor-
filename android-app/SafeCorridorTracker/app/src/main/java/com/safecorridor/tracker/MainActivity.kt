package com.safecorridor.tracker

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Bundle
import android.widget.Button
import android.widget.TextView
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity

class MainActivity : AppCompatActivity() {

    private lateinit var statusText: TextView
    private lateinit var actionButton: Button
    private var monitoring = false

    private val locationPermissionLauncher =
        registerForActivityResult(
            ActivityResultContracts.RequestPermission()
        ) { isGranted ->
            if (isGranted) {
                startTrackerService()
                updateUI(true)
            }
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        statusText = findViewById(R.id.statusText)
        actionButton = findViewById(R.id.actionButton)

        actionButton.setOnClickListener {
            if (!monitoring) {
                requestPermissionOrStart()
            } else {
                stopTrackerService()
                updateUI(false)
            }
        }
    }

    private fun requestPermissionOrStart() {
        if (checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION)
            == PackageManager.PERMISSION_GRANTED) {

            startTrackerService()
            updateUI(true)

        } else {
            locationPermissionLauncher.launch(
                Manifest.permission.ACCESS_FINE_LOCATION
            )
        }
    }

    private fun startTrackerService() {
        val intent = Intent(this, TrackerService::class.java)
        startForegroundService(intent)
    }

    private fun stopTrackerService() {
        val intent = Intent(this, TrackerService::class.java)
        stopService(intent)
    }

    private fun updateUI(isMonitoring: Boolean) {
        monitoring = isMonitoring
        if (isMonitoring) {
            statusText.text = "Status: Monitoring Active"
            actionButton.text = "End Ride"
        } else {
            statusText.text = "Status: Not Monitoring"
            actionButton.text = "Start Ride"
        }
    }
}
