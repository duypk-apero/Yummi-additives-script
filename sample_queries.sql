
-- Sample SQL Queries for KMP Projects
-- Database: additives.db

-- 1. Get all additives with high risk (Red)
SELECT e_number, name_en, name_vi, category 
FROM additives 
WHERE risk_color = 'red' 
ORDER BY e_number;

-- 2. Search for additives by name (case-insensitive)
SELECT e_number, name_en, name_vi, risk_level, category
FROM additives 
WHERE LOWER(name_en) LIKE LOWER('%curcumin%') 
   OR LOWER(name_vi) LIKE LOWER('%curcumin%')
   OR LOWER(e_number) LIKE LOWER('%e100%');

-- 3. Get vegetarian-friendly additives
SELECT e_number, name_en, name_vi, risk_level
FROM additives 
WHERE vegetarian = 'yes' 
ORDER BY risk_color, e_number;

-- 4. Get additives by category
SELECT category, COUNT(*) as count
FROM additives 
GROUP BY category 
ORDER BY count DESC;

-- 5. Get additives with EFSA evaluation
SELECT e_number, name_en, efsa_evaluation, risk_level
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
SELECT e_number, name_en, name_vi, risk_level, risk_color, category
FROM additives 
WHERE e_number = ?;  -- Parameter for E-number lookup

-- 8. Get all safe additives (Green)
SELECT e_number, name_en, name_vi, category
FROM additives 
WHERE risk_color = 'green' 
ORDER BY category, e_number;
        