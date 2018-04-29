drop table if exists question;
create table question (
	questionid 	integer primary key autoincrement,
	questiontext 	text not null,
	questionurl	text not null unique
);

drop table if exists response;
create table response (
	responseid 	integer primary key autoincrement,
	responsetime	integer not null,
	response 	integer not null,
	questionid	integer not null,
	optionid	integer not null,
	FOREIGN KEY(questionid) REFERENCES question(questionid),
	FOREIGN KEY(optionid) REFERENCES response(responseid)
);

drop table if exists option;
create table option (
	optionid	integer primary key autoincrement,
	optiontext	text not null,
	questionid	integer not null,
	FOREIGN KEY(questionid) REFERENCES question(questionid)
);
	
drop table if exists activequestion;
create table activequestion (
	activequestionid	integer primary key autoincrement,
	activequestionurl	text not null unique,
	FOREIGN KEY(questionid) REFERENCES question(questionid)
);
	

	 
