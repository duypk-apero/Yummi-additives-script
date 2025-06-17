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
                    "taxonomy_id": key,
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
        Classify risk level based on available information and scientific consensus.
        Returns (risk_level, risk_color) tuple.
        
        Risk levels:
        - GREEN: Safe additives (natural, vitamins, minerals)
        - YELLOW: Limited risk (generally safe but synthetic)
        - ORANGE: Moderate risk (some health concerns documented)
        - RED: High risk (significant health concerns or restrictions)
        """
        
        e_number = additive.get("e_number", "")
        additives_classes = str(additive.get("additives_classes", "")).lower()
        name = str(additive.get("name", "")).lower()
        efsa_eval = str(additive.get("efsa_evaluation", "")).lower()
        
        # HIGH RISK (Red) - Additives with documented health concerns
        high_risk_additives = {
            # Artificial colors linked to hyperactivity
            "102", "104", "110", "122", "124", "129", "131", "132", "133",
            "127", "154", "180",
            # Controversial sweeteners
            "951", "954", "955", "961",  # Aspartame, Saccharin, Sucralose, Neotame
            # Sulfites (allergens)
            "220", "221", "222", "223", "224", "225", "226", "227", "228",
            # Nitrates/Nitrites (preservation concerns)
            "249", "250", "251", "252",
            # MSG and related (sensitivities)
            "621", "622", "623", "624", "625",
            # Controversial preservatives
            "210", "211", "212", "213", "214", "215", "216", "217", "218", "219",
            # Trans fat related
            "441", "442",
            # Aluminum compounds
            "173", "541", "554", "555", "556", "559",
            # Questionable emulsifiers
            "407a", "425", "466"
        }
        
        if e_number in high_risk_additives:
            return "RED", "red"
        
        # ORANGE (Moderate risk) - Some concerns but widely used
        moderate_risk_additives = {
            # Some phosphates (overexposure concerns)
            "338", "339", "340", "341", "343", "450", "451", "452",
            # Some carrageenan
            "407",
            # Some antioxidants with restrictions
            "320", "321", "310", "311", "312", "319", "324",
            # Some synthetic colors (less problematic than red category)
            "123", "155", "160b", "161g", "163",
            # Some controversial thickeners
            "414", "415", "418", "460", "461", "462", "463", "464", "465",
            "466", "468", "469",
            # Potassium bromate and similar
            "924", "925", "926", "927", "928",
            # Some synthetic flavoring
            "150c", "150d"  # Caramel colors with ammonia
        }
        
        if e_number in moderate_risk_additives:
            return "ORANGE", "orange"
        
        # GREEN (Safe) - Natural, vitamins, minerals, generally recognized as safe
        safe_additives = {
            # Vitamins
            "101", "101i", "101ii",  # Riboflavin
            "300", "301", "302", "303", "304", "304i", "304ii",  # Vitamin C compounds
            "306", "307", "307a", "307b", "307c", "308", "309",  # Tocopherols (Vitamin E)
            # Natural colors
            "100",  # Curcumin
            "140", "140i", "140ii",  # Chlorophylls
            "160a", "160ai", "160aii",  # Carotenes
            "160c", "160d", "160e", "160f",  # Natural carotenoids
            "161a", "161b", "161c", "161d", "161e", "161f", "161h", "161i", "161j",
            "162",  # Beetroot red
            "163a", "163b", "163c", "163d", "163e", "163f",  # Anthocyanins
            # Natural acids and salts
            "330",  # Citric acid
            "331", "331i", "331ii", "331iii",  # Sodium citrates
            "332", "332i", "332ii",  # Potassium citrates
            "333", "333i", "333ii", "333iii",  # Calcium citrates
            "334",  # Tartaric acid
            "335", "335i", "335ii",  # Sodium tartrates
            "336", "336i", "336ii",  # Potassium tartrates
            "337",  # Potassium sodium tartrate
            # Natural extracts
            "150a",  # Plain caramel
            "200", "202", "203",  # Sorbic acid and sorbates
            "270",  # Lactic acid
            "290",  # Carbon dioxide
            "322", "322i", "322ii",  # Lecithin
            "401", "402", "403", "404", "405", "406",  # Natural gums (alginate, agar, etc.)
            "407",  # Carrageenan (basic form)
            "410", "412", "413", "415", "416", "417",  # Natural gums
            "440", "440i", "440ii",  # Pectins
            "471",  # Mono/diglycerides (when from natural sources)
            # Natural minerals
            "500", "500i", "500ii", "500iii",  # Sodium carbonates
            "501", "501i", "501ii",  # Potassium carbonates
            "503", "503i", "503ii",  # Ammonium carbonates
            "504", "504i", "504ii",  # Magnesium carbonates
            "507",  # Hydrochloric acid
            "508",  # Potassium chloride
            "509",  # Calcium chloride
            "511",  # Magnesium chloride
            "513",  # Sulfuric acid
            "514", "514i", "514ii",  # Sodium sulfates
            "515", "515i", "515ii",  # Potassium sulfates
            "516",  # Calcium sulfate
            "517",  # Ammonium sulfate
            "518",  # Magnesium sulfate
            # Natural sweeteners
            "420", "420i", "420ii",  # Sorbitol
            "965", "965i", "965ii",  # Maltitol
            "967",  # Xylitol
            "968",  # Erythritol
            "960",  # Stevia glycosides
            # Gases
            "938", "939", "941", "942", "948", "949",  # Various gases
        }
        
        if e_number in safe_additives:
            return "GREEN", "green"
        
        # Check by category for additional classification
        if "colour" in additives_classes or "color" in additives_classes:
            if any(danger in name for danger in ["artificial", "synthetic", "azo"]):
                return "ORANGE", "orange"
            else:
                return "YELLOW", "yellow"
        
        if "preservative" in additives_classes:
            if any(concern in name for concern in ["benzoate", "sulfite", "nitrite", "nitrate"]):
                return "ORANGE", "orange"
            else:
                return "YELLOW", "yellow"
        
        if "sweetener" in additives_classes:
            if "artificial" in name or any(sweet in name for sweet in ["aspartame", "saccharin", "acesulfame"]):
                return "ORANGE", "orange"
            else:
                return "YELLOW", "yellow"
        
        # Natural categories tend to be safer
        if any(natural in additives_classes for natural in ["antioxidant", "vitamin", "mineral"]):
            return "GREEN", "green"
        
        if any(natural in name for natural in ["natural", "vitamin", "mineral", "citric", "lactic", "ascorbic"]):
            return "GREEN", "green"
        
        # Emulsifiers and thickeners - mostly yellow unless specifically problematic
        if any(category in additives_classes for category in ["emulsifier", "thickener", "stabiliser", "stabilizer"]):
            return "YELLOW", "yellow"
        
        # Default to limited risk for unclassified additives
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
                "taxonomy_id": "manual_e100",
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
                "taxonomy_id": "manual_e101",
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
                "taxonomy_id": "manual_e300",
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
    
    def create_detailed_description(self, additive: Dict[str, Any], risk_level: str, category: str) -> str:
        """Create a comprehensive description for the additive."""
        e_number = additive.get("e_number", "")
        name = additive.get("name", "").strip()
        additives_classes = additive.get("additives_classes", "").lower()
        efsa_evaluation = additive.get("efsa_evaluation", "").lower()
        vegetarian = additive.get("vegetarian", "").lower()
        vegan = additive.get("vegan", "").lower()
        
        # Start with basic function description based on category and classes
        function_descriptions = {
            "Colors": "food coloring agent",
            "Preservatives": "food preservative", 
            "Antioxidants": "antioxidant to prevent spoilage",
            "Sweeteners": "artificial sweetener",
            "Emulsifiers": "emulsifier to blend ingredients",
            "Stabilizers": "stabilizer to maintain texture",
            "Thickeners": "thickening agent",
            "Acidity_Regulators": "acidity regulator",
            "Flavor_Enhancers": "flavor enhancer",
            "Anti_Caking_Agents": "anti-caking agent to prevent clumping",
            "Foaming_Agents": "foaming agent",
            "Glazing_Agents": "glazing agent for surface coating",
            "Humectants": "humectant to retain moisture",
            "Bulking_Agents": "bulking agent to add volume",
            "Sequestrants": "sequestrant to bind metals"
        }
        
        # Get base function description
        base_function = function_descriptions.get(category, "food additive")
        
        # Enhanced descriptions based on additive classes
        if "colour" in additives_classes or "color" in additives_classes:
            if "natural" in additives_classes:
                base_function = "natural food coloring derived from plants or minerals"
            elif "synthetic" in additives_classes or "artificial" in additives_classes:
                base_function = "artificial food coloring"
            else:
                base_function = "food coloring agent"
                
        elif "preservative" in additives_classes:
            if "natural" in additives_classes:
                base_function = "natural preservative to extend shelf life"
            else:
                base_function = "preservative to prevent spoilage and extend shelf life"
                
        elif "antioxidant" in additives_classes:
            if "vitamin" in additives_classes:
                base_function = "vitamin with antioxidant properties"
            elif "natural" in additives_classes:
                base_function = "natural antioxidant to prevent rancidity"
            else:
                base_function = "antioxidant to prevent oxidation and rancidity"
                
        elif "sweetener" in additives_classes:
            if "artificial" in additives_classes:
                base_function = "artificial sweetener with high sweetening power"
            elif "natural" in additives_classes:
                base_function = "natural sweetening agent"
            else:
                base_function = "sweetening agent"
                
        elif "emulsifier" in additives_classes:
            base_function = "emulsifier to help mix oil and water-based ingredients"
            
        elif "stabilizer" in additives_classes or "stabiliser" in additives_classes:
            base_function = "stabilizer to maintain food texture and consistency"
            
        elif "thickener" in additives_classes or "thickening" in additives_classes:
            base_function = "thickening agent to increase viscosity"
            
        elif "flavour" in additives_classes or "flavor" in additives_classes:
            if "enhancer" in additives_classes:
                base_function = "flavor enhancer to intensify taste"
            else:
                base_function = "flavoring agent"
                
        elif "acid" in additives_classes:
            base_function = "acidity regulator to control pH levels"
            
        # Build comprehensive description
        description_parts = []
        
        # Add the main function
        description_parts.append(f"{name} ({e_number}) is a {base_function}")
        
        # Add safety/risk information
        risk_descriptions = {
            "GREEN": "considered safe with no known health concerns",
            "YELLOW": "generally safe but may have some limitations or sensitivities", 
            "ORANGE": "has some documented health concerns or restrictions",
            "RED": "has significant health concerns and should be consumed with caution"
        }
        
        if risk_level in risk_descriptions:
            description_parts.append(f"It is {risk_descriptions[risk_level]}")
        
        # Add dietary information
        dietary_info = []
        if vegetarian == "yes":
            dietary_info.append("vegetarian-friendly")
        if vegan == "yes":
            dietary_info.append("vegan-friendly")
        elif vegetarian == "yes" and vegan != "yes":
            dietary_info.append("vegetarian-friendly but not vegan")
            
        if dietary_info:
            description_parts.append(f"This additive is {' and '.join(dietary_info)}")
        
        # Add EFSA evaluation if available
        if efsa_evaluation and "safe" in efsa_evaluation:
            description_parts.append("EFSA has evaluated this additive as safe for consumption")
        elif efsa_evaluation and efsa_evaluation not in ["", "unknown"]:
            description_parts.append(f"EFSA evaluation: {efsa_evaluation}")
        
        # Add specific usage information for common additives
        specific_usage = self.get_specific_usage_info(e_number, name.lower())
        if specific_usage:
            description_parts.append(specific_usage)
        
        return ". ".join(description_parts) + "."
    
    def get_specific_usage_info(self, e_number: str, name: str) -> str:
        """Get specific usage information for well-known additives."""
        specific_info = {
            "E100": "Commonly used in curry powders, mustard, and dairy products for its golden yellow color",
            "E101": "Essential B-vitamin naturally found in milk, eggs, and green vegetables",
            "E102": "Bright yellow synthetic dye often used in confectionery and beverages",
            "E104": "Yellow synthetic dye used in processed foods and cosmetics",
            "E110": "Orange-yellow synthetic dye commonly found in orange-flavored products",
            "E120": "Natural red dye derived from cochineal insects, used in cosmetics and foods",
            "E122": "Synthetic red dye used in confectionery, beverages, and desserts",
            "E124": "Synthetic red dye commonly used in processed foods and beverages",
            "E129": "Synthetic orange-red dye used in confectionery and beverages",
            "E131": "Synthetic blue dye used in confectionery and beverages",
            "E132": "Synthetic blue dye commonly used in processed foods",
            "E133": "Synthetic blue dye used in confectionery, beverages, and cosmetics",
            "E140": "Natural green pigment derived from plants, used in food coloring",
            "E150": "Brown coloring made from heated sugars, commonly used in cola drinks",
            "E160a": "Natural orange pigment from carrots and other plants",
            "E160c": "Natural red-orange pigment from paprika",
            "E162": "Natural purple-red pigment from beetroot",
            "E163": "Natural purple pigment from grapes and berries",
            "E200": "Natural preservative found in berries, used to prevent mold and yeast growth",
            "E202": "Synthetic preservative commonly used in baked goods and beverages",
            "E210": "Synthetic preservative used in pickled foods and beverages",
            "E211": "Synthetic preservative commonly used in soft drinks and acidic foods",
            "E220": "Preservative and antioxidant used in dried fruits and wine",
            "E249": "Preservative used primarily in processed meats to prevent botulism",
            "E250": "Preservative used in cured meats to maintain color and prevent bacteria",
            "E300": "Vitamin C, essential nutrient and powerful antioxidant",
            "E301": "Sodium salt of Vitamin C, used as antioxidant and preservative",
            "E306": "Natural Vitamin E, powerful antioxidant found in vegetable oils",
            "E330": "Natural acid found in citrus fruits, used as preservative and flavor enhancer",
            "E407": "Natural thickener derived from seaweed, used in dairy products",
            "E412": "Natural thickener from guar beans, used in gluten-free products",
            "E414": "Natural thickener from acacia trees, used in confectionery",
            "E415": "Thickener produced by fermentation, used in gluten-free baking",
            "E420": "Natural sugar alcohol used as sweetener and humectant",
            "E421": "Natural sugar alcohol found in fruits, used as sweetener",
            "E440": "Natural thickener from fruits, used in jams and jellies",
            "E471": "Emulsifier derived from plant or animal fats, used in baked goods",
            "E500": "Baking soda, natural mineral used as raising agent",
            "E621": "Flavor enhancer naturally found in seaweed and aged cheeses",
            "E950": "Artificial sweetener 200 times sweeter than sugar",
            "E951": "Artificial sweetener 200 times sweeter than sugar, contains phenylalanine",
            "E952": "Artificial sweetener used in sugar-free products",
            "E954": "Artificial sweetener 300 times sweeter than sugar",
            "E955": "Artificial sweetener 600 times sweeter than sugar"
        }
        
        # Check by E-number first
        if e_number in specific_info:
            return specific_info[e_number]
        
        # Check by name patterns
        if "curcumin" in name:
            return "Commonly used in curry powders, mustard, and dairy products for its golden yellow color"
        elif "riboflavin" in name:
            return "Essential B-vitamin naturally found in milk, eggs, and green vegetables"
        elif "ascorbic" in name:
            return "Essential vitamin and powerful antioxidant naturally found in citrus fruits"
        elif "citric" in name:
            return "Natural acid found in citrus fruits, widely used as preservative and flavor enhancer"
        elif "lecithin" in name:
            return "Natural emulsifier found in egg yolks and soybeans, used in chocolate and baked goods"
        elif "pectin" in name:
            return "Natural thickener found in fruits, commonly used in jams and jellies"
        elif "gellan" in name:
            return "Thickener produced by fermentation, used in plant-based milk alternatives"
        
        return ""
    
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
            taxonomy_id TEXT UNIQUE NOT NULL,
            e_number TEXT NOT NULL,
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
        cursor.execute('CREATE INDEX idx_taxonomy_id ON additives(taxonomy_id)')
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
                
                # Create comprehensive description
                description = self.create_detailed_description(additive, risk_level, category)
                
                cursor.execute('''
                INSERT OR REPLACE INTO additives (
                    taxonomy_id, e_number, name, risk_level, risk_color,
                    category, description, vegetarian, vegan,
                    efsa_evaluation, efsa_url, efsa_date, additives_classes,
                    sources, last_updated
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    additive.get('taxonomy_id', f"manual_{additive['e_number']}"),
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