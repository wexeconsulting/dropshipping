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

