# Yummi Additives Script

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![SQLite](https://img.shields.io/badge/SQLite-3.0+-green.svg)](https://sqlite.org/)

A comprehensive Python script to create and populate an SQLite database with food additives data for Kotlin Multiplatform (KMP) projects. This script fetches data from Open Food Facts API and creates a structured database with Vietnamese risk classifications and detailed additive information.

## 🚀 Features

- **Automated Data Fetching**: Retrieves food additives data from Open Food Facts API
- **Risk Classification**: Implements Vietnamese color-coded risk levels (Xanh Lá/Green, Vàng/Yellow, Cam/Orange, Đỏ/Red)
- **SQLite Database**: Creates optimized database with proper indexing for fast queries
- **KMP Ready**: Generates database compatible with Kotlin Multiplatform projects
- **Comprehensive Logging**: Detailed logs of the database creation process
- **Sample Queries**: Provides ready-to-use SQL queries for common operations
- **Data Validation**: Ensures data integrity and completeness

## 📋 Requirements

- Python 3.7 or higher
- Internet connection for API data fetching
- SQLite 3.0 or higher

## 🛠 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/duypk-apero/Yummi-additives-script.git
   cd Yummi-additives-script
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## 📖 Usage

### Basic Usage

Run the script to create the SQLite database:

```bash
python create_additives_sqlite.py
```

### Output Files

The script generates several files:

- `additives.db` - Main SQLite database file (~319KB)
- `sample_queries.sql` - Collection of useful SQL queries
- `additives_sqlite_creation_YYYYMMDD.log` - Detailed operation log
- `openfoodfacts_raw_YYYYMMDD.json` - Raw API response data

### Database Schema

The database contains a single optimized table with the following structure:

```sql
CREATE TABLE additives (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    e_number TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    risk_level TEXT NOT NULL,
    category TEXT,
    is_vegetarian INTEGER DEFAULT 0,
    is_vegan INTEGER DEFAULT 0,
    allergen_info TEXT,
    usage_notes TEXT,
    source TEXT DEFAULT 'Open Food Facts',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

## 🎯 KMP Integration

### Android/JVM Usage

```kotlin
class AdditiveDatabase(private val driver: SqlDriver) {
    private val database = Database(driver)
    
    fun searchAdditives(query: String): List<Additive> {
        return database.additivesQueries.searchByName(query).executeAsList()
    }
    
    fun getAdditivesByRisk(riskLevel: String): List<Additive> {
        return database.additivesQueries.getByRiskLevel(riskLevel).executeAsList()
    }
}
```

### iOS Usage

```kotlin
fun createDatabase(): Database {
    val driver = NativeSqliteDriver(
        schema = Database.Schema,
        name = "additives.db"
    )
    return Database(driver)
}
```

For complete KMP integration examples, see [`KMP_Integration_Example.kt`](KMP_Integration_Example.kt).

## 📊 Database Statistics

After running the script, you'll get statistics like:

- **Total Additives**: 541
- **Vegetarian-friendly**: 435 (80.4%)
- **Vegan-friendly**: 431 (79.7%)
- **Risk Distribution**:
  - Yellow (Vàng): 95.7%
  - Green (Xanh Lá): 4.3%
- **Top Categories**: Mixed (48.6%), Emulsifiers (18.3%), Colors (8.7%)

## 🔍 Sample Queries

The script generates useful SQL queries in `sample_queries.sql`:

### Search by Name
```sql
SELECT * FROM additives 
WHERE name LIKE '%tartrazine%' 
ORDER BY name;
```

### Filter by Risk Level
```sql
SELECT e_number, name, risk_level 
FROM additives 
WHERE risk_level = 'Đỏ' 
ORDER BY e_number;
```

### Vegetarian/Vegan Options
```sql
SELECT COUNT(*) as vegan_count 
FROM additives 
WHERE is_vegan = 1;
```

### Category Distribution
```sql
SELECT category, COUNT(*) as count 
FROM additives 
GROUP BY category 
ORDER BY count DESC;
```

## 🧩 Risk Classification System

The database implements a Vietnamese risk classification system:

| Risk Level | Color | Description |
|------------|-------|-------------|
| Xanh Lá | 🟢 Green | Generally safe for consumption |
| Vàng | 🟡 Yellow | Moderate risk, use with caution |
| Cam | 🟠 Orange | Higher risk, limit consumption |
| Đỏ | 🔴 Red | High risk, avoid if possible |

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Open Food Facts](https://openfoodfacts.org/) for providing comprehensive food additives data
- Vietnamese documentation "Hướng Dẫn Cập Nhật Dữ Liệu Phụ Gia Thực Phẩm" for risk classification guidelines
- SQLite team for the excellent database engine
- Kotlin Multiplatform community for cross-platform development tools

## 📞 Support

If you encounter any issues or have questions:

1. Check existing [Issues](https://github.com/duypk-apero/Yummi-additives-script/issues)
2. Create a new issue with detailed information
3. Include logs and system information

## 🔄 Updates

To update the database with the latest food additives data:

```bash
# Backup existing database
cp additives.db additives_backup.db

# Run the script to fetch fresh data
python create_additives_sqlite.py
```

---

**Made with ❤️ for the Vietnamese food safety community** 