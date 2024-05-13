#!/bin/sh
read -p "Archive Bucket: " archive_bucket
read -p "V1 DB Endpoint: " v1_endpoint
read -p "V1 DB Database: " v1_database
read -p "V1 DB Username: " v1_user
read -s -p "V1 DB Password: " v1_password
echo
read -p "V2 DB Endpoint: " v2_endpoint
read -p "V2 DB Database: " v2_database
read -p "V2 DB Username: " v2_user
read -s -p "V2 DB Password: " v2_password
 
PGPASSWORD=$v1_password psql --host=$v1_endpoint --port=5432 --username=v1_user --dbname=v1_database -c "SELECT 'collections' AS v1_cluster, COUNT(*) AS row_count FROM collections
UNION ALL SELECT 'files' AS files, COUNT(*) AS row_count FROM files
UNION ALL SELECT 'granules' AS granules , COUNT(*) AS row_count FROM granules
UNION ALL SELECT 'providers' AS providers, COUNT(*) as row_count FROM providers
UNION ALL SELECT 'reconcile_catalog_mismatch_report' AS reconcile_catalog_mismatch_report, COUNT(*) as row_count from reconcile_catalog_mismatch_report
UNION ALL SELECT 'reconcile_job' AS reconcile_job, COUNT(*) as row_count FROM reconcile_job
UNION ALL SELECT 'reconcile_orphan_report' AS reconcile_orphan_report, COUNT(*) as row_count FROM reconcile_orphan_report
UNION ALL SELECT 'reconcile_phantom_report' AS reconcile_phantom_report, COUNT(*) as row_count FROM reconcile_phantom_report
UNION ALL SELECT 'reconcile_s3_object' AS reconcile_s3_object, COUNT(*) as row_count FROM reconcile_s3_object
UNION ALL SELECT 'reconcile_s3_object_$archive_bucket' AS reconcile_s3_object_$archive_bucket, COUNT(*) as row_count FROM reconcile_s3_object_$archive_bucket
UNION ALL SELECT 'reconcile_status' AS reconcile_status, COUNT(*) as row_count FROM reconcile_status
UNION ALL SELECT 'recovery_file' AS recovery_file, COUNT(*) as row_count FROM recovery_file
UNION ALL SELECT 'recovery_job' AS recovery_job, COUNT(*) as row_count FROM recovery_job
UNION ALL SELECT 'recovery_status' AS recovery_status, COUNT(*) as row_count FROM recovery_status
UNION ALL SELECT 'schema_versions' AS schema_versions, COUNT(*) as row_count FROM schema_versions
UNION ALL SELECT 'storage_class' AS storage_class, COUNT(*) as row_count FROM storage_class"
 
 
PGPASSWORD=$v2_password psql --host=$v2_endpoint --port=5432 --username=$v2_user --dbname=$v2_database -c "SELECT 'collections' AS v2_cluster, COUNT(*) AS row_count FROM collections
UNION ALL SELECT 'files' AS files, COUNT(*) AS row_count FROM files
UNION ALL SELECT 'granules' AS granules , COUNT(*) AS row_count FROM granules
UNION ALL SELECT 'providers' AS providers, COUNT(*) as row_count FROM providers
UNION ALL SELECT 'reconcile_catalog_mismatch_report' AS reconcile_catalog_mismatch_report, COUNT(*) as row_count from reconcile_catalog_mismatch_report
UNION ALL SELECT 'reconcile_job' AS reconcile_job, COUNT(*) as row_count FROM reconcile_job
UNION ALL SELECT 'reconcile_orphan_report' AS reconcile_orphan_report, COUNT(*) as row_count FROM reconcile_orphan_report
UNION ALL SELECT 'reconcile_phantom_report' AS reconcile_phantom_report, COUNT(*) as row_count FROM reconcile_phantom_report
UNION ALL SELECT 'reconcile_s3_object' AS reconcile_s3_object, COUNT(*) as row_count FROM reconcile_s3_object
UNION ALL SELECT 'reconcile_s3_object_$archive_bucket' AS reconcile_s3_object_$archive_bucket, COUNT(*) as row_count FROM reconcile_s3_object_$archive_bucket
UNION ALL SELECT 'reconcile_status' AS reconcile_status, COUNT(*) as row_count FROM reconcile_status
UNION ALL SELECT 'recovery_file' AS recovery_file, COUNT(*) as row_count FROM recovery_file
UNION ALL SELECT 'recovery_job' AS recovery_job, COUNT(*) as row_count FROM recovery_job
UNION ALL SELECT 'recovery_status' AS recovery_status, COUNT(*) as row_count FROM recovery_status
UNION ALL SELECT 'schema_versions' AS schema_versions, COUNT(*) as row_count FROM schema_versions
UNION ALL SELECT 'storage_class' AS storage_class, COUNT(*) as row_count FROM storage_class"