
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

-- 9. Search by taxonomy ID (exact match for variants)
SELECT taxonomy_id, e_number, name, risk_level, risk_color
FROM additives 
WHERE taxonomy_id = ?;  -- Parameter for exact taxonomy lookup (e.g., 'en:e420i')

-- 10. Get all variants of a specific E-number
SELECT taxonomy_id, e_number, name, risk_level, risk_color
FROM additives 
WHERE e_number = '420'  -- Shows E420, E420i, E420ii
ORDER BY taxonomy_id;

-- 11. Compare risk levels within same E-number family
SELECT 
    e_number,
    COUNT(*) as variant_count,
    COUNT(DISTINCT risk_level) as different_risk_levels,
    GROUP_CONCAT(DISTINCT risk_level) as risk_levels
FROM additives 
GROUP BY e_number 
HAVING COUNT(*) > 1 AND COUNT(DISTINCT risk_level) > 1
ORDER BY different_risk_levels DESC;

-- 12. Find potentially risky variants within safe E-numbers
SELECT 
    a1.e_number,
    a1.taxonomy_id as safe_variant,
    a1.risk_level as safe_risk,
    a2.taxonomy_id as risky_variant,
    a2.risk_level as risky_risk
FROM additives a1
JOIN additives a2 ON a1.e_number = a2.e_number
WHERE a1.risk_color = 'green' 
  AND a2.risk_color IN ('orange', 'red')
ORDER BY a1.e_number;
        