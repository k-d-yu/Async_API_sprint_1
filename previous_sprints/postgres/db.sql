/* создание схемы */

create schema if not exists content;

alter role ALL set search_path to content,public; 

/* добавление необходимых типов */

create type content.gender as enum('male', 'female');

create type content.type_prod as enum('tv_show', 'movie');

/* создание таблиц сущностей */

create table if not exists content.film_work (
    id            uuid primary key,
    created       timestamp with time zone not null,
    modified      timestamp with time zone not null,
    title         text not null,
    description   text not null,
    creation_date date,
    rating        numeric(3, 1),
    type          content.type_prod not null
);

create table if not exists content.genre (
    id          uuid primary key,
    created     timestamp with time zone not null,
    modified    timestamp with time zone not null,
    name        text not null,
    description text not null
);

create table if not exists content.person (
    id        uuid primary key,
    created   timestamp with time zone not null,
    modified  timestamp with time zone not null,
    full_name text not null
);

/* создание таблиц пересечений между сущностями */
create table if not exists content.genre_film_work (
    id           uuid primary key,
    created      timestamp with time zone not null,
    genre_id     uuid references content.genre,
    film_work_id uuid references content.film_work
);

create table if not exists content.person_film_work (
    id           uuid primary key,
    created      timestamp with time zone not null,
    person_id    uuid references content.person,
    film_work_id uuid references content.film_work,
    role         text not null
);

/* создание индексов для сущностей */

create index film_work_composite_idx on content.film_work(modified, rating, title);

create index genre_name_idx on content.genre(name);

/* создание индексов для таблиц пересечений */

create unique index genre_film_work_idx on content.genre_film_work(film_work_id, genre_id);

create unique index film_work_person_idx ON content.person_film_work (film_work_id, person_id, role);