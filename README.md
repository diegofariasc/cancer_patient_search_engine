# Search cancer BM25-based engine
### Problem description
According to the American Cancer Society, more than 2 million patients will be diagnosed with some form of cancer in the US this year. These figures are expected to annually increase at a rate of 0.6%-1% (Siegel et al, 2024). Such a medical condition is often accompanied by feelings of depression, insecurity and anxiety, which leads patients to search for information related to their life expectancy, survival odds, treatment options, among other topics. (Melhem et al, 2024). Nevertheless, according to (King & Greene, 2024), the information that is available online tends to be imprecise. Alomst 70% of all articles on social networks or popular information sources contain erroneous or misleading information about this disease.

Amid this scenario **Search Cancer** has been created. This is a a specialized search engine for cancer patients that provides reliable information on patient life expectancies, treatment options, technologies and procedures which is gathered from trustworthy sources. Sources are listed below:

#### Indexed websites
1. American Cancer Society
2. Myeloma Working Group
3. Multiple Myeloma Research Foundation
4. Cleveland Clinic
5. Leukemia and Lymphoma Society
6. American Society of Hematology
7. WebMD
8. National Cancer Institute
9. Centers for Disease Control and Prevention
10. Memorial Sloan Kettering Cancer Center
11. National Institute for Health and Care Excellence
12. Asociación Española Contra el Cáncer
13. Ministerio de Salud de Argentina
14. Instituto Nacional de Cancerología Colombia
15. World Health Organization
16. Sociedad Española de Oncología Médica
17. Asociación Mexicana de la Lucha Contra el Cáncer

#### Indexed research-paper repositories
1. ArXiv e-Print archive
2. PubMed Central
3. DOAJ: Directory of Open Access Journals
4. CORE UK

In research paper respositories, only cancer-related papers are indexed

#### Retrieval mechanism
The project is primarily supported by **BM25**. This model determines the relevance of a document `d` given a query `q` through the frequency of the terms that constitute it `c(w,d)`, the inverse frequency of the document `IDF(w)`, and two free variables `k` and `b ∈ [0,1]`, which control the impact of term frequency and the degree of normalization that is applied to the scores of each document.

Formally, the BM25 weighing function is defined as:
![BM25 equation](BM25equation.svg)

Where:
- `c(w, q)` denotes the frequency of the terms in the query `q`,
- `c(w, d)` represents term frequency (TF),
- `|d|` stands for document length,
- and `avdl` represents the average document length.


### How to use the system?
#### Accessing the system
##### UI Plugin

In this repository, you'll find the complete source code used to implement **Search Cancer**. However, the final product has been deployed to the web and can be accessed via the following URL: [https://www.search-cancer.com](https://www.search-cancer.com). 

Reviewers can access and test the system by simply clicking the link above or entering the URL into their browser. Both desktop and mobile experiences are available, with support for popular browsers like Chrome and Firefox tested. However, **it is recommended to use a desktop browser for a better experience**.

The search engine UI is designed to be simple and user-friendly, specifically for cancer patients seeking information about their disease. Upon entering the URL, you will see a single text input field along with a search button. You can type any query and click "Search". This will redirect you to a results page, where all 2000+ available documents and webpages are displayed, sorted by BM25 relevance. Results are paginated to avoid browser and server overload, initially showing the 20 most relevant documents. You can view more results by using the "Next" and "Previous" buttons at the bottom of the results section.

If you want to refine the query from the results page, simply modify it in the text input field and either click the magnifying glass icon or press the Enter key.

To access a resource, click on its title. For academic sources such as ArXiv, PubMed, CORE, and DOAJ, you will be redirected directly to the PDF file. For websites, you will be directed to the specific subsite containing the selected article. To access the main website of an information provider, click on the link below its name.

##### REST API
As part of this final project, a REST API has been made available. Reviewers may choose to access it directly if desired. However, it’s important to note that **all available operations and functionalities are exposed through the UI plugin, so accessing the API manually is not necessary for reviw**. 

