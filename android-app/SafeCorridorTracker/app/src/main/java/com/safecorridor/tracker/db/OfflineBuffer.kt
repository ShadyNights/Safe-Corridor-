package com.safecorridor.tracker.db

import androidx.room.*
import android.content.Context

@Entity(tableName = "telemetry_queue")
data class TelemetryPoint(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val timestamp: Long,
    val lat: Double,
    val lng: Double,
    val speed: Float,
    val sent: Boolean = false
)

@Dao
interface TelemetryDao {
    @Insert
    fun insert(point: TelemetryPoint)

    @Query("SELECT * FROM telemetry_queue WHERE sent = 0 ORDER BY timestamp ASC LIMIT 50")
    fun getUnsent(): List<TelemetryPoint>

    @Query("DELETE FROM telemetry_queue WHERE id = :id")
    fun delete(id: Long)
    
    @Query("SELECT COUNT(*) FROM telemetry_queue")
    fun getCount(): Int
}

@Database(entities = [TelemetryPoint::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun telemetryDao(): TelemetryDao

    companion object {
        @Volatile private var instance: AppDatabase? = null
        
        fun getDatabase(context: Context): AppDatabase {
            return instance ?: synchronized(this) {
                instance ?: Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "safecorridor_buffer"
                ).build().also { instance = it }
            }
        }
    }
}
