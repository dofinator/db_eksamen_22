begin;
--abort;
drop table if exists error_log;
drop table if exists users; 
drop table if exists roles;


--------------------------------------------------------

-- Create tables

create table users(
	id serial primary key,
	email text unique,
	password text,
	name text,
	role text default 'user',
	admin_is_allowed boolean default false,
	created_on timestamptz null default now(),
	modified_on timestamptz null default now()
);

create table roles(
	role text primary key,
	created_on timestamptz null default now(),
	modified_on timestamptz null default now()
);


create table error_log(
	id serial primary key,
	fk_user_id int default null,
	error text,
	registered_on timestamptz null default now()
);


--------------------------------------------------------

-- Set foriegn keys

alter table public.error_log add constraint fk_user_id foreign key (fk_user_id) references public.users(id);
alter table public.users add constraint fk_role foreign key (role) references public.roles(role);
--------------------------------------------------------

-- Trigger for when any of the users data is modified

/* Function for setting modified_on = now() timestamptz*/
CREATE OR REPLACE FUNCTION trigger_set_timestamptz_on()
RETURNS TRIGGER AS $$
BEGIN
  new.modified_on = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

/* Trigger on the users table */
CREATE TRIGGER set_timestamptz_modified_on
before update on public.users
FOR EACH row 
EXECUTE PROCEDURE trigger_set_timestamptz_on();

/* Trigger on the users table */
CREATE TRIGGER set_timestamptz_modified_on
before update on public.roles
FOR EACH row 
EXECUTE PROCEDURE trigger_set_timestamptz_on();

--------------------------------------------------------

-- Insert roles
insert into public.roles (role) values ('user');
insert into public.roles (role) values ('admin');

-- Insert admin
insert into public.users (email,"password",name,role) values ('admin@admin.com','pbkdf2:sha256:260000$BF5lbo1SVwscE7BL$234537f55d246ae028b4a704c68189857ebabb7ae4b271e83232bd2c8b68b1fa','christoffer','admin');
insert into public.users (email,"password",name,role) values ('user@user.com','pbkdf2:sha256:260000$BF5lbo1SVwscE7BL$234537f55d246ae028b4a704c68189857ebabb7ae4b271e83232bd2c8b68b1fa','sumit','user');

commit;