CREATE TYPE stream_event_type     AS ENUM ('post', 'comment', 'share', 'topic_post');
CREATE TYPE stream_action_type    AS ENUM ('new', 'update', 'delete', 'restore');
CREATE TYPE user_deactivated_type AS ENUM ('deleted', 'banned');
-- CREATE TYPE stream_event_platform_type AS ENUM ('new', 'update', 'delete', 'restore');

create table event_authors (
    user_id             bigint primary key,
    update_time         timestamp,
    is_closed           boolean,
    can_access_closed   boolean,
    has_mobile          boolean,
    has_photo           boolean,
    current_city_id     integer,
    country_id          integer,
    military_until      integer,
    photos_count        integer,
    sex                 integer,
    verified            integer,
    relation            integer, -- семейное положение
    education_graduation integer,

    -- counters
    followers_count     integer,
    friends_count       integer,
    groups_count        integer,

    deactivated         user_deactivated_type,

    personal_position   jsonb,
    schools             jsonb,
    universities        jsonb,

    relatives_id        integer[],

    last_name           varchar(128),
    first_name          varchar(128),
    -- contacts
    phone               char(64),
    skype               varchar(128),
    facebook            varchar(128),
    twitter             varchar(128),
    livejournal         varchar(128),
    instagram           varchar(128),
    -- stuff
    education_university varchar(128),
    home_town           varchar(128),

    about               text,
    activities          text,
    birthdate           text
);

create table stream_events (
    id              serial primary key,
    author_id       bigint not null references event_authors(user_id),
    shared_post_author_id bigint,
    action_time     timestamp,
    creation_time   timestamp,
    platform        smallint,
    event_type      stream_event_type,
    action          stream_action_type,
    -- objects
    attachments     jsonb,
    geo             jsonb,
    event_id        jsonb,
    tags            text[],
    event_text      text
);
