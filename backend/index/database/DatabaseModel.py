from dotenv import load_dotenv

import cx_Oracle
import os


class DatabaseModel:
    def __init__(self):

        # Retrieve params
        load_dotenv()
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        dir_name = os.getenv("DB_WALLET_DIR_NAME")
        dsn = os.getenv("DB_DSN")

        # Set TNS_ADMIN
        current_dir = os.path.dirname(os.path.abspath(__file__))
        wallet_dir = os.path.join(current_dir, dir_name)
        os.environ["TNS_ADMIN"] = wallet_dir

        # Connect
        self.__connection = cx_Oracle.connect(user, password, dsn=dsn, encoding="UTF-8")

    # Method to execute a command in the database
    def __execute(self, query: str, isQuery=True):
        with self.__connection.cursor() as cursor:
            cursor.execute(query)
            if isQuery:
                return cursor.fetchall()
            else:
                self.__connection.commit()
                return None

    # Method to add a new source. Returns the auto-generated id of the new item in the DB
    def insert_source(self, source_name: str, base_url: str) -> int:
        query = """
            INSERT INTO SOURCE (SOURCE_NAME, BASE_URL)
            VALUES (:source_name, :base_url)
            RETURNING ID INTO :new_id
        """
        new_id = [None]
        params = (source_name, base_url, new_id)
        self.__execute(query, params, isQuery=False)
        return new_id[0]

    # Method to add a new document. Returns the auto-generated id of the new item in the DB
    def insert_document(
        self,
        source_id: int,
        document_type: str,
        summary: str,
        publish_date: str,
        document_url: str,
        document_length: int,
        document_language: str,
    ) -> int:
        query = """
            INSERT INTO DOCUMENT (SOURCE_ID, DOCUMENT_TYPE, SUMMARY, PUBLISH_DATE, DOCUMENT_URL, DOCUMENT_LENGTH, DOCUMENT_LANGUAGE)
            VALUES (:source_id, :document_type, :summary, TO_DATE(:publish_date, 'YYYY-MM-DD'), :document_url, :document_length, :document_language)
            RETURNING ID INTO :new_id
        """
        new_id = [None]
        params = (
            source_id,
            document_type,
            summary,
            publish_date,
            document_url,
            document_length,
            document_language,
            new_id,
        )
        self.__execute(query, params, isQuery=False)
        return new_id[0]

    def register_appearances(self, document_id: int, term: str, term_frequency: int):
        query = """
            INSERT INTO APPEARS (DOCUMENT_ID, TERM, TERM_FREQUENCY)
            VALUES (:document_id, :term, :term_frequency)
        """
        params = (document_id, term, term_frequency)
        self.__execute(query, params, isQuery=False)

    def __del__(self):
        self.__connection.close()
