import { SourceId } from "./typeAliases";

export enum DocumentType {
    Paper = "paper",
    Website = "website",
}

export enum DocumentLanguage {
    English = "english",
    Spanish = "spanish",
}

export type Source = {
    id: SourceId;
    sourceName: string;
    baseUrl: string;
    icon?: string;
};

export type Document = {
    title: string;
    summary: string;
    documentType: DocumentType;
    publishDate?: Date;
    documentUrl: string;
    documentLanguage: DocumentLanguage;
    sourceId: number;
};

export type DocumentStatistics = {
    averageDocumentLength: number;
    documentCount: number;
};

export type DocumentWithSourceData = Omit<Document, "sourceId"> & Partial<Omit<Source, "id">>;
