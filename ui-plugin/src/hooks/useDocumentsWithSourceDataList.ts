import { useState, useCallback } from "react";
import { apiClient } from "../api/apiClient";
import { DocumentWithSourceData } from "../types/databaseTypes";
import { getApiErrorMessage } from "../utils/apiUtils";
import { useDataCache } from "./useDataCache";
import { DEFAULT_MAX_SUMMARY_LENGTH, DEFAULT_PAGE_SIZE } from "../utils/constants";

export const useDocumentsWithSourceDataList = (query: string, page: number) => {
    const [data, setData] = useState<DocumentWithSourceData[]>();
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string>();

    const { sourcesRecord, initCache } = useDataCache();

    const refreshDocuments = useCallback(async () => {
        setLoading(true);
        setError(undefined);
        try {
            const documents = await apiClient.listRankedDocuments({
                query,
                page,
                limit: DEFAULT_PAGE_SIZE,
                maxSummaryLen: DEFAULT_MAX_SUMMARY_LENGTH,
            });

            const initializedCacheSources = sourcesRecord || (await initCache())?.sources || {};
            const documentsWithSource = documents.map((item) => {
                const sourceData = initializedCacheSources?.[item.sourceId];
                const documentWithSource: DocumentWithSourceData = {
                    ...sourceData,
                    ...item,
                };
                return documentWithSource;
            });

            setData(documentsWithSource);
        } catch (error) {
            const errorMessage = getApiErrorMessage(error);
            setError(errorMessage);
        }
        setLoading(false);
    }, [query, page, sourcesRecord]);

    return { data, loading, error, refreshDocuments };
};
