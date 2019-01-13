from unittest import TestCase
from datetime import datetime
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from ..dbuid import generate, initialize_database
from ..util import pack, unpack

class UidTests(TestCase):
    TEST_DB_NAME = 'unittest_uidmodel_lib_uid'
    SHARD_ID = 255
    created_db = False
    connection = None

    @classmethod
    def setUpClass(cls):
        # act differently if py unittest testing vs. django testing
        try:
            from django.apps import apps
            cls.django_testing = apps.ready
        except ImportError:
            cls.django_testing = False
        # create db if needed
        if cls.django_testing:
            from django.db import connection
            cls.connection = connection
        else:
            if not cls.run_admin_sql("""
                SELECT EXISTS(
                    SELECT datname FROM pg_catalog.pg_database WHERE LOWER(datname) = LOWER(%s)
                )
            """, [ cls.TEST_DB_NAME ])[0]:
                cls.run_admin_sql("CREATE DATABASE {}".format(cls.TEST_DB_NAME))
                cls.created_db = True
            # open a connection to use for tests
            cls.connection = psycopg2.connect(dbname=cls.TEST_DB_NAME)
            cls.connection.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        # create the db function
        initialize_database(cls.connection, cls.SHARD_ID)

    @classmethod
    def tearDownClass(cls):
        if not cls.django_testing:
            cls.connection.close()
        if cls.created_db:
            cls.run_admin_sql("DROP DATABASE {}".format(cls.TEST_DB_NAME))

    @classmethod
    def run_admin_sql(cls, sql, params=None):
        # runs SQL as the postgres user. (assumes .pgpass file for password)
        conn = psycopg2.connect(dbname='postgres')
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        cursor.execute(sql, params if params is not None else [])
        result = cursor.fetchone() if cursor.description is not None else None
        cursor.close()
        conn.close()
        return result


    #########################################
    ###   Uid tests

    def test_uid(self):
        # generate 100 uids, make sure they are unique
        uids = set(( generate(self.connection) for i in range(100) ))
        self.assertEqual(len(uids), 100)

    def test_pack_unpack(self):
        uid1 = generate(self.connection)
        uid2 = generate(self.connection)
        # unpack
        dt, counter, shard_id = unpack(uid1)
        dt2, counter2, shard_id2 = unpack(uid2)
        self.assertLess((dt2 - dt).total_seconds(), 10)  # two dates within 10 seconds of each other
        self.assertLess((datetime.utcnow() - dt).total_seconds(), 10)      # date within 10 seconds of UTC now
        self.assertEqual(counter + 1, counter2)
        self.assertEqual(shard_id, self.SHARD_ID)
        # pack
        self.assertEqual(uid1, pack(dt, counter, shard_id))
        self.assertEqual(uid2, pack(dt2, counter2, shard_id2))
