import { apiClient } from "../api/apiClient";
import { DocumentStatistics, Source } from "../types/databaseTypes";
import { SourceId } from "../types/typeAliases";

type DataCache = { sources: Map<SourceId, Source>; statistics: DocumentStatistics; lastRenewed: number };

const CACHE_KEY = "search-cancer-sources-cache";
const CACHE_EXPIRY_TIME = 24 * 60 * 60 * 1000; // 1 day

let cache: DataCache | undefined;

export const loadCache = () => {
    const cacheData = localStorage.getItem(CACHE_KEY);
    if (cacheData) {
        cache = JSON.parse(cacheData) as DataCache;
    }
};

const saveCache = () => {
    localStorage.setItem(CACHE_KEY, JSON.stringify(cache));
};

const shouldFetch = () => {
    if (!cache?.sources?.size || !cache.statistics) {
        return true;
    }

    const currentTime = Date.now();
    return cache.lastRenewed + CACHE_EXPIRY_TIME > currentTime;
};

export const renewCache = async () => {
    const promises = [apiClient.listSources(), apiClient.getStatistics()];
    const resolvedPromises = await Promise.all(promises);

    const sources = resolvedPromises[0] as Source[];
    const statistics = resolvedPromises[1] as DocumentStatistics;

    const sourcesMap = new Map(sources.map((source) => [source.id, source]));
    cache = { sources: sourcesMap, statistics, lastRenewed: Date.now() };
    saveCache();
    return cache!;
};

export const getSourcesMap = async () => {
    if (!cache) {
        loadCache();
    }
    if (shouldFetch()) {
        await renewCache();
    }

    return cache!.sources;
};

export const getPageCount = async () => {
    if (!cache) {
        loadCache();
    }
    if (shouldFetch()) {
        await renewCache();
    }

    return cache!.sources;
};
