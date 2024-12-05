import sys

sys.path.append("/root/cancer_patient_search_engine")

import math
from flask import Flask, jsonify, request
from threading import Thread
from backend.api.utils import fix_value_between
from backend.index.database.DatabaseModel import DatabaseModel
from backend.engine.TermProcessor import TermProcessor


class Server:
    def __init__(self):
        self.__app = Flask(__name__)
        self.__model = DatabaseModel()
        self.__termProcessor = TermProcessor()
        self.__setup_routes()

        self.__average_document_length = self.__model.get_document_statistics()

        if not self.__average_document_length:
            raise ValueError(
                "Document statistics were not retrieved. Cannot start service"
            )

    def __setup_routes(self):
        @self.__app.route("/query", methods=["GET"])
        def index():
            # Get params and validate them
            limit = fix_value_between(int(request.args.get("limit", 100)), 1, 1000)
            max_pages = math.ceil(
                self.__average_document_length.get_document_count() / limit
            )
            page = fix_value_between(int(request.args.get("page", 1)), 1, max_pages)
            max_summary_len = fix_value_between(
                int(request.args.get("max_summary_len", 1)), 1, 4000
            )
            query = request.args.get("query", "")

            return jsonify(
                self.__model.get_ranked_documents_dictionaries(
                    self.__average_document_length,
                    self.__termProcessor,
                    query,
                    page=page,
                    limit=limit,
                    max_summary_len=max_summary_len,
                )
            )

    def run(self):
        thread = Thread(target=self.__model.keep_connection_alive)
        thread.daemon = True
        thread.start()

        self.__app.run(debug=True)


# Launch server
if __name__ == "__main__":
    app = Server()
    app.run()
