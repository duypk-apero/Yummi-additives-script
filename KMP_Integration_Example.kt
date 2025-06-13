/**
 * KMP Integration Example for Food Additives Database
 * Generated from Vietnamese documentation: Hướng Dẫn Cập Nhật Dữ Liệu Phụ Gia Thực Phẩm
 */

import androidx.room.*
import kotlinx.coroutines.flow.Flow

// Entity representing the additives table
@Entity(tableName = "additives")
data class Additive(
    @PrimaryKey val id: Int,
    @ColumnInfo(name = "e_number") val eNumber: String,
    @ColumnInfo(name = "name_en") val nameEn: String,
    @ColumnInfo(name = "name_vi") val nameVi: String,
    @ColumnInfo(name = "risk_level") val riskLevel: String,
    @ColumnInfo(name = "risk_color") val riskColor: String,
    val category: String?,
    @ColumnInfo(name = "description_en") val descriptionEn: String?,
    @ColumnInfo(name = "description_vi") val descriptionVi: String?,
    val vegetarian: String?,
    val vegan: String?,
    @ColumnInfo(name = "efsa_evaluation") val efsaEvaluation: String?,
    @ColumnInfo(name = "efsa_url") val efsaUrl: String?,
    @ColumnInfo(name = "efsa_date") val efsaDate: String?,
    @ColumnInfo(name = "additives_classes") val additivesClasses: String?,
    val sources: String?,
    @ColumnInfo(name = "last_updated") val lastUpdated: String,
    @ColumnInfo(name = "created_at") val createdAt: String?
)

// DAO for database operations
@Dao
interface AdditiveDao {
    
    // Basic queries
    @Query("SELECT * FROM additives WHERE e_number = :eNumber")
    suspend fun getByENumber(eNumber: String): Additive?
    
    @Query("SELECT * FROM additives WHERE risk_color = :riskColor ORDER BY e_number")
    suspend fun getByRiskLevel(riskColor: String): List<Additive>
    
    @Query("SELECT * FROM additives ORDER BY e_number")
    fun getAllAdditives(): Flow<List<Additive>>
    
    // Search queries
    @Query("""
        SELECT * FROM additives 
        WHERE LOWER(name_en) LIKE LOWER('%' || :query || '%') 
           OR LOWER(name_vi) LIKE LOWER('%' || :query || '%')
           OR LOWER(e_number) LIKE LOWER('%' || :query || '%')
        ORDER BY e_number
    """)
    suspend fun searchByName(query: String): List<Additive>
    
    // Filter queries
    @Query("SELECT * FROM additives WHERE vegetarian = 'yes' ORDER BY risk_color, e_number")
    suspend fun getVegetarianFriendly(): List<Additive>
    
    @Query("SELECT * FROM additives WHERE vegan = 'yes' ORDER BY risk_color, e_number")
    suspend fun getVeganFriendly(): List<Additive>
    
    @Query("SELECT * FROM additives WHERE category = :category ORDER BY e_number")
    suspend fun getByCategory(category: String): List<Additive>
    
    // Statistics queries
    @Query("SELECT COUNT(*) FROM additives")
    suspend fun getTotalCount(): Int
    
    @Query("""
        SELECT risk_level, risk_color, COUNT(*) as count,
        ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM additives), 2) as percentage
        FROM additives 
        GROUP BY risk_level, risk_color 
        ORDER BY count DESC
    """)
    suspend fun getRiskLevelStatistics(): List<RiskStatistic>
    
    @Query("""
        SELECT category, COUNT(*) as count
        FROM additives 
        GROUP BY category 
        ORDER BY count DESC
    """)
    suspend fun getCategoryStatistics(): List<CategoryStatistic>
}

// Data classes for statistics
data class RiskStatistic(
    @ColumnInfo(name = "risk_level") val riskLevel: String,
    @ColumnInfo(name = "risk_color") val riskColor: String,
    val count: Int,
    val percentage: Double
)

