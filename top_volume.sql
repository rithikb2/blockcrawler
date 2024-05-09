SELECT b.block_hex, SUM(t.transaction_value) as total_value 
FROM blocks b, transactions t
WHERE b.block_hex = t.block_hex AND b.block_timestamp BETWEEN '2024-01-01 00:00:00' AND '2024-01-01 00:30:00'
GROUP BY b.block_hex
ORDER BY total_value DESC
LIMIT 1;