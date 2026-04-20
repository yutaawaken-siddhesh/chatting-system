create database chat_app_db;
use chat_app_db;

create table users (
    id int auto_increment primary key,
    username varchar(50) not null unique,
    email varchar(100) not null unique,
    password_hash varchar(255) not null,
    created_at timestamp default current_timestamp
);

create table  profiles (
    user_id int primary key,
    bio text,
    avatar_url varchar(255),
    updated_at timestamp default current_timestamp on update current_timestamp,
    foreign key (user_id) references users(id) on delete cascade
);

create table  friendships (
    user_id1 int,
    user_id2 int,
    status varchar(20) not null default 'pending',
    created_at timestamp default current_timestamp,
    primary key (user_id1, user_id2),
    foreign key (user_id1) references users(id) on delete cascade,
    foreign key (user_id2) references users(id) on delete cascade,
    constraint chk_no_self_friend check (user_id1 != user_id2),
    constraint chk_friend_status check (status in ('pending', 'accepted', 'blocked'))
);

create table  chats (
    id int auto_increment primary key,
    is_group boolean default false,
    created_at timestamp default current_timestamp
);

create table  chat_participants (
    chat_id int,
    user_id int,
    joined_at timestamp default current_timestamp,
    primary key (chat_id, user_id),
    foreign key (chat_id) references chats(id) on delete cascade,
    foreign key (user_id) references users(id) on delete cascade
);

create table  messages (
    id int auto_increment primary key,
    chat_id int not null,
    sender_id int not null,
    message_type varchar(20) not null default 'text',
    content text,
    sent_at timestamp default current_timestamp,
    foreign key (chat_id) references chats(id) on delete cascade,
    foreign key (sender_id) references users(id) on delete cascade,
    constraint chk_msg_type check (message_type in ('text', 'image', 'file'))
);

create table  message_status (
    message_id int,
    user_id int,
    status varchar(20) not null default 'sent',
    updated_at timestamp default current_timestamp on update current_timestamp,
    primary key (message_id, user_id),
    foreign key (message_id) references messages(id) on delete cascade,
    foreign key (user_id) references users(id) on delete cascade,
    constraint chk_msg_status check (status in ('sent', 'delivered', 'read'))
);

create table  attachments (
    id int auto_increment primary key,
    message_id int not null,
    file_url varchar(255) not null,
    file_type varchar(50),
    foreign key (message_id) references messages(id) on delete cascade
);

-- View to get the latest message for each chat . ordering them by 'sent_at' desc, so rank '1' means the latest message.
create or replace view view_latest_messages as
select chat_id, id as message_id, sender_id, content, sent_at
from (
    select 
        m.chat_id, 
        m.id, 
        m.sender_id, 
        m.content, 
        m.sent_at,
        row_number() over(partition by m.chat_id order by m.sent_at desc) as rn
    from messages m
) as ranked_messages
where rn = 1;


select * from chat_participants ;
select * from users;
select * from profiles;
select * from friendships;
select * from chats;
select * from messages;
select * from attachments;
select * from message_status;

create index idx_messages_chat_id on messages(chat_id);
create index idx_messages_sender_id on messages(sender_id);

select 'USERS' as tablename, count(*) as rowcount from users
union all
select 'MESSAGES', count(*) from messages
union all
select 'CHATS', count(*) from chats;