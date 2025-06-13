# SQLite Database Integration for KMP Projects

This documentation provides detailed information about integrating the food additives SQLite database into Kotlin Multiplatform (KMP) projects.

## Database Overview

The `additives.db` SQLite database contains comprehensive information about food additives with:
- E-numbers and English names
- Risk classification system using color-coded levels
- Category information
- Vegetarian and vegan compatibility
- EFSA evaluation data

## Risk Classification System

The database implements a color-coded risk classification system:

- **GREEN**: Safe additives - natural ingredients, vitamins, minerals
- **YELLOW**: Limited risk - artificial but generally safe additives
- **ORANGE**: Moderate risk - additives with some concerns or restrictions
- **RED**: High risk - additives with significant health concerns or banned in some countries

## Database Schema

The main table structure:

```sql
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
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| id | INTEGER | Primary key |
| e_number | TEXT | E-number (e.g., "E100") |
| name | TEXT | English name |
| risk_level | TEXT | Risk level (GREEN, YELLOW, ORANGE, RED) |
| risk_color | TEXT | Color code for UI |
| category | TEXT | Additive category |
| description | TEXT | English description |
| vegetarian | TEXT | Vegetarian compatibility |
| vegan | TEXT | Vegan compatibility |
| efsa_evaluation | TEXT | EFSA safety evaluation |
| efsa_url | TEXT | EFSA evaluation URL |
| efsa_date | TEXT | Evaluation date |
| additives_classes | TEXT | Additive classes |
| sources | TEXT | Data sources |
| last_updated | TEXT | Last update timestamp |
| created_at | TIMESTAMP | Record creation time |

## Integration Methods

### Method 1: SQLDelight (Recommended for KMP)

1. Add SQLDelight to your project
2. Copy the database schema to `.sq` files
3. Use generated type-safe APIs

```kotlin
// Database queries
selectByENumber:
SELECT * FROM additives WHERE e_number = ?;

searchByName:
SELECT * FROM additives WHERE LOWER(name) LIKE LOWER('%' || ? || '%');
```

### Method 2: Room Database (Android)

1. Copy `additives.db` to `assets/` folder
2. Use Room's `createFromAsset()` method
3. Define entities and DAOs

```kotlin
@Database(entities = [Additive::class], version = 1)
@TypeConverters(Converters::class)
abstract class AdditiveDatabase : RoomDatabase() {
    abstract fun additiveDao(): AdditiveDao
}
```

### Method 3: Direct SQLite

For simple use cases, use platform-specific SQLite drivers directly.

## Common Queries

### Search by E-number
```sql
SELECT * FROM additives WHERE e_number = 'E100';
```

### Get high-risk additives
```sql
SELECT e_number, name, risk_level 
FROM additives 
WHERE risk_level = 'RED' 
ORDER BY e_number;
```

### Search by name
```sql
SELECT * FROM additives 
WHERE LOWER(name) LIKE LOWER('%vitamin%') 
ORDER BY name;
```

### Filter by dietary preferences
```sql
-- Vegetarian-friendly
SELECT * FROM additives WHERE vegetarian = 'yes';

-- Vegan-friendly  
SELECT * FROM additives WHERE vegan = 'yes';
```

### Get statistics
```sql
SELECT risk_level, COUNT(*) as count 
FROM additives 
GROUP BY risk_level 
ORDER BY count DESC;
```

## Platform-Specific Implementation

### Android
- Use Room or SQLDelight
- Copy database to assets folder
- Handle database versioning

### iOS
- Use SQLite.swift or SQLDelight
- Bundle database with app
- Handle Core Data integration if needed

### Desktop/JVM
- Use JDBC SQLite driver
- File-based or in-memory database

## Performance Considerations

1. **Indexes**: The database includes optimized indexes for common queries
2. **Caching**: Consider caching frequently accessed data
3. **Pagination**: For large result sets, implement pagination
4. **Background Processing**: Perform database operations off the main thread

## Data Updates

The database can be updated by:
1. Re-running the Python script
2. Downloading updated database file
3. Implementing incremental updates via API

## Error Handling

Common scenarios to handle:
- Database file not found
- Corrupted database
- Missing additive data
- Network errors during updates

## Security Considerations

- Validate E-number inputs
- Sanitize search queries
- Implement proper access controls
- Consider data encryption for sensitive applications

## Testing

Sample test data is included for:
- All risk levels
- Various categories
- Vegetarian/vegan options
- EFSA-evaluated additives

## Support

For integration issues:
1. Check the database schema matches your entity definitions
2. Verify index usage for performance
3. Test with sample queries provided
4. Review platform-specific documentation 