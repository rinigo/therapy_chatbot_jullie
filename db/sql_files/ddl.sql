create table if not exists users (
id bigserial primary key,
sender_id bigint not null unique,
first_name varchar(255) not null,
middle_name varchar(255) null default null,
last_name varchar(255) null default null,
nickname varchar(255) null default null,
status smallint not null default 0,
created_at timestamp not null default CURRENT_TIMESTAMP
);

create table sessions (
id bigserial primary key,
user_id bigint not null references users(id),
status smallint not null default 0,
mood_start varchar(255) null default null,
mood_end varchar(255) null default null,
created_at timestamp not null default current_timestamp,
finish_at timestamp  not null default current_timestamp
);

create table if not exists message_clusters (
id bigserial primary key,
user_id bigint not null references users(id),
length varchar(255) null default null,
created_at timestamp not null default CURRENT_TIMESTAMP
);

create table if not exists reactions (
id bigserial primary key,
user_id bigint references users(id),
reaction_id smallint not null default 0,
reaction_type varchar(255) not null,
status smallint not null default 0,
created_at timestamp not null default CURRENT_TIMESTAMP
);

create table if not exists messages (
id bigserial primary key,
user_id bigint not null references users(id),
cluster_id bigint null default null references message_clusters(id),
message varchar(255) not null,
status smallint not null default 0,
read_flag smallint not null default 0,
intent varchar(255) default null,
created_at timestamp not null default CURRENT_TIMESTAMP
);

create table if not exists responses (
id bigserial primary key,
user_id bigint references users(id),
cluster_id bigint references message_clusters(id),
response varchar(255) not null,
sent_at timestamp not null,
sent_flag smallint not null default 0,
created_at timestamp not null default CURRENT_TIMESTAMP
);

create table if not exists reminds (
id bigserial primary key, 
user_id bigint references users(id),
type smallint not null default 0,
created_at timestamp not null default CURRENT_TIMESTAMP
);

create table if not exists users_feelings (
id bigserial primary key,
user_id bigint references users(id),
keyword varchar(255) not null,
created_at timestamp not null default CURRENT_TIMESTAMP
);

create table if not exists intro_positions (
id bigserial primary key,
user_id bigint references users(id),
position varchar(255) not null default 0,
created_at timestamp not null default CURRENT_TIMESTAMP,
finished_at timestamp default CURRENT_TIMESTAMP
);