You may find the API endpoints, along with their input parameters and expected outputs, on the SwaggerHub page: [https://app.swaggerhub.com/apis/FARIASCODIEGO/SearchCancerAPI/1.0.0](https://app.swaggerhub.com/apis/FARIASCODIEGO/SearchCancerAPI/1.0.0). This API is public and requires no authentication.

In the SwaggerHub portal, there is a "Try it out" option that allows you to call the endpoint directly without needing to write any code. Alternatively, if you're having difficulties accessing SwaggerHub, you can find the complete API documentation in the `APIDescription.html` file. This file can be opened in any web browser.

##### Tutorial
A simple video tutorial has been created and added to Illinois Media Space. Reviewers can access it following this url: https://mediaspace.illinois.edu/media/t/1_y2f1n4vk


## System implementation 
The system is made up of 5 main components: the database (and database model), a website scrapper, a collection of extractors, an indexer, a REST API and a user interface. Below you will find an architecture diagram which depicts all these components and their relations

![Architecture Diagram](ArchitectureDiagram.svg)

### Database  
#### Schema
To store the BM25 index, an Oracle Cloud Autonomous Database instance was created using their Always Free tier. The database schema consists of 5 tables:

1. **`SOURCE`**: Represents an information provider.
2. **`DOCUMENT`**: Holds information about every indexed webpage or research paper.
3. **`TERM`**: Represents each unique term in the corpus.
4. **`APPEARS`**: Represents the term frequency (TF). Each record links a document and a term, specifying the number of occurrences of that term in the document, i.e., `c(w,d)`.
5. **`DOCUMENT_STATISTICS`**: An auxiliary table that holds the document count and average document length. This table is included for performance reasons to avoid calculating `COUNT(*)` and `AVG(DOCUMENT_LENGTH)` on the `DOCUMENT` table every time a query is executed.

Below is an entity-relationship diagram depicting these tables and their relationships:

![Architecture Diagram](DatabaseDiagram.svg)

The SQL script that creates this schema can be found in `backend/index/database/scripts/buildDatabase.sql`.

#### Python database model
The **Database Model** is a Python component designed to retrieve and manipulate records from an Oracle Autonomous Database (ADB) instance within the application. It utilizes the `cx_Oracle` connector and a configured database wallet, which can be set up by following these instructions: [Oracle ADB Connection Guide](https://docs.oracle.com/en/database/oracle/developer-tools-for-vscode/getting-started/connecting-oracle-autonomous-database-adb.html). For security reasons, the database wallet is not included in this repository.

The model exposes the following methods for interacting with the database:

1. **Insert and Indexing Methods:**
   `insert_source`, `insert_document`, and `record_term_frequency`. These methods allow for the insertion of records into the database while building UP the index. 

   **Note**: Given the limited resources of the **Always Free** tier of Oracle Autonomous Database (20GB storage, 1 OCPU, 1GB RAM, and up to 30 active connections), these methods do not directly execute SQL statements upon being called. Instead, they simulate the insertion and store the data in local Python data structures. The actual database insertion is deferred and occurs later in bulk when the `commit_insertions` method is invoked. This approach prevents overloading the database, reduces indexing time, and significantly improves performance. However, it does increase primary memory consumption on the machine running the indexer. The indexing process was successfully executed on a machine with 32GB of RAM, which is considerably higher than the 20GB storage limit of the ADB instance.

2. **Query and Data Retrieval Methods:**
   `get_document_statistics`, `get_ranked_documents_dictionaries`, and `get_sources`. These methods execute queries on the database, preprocess the results, and return the information to the API for further use. They provide the necessary data for retrieving document statistics, ranked documents based on search terms, and source information.
   
3. **Connection Management:**
   `keep_connection_alive`: A simple ping method that submits a basic query to the database at regular intervals to keep the connection active, preventing it from timing out.

4. **Commit Method:**
   `commit_insertions`: This method is responsible for executing the SQL insert statements into the database. It takes all data accumulated in the Python data structures (holding indexing information) and converts it into a large batch of SQL `INSERT` statements. These are then executed in bulk using the `executemany` method, optimizing the insertion process and minimizing individual query execution time.


### Website scrapper 
This Python module has been built using `BeautifulSoup` and `aiohttp` to scrape the contents of a website, starting from its base URL and recursively visiting all its subsites up to a specified depth. The scraper allows to extract relevant textual data, such as the document title and content, from each page it visits. 

The scraper is initialized using four main parameters:

1. **`base_url`**: The main URL of the site to begin scraping.
2. **`source_name`**: The name of the site being analyzed.
3. **`max_depth`**: The maximum number of sub-links to follow from the base URL.
4. **`scraping_delay`**: The interval between each GET request to avoid server overload and prevent potential banning.

The algorithm for the scraper works as follows:

1. **Access the Base Website**: The scraper starts by accessing the `base_url` provided.
2. **Extract Links**: The HTML content of the page is fetched, and all anchor tags `<a>` with `href` attributes are identified.
3. **Follow Links**: For each link on the page, the scraper checks if it is a valid subsite within the allowed domain and whether it has been visited already. If the link has not been visited, it is added to the visited set, and the scraper proceeds to fetch and parse the content of the new page.
4. **Recursive Traversal**: If a subsite contains links to further pages, the scraper recursively visits those pages, up to the specified `max_depth`.
5. **Extract Content**: For each page, the scraper extracts the title and text content, sanitizing the text to remove unnecessary elements like scripts, styles, and URLs.
6. **Throttle Requests**: To avoid overwhelming the server, a delay `scraping_delay` is inserted between each request.

To ensure the reliability and trustworthiness of the information, the scraper verifies that all explored subpages have the are part of the same domain as the original `base_url`. This verification is crucial for preventing the scraping of external sources that may not be reliable. If a subpage's URL does not match the original base URL, it is omitted from the scraping process.

### Extractors
#### Description

**Extractors** are specialized python components that allow to retrieve document data from various external sources like ArXiv, CORE, DOAJ, and PubMed. These extractors interact with the respective APIs to fetch relevant academic papers and research articles, parse their metadata, and structure the data into `Document` objects that can later be indexed for further processing. Below is the list of all invoked endpoints. Some of them require an API key. This is not included in the source code for security reasons. 

The following are the API endpoints are called by each extractor to fetch document data.

##### 1. **ArXivExtractor**
- `http://export.arxiv.org/api/query` searches ArXiv articles based on predefined query terms and returns results in XML format.

##### 2. **COREExtractor**
-  `https://api.core.ac.uk/v3/search/works` searches CORE database using predefined query terms and returns results in JSON format. An API key is required for this endpoint

##### 3. **DOAJExtractor**
- Endpoint: `https://doaj.org/api/search/articles/{encoded_query}` searches DOAJ for articles using encoded query terms and returns results in JSON format.

##### 4. **PubMedExtractor**
- `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi` searches PubMed for articles based on predefined query terms and returns results in JSON format.

- `https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi` fetches detailed document information from PubMed using IDs retrieved from the search endpoint.

To ensure that documents being retrieved are relevant and scoped to cancer research and oncology, each extractor uses a predefined set of query terms. These query terms include a wide range of keywords related to various forms of cancer both in Spanish and English e.g., **oncología**, **neoplasia**, **tumor**, **carcinoma** as well as terms related to cancer treatments e.g., **quimioterapia**, **radioterapia**, **inmunoterapia**, and associated biological processes e.g., **angiogenesis**, **hematopoiesis**, **oncogenesis**.

Below is a list of all key search terms used across the extractors:

- **Cancer-related terms:** "cancer", "oncología", "neoplasia", "tumor", "malignidad", "carcinoma", "leukemia", "lymphoma", "sarcoma", "melanoma", "glioblastoma", "blastoma"
- **Treatment-related terms:** "chemotherapy", "radiotherapy", "immunotherapy", "chemoradiation"
- **Biological and genetic terms:** "angiogenesis", "oncogene", "cytology", "mutagenesis", "biomolecular", "tumorigenesis"
- **Other related terms:** "metastasis", "relapse", "remission", "neurofibromatosis", "histiocytosis"

The full list of query terms is defined in `backend/index/extraction/queryTerms.py`

Extractors can generate indexing entries either using their **full text** (if available)or their summaries. This in order to minimize indexing time and computational load. This feature is controlld by the `use_full_text` parameter.

### Indexer

The Indexer is a Python module that is responsible of conducting the indexing process. It begins by reading the contents of `backend/index/websites_data.csv`, a file that contains a list of trusted oncological and medical websites. For each website, an instance oft the `WebsiteScraper` is created. Alongside the scrapers, instances of each `Extractor` type are also initialized.

These components are executed asynchronously, with each resource's data being retrieved in parallel. Once the data for a resource is collected, it is processed through the **Term Processor**. This submodule cleans and optimizes the document content to reduce the index size and enhance retrieval performance. The Term Processor leverages several libraries, including:

- **NLTK**: For tokenizing the content.
- **langdetect**: For identifying the document's language.
- **Snowball**: For performing stemming on each term.

After processing, the frequencies of the terms are calculated using Python dictionaries. This term frequency data, along with details of each document and its corresponding provider, is then passed to the database model for persistence.

### REST API and UI plugin
These components interact directly with the client.

The REST API is developed using Flask. You can review its specification at the following link: [https://app.swaggerhub.com/apis/FARIASCODIEGO/SearchCancerAPI/1.0.0](https://app.swaggerhub.com/apis/FARIASCODIEGO/SearchCancerAPI/1.0.0). The REST API handles requests to the database through the DatabaseModel to retrieve the necessary information based on user requests.

Both the REST API and UI plugin are deployed on a Microsoft Azure virtual machine with the Standard_B1ms size, which includes a vCPU, 2GB of RAM, and a public IP address. An Nginx server is configured to receive incoming requests and route them appropriately.

The UI was developed with React.js and Chakra UI components (Chakra UI).

Both services are deployed on the same machine. The UI service is available on ports 80 and 443, while the Flask server is running on port 5000. For enhanced security, an SSL certificate was configured using Certbot from Let's Encrypt. Additionally, Cross-Origin Resource Sharing (CORS) is enabled to prevent browser rejections when accessing the site from different origins.

In this setup, Nginx acts as the reverse proxy, receiving incoming requests on port 80 or 443 and forwarding them to the appropriate service. The Flask server listens on 127.0.0.1:5000, ensuring that direct access to the API is restricted, and only Nginx can route requests to it.

## Results
A usability test was conducted to assess the effectiveness of the information retrieval system, with a real cancer patient as the participant. Before the test, the patient was informed about the purpose of the study i.e., `to evaluate the effectiveness of an information retrieval system designed specifically for cancer patients`. The patient was also made aware on the data that would be collected, which included languages spoken, age range, medical diagnosis, and submitted queries. Furthermore, the patient was informed about the implications and benefits of their participation, as well as how the results would be used. The patient was assured that he/she could withdraw from the study at any time without any consequences. The patient provided informed consent.

The participant is a 50-60 year-old individual diagnosed with IgG kappa Multiple Myeloma, Stage I, according to the International Myeloma Working Group standards. The diagnosis was confirmed in January 2024. The patient mentioned he/she was receiving hematological care and undergoing standard chemotherapy treatment, for which he/She requested more information. 

The patient was asked to formulate at least three queries, one of which should be in Spanish, and rate the top 10 results on a scale of 1 to 3, where 1 indicates low relevance and 3 indicates high relevance. The patient formulated the following queries:

1. "What is multiple myeloma?"
2. "Multiple myeloma treatment"
3. "Estudios mieloma múltiple" (Multiple Myeloma Research Studies)

The patient rated the search results as follows:

**Query: "What is multiple myeloma?**
Ratings: 1, 1, 3, 2, 2, 2, 1, 3, 1, 1

**Query: "multiple myeloma treatment**
Ratings: 2, 3, 2, 2, 2, 3, 1, 3, 1, 1

**Query: "Estudios mieloma múltiple (Multiple Myeloma Research Studies)**
Ratings: 2, 2, 2, 1, 2, 2, 2, 3, 2, 1

Next, the patient repeated the queries using Google Scholar (Google Search Academic) to obtain documents of a similar format to those indexed in the system. The ratings assigned were as follows:

**Query: "What is multiple myeloma?**
Ratings: 3, 1, 1, 2, 2, 2, 2, 2, 3, 2

**Query: "multiple myeloma treatment**
Ratings: 3, 3, 3, 3, 2, 2, 3, 3, 2, 3

**Query: "Estudios mieloma múltiple (Multiple Myeloma Research Studies)**
Ratings: 2, 1, 2, 3, 3, 1, 2, 2, 3, 3

Using the ratings from both the index-based system and Google Scholar, Precision and NDCG@10 were computed for each query. Since the total set of relevant documents is unknown, Recall could not be calculated. For precision, a score of at least 2 was considered sufficient to classify a document as relevant. Results are presented below

**Search cancer**
- Query: What is multiple myeloma?
  - Precision: 0.50
  - NDCG@10: 0.81

- Query: Multiple myeloma treatment
  - Precision: 0.70
  - NDCG@10: 0.92

- Query: Estudios mieloma múltiple (Multiple Myeloma Research Studies)
  - Precision: 0.80
  - NDCG@10: 0.91

**Google Search Academic**

- Query: What is multiple myeloma?
  - Precision: 0.80
  - NDCG@10: 0.91

- Query: Multiple myeloma treatment
  - Precision: 1.00
  - NDCG@10: 0.99

- Query: Estudios mieloma múltiple (Multiple Myeloma Research Studies)
  - Precision: 0.80
  - NDCG@10: 0.86

### Conclusion

Overall, the Google Search engine performed better in most metrics, particularly in the "Multiple myeloma treatment" query, where it achieved an astonoshing precision of 1.00 and NDCG@10 of 0.99. However, it is important to note that Google's search engine has a substantially larger database, with approximately 160 million indexed documents in its academic section, compared to the 2,000+ documents indexed by the Search Cancer system. This difference in database size makes it more likely for Google to successfully answer a query. Nonetheless, despite these differences, the Search Cancer system achieved reasonably comparable NDCG@10 and precision values, which suggests that the results are satisfactory. Further improvements, such as expanding the indexed corpus, could enable it to compete more effectively with large-scale solutions like Google Search.
