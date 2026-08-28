package com.example.toxin

import java.time.Instant
import java.time.Duration

/**
 * Temporal State Machine for Toxin Components
 * Based on: Temporal Logic for AI Agent Goals
 * 
 * Tracks component initialization with time bounds and state transitions.
 * Ensures all operations have deadlines and progress is monitorable.
 */

enum class ComponentStatus {
    PENDING,        // Not started
    INITIALIZING,   // Setup in progress
    ACTIVE,         // Running normally
    DEGRADED,       // Partial functionality
    ERROR,          // Failure state
    RESOLVED        // Complete/stopped
}

/**
 * Represents the state of a single component with temporal properties
 */
data class ComponentState(
    val name: String,
    val status: ComponentStatus,
    val startTime: Instant,
    val expectedDuration: Duration,
    val lastUpdate: Instant,
    val errorMessage: String? = null,
    val progressMessage: String? = null
) {
    /**
     * Check if this component has exceeded its deadline
     */
    val isOverdue: Boolean
        get() = Instant.now() > startTime.plus(expectedDuration)

    /**
     * Calculate progress as percentage of expected duration
     */
    val progressPercent: Int
        get() {
            val elapsed = Duration.between(startTime, Instant.now())
            val percent = if (expectedDuration.seconds > 0) {
                (elapsed.seconds * 100 / expectedDuration.seconds).toInt()
            } else {
                0
            }
            return minOf(percent, 100)
        }

    /**
     * Calculate time remaining until deadline
     */
    val timeRemaining: Duration
        get() {
            val deadline = startTime.plus(expectedDuration)
            val now = Instant.now()
            return if (deadline > now) {
                Duration.between(now, deadline)
            } else {
                Duration.ZERO
            }
        }

    /**
     * Human-readable status summary
     */
    val statusSummary: String
        get() {
            val overdue = if (isOverdue) " [OVERDUE]" else ""
            val progress = if (status == ComponentStatus.INITIALIZING) {
                " ($progressPercent%)"
            } else {
                ""
            }
            return "$status$progress$overdue"
        }

    /**
     * Convert to JSON representation for logging/transmission
     */
    fun toJson(): String {
        return """
{
  "name": "$name",
  "status": "$status",
  "started": "$startTime",
  "deadline": "${startTime.plus(expectedDuration)}",
  "is_overdue": $isOverdue,
  "progress_percent": $progressPercent,
  "time_remaining_seconds": ${timeRemaining.seconds},
  "last_update": "$lastUpdate",
  "error": ${if (errorMessage != null) "\"$errorMessage\"" else "null"},
  "message": ${if (progressMessage != null) "\"$progressMessage\"" else "null"}
}
        """.trimIndent()
    }
}

/**
 * Tracks all component states and provides query interface
 * Thread-safe operations on component state
 */
class ComponentStateTracker {
    private val states = mutableMapOf<String, ComponentState>()
    private val stateHistory = mutableListOf<Pair<Instant, String>>()  // For audit
    private val lock = Any()  // Synchronization lock for thread safety

    /**
     * Initialize tracking for a component
     * @param name Component name
     * @param expectedDurationSeconds Expected time to completion
     */
    fun initializeComponent(
        name: String,
        expectedDurationSeconds: Long = 60
    ) {
        val now = Instant.now()
        states[name] = ComponentState(
            name = name,
            status = ComponentStatus.PENDING,
            startTime = now,
            expectedDuration = Duration.ofSeconds(expectedDurationSeconds),
            lastUpdate = now
        )
        logStateChange(name, ComponentStatus.PENDING)
    }

    /**
     * Update component status
     */
    fun updateStatus(
        name: String,
        newStatus: ComponentStatus,
        error: String? = null,
        message: String? = null
    ) {
        states[name]?.let { current ->
            states[name] = current.copy(
                status = newStatus,
                lastUpdate = Instant.now(),
                errorMessage = error,
                progressMessage = message
            )
            logStateChange(name, newStatus)
        }
    }

    /**
     * Log a state change for audit trail
     * @private
     */
    private fun logStateChange(componentName: String, status: ComponentStatus) {
        stateHistory.add(Pair(Instant.now(), "$componentName -> $status"))
    }

