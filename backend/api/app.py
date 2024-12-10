import sys

sys.path.append("/root/cancer_patient_search_engine")

import math
from flask import Flask, jsonify, request
from flask_cors import CORS 
from threading import Thread
from backend.api.utils import fix_value_between
from backend.index.database.DatabaseModel import DatabaseModel
from backend.engine.TermProcessor import TermProcessor


class Server:
    def __init__(self):
        self.app = Flask(__name__)

        CORS(self.app)

        self.__model = DatabaseModel()
        self.__termProcessor = TermProcessor()
        self.__setup_routes()

        self.__average_document_length = self.__model.get_document_statistics()

        if not self.__average_document_length:
            raise ValueError(
                "Document statistics were not retrieved. Cannot start service"
            )

    def __setup_routes(self):
        @self.app.route("/api/statistics", methods=["GET"])
        def get_statistics():
            statistics = self.__model.get_document_statistics()
            return jsonify(
               { 
                    "DOCUMENT_COUNT": statistics.get_document_count(), 
                    "AVERAGE_DOCUMENT_LENGTH": statistics.get_average_document_length() 
                }
            )

        @self.app.route("/api/sources", methods=["GET"])
        def get_sources():
            return jsonify(
                self.__model.get_sources()
            )

        @self.app.route("/api/query", methods=["GET"])
        def query():
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

        self.app.run(debug=True, host='127.0.0.1', port=5000)


# Launch server
app = Server()
app.run()