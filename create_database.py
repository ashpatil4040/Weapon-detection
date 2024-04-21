import sqlite3


def create_database_here():
    conn = sqlite3.connect('WeaponDetection.db')
    cursor = conn.cursor()

    sql_command8 = """CREATE TABLE IF NOT EXISTS client
                            ( client_name   VARCHAR(200),
                              client_email  VARCHAR(300),
                              client_password      VARCHAR(300) );"""
    cursor.execute(sql_command8)
    conn.commit()

    sql_command8 = """CREATE TABLE IF NOT EXISTS server
                                ( server_name           VARCHAR(200),
                                  server_email          VARCHAR(300),
                                  server_password       VARCHAR(300) );"""
    cursor.execute(sql_command8)
    conn.commit()

    sql_command8 = """CREATE TABLE IF NOT EXISTS camera
                                ( client_email      VARCHAR(300),
                                  camera_protocol   VARCHAR(300),
                                  camera_ip         VARCHAR(300),
                                  camera_username   VARCHAR(300),
                                  camera_name       VARCHAR(300),
                                  password          VARCHAR(300) );"""
    cursor.execute(sql_command8)
    conn.commit()

    sql_command8 = """CREATE TABLE IF NOT EXISTS history
                                    ( client_email      VARCHAR(300),
                                      camera_username   VARCHAR(300),
                                      date              DATE,
                                      time              VARCHAR(300),
                                      pic_path          VARCHAR(800),
                                      password          VARCHAR(300) );"""
    cursor.execute(sql_command8)
    conn.commit()

    conn.close()