    /**
     * Get current state of a component
     */
    fun getComponentState(name: String): ComponentState? {
        return states[name]
    }

    /**
     * Get all components that are overdue
     */
    fun getOverdueComponents(): List<String> {
        return states.filter { (_, state) ->
            state.isOverdue && state.status != ComponentStatus.RESOLVED
        }.keys.toList()
    }

    /**
     * Get all components with errors
     */
    fun getErrorComponents(): List<String> {
        return states.filter { (_, state) ->
            state.status == ComponentStatus.ERROR
        }.keys.toList()
    }

    /**
     * Get components still initializing
     */
    fun getInitializingComponents(): List<String> {
        return states.filter { (_, state) ->
            state.status == ComponentStatus.INITIALIZING
        }.keys.toList()
    }

    /**
     * Get overall system health status
     */
    fun getSystemHealth(): String {
        val total = states.size
        val active = states.values.count { it.status == ComponentStatus.ACTIVE }
        val error = states.values.count { it.status == ComponentStatus.ERROR }
        val overdue = getOverdueComponents().size

        return when {
            error > 0 -> "ERROR ($error/$total failed)"
            overdue > 0 -> "DEGRADED ($overdue/$total overdue)"
            active == total -> "HEALTHY ($active/$total active)"
            else -> "INITIALIZING"
        }
    }

    /**
     * Get all components as JSON array
     */
    fun getAllComponentsJson(): String {
        return states.values.joinToString(
            ",\n  ",
            "[\n  ",
            "\n]"
        ) { it.toJson() }
    }

    /**
     * Get status dashboard summary
     */
    fun getStatusDashboard(): String {
        val health = getSystemHealth()
        val componentsList = states.entries.joinToString("\n") { (name, state) ->
            val indicator = when (state.status) {
                ComponentStatus.ACTIVE -> "✓"
                ComponentStatus.INITIALIZING -> "↻"
                ComponentStatus.PENDING -> "○"
                ComponentStatus.ERROR -> "✗"
                ComponentStatus.RESOLVED -> "✔"
                else -> "?"
            }
            val timeStr = if (state.isOverdue) {
                "OVERDUE"
            } else {
                "${state.timeRemaining.seconds}s"
            }
            "$indicator $name: ${state.status} [$timeStr]"
        }

        return """
╔════════════════════════════════════════╗
║  Toxin Temporal Status Dashboard       ║
╚════════════════════════════════════════╝

System Health: $health

Components:
$componentsList

╔════════════════════════════════════════╝
        """.trimIndent()
    }

    /**
     * Get audit log of state changes
     */
    fun getAuditLog(): List<String> {
        return stateHistory.map { (instant, change) ->
            "$instant — $change"
        }
    }

    /**
     * Get detailed JSON representation of entire tracker state
     */
    fun toDetailedJson(): String {
        return """{
  "timestamp": "${Instant.now()}",
  "system_health": "${getSystemHealth()}",
  "components": ${getAllComponentsJson()},
  "overdue_components": ${getOverdueComponents().let { if (it.isEmpty()) "[]" else "\"${it.joinToString(", ")}\"" }},
  "error_components": ${getErrorComponents().let { if (it.isEmpty()) "[]" else "\"${it.joinToString(", ")}\"" }},
  "initializing_components": ${getInitializingComponents().let { if (it.isEmpty()) "[]" else "\"${it.joinToString(", ")}\"" }}
}"""
    }

    /**
     * Generate temporal logic constraints for Phage (LLM) layer
     * Provides decidable constraints for AI agent decision-making
     */
    fun getTemporalConstraintsForLLM(): String {
        synchronized(lock) {
            val constraints = mutableListOf<String>()
            
            for ((name, state) in states) {
                val deadline = state.startTime.plus(state.expectedDuration)
                val timeRemaining = state.timeRemaining.seconds
                
                constraints.add("""
                    COMPONENT: $name
                    STATUS: ${state.status}
                    DEADLINE: $deadline
                    TIME_REMAINING_SECONDS: $timeRemaining
                    IS_OVERDUE: ${state.isOverdue}
                    BOUNDED_CONSTRAINT: All operations must complete within ${state.expectedDuration.seconds}s from start
                """.trimIndent())
            }
            
            return "TEMPORAL_LOGIC_CONSTRAINTS {\n" + 
                   constraints.joinToString("\n---\n") + 
                   "\n}"
        }
    }

