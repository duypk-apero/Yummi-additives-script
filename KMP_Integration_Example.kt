/**
 * Kotlin Multiplatform (KMP) Integration Example for Food Additives Database
 * 
 * This file provides complete integration examples for using the food additives SQLite database
 * in Kotlin Multiplatform projects, including Android, iOS, and Desktop.
 */

package com.yummi.additives

import app.cash.sqldelight.db.SqlDriver
import app.cash.sqldelight.driver.android.AndroidSqliteDriver
import app.cash.sqldelight.driver.native.NativeSqliteDriver
import app.cash.sqldelight.driver.jdbc.sqlite.JdbcSqliteDriver
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.datetime.Clock
import kotlinx.datetime.Instant

// Database Schema Definition (using SQLDelight)
// File: src/commonMain/sqldelight/com/yummi/additives/Database.sq

/*
CREATE TABLE additives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    e_number TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    risk_level TEXT NOT NULL,
    risk_color TEXT NOT NULL,
    category TEXT,
    description TEXT,
    vegetarian TEXT,
    vegan TEXT,
    efsa_evaluation TEXT,
    efsa_url TEXT,
    efsa_date TEXT,
    additives_classes TEXT,
    sources TEXT,
    last_updated TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for better performance
CREATE INDEX idx_e_number ON additives(e_number);
CREATE INDEX idx_risk_level ON additives(risk_level);
CREATE INDEX idx_category ON additives(category);
CREATE INDEX idx_name ON additives(name);

-- Sample Queries
selectAll:
SELECT * FROM additives;

selectByENumber:
SELECT * FROM additives WHERE e_number = ?;

searchByName:
SELECT * FROM additives WHERE LOWER(name) LIKE LOWER('%' || ? || '%');

selectByRiskLevel:
SELECT * FROM additives WHERE risk_level = ?;

selectVegetarian:
SELECT * FROM additives WHERE vegetarian = 'yes';

selectVegan:
SELECT * FROM additives WHERE vegan = 'yes';

selectByCategory:
SELECT * FROM additives WHERE category = ?;

getRiskLevelStats:
SELECT risk_level, COUNT(*) as count FROM additives GROUP BY risk_level;

getCategoryStats:
SELECT category, COUNT(*) as count FROM additives GROUP BY category ORDER BY count DESC;
*/

// Data Models
data class Additive(
    val id: Long,
    val eNumber: String,
    val name: String,
    val riskLevel: String,
    val riskColor: String,
    val category: String?,
    val description: String?,
    val vegetarian: String?,
    val vegan: String?,
    val efsaEvaluation: String?,
    val efsaUrl: String?,
    val efsaDate: String?,
    val additivesClasses: String?,
    val sources: String?,
    val lastUpdated: String,
    val createdAt: String?
)

data class RiskLevelStat(
    val riskLevel: String,
    val count: Long,
    val percentage: Double
)

data class CategoryStat(
    val category: String,
    val count: Long,
    val percentage: Double
)

// Risk Level Enum
enum class RiskLevel(val color: String) {
    GREEN("green"),
    YELLOW("yellow"),
    ORANGE("orange"),
    RED("red");
    
    companion object {
        fun fromString(value: String): RiskLevel? {
            return values().find { it.name.equals(value, ignoreCase = true) }
        }
    }
}

// Platform-specific Database Drivers
expect class DatabaseDriverFactory {
    fun createDriver(): SqlDriver
}

// Android Implementation
class AndroidDatabaseDriverFactory(private val context: android.content.Context) : DatabaseDriverFactory {
    override fun createDriver(): SqlDriver {
        return AndroidSqliteDriver(Database.Schema, context, "additives.db")
    }
}

// iOS Implementation  
class IOSDatabaseDriverFactory : DatabaseDriverFactory {
    override fun createDriver(): SqlDriver {
        return NativeSqliteDriver(Database.Schema, "additives.db")
    }
}

// Desktop/JVM Implementation
class DesktopDatabaseDriverFactory : DatabaseDriverFactory {
    override fun createDriver(): SqlDriver {
        return JdbcSqliteDriver(JdbcSqliteDriver.IN_MEMORY)
    }
}

// Repository Pattern Implementation
class AdditivesRepository(databaseDriverFactory: DatabaseDriverFactory) {
    private val database = Database(databaseDriverFactory.createDriver())
    private val queries = database.databaseQueries
    
    // Get all additives
    fun getAllAdditives(): List<Additive> {
        return queries.selectAll().executeAsList().map { it.toAdditive() }
    }
    
    // Search by E-number
    fun getAdditiveByENumber(eNumber: String): Additive? {
        return queries.selectByENumber(eNumber).executeAsOneOrNull()?.toAdditive()
    }
    
    // Search by name
    fun searchAdditivesByName(query: String): List<Additive> {
        return queries.searchByName(query).executeAsList().map { it.toAdditive() }
    }
    
    // Filter by risk level
    fun getAdditivesByRiskLevel(riskLevel: RiskLevel): List<Additive> {
        return queries.selectByRiskLevel(riskLevel.name).executeAsList().map { it.toAdditive() }
    }
    
