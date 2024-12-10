import base64
from datetime import datetime
import json
import time
import cx_Oracle
import os

from dotenv import load_dotenv
from backend.documentTypes import DocumentLanguage
from backend.engine.TermProcessor import TermProcessor
from backend.index.database.entities.DocumentStatistics import DocumentStatistics
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

        # Temp variables for insertions. Avoid single slow insertions
        self.__sources_to_insert: list[tuple] = []
        self.__documents_to_insert: list[tuple] = []
        self.__document_lengths = {}
        self.__inverted_index = {}

        current_directory = os.path.dirname(os.path.abspath(__file__))
        self.__insertions_file_path = f"{current_directory}/insertions.dbmodel.dumpdata"

    def insert_source(self, source: Source) -> int:
        db_tuple = source.to_dict()
        self.__sources_to_insert.append(db_tuple)
        return len(self.__sources_to_insert)

    def insert_document(self, document: Document) -> int:
        db_tuple = document.to_tuple()
        self.__documents_to_insert.append(db_tuple)
        return len(self.__documents_to_insert)

    def record_term_frequency(self, document_id: int, term: str, term_frequency: int):
        if document_id in self.__document_lengths:
            self.__document_lengths[document_id] += term_frequency
        else:
            self.__document_lengths[document_id] = term_frequency

        if term not in self.__inverted_index:
            self.__inverted_index[term] = {}

        document_dict = self.__inverted_index[term]
        document_dict[document_id] = term_frequency

    def __execute__query(
        self,
        statement: str,
        params: dict = {},
    ):
        with self.__connection.cursor() as cursor:
            try:
                cursor.execute(statement, params)
                result = cursor.fetchall()
                return result
            except Exception as e:
                print("Database error with query:", f"'{statement}'", e)
                return []

    def __execute_statement(
        self,
        statement: str,
        params: dict = {},
    ):
        with self.__connection.cursor() as cursor:
            try:
                cursor.execute(statement, params)
                self.__connection.commit()
            except Exception as e:
                print("database error with statement:", f"'{statement}'", e)
                raise e

    def __execute_bulk_statement(
        self,
        statement: str,
        params: list = [],
    ):
        with self.__connection.cursor() as cursor:
            try:
                cursor.executemany(statement, params)
                self.__connection.commit()
            except Exception as e:
                print("database error with statement:", f"'{statement}'")
                raise e

    def __bulk_insert_sources(self):
        statement = """
        INSERT INTO SOURCE (SOURCE_NAME, BASE_URL, ICON)
        VALUES (:source_name, :base_url, :icon)
        """
        self.__execute_bulk_statement(statement, self.__sources_to_insert)

    def __bulk_insert_documents(self):
        # Add length to documents

        documents_tuples_with_length = []
        for i, document_tuple in enumerate(self.__documents_to_insert):
            changed_tuple = tuple(
                list(document_tuple)
                + [
                    (
                        self.__document_lengths[str(i + 1)]
                        if str(i + 1) in self.__document_lengths
                        else 0
                    )
                ]
            )
            documents_tuples_with_length.append(changed_tuple)

        statement = """
        INSERT INTO DOCUMENT (TITLE, SUMMARY, DOCUMENT_TYPE, PUBLISH_DATE, DOCUMENT_URL, DOCUMENT_LANGUAGE, SOURCE_ID, DOCUMENT_LENGTH)
        VALUES (:title, :summary, :document_type, :publish_date, :document_url, :document_language, :source_id, :document_length)
        """
        self.__execute_bulk_statement(statement, documents_tuples_with_length)

    def __bulk_insert_terms(self):
        statement = """
        INSERT INTO TERM (TERM, DOCUMENT_FREQUENCY, IDF)
        VALUES(:term, :document_frequency, :idf)
        """
        term_set = set(self.__inverted_index.keys())
        document_count = len(self.__documents_to_insert)
        self.__execute_bulk_statement(
            statement,
            [
                (
                    term,
                    len(self.__inverted_index[term]),
                    document_count / len(self.__inverted_index[term]),
                )
                for term in term_set
            ],
        )

    def __bulk_register_appearances(self):
        statement = """
        INSERT INTO APPEARS (DOCUMENT_ID, TERM, TERM_FREQUENCY)
        VALUES (:document_id, :term, :term_frequency)
        """
        appearances = [
            (document_id, term, freq)
            for term, documents in self.__inverted_index.items()
            for document_id, freq in documents.items()
        ]
        self.__execute_bulk_statement(statement, appearances)

    def __register_document_statistics(self):
        statement = """
        INSERT INTO DOCUMENT_STATISTICS (DOCUMENT_COUNT, AVERAGE_DOCUMENT_LENGTH)
        VALUES (:document_count, :average_document_length)
        """
        document_count = len(self.__documents_to_insert)
        average_document_length = (
            sum(self.__document_lengths.values()) / document_count
            if document_count > 0
            else 0
        )
        self.__execute_statement(statement, (document_count, average_document_length))

    def get_sources(self):
        statement = """
        SELECT ID, SOURCE_NAME, BASE_URL, ICON
        FROM SOURCE
        """

        document_keys = [
            "ID",
            "SOURCE_NAME",
            "BASE_URL",
            "ICON",
        ]

        result = self.__execute__query(statement)

        sources_dictionaries = []
        for row in result:
            dictionary = {}
            for i, key in enumerate(document_keys):
                if key == "ICON":
                    dictionary[key] = base64.b64encode(row[i].read()).decode('utf-8') if row[i] else None
                else:
                    dictionary[key] = row[i]

            sources_dictionaries.append(dictionary)

        return sources_dictionaries
    
    def __serialize_data(self, filename: str, data):
        try:
            with open(filename, "w") as file:
                json.dump(data, file, default=str, indent=4)
        except Exception as e:
            print(f"Error serializing data:", e)
            raise e

    def __deserialize_data(self, filename: str):
        try:
            with open(filename, "r") as file:
                data = json.load(file)
            return data
        except Exception:
            return None

    # Locally store insertions to prevent data loss
    def __locally_save_insertions(self):
        insertions_data = {
            "sources_to_insert": self.__sources_to_insert,
            "documents_to_insert": self.__documents_to_insert,
            "document_lengths": self.__document_lengths,
            "inverted_index": self.__inverted_index,
        }
        self.__serialize_data(self.__insertions_file_path, insertions_data)

    def is_insertions_record_available(self):
        return os.path.exists(self.__insertions_file_path)

    def delete_insertions_record(self):
        return os.remove(self.__insertions_file_path)

    def load_insertions_record(self):
        data = self.__deserialize_data(self.__insertions_file_path)
        if data:
            self.__sources_to_insert = data["sources_to_insert"]
            self.__documents_to_insert = data["documents_to_insert"]
            self.__document_lengths = data["document_lengths"]
            self.__inverted_index = data["inverted_index"]

    def get_document_statistics(self) -> DocumentStatistics:
        query = f"""
        SELECT DOCUMENT_COUNT,AVERAGE_DOCUMENT_LENGTH 
        FROM DOCUMENT_STATISTICS 
        """
        result = self.__execute__query(query)
        if len(result) < 1:
            return None

        return DocumentStatistics(result[0][0], result[0][1])

    def get_ranked_documents_dictionaries(
        self,
        statistics: DocumentStatistics,
        termProcessor: TermProcessor,
        query: str,
        k1: float = 1.5,
        b: float = 0.75,
        page: int = 1,
        limit: int = 10,
        max_summary_len: str = 1000,
    ) -> list[dict]:
        terms = termProcessor.get_terms(query)

        query_placeholder = " OR ".join(
            [f"AP.TERM = :term_{i}" for i in range(len(terms))]
        )

        offset = (page - 1) * limit
        params = {
            "offset": offset,
            "limit": limit,
            "k1": k1,
            "b": b,
            "max_summary_len": max_summary_len,
            "avdl": statistics.get_average_document_length(),
        }

        # Add terms to params dictionary safely
        for i, term in enumerate(terms):
            params[f"term_{i}"] = term

        sql = f"""
        WITH BM25_SCORES AS (
            SELECT D.ID, SUM( (AP.TERM_FREQUENCY * (:k1 + 1)) / (AP.TERM_FREQUENCY + :k1 * (1 - :b + :b * D.DOCUMENT_LENGTH / :avdl))) AS BM25_SCORE
            FROM DOCUMENT D
            JOIN APPEARS AP ON D.ID = AP.DOCUMENT_ID
            WHERE {query_placeholder if query_placeholder else "1=1"}
            GROUP BY ID
        )
        SELECT TITLE, DBMS_LOB.SUBSTR(SUMMARY, :max_summary_len, 1) AS SUMMARY, DOCUMENT_TYPE, PUBLISH_DATE, DOCUMENT_URL, DOCUMENT_LANGUAGE, SOURCE_ID
        FROM DOCUMENT 
        LEFT JOIN BM25_SCORES ON BM25_SCORES.ID = DOCUMENT.ID
        ORDER BY COALESCE(BM25_SCORE, 0) DESC
        OFFSET :offset ROWS
        FETCH NEXT :limit ROWS ONLY
        """

        result = self.__execute__query(sql, params)

        document_keys = [
            "TITLE",
            "SUMMARY",
            "DOCUMENT_TYPE",
            "PUBLISH_DATE",
            "DOCUMENT_URL",
            "DOCUMENT_LANGUAGE",
            "SOURCE_ID",
        ]

        documents_dictionaries = []
        for row in result:
            dictionary = {}
            for i, key in enumerate(document_keys):
                dictionary[key] = row[i]

            documents_dictionaries.append(dictionary)

        return documents_dictionaries

    def keep_connection_alive(self):
        while True:
            self.__execute__query("SELECT 1 FROM DUAL")
            time.sleep(60)

    def commit_insertions(self):
        print("Started bulk transactions to database")
        print(
            "Commiting:",
            len(self.__sources_to_insert),
            "sources,",
            len(self.__documents_to_insert),
            "documents,",
            len(set(self.__inverted_index.keys())),
            "terms",
        )

        print(
            f"Auto saving insertions record into {self.__insertions_file_path} in case of failure..."
        )
        self.__locally_save_insertions()
        print(
            f"Insertions record auto-saved to {self.__insertions_file_path}. Proceeding to database operations"
        )

        self.__bulk_insert_sources()
        self.__bulk_insert_documents()
        self.__bulk_insert_terms()
        self.__bulk_register_appearances()
        self.__register_document_statistics()

        print("Database operations completed")
        self.delete_insertions_record()
        print("Insertions record automatically delete")