    /**
     * Get decidable predicates for Carnage (ACL) security layer
     * Ensures all access control decisions are formally decidable
     */
    fun getDecidablePredicates(): String {
        synchronized(lock) {
            val predicates = mutableListOf<String>()
            
            for ((name, state) in states) {
                val isHealthy = state.status in listOf(
                    ComponentStatus.ACTIVE, 
                    ComponentStatus.RESOLVED
                )
                val isDead = state.status == ComponentStatus.ERROR
                val isUnderway = state.status == ComponentStatus.INITIALIZING
                
                predicates.add("""
                    DECIDABLE($name): {
                      healthy($name) ≡ $isHealthy
                      failed($name) ≡ $isDead
                      initializing($name) ≡ $isUnderway
                      overdue($name) ≡ ${state.isOverdue}
                    }
                """.trimIndent())
            }
            
            return "DECIDABLE_PREDICATES {\n" + 
                   predicates.joinToString("\n") + 
                   "\n}"
        }
    }

    /**
     * Thread-safe initialization wrapper
     */
    fun initializeComponentSafe(
        name: String,
        expectedDurationSeconds: Long = 60
    ) {
        synchronized(lock) {
            initializeComponent(name, expectedDurationSeconds)
        }
    }

    /**
     * Thread-safe status update wrapper
     */
    fun updateStatusSafe(
        name: String,
        newStatus: ComponentStatus,
        error: String? = null,
        message: String? = null
    ) {
        synchronized(lock) {
            updateStatus(name, newStatus, error, message)
        }
    }
}

/**
 * Application-level state tracker for Symbiote-OS Toxin integration
 */
class ToxinApplicationState {
    private val componentTracker = ComponentStateTracker()
    private var appStartTime: Instant = Instant.now()
    private var appStatus: ComponentStatus = ComponentStatus.PENDING

    /**
     * Initialize Toxin application with standard components
     */
    fun initializeToxinApp() {
        appStartTime = Instant.now()
        appStatus = ComponentStatus.INITIALIZING

        // Initialize standard Toxin components with expected durations
        componentTracker.initializeComponent("microG", 30)      // 30s setup
        componentTracker.initializeComponent("Syncthing", 45)   // 45s setup
        componentTracker.initializeComponent("Shelter", 20)     // 20s setup
        componentTracker.initializeComponent("Venom-Connection", 60)  // 60s
        componentTracker.initializeComponent("Tor-Bridge", 40)  // 40s
    }

    /**
     * Simulate component initialization progress
     */
    fun simulateComponentSetup() {
        // microG: Ready immediately
        Thread {
            Thread.sleep(1000)
            componentTracker.updateStatus("microG", ComponentStatus.ACTIVE, message = "GmsCore configured")
        }.start()

        // Syncthing: Takes longer
        Thread {
            Thread.sleep(2000)
            componentTracker.updateStatus("Syncthing", ComponentStatus.INITIALIZING, message = "Scanning folders...")
            Thread.sleep(2000)
            componentTracker.updateStatus("Syncthing", ComponentStatus.ACTIVE, message = "Sync ready")
        }.start()

        // Shelter: Quick setup
        Thread {
            Thread.sleep(1500)
            componentTracker.updateStatus("Shelter", ComponentStatus.ACTIVE, message = "Work profile isolated")
        }.start()

        // Tor connection
        Thread {
            Thread.sleep(3000)
            componentTracker.updateStatus("Tor-Bridge", ComponentStatus.ACTIVE, message = "Connected to Venom")
        }.start()
    }

    /**
     * Get current app state as string (for display)
     */
    fun getAppStateDisplay(): String {
        return componentTracker.getStatusDashboard()
    }

    /**
     * Get component tracker for direct access
     */
    fun getComponentTracker(): ComponentStateTracker {
        return componentTracker
    }

    /**
     * Check if app is ready for use
     */
    fun isReady(): Boolean {
        val errors = componentTracker.getErrorComponents()
        val overdue = componentTracker.getOverdueComponents()
        return errors.isEmpty() && overdue.isEmpty()
    }
}
