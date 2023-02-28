import psycopg2

DSN = "postgresql://postgres:12345@localhost:5432/matched_users"


def create_db():
    conn = psycopg2.connect(
        database="matched_users",
        user="postgres",
        password="12345",
        host="localhost",
        port="5432",
    )
    conn.close()


def create_matches_table():
    with psycopg2.connect(
        database="matched_users",
        user="postgres",
        password="12345",
        host="localhost",
        port="5432",
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
            create table if not exists matches (
            id serial primary key, 
            user_id integer not null,
            match_id integer not null
            );
            """
            )
            conn.commit()


def create_user_info_table():
    with psycopg2.connect(
        database="matched_users",
        user="postgres",
        password="12345",
        host="localhost",
        port="5432",
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                """
            create table if not exists user_info (
            id serial primary key, 
            user_id integer not null,
            city varchar(40) not null,
            age integer not null,
            sex integer not null,
            relation integer not null
            );
            """
            )
            conn.commit()


def save_user_info_to_bd(user_id, age, city, sex, relation):
    with psycopg2.connect(
        database="matched_users",
        user="postgres",
        password="12345",
        host="localhost",
        port="5432",
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                f"""
            insert into user_info (user_id, city, age, sex, relation)
            values ({user_id},'{city}',{age},{sex},{relation})
            ON CONFLICT (user_id) DO UPDATE 
            SET city = excluded.city, 
            age = excluded.age,
            sex = excluded.sex,
            relation = excluded.relation;
            """
            )
            conn.commit()


def save_user_and_match_id(user_id, match_id):
    with psycopg2.connect(
        database="matched_users",
        user="postgres",
        password="12345",
        host="localhost",
        port="5432",
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                f"""
            insert into matches (user_id, match_id)
            values ({user_id}, {match_id});
            """
            )
            conn.commit()


def is_already_matched(user_id, match_id):
    with psycopg2.connect(
        database="matched_users",
        user="postgres",
        password="12345",
        host="localhost",
        port="5432",
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                f"""
            select exists(select 1 from matches
            where user_id={user_id} and match_id={match_id});
            """
            )
            return cursor.fetchone()[0]


def get_user_info_from_bd(user_id):
    with psycopg2.connect(
        database="matched_users",
        user="postgres",
        password="12345",
        host="localhost",
        port="5432",
    ) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                f"""
            select * from user_info
            where user_id={user_id};
            """
            )
            response = cursor.fetchone()
            if response:
                return {
                    "city": response[2],
                    "age": response[3],
                    "sex": response[4],
                    "relation": response[5],
                }
