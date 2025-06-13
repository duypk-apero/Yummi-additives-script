#!/usr/bin/env python3
"""
Food Additives SQLite Database Creator for KMP Projects

This script creates a SQLite database containing food additives with risk levels
suitable for import into Kotlin Multiplatform (KMP) projects.
"""

import requests
import json
import sqlite3
import pandas as pd
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
import os
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"additives_sqlite_creation_{datetime.now().strftime('%Y%m%d')}.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

class AdditivesSQLiteCreator:
    """Creates SQLite database for food additives with KMP-compatible structure."""
    
    def __init__(self, db_path: str = "additives.db"):
        self.db_path = db_path
        self.additives_data: List[Dict[str, Any]] = []
        
    def download_openfoodfacts_data(self) -> Optional[Dict]:
        """Download additives data from Open Food Facts API."""
        logger.info("Downloading data from Open Food Facts...")
        
        try:
            url = "https://static.openfoodfacts.org/data/taxonomies/additives.json"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Save raw data for reference
            timestamp = datetime.now().strftime('%Y%m%d')
            with open(f"openfoodfacts_raw_{timestamp}.json", "w", encoding="utf-8") as f:
                f.write(response.text)
            
            logger.info("Successfully downloaded Open Food Facts data")
            return json.loads(response.text)
            
        except requests.RequestException as e:
            logger.error(f"Failed to download Open Food Facts data: {e}")
            return None
    
    def process_openfoodfacts_data(self, raw_data: Dict) -> List[Dict[str, Any]]:
        """Process raw Open Food Facts data into structured format."""
        logger.info("Processing Open Food Facts data...")
        
        processed_additives = []
        
        for key, value in raw_data.items():
            if not key.startswith("en:e"):
                continue
                
            try:
                # Extract E-number
                e_number = value.get("e_number", {}).get("en", "")
                if not e_number:
                    continue
                
                # Extract names (English only)
                name_en = value.get("name", {}).get("en", "")
                
                # Extract additional information
                vegetarian = value.get("vegetarian", {}).get("en", "")
                vegan = value.get("vegan", {}).get("en", "")
                efsa_evaluation = value.get("efsa_evaluation", {}).get("en", "")
                efsa_url = value.get("efsa_evaluation_url", {}).get("en", "")
                efsa_date = value.get("efsa_evaluation_date", {}).get("en", "")
                additives_classes = value.get("additives_classes", {}).get("en", "")
                
                # Create additive record
                additive = {
                    "e_number": e_number,
                    "name": name_en,
                    "vegetarian": vegetarian,
                    "vegan": vegan,
                    "efsa_evaluation": efsa_evaluation,
                    "efsa_url": efsa_url,
                    "efsa_date": efsa_date,
                    "additives_classes": additives_classes,
                    "source": "Open Food Facts",
                    "last_updated": datetime.now().isoformat()
                }
                
                processed_additives.append(additive)
                
            except Exception as e:
                logger.warning(f"Error processing additive {key}: {e}")
                continue
        
        logger.info(f"Processed {len(processed_additives)} additives from Open Food Facts")
        return processed_additives
    
    def classify_risk_level(self, additive: Dict[str, Any]) -> tuple[str, str]:
        """
        Classify risk level based on available information.
        Returns (risk_level, risk_color) tuple.
        
        Risk levels:
        - GREEN: Safe additives
        - YELLOW: Limited risk
        - ORANGE: Moderate risk  
        - RED: High risk
        """
        
        efsa_eval = str(additive.get("efsa_evaluation", "")).lower()
        additives_classes = str(additive.get("additives_classes", "")).lower()
        e_number = additive.get("e_number", "")
        
        # High risk (Red) - Known problematic additives
        high_risk_additives = [
            "E102", "E104", "E110", "E122", "E124", "E129",  # Artificial colors
            "E621", "E622", "E623", "E624", "E625",  # MSG and glutamates
            "E951", "E954", "E955",  # Artificial sweeteners
            "E220", "E221", "E222", "E223", "E224", "E225", "E226", "E227", "E228"  # Sulfites
        ]
        
        if (e_number in high_risk_additives or 
            "high concern" in efsa_eval or 
            "banned" in efsa_eval or
            "carcinogen" in efsa_eval):
            return "RED", "red"
        
        # Moderate risk (Orange)
        moderate_risk_keywords = ["concern", "restricted", "allergy", "hyperactivity"]
        if (any(keyword in efsa_eval for keyword in moderate_risk_keywords) or
            any(keyword in additives_classes for keyword in moderate_risk_keywords)):
            return "ORANGE", "orange"
        
        # Limited risk (Yellow) - Artificial but generally safe
        artificial_keywords = ["artificial", "synthetic", "chemical"]
        if (any(keyword in additives_classes for keyword in artificial_keywords) or
            "minor concern" in efsa_eval):
            return "YELLOW", "yellow"
        
        # No risk (Green) - Natural or well-studied safe additives
        safe_keywords = ["natural", "vitamin", "mineral", "safe", "acceptable"]
        if (any(keyword in efsa_eval for keyword in safe_keywords) or
            any(keyword in additives_classes for keyword in safe_keywords) or
            "acceptable daily intake" in efsa_eval):
            return "GREEN", "green"
        
        # Default to limited risk if no clear classification
        return "YELLOW", "yellow"
    
    def get_additive_category(self, additive: Dict[str, Any]) -> str:
        """Determine additive category based on class information."""
        classes = str(additive.get("additives_classes", "")).lower()
        
        category_mapping = {
            "colour": "Food Colors",
            "color": "Food Colors", 
            "preservative": "Preservatives",
            "antioxidant": "Antioxidants",
            "sweetener": "Sweeteners",
            "emulsifier": "Emulsifiers",
            "stabiliser": "Stabilizers",
            "stabilizer": "Stabilizers",
            "thickener": "Thickeners",
            "flavour enhancer": "Flavor Enhancers",
            "flavor enhancer": "Flavor Enhancers",
            "acidity regulator": "Acidity Regulators",
            "anti-caking": "Anti-Caking Agents"
        }
        
        for keyword, category in category_mapping.items():
            if keyword in classes:
                return category
        
        return "Other"
    
    def add_manual_additives(self) -> List[Dict[str, Any]]:
        """Add manually curated additives data for completeness."""
        logger.info("Adding manual additives data...")
        
        manual_additives = [
            {
                "e_number": "E100",
                "name": "Curcumin",
                "vegetarian": "yes",
                "vegan": "yes",
                "efsa_evaluation": "safe",
                "efsa_url": "",
                "efsa_date": "",
                "additives_classes": "natural colour",
                "source": "Manual",
                "last_updated": datetime.now().isoformat()
            },
            {
                "e_number": "E101", 
                "name": "Riboflavin",
                "vegetarian": "yes",
                "vegan": "yes",
                "efsa_evaluation": "safe vitamin",
                "efsa_url": "",
                "efsa_date": "",
                "additives_classes": "natural vitamin colour",
                "source": "Manual",
                "last_updated": datetime.now().isoformat()
            },
            {
                "e_number": "E300",
                "name": "Ascorbic acid",
                "vegetarian": "yes",
                "vegan": "yes", 
                "efsa_evaluation": "safe vitamin",
                "efsa_url": "",
                "efsa_date": "",
                "additives_classes": "natural antioxidant vitamin",
                "source": "Manual",
                "last_updated": datetime.now().isoformat()
            }
        ]
        
        return manual_additives
    
    def create_database_schema(self):
        """Create SQLite database schema optimized for KMP projects."""
        logger.info(f"Creating database schema in {self.db_path}...")
        
        # Remove existing database
        if os.path.exists(self.db_path):
            os.remove(self.db_path)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create main additives table
        cursor.execute('''
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
        )
        ''')
        
        # Create indexes for better performance in KMP
        cursor.execute('CREATE INDEX idx_e_number ON additives(e_number)')
        cursor.execute('CREATE INDEX idx_risk_level ON additives(risk_level)')
        cursor.execute('CREATE INDEX idx_category ON additives(category)')
        cursor.execute('CREATE INDEX idx_name_en ON additives(name)')
        
        # Create metadata table for versioning
        cursor.execute('''
        CREATE TABLE metadata (
            key TEXT PRIMARY KEY,
            value TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # Insert metadata
        cursor.execute('''
        INSERT INTO metadata (key, value) VALUES 
        ('version', '1.0'),
        ('created_date', ?),
        ('total_additives', '0'),
        ('data_sources', 'Open Food Facts, Manual')
        ''', (datetime.now().isoformat(),))
        
        conn.commit()
        conn.close()
        logger.info("Database schema created successfully")
    
    def insert_additives_data(self, additives_list: List[Dict[str, Any]]):
        """Insert additives data into the database."""
        logger.info(f"Inserting {len(additives_list)} additives into database...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        inserted_count = 0
        error_count = 0
        
        for additive in additives_list:
            try:
                # Classify risk level
                risk_level, risk_color = self.classify_risk_level(additive)
                
                # Get category
                category = self.get_additive_category(additive)
                
                # Create description
                description = f"Food additive {additive['e_number']}"
                
                cursor.execute('''
                INSERT OR REPLACE INTO additives (
                    e_number, name, risk_level, risk_color,
                    category, description, vegetarian, vegan,
                    efsa_evaluation, efsa_url, efsa_date, additives_classes,
                    sources, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    additive['e_number'],
                    additive['name'],
                    risk_level,
                    risk_color,
                    category,
                    description,
                    additive.get('vegetarian', ''),
                    additive.get('vegan', ''),
                    additive.get('efsa_evaluation', ''),
                    additive.get('efsa_url', ''),
                    additive.get('efsa_date', ''),
                    additive.get('additives_classes', ''),
                    additive.get('source', ''),
                    additive.get('last_updated', datetime.now().isoformat())
                ))
                
                inserted_count += 1
                
            except Exception as e:
                logger.error(f"Error inserting additive {additive.get('e_number', 'Unknown')}: {e}")
                error_count += 1
                continue
        
        # Update metadata
        cursor.execute('''
        UPDATE metadata SET value = ?, updated_at = CURRENT_TIMESTAMP 
        WHERE key = 'total_additives'
        ''', (str(inserted_count),))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Successfully inserted {inserted_count} additives")
        if error_count > 0:
            logger.warning(f"Failed to insert {error_count} additives")
    
    def generate_statistics(self):
        """Generate and display database statistics."""
        logger.info("Generating database statistics...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Total count
        cursor.execute("SELECT COUNT(*) FROM additives")
        total_count = cursor.fetchone()[0]
        
        # Risk level distribution
        cursor.execute('''
        SELECT risk_level, COUNT(*) 
        FROM additives 
        GROUP BY risk_level 
        ORDER BY COUNT(*) DESC
        ''')
        risk_distribution = cursor.fetchall()
        
        # Category distribution
        cursor.execute('''
        SELECT category, COUNT(*) 
        FROM additives 
        GROUP BY category 
        ORDER BY COUNT(*) DESC
        ''')
        category_distribution = cursor.fetchall()
        
        # Vegetarian/Vegan stats
        cursor.execute("SELECT COUNT(*) FROM additives WHERE vegetarian = 'yes'")
        vegetarian_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM additives WHERE vegan = 'yes'")
        vegan_count = cursor.fetchone()[0]
        
        conn.close()
        
        # Display statistics
        print("\n" + "="*60)
        print("DATABASE STATISTICS")
        print("="*60)
        print(f"Total Additives: {total_count}")
        print(f"Vegetarian-friendly: {vegetarian_count}")
        print(f"Vegan-friendly: {vegan_count}")
        
        print("\nRisk Level Distribution:")
        for risk_level, count in risk_distribution:
            percentage = (count / total_count) * 100 if total_count > 0 else 0
            print(f"  {risk_level}: {count} ({percentage:.1f}%)")
        
        print("\nCategory Distribution:")
        for category, count in category_distribution[:10]:  # Top 10
            percentage = (count / total_count) * 100 if total_count > 0 else 0
            print(f"  {category}: {count} ({percentage:.1f}%)")
        
        print("="*60)
    
    def export_sample_queries(self):
        """Export sample SQL queries for KMP usage."""
        sample_queries = '''
-- Sample SQL Queries for KMP Projects
-- Database: additives.db

-- 1. Get all additives with high risk (Red)
SELECT e_number, name, risk_level
FROM additives 
WHERE risk_color = 'red' 
ORDER BY e_number;

-- 2. Search for additives by name (case-insensitive)
SELECT e_number, name, risk_level
FROM additives 
WHERE LOWER(name) LIKE LOWER('%curcumin%');

-- 3. Get vegetarian-friendly additives
SELECT e_number, name, risk_level
FROM additives 
WHERE vegetarian = 'yes' 
ORDER BY risk_color, e_number;

-- 4. Get additives by category
SELECT category, COUNT(*) as count
FROM additives 
GROUP BY category 
ORDER BY count DESC;

-- 5. Get additives with EFSA evaluation
SELECT e_number, name, efsa_evaluation, risk_level
FROM additives 
WHERE efsa_evaluation != '' 
ORDER BY e_number;

-- 6. Risk level summary
SELECT 
    risk_level,
    risk_color,
    COUNT(*) as count,
    ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM additives), 2) as percentage
FROM additives 
GROUP BY risk_level, risk_color 
ORDER BY count DESC;

-- 7. Search additives for ingredient scanning (by E-number)
SELECT e_number, name, risk_level, risk_color
FROM additives 
WHERE e_number = ?;  -- Parameter for E-number lookup

-- 8. Get all safe additives (Green)
SELECT e_number, name, risk_level
FROM additives 
WHERE risk_color = 'green' 
ORDER BY risk_level, e_number;
        '''
        
        with open("sample_queries.sql", "w", encoding="utf-8") as f:
            f.write(sample_queries)
        
        logger.info("Sample queries exported to sample_queries.sql")
    
    def validate_database(self):
        """Validate the created database structure and data."""
        logger.info("Validating database...")
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Check table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='additives'")
        if not cursor.fetchone():
            raise Exception("Additives table not found!")
        
        # Check for duplicate E-numbers
        cursor.execute('''
        SELECT e_number, COUNT(*) 
        FROM additives 
        GROUP BY e_number 
        HAVING COUNT(*) > 1
        ''')
        duplicates = cursor.fetchall()
        if duplicates:
            logger.warning(f"Found {len(duplicates)} duplicate E-numbers")
        
        # Check for missing required fields
        cursor.execute("SELECT COUNT(*) FROM additives WHERE e_number = '' OR name = ''")
        missing_required = cursor.fetchone()[0]
        if missing_required > 0:
            logger.warning(f"Found {missing_required} records with missing required fields")
        
        # Check risk level distribution
        cursor.execute("SELECT DISTINCT risk_level FROM additives")
        risk_levels = [row[0] for row in cursor.fetchall()]
        expected_levels = ["GREEN", "YELLOW", "ORANGE", "RED"]
        
        for level in risk_levels:
            if level not in expected_levels:
                logger.warning(f"Unexpected risk level found: {level}")
        
        conn.close()
        logger.info("Database validation completed")
    
    def create_kmp_ready_database(self):
        """Main method to create KMP-ready SQLite database."""
        logger.info("Starting SQLite database creation for KMP project...")
        
        try:
            # Step 1: Download data from Open Food Facts
            raw_data = self.download_openfoodfacts_data()
            if not raw_data:
                logger.error("Failed to download data. Exiting.")
                return False
            
            # Step 2: Process the data
            processed_additives = self.process_openfoodfacts_data(raw_data)
            
            # Step 3: Add manual additives for completeness
            manual_additives = self.add_manual_additives()
            all_additives = processed_additives + manual_additives
            
            # Step 4: Create database schema
            self.create_database_schema()
            
            # Step 5: Insert data
            self.insert_additives_data(all_additives)
            
            # Step 6: Validate database
            self.validate_database()
            
            # Step 7: Generate statistics
            self.generate_statistics()
            
            # Step 8: Export sample queries
            self.export_sample_queries()
            
            logger.info(f"Successfully created SQLite database: {self.db_path}")
            logger.info("Database is ready for import into KMP project!")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to create database: {e}")
            return False

def main():
    """Main function to run the script."""
    print("Food Additives SQLite Database Creator for KMP Projects")
    print("=" * 60)
    
    # Allow custom database path via command line argument
    db_path = sys.argv[1] if len(sys.argv) > 1 else "additives.db"
    
    creator = AdditivesSQLiteCreator(db_path)
    success = creator.create_kmp_ready_database()
    
    if success:
        print(f"\n✅ Database successfully created: {db_path}")
        print("Files generated:")
        print(f"  - {db_path} (SQLite database)")
        print("  - sample_queries.sql (SQL examples)")
        print(f"  - additives_sqlite_creation_{datetime.now().strftime('%Y%m%d')}.log (log file)")
        print("\nThe database is now ready for import into your KMP project!")
    else:
        print("\n❌ Failed to create database. Check the log file for details.")
        sys.exit(1)

if __name__ == "__main__":
    main() 