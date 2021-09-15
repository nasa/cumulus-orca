SELECT pg_terminate_backend(pg_stat_activity.pid)
FROM pg_stat_activity
WHERE pg_stat_activity.datname = 'disaster_recovery';
DROP DATABASE disaster_recovery
GO