data class CategoryStatistic(
    val category: String?,
    val count: Int
)

// Database class
@Database(
    entities = [Additive::class],
    version = 1,
    exportSchema = false
)
abstract class AdditiveDatabase : RoomDatabase() {
    abstract fun additiveDao(): AdditiveDao
}

// Repository class for business logic
class AdditiveRepository(private val dao: AdditiveDao) {
    
    fun getAllAdditives() = dao.getAllAdditives()
    
    suspend fun searchAdditive(query: String): List<Additive> {
        return dao.searchByName(query)
    }
    
    suspend fun getAdditiveByENumber(eNumber: String): Additive? {
        return dao.getByENumber(eNumber.uppercase())
    }
    
    suspend fun getAdditivesByRiskLevel(riskLevel: RiskLevel): List<Additive> {
        return dao.getByRiskLevel(riskLevel.color)
    }
    
    suspend fun getVegetarianAdditives(): List<Additive> {
        return dao.getVegetarianFriendly()
    }
    
    suspend fun getVeganAdditives(): List<Additive> {
        return dao.getVeganFriendly()
    }
    
    suspend fun getStatistics(): AdditiveStatistics {
        val total = dao.getTotalCount()
        val riskStats = dao.getRiskLevelStatistics()
        val categoryStats = dao.getCategoryStatistics()
        
        return AdditiveStatistics(
            totalAdditives = total,
            riskLevelDistribution = riskStats,
            categoryDistribution = categoryStats
        )
    }
}

// Enum for risk levels
enum class RiskLevel(val vietnameseName: String, val color: String) {
    GREEN("Xanh Lá", "green"),
    YELLOW("Vàng", "yellow"), 
    ORANGE("Cam", "orange"),
    RED("Đỏ", "red")
}

// Data class for overall statistics
data class AdditiveStatistics(
    val totalAdditives: Int,
    val riskLevelDistribution: List<RiskStatistic>,
    val categoryDistribution: List<CategoryStatistic>
)

// Usage example in ViewModel or Use Case
class AdditiveSearchUseCase(private val repository: AdditiveRepository) {
    
    suspend fun searchForIngredientScanning(eNumber: String): AdditiveSearchResult {
        val additive = repository.getAdditiveByENumber(eNumber)
        
        return if (additive != null) {
            AdditiveSearchResult.Found(
                additive = additive,
                riskLevel = RiskLevel.values().find { it.color == additive.riskColor }
                    ?: RiskLevel.YELLOW,
                isVegetarian = additive.vegetarian == "yes",
                isVegan = additive.vegan == "yes"
            )
        } else {
            AdditiveSearchResult.NotFound(eNumber)
        }
    }
    
    suspend fun getHealthyAlternatives(currentRiskLevel: RiskLevel): List<Additive> {
        return when (currentRiskLevel) {
            RiskLevel.RED, RiskLevel.ORANGE -> repository.getAdditivesByRiskLevel(RiskLevel.GREEN)
            RiskLevel.YELLOW -> repository.getAdditivesByRiskLevel(RiskLevel.GREEN)
            RiskLevel.GREEN -> emptyList()
        }
    }
}

sealed class AdditiveSearchResult {
    data class Found(
        val additive: Additive,
        val riskLevel: RiskLevel,
        val isVegetarian: Boolean,
        val isVegan: Boolean
    ) : AdditiveSearchResult()
    
    data class NotFound(val searchedENumber: String) : AdditiveSearchResult()
}

/**
 * Database initialization for KMP project
 * 
 * Steps to integrate:
 * 1. Copy additives.db to your app's assets folder
 * 2. Use Room's createFromAsset() method to populate the database
 * 3. Set up dependency injection for the repository
 * 
 * Example in Android:
 * Room.databaseBuilder(context, AdditiveDatabase::class.java, "additives")
 *     .createFromAsset("additives.db")
 *     .build()
 */ 