import { Document, DocumentLanguage, DocumentStatistics, DocumentType, Source } from "../types/databaseTypes";
import { SourceId } from "../types/typeAliases";

const BASE_ENDPOINT = "https://search-cancer.com/api";

enum Endpoint {
    Query = `${BASE_ENDPOINT}/query`,
    Sources = `${BASE_ENDPOINT}/sources`,
    Statistics = `${BASE_ENDPOINT}/statistics`,
}

type ParamsRecord = Record<string, string | number | undefined>;

const convertParamsToQueryString = (params: ParamsRecord) => {
    return Object.entries(params)
        .filter(([_, value]) => value !== undefined)
        .map(([key, value]) => `${encodeURIComponent(key)}=${encodeURIComponent(String(value))}`)
        .join("&");
};

const doGetRequestWithJsonResult = async (endpoint: Endpoint, params?: ParamsRecord) => {
    try {
        const paramsString = params ? `?${convertParamsToQueryString(params)}` : "";
        const response = await fetch(`${endpoint}${paramsString}`, {
            method: "GET",
            headers: {
                "Content-Type": "application/json",
                Accept: "application/json",
            },
        });

        if (response.ok) {
            const data = await response.json();
            return data;
        } else {
            throw new Error(`GET Request error: ${response.status} ${response.statusText}`);
        }
    } catch (error) {
        throw new Error(`GET Request error: ${error}`);
    }
};

const listRankedDocuments = async (params: {
    query: string;
    limit?: number;
    page?: number;
    maxSummaryLen?: number;
}) => {
    const { query, limit, page, maxSummaryLen } = params;
    const records = (await doGetRequestWithJsonResult(Endpoint.Query, {
        query,
        limit,
        page,
        ["max_summary_len"]: maxSummaryLen,
    })) as Record<string, unknown>[];

    return records.map((record) => {
        const document: Document = {
            title: record["TITLE"] as string,
            summary: record["SUMMARY"] as string,
            documentType: record["DOCUMENT_TYPE"] as DocumentType,
            documentUrl: record["DOCUMENT_URL"] as string,
            documentLanguage: record["DOCUMENT_LANGUAGE"] as DocumentLanguage,
            sourceId: record["SOURCE_ID"] as number,
        };
        return document;
    });
};

const listSources = async () => {
    const records = (await doGetRequestWithJsonResult(Endpoint.Sources)) as Record<string, unknown>[];

    return records.map((record) => {
        const source: Source = {
            id: record["ID"] as SourceId,
            sourceName: record["SOURCE_NAME"] as string,
            baseUrl: record["BASE_URL"] as string,
            icon: record["ICON"] as string,
        };
        return source;
    });
};

const getStatistics = async () => {
    const record = (await doGetRequestWithJsonResult(Endpoint.Statistics)) as Record<string, number>;

    const statistics: DocumentStatistics = {
        averageDocumentLength: record["AVERAGE_DOCUMENT_LENGTH"],
        documentCount: record["DOCUMENT_COUNT"],
    };

    return statistics;
};

export const apiClient = {
    listRankedDocuments,
    listSources,
    getStatistics,
};
