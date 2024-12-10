import { useEffect, useState } from "react";
import { apiClient } from "../api/apiClient";
import { DocumentStatistics, Source } from "../types/databaseTypes";
import { SourceId } from "../types/typeAliases";

type DataCache = { sources: Map<SourceId, Source>; statistics: DocumentStatistics; lastRenewed: number };

const CACHE_KEY = "search-cancer-sources-cache";

export const useDataCache = () => {
    const [cache, setCache] = useState<DataCache>();

    // Init cache
    useEffect(() => {
        const initCache = async () => {
            const cacheData = localStorage.getItem(CACHE_KEY);

            if (cacheData) {
                setCache(JSON.parse(cacheData) as DataCache);
                return;
            }

            const promises = [apiClient.listSources(), apiClient.getStatistics()];
            const resolvedPromises = await Promise.all(promises);

            const sources = resolvedPromises[0] as Source[];
            const statistics = resolvedPromises[1] as DocumentStatistics;

            const sourcesMap = new Map(sources.map((source) => [source.id, source]));
            const newCache = { sources: sourcesMap, statistics, lastRenewed: Date.now() };

            localStorage.setItem(CACHE_KEY, JSON.stringify(newCache));
            setCache(newCache);
        };

        initCache();
    }, []);

    return { sourcesMap: cache?.sources, statistics: cache?.statistics };
};
