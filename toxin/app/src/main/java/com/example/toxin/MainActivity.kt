package com.example.toxin

import android.app.Activity
import android.os.Bundle
import android.widget.TextView
import android.graphics.Color
import android.os.Handler
import android.os.Looper

class MainActivity : Activity() {
    private lateinit var appState: ToxinApplicationState
    private lateinit var textView: TextView
    private val handler = Handler(Looper.getMainLooper())
    private val updateInterval = 1000L  // Update UI every 1 second

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        
        // Initialize temporal state tracking
        appState = ToxinApplicationState()
        appState.initializeToxinApp()
        appState.simulateComponentSetup()
        
        // Create main display
        textView = TextView(this).apply {
            setTextColor(Color.WHITE)
            setBackgroundColor(Color.parseColor("#1a1a2e"))
            setPadding(16, 16, 16, 16)
            setTextSize(12f)
            typeface = android.graphics.Typeface.MONOSPACE
            setLineSpacing(2f, 1.1f)
        }
        
        setContentView(textView)
        
        // Start periodic UI updates based on temporal state changes
        startUIUpdates()
    }

    /**
     * Periodic UI update based on component state changes
     */
    private fun startUIUpdates() {
        val updateRunnable = object : Runnable {
            override fun run() {
                updateDisplayWithTemporalState()
                handler.postDelayed(this, updateInterval)
            }
        }
        handler.post(updateRunnable)
    }

    /**
     * Update UI with current temporal state of components
     */
    private fun updateDisplayWithTemporalState() {
        val tracker = appState.getComponentTracker()
        val display = buildTemporalDisplay(tracker)
        textView.text = display
    }

    /**
     * Build formatted display showing temporal state of all components
     */
    private fun buildTemporalDisplay(tracker: ComponentStateTracker): String {
        val header = """
╔═══════════════════════════════════════════════════════╗
║     Symbiote Toxin — Temporal Status Dashboard       ║
║     Android 14 (API 34) | LineageOS + microG         ║
╚═══════════════════════════════════════════════════════╝

""".trimIndent()

        val dashboard = tracker.getStatusDashboard()
        
        val footer = """

╔═══════════════════════════════════════════════════════╗
║ Phase 6: Mobile spawn with temporal logic tracking   ║
║ Updated: ${java.time.Instant.now()}  ║
╚═══════════════════════════════════════════════════════╝
""".trimIndent()

        return header + dashboard + footer
    }

    override fun onDestroy() {
        super.onDestroy()
        // Cleanup if needed
        handler.removeCallbacksAndMessages(null)
    }
}
