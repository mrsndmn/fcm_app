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
    author_id       bigint not null, -- references event_authors(user_id)
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

alter table stream_events add column attachment_text text;

update stream_events set attachment_text = att.attachment_text
    from
    stream_events se,
    lateral (
        select case
            when jsonb_extract_path_text(a.value, 'type') = 'link'           then jsonb_extract_path_text(a.value, 'link', 'title') || ' ' || jsonb_extract_path(a.value, 'link', 'description')
            when jsonb_extract_path_text(a.value, 'type') = 'photo'          then jsonb_extract_path_text(a.value, 'photo', 'text')
            when jsonb_extract_path_text(a.value, 'type') = 'video'          then jsonb_extract_path_text(a.value, 'video', 'title') || ' ' || jsonb_extract_path(a.value, 'video', 'description')
            when jsonb_extract_path_text(a.value, 'type') = 'audo'           then jsonb_extract_path_text(a.value, 'audio', 'title') || ' ' || jsonb_extract_path(a.value, 'audio', 'artist')
            when jsonb_extract_path_text(a.value, 'type') = 'album'          then jsonb_extract_path_text(a.value, 'album', 'title') || ' ' || jsonb_extract_path(a.value, 'album', 'text')
            when jsonb_extract_path_text(a.value, 'type') = 'doc'            then jsonb_extract_path_text(a.value, 'doc', 'title')
            when jsonb_extract_path_text(a.value, 'type') = 'page'           then jsonb_extract_path_text(a.value, 'page', 'title')
            when jsonb_extract_path_text(a.value, 'type') = 'poll'           then jsonb_extract_path_text(a.value, 'poll', 'question')
            when jsonb_extract_path_text(a.value, 'type') = 'market_album'   then jsonb_extract_path_text(a.value, 'market_album', 'title')
            when jsonb_extract_path_text(a.value, 'type') = 'podcast'        then jsonb_extract_path_text(a.value, 'podcast', 'title')
            when jsonb_extract_path_text(a.value, 'type') = 'podcast'        then jsonb_extract_path_text(a.value, 'podcast', 'title')
            when jsonb_extract_path_text(a.value, 'type') = 'note'           then jsonb_extract_path_text(a.value, 'note', 'title') || ' ' || jsonb_extract_path(a.value, 'note', 'text')
            else ''
        end as attachment_text
        from jsonb_array_elements(se.attachments) a
    ) att
where jsonb_typeof(se.attachments) != 'null';

update stream_events set attachment_text = att.attachment_text
    from
    stream_events se,
    lateral (
        select case
            when jsonb_extract_path_text(a.value, 'type') = 'link'           then jsonb_extract_path_text(a.value, 'link', 'title') || ' ' || jsonb_extract_path(a.value, 'link', 'description')
            when jsonb_extract_path_text(a.value, 'type') = 'photo'          then jsonb_extract_path_text(a.value, 'photo', 'text')
            when jsonb_extract_path_text(a.value, 'type') = 'video'          then jsonb_extract_path_text(a.value, 'video', 'title') || ' ' || jsonb_extract_path(a.value, 'video', 'description')
            when jsonb_extract_path_text(a.value, 'type') = 'audo'           then jsonb_extract_path_text(a.value, 'audio', 'title') || ' ' || jsonb_extract_path(a.value, 'audio', 'artist')
            when jsonb_extract_path_text(a.value, 'type') = 'album'          then jsonb_extract_path_text(a.value, 'album', 'title') || ' ' || jsonb_extract_path(a.value, 'album', 'text')
            when jsonb_extract_path_text(a.value, 'type') = 'doc'            then jsonb_extract_path_text(a.value, 'doc', 'title')
            when jsonb_extract_path_text(a.value, 'type') = 'page'           then jsonb_extract_path_text(a.value, 'page', 'title')
            when jsonb_extract_path_text(a.value, 'type') = 'poll'           then jsonb_extract_path_text(a.value, 'poll', 'question')
            when jsonb_extract_path_text(a.value, 'type') = 'market_album'   then jsonb_extract_path_text(a.value, 'market_album', 'title')
            when jsonb_extract_path_text(a.value, 'type') = 'podcast'        then jsonb_extract_path_text(a.value, 'podcast', 'title')
            when jsonb_extract_path_text(a.value, 'type') = 'podcast'        then jsonb_extract_path_text(a.value, 'podcast', 'title')
            when jsonb_extract_path_text(a.value, 'type') = 'note'           then jsonb_extract_path_text(a.value, 'note', 'title') || ' ' || jsonb_extract_path(a.value, 'note', 'text')
            else ''
        end as attachment_text
        from jsonb_array_elements(se.attachments) a
    ) att
where jsonb_typeof(se.attachments) != 'null' and stream_events.id = se.id;

alter table stream_events drop column attachments;
vacuum full;

alter table stream_events add column text_tsvector tsvector;
update stream_events set text_tsvector = to_tsvector('russian', event_text || attachment_text );

-- alter table stream_events rename column tags stream_tags;
-- alter table add column tags []text;


create table stream_rules (
    id serial primary key,
    value varchar(1024) not null,
    last_updated timestamp without time zone default CURRENT_TIMESTAMP not null
);