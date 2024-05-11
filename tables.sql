create database divar;
show databases;

# entity
CREATE TABLE divar.normal_user(
    userID int primary key not null,
    first_name varchar(255),
    last_name varchar(255),
	registered_at datetime not null,
    country varchar(255),
    state varchar(255),
    city varchar(255),
    street varchar(255),
    house_num int,
    is_active boolean
);

# entity
CREATE TABLE divar.admin_user(
    userID int primary key not null references user,
    first_name varchar(255),
    last_name varchar(255),
	registered_at datetime not null,
    country varchar(255),
    state varchar(255),
    city varchar(255),
    street varchar(255),
    house_num int
);

# error
# MN relation
CREATE TABLE divar.visit(
    userID int primary key not null references normal_user,
    adID int primary key not null references advertise
);

# multivalue adj
CREATE TABLE divar.email(
    userID int not null references normal_user,
    email varchar(255) primary key not null
);

# multivalue adj
CREATE TABLE divar.phone(
    userID int not null references normal_user,
    phone varchar(255) primary key not null
);

# entity
CREATE TABLE divar.business(
    businessID int primary key not null,
    userID int not null references normal_user,
    bus_name varchar(255) not null,
    category varchar(255),
    registration_num int,
    country varchar(255),
    state varchar(255),
    city varchar(255),
    street varchar(255),
    house_num int
);

# entity
CREATE TABLE divar.creator(
    creatorID int primary key not null,
    creator_type varchar(255) not null, 
    is_active boolean
);

# error 
# entity
CREATE TABLE divar.advertise(
    adID int primary key not null,
    creatorID int primary key not null references normal_user,
    title varchar(255) not null,
    price varchar(255) not null,
    descriptions varchar(255),
    subtitle varchar(255),
    country varchar(255),
    state varchar(255),
    city varchar(255),
    street varchar(255),
    house_num int,
    created_at datetime not null,
    updated_at datetime not null
);

# can't test because of ad
# multivalue adj
CREATE TABLE divar.images(
    adID int not null references advertise,
    image blob primary key not null
);

# error
# weak entity
# how to have sth like enum (specific values)
# isn't it better to add this to ad table?
CREATE TABLE divar.ad_status(
	adID int primary key not null references advertise,
    status_comment varchar(255),
    state ??? not null,
    updated_at datetime not null
);

# error
# MN relation
CREATE TABLE divar.modify_status(
	adID int primary key not null references advertise,
    userID int primary key not null references admin_user
);

# error
# weak entity
# sefat momayeze (Discriminator) ???
CREATE TABLE divar.ad_report(
	report_num int primary key not null,
    adID int primary key not null references advertise,
    userID int not null references normal_user,
    category varchar(255) not null,
    content varchar(255)
);

# error
# MN relation
CREATE TABLE divar.check_report(
	adID int primary key not null references report,
    report_num int primary key not null references report,
    userID int primary key not null references normal_user
);

# can't test because of ad
# entity
CREATE TABLE divar.general_cat(
    adID int primary key not null references advertise
);

# can't test because of ad
# error
# entity
CREATE TABLE divar.transportation_cat(
    adID int primary key not null references advertise,
    creatorID int primary key not null references normal_user,
    brand varchar(255),
    vehicle_type varchar(255),
    vehicle_engine varchar(255)
);

# can't test because of ad
# error
# entity
CREATE TABLE divar.home_cat(
    adID int primary key not null references advertise,
    creatorID int primary key not null references normal_user,
    factory varchar(255),
    size varchar(255),
    material varchar(255)
);

# can't test because of ad
# error
# entity
CREATE TABLE divar.real_cat(
    adID int primary key not null references advertise,
    creatorID int primary key not null references normal_user,
    meterage varchar(255),
    title_deed varchar(255),
    constructed_at datetime not null
);

# can't test because of ad
# error
# entity
CREATE TABLE divar.transportation_cat(
    adID int primary key not null references advertise,
    creatorID int primary key not null references normal_user,
    brand varchar(255),
    model varchar(255),
    battery varchar(255)
);

drop table admin_user;
desc divar.email; 
show tables from divar;
drop database divar;