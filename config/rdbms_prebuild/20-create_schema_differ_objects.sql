/*
+------------------------------------------------------------+
| SOURCE SCHEMA                                              |
+------------------------------------------------------------+
*/

drop table if exists schema_differ_source.schema_differ_ref_modify;
create table schema_differ_source.schema_differ_ref_modify
(
    id int unsigned not null auto_increment primary key,
    value varchar(32) not null,
    display_order int not null
) engine = innodb default charset = utf8 collate = utf8_unicode_ci;

drop table if exists schema_differ_source.schema_differ_ref_add;
create table schema_differ_source.schema_differ_ref_add
(
    id int unsigned not null auto_increment primary key,
    value varchar(32) not null,
    display_order int not null
) engine = innodb default charset = utf8 collate = utf8_unicode_ci;

drop table if exists schema_differ_source.schema_differ_add;
create table schema_differ_source.schema_differ_add
(
    col_a int unsigned not null primary key,
    col_b varchar(30) not null collate utf8_unicode_ci default 'abc',
    col_c bigint(10) unsigned not null unique
) engine = innodb default charset = utf8 collate = utf8_unicode_ci;

drop table if exists schema_differ_source.schema_differ_cols;
create table schema_differ_source.schema_differ_cols
(
    col_a int unsigned not null unique,
    col_b varchar(100) not null,
    col_c char(3) default 'abc'
) engine = innodb default charset = utf8 collate = utf8_unicode_ci;

drop table if exists schema_differ_source.schema_differ_fks;
create table schema_differ_source.schema_differ_fks
(
    id int unsigned not null,
    col_a int unsigned not null
) engine = innodb default charset = utf8 collate = utf8_unicode_ci;

drop table if exists schema_differ_source.schema_differ_remove_uk;
create table schema_differ_source.schema_differ_remove_uk
(
    id int not null primary key,
    value int unsigned not null
) engine = innodb default charset = utf8 collate = utf8_unicode_ci;

alter table schema_differ_source.schema_differ_fks
        add constraint schema_differ_fks_0_fk
    foreign key (id)
 references schema_differ_source.schema_differ_ref_modify (id);

alter table schema_differ_source.schema_differ_fks
        add constraint schema_differ_fks_1_fk
    foreign key (col_a)
 references schema_differ_source.schema_differ_add (col_a)
  on delete cascade;

/**
 * This index should not show up in the differ because it is being added
 * when the table is created.
 */
create index schema_differ_add_0_idx
    on schema_differ_source.schema_differ_add
        (col_a, col_b, col_c);

create index schema_differ_add_1_idx
    on schema_differ_source.schema_differ_ref_modify
        (display_order);

create index schema_differ_mod_2_idx
    on schema_differ_source.schema_differ_cols
        (col_b, col_c);

/**
 * This index should not show up in the differ because it is being added
 * when the table is created.
 */
create unique index schema_differ_add_0_uk
    on schema_differ_source.schema_differ_add
        (col_c);

create unique index schema_differ_add_1_uk
    on schema_differ_source.schema_differ_ref_modify
        (value);

create unique index schema_differ_mod_2_uk
    on schema_differ_source.schema_differ_cols
        (col_c, col_b);

insert into schema_differ_source.schema_differ_ref_modify
(
    id,
    value,
    display_order
)
values
(
    1,
    'abc',
    1
);
commit;

insert into schema_differ_source.schema_differ_ref_modify
(
    id,
    value,
    display_order
)
values
(
    2,
    'def',
    2
);
commit;

create table schema_differ_source.schema_differ_updated_def_val(
    date_updated timestamp default '0000-00-00 00:00:00' on update current_timestamp
) engine = innodb default charset = utf8 collate = utf8_unicode_ci;

/*
+------------------------------------------------------------+
| TARGET SCHEMA                                              |
+------------------------------------------------------------+
*/

drop table if exists schema_differ_target.schema_differ_ref_modify;
create table schema_differ_target.schema_differ_ref_modify
(
    id int unsigned not null auto_increment primary key,
    value varchar(32) not null,
    display_order int not null
) engine = innodb default charset = utf8 collate = utf8_unicode_ci;

drop table if exists schema_differ_target.schema_differ_ref_drop;
create table schema_differ_target.schema_differ_ref_drop
(
    id int unsigned not null auto_increment primary key,
    value varchar(32) not null,
    display_order int not null
) engine = innodb default charset = utf8 collate = utf8_unicode_ci;

drop table if exists schema_differ_target.schema_differ_drop;
create table schema_differ_target.schema_differ_drop
(
    col_a int unsigned not null primary key,
    col_b varchar(30) not null collate utf8_unicode_ci default 'abc',
    col_c bigint(10) unsigned not null unique
) engine = innodb default charset = utf8 collate = utf8_unicode_ci;

drop table if exists schema_differ_target.schema_differ_cols;
create table schema_differ_target.schema_differ_cols
(
    col_a int unsigned not null unique,
    col_b varchar(50),
    col_z int
) engine = innodb default charset = utf8 collate = utf8_unicode_ci;

drop table if exists schema_differ_target.schema_differ_fks;
create table schema_differ_target.schema_differ_fks
(
    id int unsigned not null,
    col_a int unsigned not null
) engine = innodb default charset = utf8 collate = utf8_unicode_ci;

drop table if exists schema_differ_target.schema_differ_remove_uk;
create table schema_differ_target.schema_differ_remove_uk
(
    id int not null primary key,
    value int unsigned not null unique
) engine = innodb default charset = utf8 collate = utf8_unicode_ci;

alter table schema_differ_target.schema_differ_fks
        add constraint schema_differ_fks_100_fk
    foreign key (id)
 references schema_differ_target.schema_differ_drop (col_a);

alter table schema_differ_target.schema_differ_fks
        add constraint schema_differ_fks_1_fk
    foreign key (col_a)
 references schema_differ_target.schema_differ_cols (col_a);

create index schema_differ_mod_2_idx
    on schema_differ_target.schema_differ_cols
        (col_b);

create index schema_differ_drop_3_idx
    on schema_differ_target.schema_differ_ref_modify
        (id);

create unique index schema_differ_mod_2_uk
    on schema_differ_target.schema_differ_cols
        (col_b);

create unique index schema_differ_drop_3_uk
    on schema_differ_target.schema_differ_ref_modify
        (display_order);

insert into schema_differ_target.schema_differ_ref_modify
(
    id,
    value,
    display_order
)
values
(
    2,
    'xyz',
    2
);
commit;

insert into schema_differ_target.schema_differ_ref_modify
(
    id,
    value,
    display_order
)
values
(
    3,
    'def',
   3
);
commit;

create table schema_differ_target.schema_differ_updated_def_val(
    date_updated timestamp
) engine = innodb default charset = utf8 collate = utf8_unicode_ci;
