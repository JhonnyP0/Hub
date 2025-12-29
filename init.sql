create table users (
    id int auto_increment primary key,
    username varchar(50) not null unique,
    password_hash varchar(255) not null,
    email varchar(100) not null unique,
    is_confirmed boolean default false,
    created_at timestamp default current_timestamp
);

create table posts (
    id int auto_increment primary key,
    user_id int not null,
    content text not null,
    opinion_score tinyint default 10,
    created_at timestamp default current_timestamp,
    foreign key (user_id) references users(id) on delete cascade
);