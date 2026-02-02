UPDATE clean_store_transactions
SET DATE = SUBDATE(date(now()),1)
WHERE DATE != SUBDATE(date(now()),1)