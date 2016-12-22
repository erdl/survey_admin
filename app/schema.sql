drop table if exists questions;
create table questions (
	id integer primary key autoincrement,
	question text not null,
	answer text not null
);
