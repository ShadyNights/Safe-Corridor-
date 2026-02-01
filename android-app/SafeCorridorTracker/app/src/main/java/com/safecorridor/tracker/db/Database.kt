package com.safecorridor.tracker.db

import android.content.Context
import androidx.room.*

@Entity
data class TelemetryPoint(
    @PrimaryKey(autoGenerate = true) val id: Int = 0,
    val timestamp: Long,
    val lat: Double,
    val lng: Double,
    val speed: Float,
    val isMock: Boolean
)

@Dao
interface TelemetryDao {
    @Insert
    suspend fun insert(point: TelemetryPoint)

    @Query("SELECT * FROM TelemetryPoint")
    suspend fun getUnsent(): List<TelemetryPoint>

    @Query("DELETE FROM TelemetryPoint WHERE id = :id")
    suspend fun delete(id: Int)
}

@Database(entities = [TelemetryPoint::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun telemetryDao(): TelemetryDao

    companion object {
        @Volatile
        private var INSTANCE: AppDatabase? = null

        fun getDatabase(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "telemetry_database"
                ).build()
                INSTANCE = instance
                instance
            }
        }
    }
}
