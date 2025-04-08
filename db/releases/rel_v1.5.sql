create table if not exists  
product_ean_mapping 
(ean varchar(50) not null,
 product_id varchar(50) not null,
 primary key (ean));

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM jobs
        WHERE name = 'ETL_import_product_ids'
    ) THEN
        insert into jobs (name, schedule, active) 
            values ('ETL_import_product_ids', '0 6 * * *', true);
    END IF;
END $$;

update jobs
set schedule = '0 6 * * *',
    parameters = '{"url": "https://panel-e.baselinker.com/inventory_export.php?hash=2842f5bb1c19498c5cfa69f0216b94be"}'
    active = true
where name = 'ETL_import_product_ids';