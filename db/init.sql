create table if not exists 
jobs (
    id serial primary key,
    name varchar(100) not null,
    schedule varchar(100) not null,
    parameters jsonb,
    active boolean default true
);

create table if not exists 
configs (
    id serial primary key,
    name varchar(100) not null,
    url varchar(1000) not null,
    value jsonb
    
);

create table if not exists 
margin_data (
    ean varchar(100) not null,
    margin float not null,
    configs_id int not null,
    foreign key (configs_id) references configs(id),
    primary key (ean, configs_id)
);

DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM configs
        WHERE name = 'HomeGarden'
    ) THEN
        INSERT INTO configs ("name", value, url) VALUES
            ('HomeGarden', '{"fields": {"ean": "Ean", "name": "Nazwa", "price": "Cena_zakupu_netto", "photos": {"prefix": "image_extra_", "firstElem": "image", "collection": "Linki_do_zdjec/Link_do_zdjecia", "maxMappedElems": 16}, "quantity": "Stan_mag", "tax_rate": "Vat", "description": "Opis", "category_name": "Kategoria", "manufacturer_name": "Marka"}, "defaultMargin": 0.2, "product_index": "./Produkt"}', 'https://pim.homegarden.com.pl/feeds/vip-h2g5xfm456');
    END IF;
END $$;