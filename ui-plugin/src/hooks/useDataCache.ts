import { useCallback, useEffect, useState } from "react";
import { apiClient } from "../api/apiClient";
import { DocumentStatistics, Source } from "../types/databaseTypes";
import { SourceId } from "../types/typeAliases";

type DataCache = { sources: Record<SourceId, Source>; statistics: DocumentStatistics; lastRenewed: number };

const CACHE_KEY = "search-cancer-sources-cache";

export const useDataCache = () => {
    const [cache, setCache] = useState<DataCache>();

    const initCache = useCallback(async () => {
        const cacheData = localStorage.getItem(CACHE_KEY);

        if (cacheData) {
            const availableCache = JSON.parse(cacheData) as DataCache;
            setCache(availableCache);
            return availableCache;
        }

        const promises = [apiClient.listSources(), apiClient.getStatistics()];
        const resolvedPromises = await Promise.all(promises);

        const sources = resolvedPromises[0] as Source[];
        const statistics = resolvedPromises[1] as DocumentStatistics;

        const sourcesRecord: Record<SourceId, Source> = {};
        sources.forEach((source) => {
            sourcesRecord[source.id] = source;
        });

        const newCache = { sources: sourcesRecord, statistics, lastRenewed: Date.now() };

        localStorage.setItem(CACHE_KEY, JSON.stringify(newCache));
        setCache(newCache);

        return newCache;
    }, []);

    // Init cache
    useEffect(() => {
        initCache();
    }, []);

    return { sourcesRecord: cache?.sources, statistics: cache?.statistics, initCache };
};