    // Get vegetarian additives
    fun getVegetarianAdditives(): List<Additive> {
        return queries.selectVegetarian().executeAsList().map { it.toAdditive() }
    }
    
    // Get vegan additives
    fun getVeganAdditives(): List<Additive> {
        return queries.selectVegan().executeAsList().map { it.toAdditive() }
    }
    
    // Filter by category
    fun getAdditivesByCategory(category: String): List<Additive> {
        return queries.selectByCategory(category).executeAsList().map { it.toAdditive() }
    }
    
    // Get risk level statistics
    fun getRiskLevelStats(): List<RiskLevelStat> {
        val total = queries.selectAll().executeAsList().size.toDouble()
        return queries.getRiskLevelStats().executeAsList().map { 
            RiskLevelStat(
                riskLevel = it.risk_level,
                count = it.count_,
                percentage = (it.count_.toDouble() / total) * 100
            )
        }
    }
    
    // Get category statistics
    fun getCategoryStats(): List<CategoryStat> {
        val total = queries.selectAll().executeAsList().size.toDouble()
        return queries.getCategoryStats().executeAsList().map {
            CategoryStat(
                category = it.category ?: "Unknown",
                count = it.count_,
                percentage = (it.count_.toDouble() / total) * 100
            )
        }
    }
}

// Use Cases for Business Logic
class GetAdditiveByENumberUseCase(private val repository: AdditivesRepository) {
    suspend operator fun invoke(eNumber: String): Additive? {
        return repository.getAdditiveByENumber(eNumber.uppercase())
    }
}

class SearchAdditivesUseCase(private val repository: AdditivesRepository) {
    suspend operator fun invoke(query: String): List<Additive> {
        return repository.searchAdditivesByName(query)
    }
}

class GetSafeAdditivesUseCase(private val repository: AdditivesRepository) {
    suspend operator fun invoke(): List<Additive> {
        return repository.getAdditivesByRiskLevel(RiskLevel.GREEN)
    }
}

class GetHighRiskAdditivesUseCase(private val repository: AdditivesRepository) {
    suspend operator fun invoke(): List<Additive> {
        return repository.getAdditivesByRiskLevel(RiskLevel.RED)
    }
}

class GetVegetarianFriendlyAdditivesUseCase(private val repository: AdditivesRepository) {
    suspend operator fun invoke(): List<Additive> {
        return repository.getVegetarianAdditives()
    }
}

// Extension function to convert database model to domain model
private fun SelectAll.toAdditive(): Additive {
    return Additive(
        id = id,
        eNumber = e_number,
        name = name,
        riskLevel = risk_level,
        riskColor = risk_color,
        category = category,
        description = description,
        vegetarian = vegetarian,
        vegan = vegan,
        efsaEvaluation = efsa_evaluation,
        efsaUrl = efsa_url,
        efsaDate = efsa_date,
        additivesClasses = additives_classes,
        sources = sources,
        lastUpdated = last_updated,
        createdAt = created_at
    )
}

// Usage Examples

// Example 1: Android Fragment
/*
class AdditivesFragment : Fragment() {
    private val repository by lazy { 
        AdditivesRepository(AndroidDatabaseDriverFactory(requireContext()))
    }
    
    private fun searchAdditive(eNumber: String) {
        lifecycleScope.launch {
            val additive = repository.getAdditiveByENumber(eNumber)
            additive?.let { 
                displayAdditiveInfo(it)
            } ?: showNotFoundMessage()
        }
    }
    
    private fun displayAdditiveInfo(additive: Additive) {
        // Update UI with additive information
        binding.textENumber.text = additive.eNumber
        binding.textName.text = additive.name
        binding.textRiskLevel.text = additive.riskLevel
        
        // Set risk color
        val color = when(additive.riskLevel) {
            "GREEN" -> ContextCompat.getColor(requireContext(), R.color.green)
            "YELLOW" -> ContextCompat.getColor(requireContext(), R.color.yellow)
            "ORANGE" -> ContextCompat.getColor(requireContext(), R.color.orange)
            "RED" -> ContextCompat.getColor(requireContext(), R.color.red)
            else -> ContextCompat.getColor(requireContext(), R.color.gray)
        }
        binding.viewRiskColor.setBackgroundColor(color)
    }
}
*/

// Example 2: iOS SwiftUI Integration
/*
struct AdditiveDetailView: View {
    let additive: Additive
    
    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            Text(additive.eNumber)
                .font(.title)
                .fontWeight(.bold)
            
            Text(additive.name)
                .font(.headline)
            
            HStack {
                Circle()
                    .fill(riskColor)
                    .frame(width: 20, height: 20)
                
                Text(additive.riskLevel)
                    .font(.subheadline)
            }
            
            if let category = additive.category {
                Text("Category: \(category)")
                    .font(.caption)
                    .foregroundColor(.secondary)
            }
            
            Spacer()
        }
        .padding()
    }
    
    private var riskColor: Color {
        switch additive.riskLevel {
        case "GREEN": return .green
        case "YELLOW": return .yellow
        case "ORANGE": return .orange
        case "RED": return .red
        default: return .gray
        }
    }
}
*/ 