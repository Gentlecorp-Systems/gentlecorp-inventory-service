-- drop.sql
-- Drop the reserved_products table first due to the foreign key constraint
DROP TABLE IF EXISTS reserved_item;

-- Drop the inventory table
DROP TABLE IF EXISTS inventory;
