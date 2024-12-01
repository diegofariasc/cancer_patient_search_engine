from dotenv import load_dotenv

import cx_Oracle
import os

from backend.index.database.entities.Document import Document
from backend.index.database.entities.Source import Source


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

    def __execute_query(self, query: str):
        with self.__connection.cursor() as cursor:
            cursor.execute(query)
            return cursor.fetchall()

    def __execute_statement(
        self, query: str, params: dict, output: dict = None, output_param: str = None
    ):
        with self.__connection.cursor() as cursor:
            cursor.execute(query, params)

            # Check if there's output param
            if output is not None and output_param is not None:
                result = cursor.fetchone()  # Execute RETURNING
                if result:
                    output[output_param] = result[0]

    def commit_changes(self):
        with self.__connection.cursor() as cursor:
            self.__connection.commit()

    def insert_source(self, source: Source) -> int:
        params = source.to_dict()
        output = {"id": None}

        query = """
        INSERT INTO SOURCE (SOURCE_NAME, BASE_URL, ICON)
        VALUES (:source_name, :base_url, :icon)
        RETURNING ID INTO :id
        """

        self.__execute_statement(query, params, output, "id")
        return output["id"]

    def insert_document(self, document: Document):
        params = document.to_dict()
        output = {'id': None}

        query = """
        INSERT INTO DOCUMENT (TITLE, AUTHORS, SUMMARY, DOCUMENT_TYPE, DOI, COUNTRY, PUBLISH_DATE, DOCUMENT_URL, DOCUMENT_LENGTH, DOCUMENT_LANGUAGE, SOURCE_ID)
        VALUES (:title, :authors, :summary, :document_type, :doi, :country, :publish_date, :document_url, :document_length, :document_language, :source_id)
        RETURNING ID INTO :id
        """
        
        self.__execute_statement(query, params, output, 'id')
        return output['id']

    def record_term_frequency(self, document_id: int, term: str, term_frequency: int):
        query = """
            INSERT INTO APPEARS (DOCUMENT_ID, TERM, TERM_FREQUENCY)
            VALUES (:document_id, :term, :term_frequency)
        """
        params = (document_id, term, term_frequency)
        self.__execute_statement(query, params)

    def __del__(self):
        self.__connection.close()
