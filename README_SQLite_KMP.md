# Food Additives SQLite Database for KMP Projects

This Python script creates a SQLite database containing food additives with risk classifications, specifically designed for import into Kotlin Multiplatform (KMP) projects.

## Features

- Downloads data from Open Food Facts API
- Classifies additives into risk levels (Green, Yellow, Orange, Red)
- Vietnamese and English names support
- KMP-optimized database schema with indexes
- Sample SQL queries for common use cases
- Comprehensive logging and validation

## Risk Level Classification

Based on the Vietnamese documentation, additives are classified into:

- **Xanh Lá (Green)**: Safe additives - natural ingredients, vitamins, minerals
- **Vàng (Yellow)**: Limited risk - artificial but generally safe additives
- **Cam (Orange)**: Moderate risk - additives with some concerns or restrictions
- **Đỏ (Red)**: High risk - additives with significant health concerns or banned in some countries

## Installation

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage
```bash
python create_additives_sqlite.py
```

### Custom Database Path
```bash
python create_additives_sqlite.py my_additives.db
```

## Generated Files

- `additives.db` - SQLite database ready for KMP import
- `sample_queries.sql` - Example SQL queries for KMP usage
- `additives_sqlite_creation_YYYYMMDD.log` - Detailed execution log
- `openfoodfacts_raw_YYYYMMDD.json` - Raw data backup

## Database Schema

### Additives Table

| Column | Type | Description |
|--------|------|-------------|
| id | INTEGER | Primary key |
| e_number | TEXT | E-number (e.g., E100) |
| name_en | TEXT | English name |
| name_vi | TEXT | Vietnamese name |
| risk_level | TEXT | Risk level in Vietnamese |
| risk_color | TEXT | Risk color (green, yellow, orange, red) |
| category | TEXT | Additive category |
| description_en | TEXT | English description |
| description_vi | TEXT | Vietnamese description |
| vegetarian | TEXT | Vegetarian-friendly (yes/no) |
| vegan | TEXT | Vegan-friendly (yes/no) |
| efsa_evaluation | TEXT | EFSA evaluation status |
| efsa_url | TEXT | EFSA evaluation URL |
| efsa_date | TEXT | EFSA evaluation date |
| additives_classes | TEXT | Additive classes |
| sources | TEXT | Data sources |
| last_updated | TEXT | Last update timestamp |
| created_at | TIMESTAMP | Record creation time |

### Metadata Table

Stores database versioning and metadata information.

## KMP Integration Examples

### Kotlin Data Class
```kotlin
@Entity(tableName = "additives")
data class Additive(
    @PrimaryKey val id: Int,
    @ColumnInfo(name = "e_number") val eNumber: String,
    @ColumnInfo(name = "name_en") val nameEn: String,
    @ColumnInfo(name = "name_vi") val nameVi: String,
    @ColumnInfo(name = "risk_level") val riskLevel: String,
    @ColumnInfo(name = "risk_color") val riskColor: String,
    val category: String,
    val vegetarian: String,
    val vegan: String
)
```

### Room DAO Example
```kotlin
@Dao
interface AdditiveDao {
    @Query("SELECT * FROM additives WHERE e_number = :eNumber")
    suspend fun getByENumber(eNumber: String): Additive?
    
    @Query("SELECT * FROM additives WHERE risk_color = :riskColor")
    suspend fun getByRiskLevel(riskColor: String): List<Additive>
    
    @Query("SELECT * FROM additives WHERE LOWER(name_en) LIKE LOWER(:query) OR LOWER(name_vi) LIKE LOWER(:query)")
    suspend fun searchByName(query: String): List<Additive>
}
```

### Database Setup in KMP
```kotlin
// commonMain
@Database(
    entities = [Additive::class],
    version = 1,
    exportSchema = false
)
abstract class AdditiveDatabase : RoomDatabase() {
    abstract fun additiveDao(): AdditiveDao
}

// Copy the SQLite file to your app's assets folder
// The database will be automatically imported when the app starts
```

## Sample Queries

The script generates `sample_queries.sql` with common use cases:

1. Search by E-number for barcode scanning
2. Filter by risk level for health-conscious users
3. Vegetarian/vegan filtering
4. Category-based browsing
5. Full-text search functionality

## Data Sources

- **Open Food Facts**: Primary data source with taxonomies
- **Manual curation**: Additional high-quality data for common additives
- **EFSA evaluations**: European Food Safety Authority assessments

## Customization

You can modify the risk classification logic in the `classify_risk_level()` method to adjust risk levels based on your specific requirements or regional regulations.

## Logging

The script provides comprehensive logging including:
- Data download progress
- Processing statistics
- Database validation results
- Error handling and warnings

## Updates

To update the database with new data:
1. Run the script again (it will overwrite the existing database)
2. The script automatically downloads the latest data from Open Food Facts
3. Check the log file for any changes or new additives

## Support

For issues or questions about the Vietnamese documentation that this script is based on, refer to the source documentation: "Hướng Dẫn Cập Nhật Dữ Liệu Phụ Gia Thực Phẩm". 