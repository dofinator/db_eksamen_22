begin;

drop table error_log;
drop table users; 
--------------------------------------------------------

-- Create tables

create table users(
	id serial primary key,
	email text UNIQUE,
	password text,
	name text,
	created_on timestamptz NULL DEFAULT now(),
	modified_on timestamptz null default now()
);


create table error_log(
	id serial primary key,
	fk_user_id int,
	error text,
	registered_on timestamptz null default now()
);


--------------------------------------------------------

-- Set foriegn keys

ALTER TABLE public.error_log ADD CONSTRAINT fk_user_id FOREIGN KEY (fk_user_id) REFERENCES public.users(id);

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


--------------------------------------------------------

-- Insert test users

insert into public.users (email,"password",name) values ('test@test.dk','test','test');

insert into public.users (email,"password",name) values ('test2@test.dk','test2','test2');

commit;
