import React, { useCallback, useEffect, useRef, useState } from "react";
import Base64IconDisplay from "./IconDisplay";

import { Input, Button, Divider, Link, useEditable, Spinner, Heading, Icon } from "@chakra-ui/react";
import { FaRedo, FaRegPlayCircle, FaReply, FaSearch } from "react-icons/fa";
import { useLocation, useNavigate } from "react-router-dom";
import { PageFooter } from "../PageFooter/PageFooter";
import { LogoElement, LogoElementSize } from "../LogoElement/LogoElement";
import { useDocumentsWithSourceDataList } from "../../hooks/useDocumentsWithSourceDataList";
import { parseNumber } from "../../utils/helpers";
import { readUrlParam } from "../../utils/urlHelpers";
import { PageControl } from "./PageControl";
import { WarningTwoIcon } from "@chakra-ui/icons";

import "./styles.less";

export const ResultsPage: React.FC = () => {
    const location = useLocation();
    const urlQuery = readUrlParam("query", location) || "";

    const inputText = useRef(urlQuery);

    const [query, setQuery] = useState(urlQuery);
    const [page, setPage] = useState(parseNumber(readUrlParam("page", location)));

    const { data: documents, loading, error, refreshDocuments } = useDocumentsWithSourceDataList(query, page);

    const navigate = useNavigate();

    useEffect(() => {
        const encodedNewQuery = `query=${encodeURIComponent(query)}`;
        const encodedNewPage = `&page=${encodeURIComponent(page ?? 1)}`;
        navigate(`/search?${encodedNewQuery}${encodedNewPage}`);
        refreshDocuments();
    }, [query, page]);

    const onInputKeyDown = useCallback((event: React.KeyboardEvent<HTMLInputElement>) => {
        if (event.key === "Enter" && inputText.current) {
            setQuery(inputText.current);
        }
    }, []);

    const onInputChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
        inputText.current = event.currentTarget.value;
    }, []);

    const onSearchButtonClick = useCallback(() => {
        if (inputText.current) {
            setQuery(inputText.current);
        }
    }, []);

    return (
        <div className="results-page-wrapper">
            <div className="results-page-content">
                <div className="results-page-header">
                    <div className="results-page-search-area">
                        <LogoElement size={LogoElementSize.Small} />
                        <div className="results-page-search-bar">
                            <Input
                                defaultValue={urlQuery}
                                placeholder="Search for treatments, studies, and resources..."
                                w="100%"
                                bg="gray.100"
                                borderRadius="md"
                                focusBorderColor="teal.400"
                                onKeyDown={onInputKeyDown}
                                onChange={onInputChange}
                                mb={3}
                            />
                            <Button
                                onClick={onSearchButtonClick}
                                colorScheme="teal"
                                borderRadius="md"
                                leftIcon={<FaSearch />}
                            />
                        </div>
                    </div>
                    <Divider />
                </div>
                <div className="results-page-result-area">
                    {documents && !loading && !error && (
                        <>
                            {documents.map((document, i) => (
                                <div className="result-item" key={i}>
                                    <div className="result-item-source-area">
                                        {document.icon && <Base64IconDisplay base64String={document.icon} />}
                                        {document.sourceName && document.baseUrl && (
                                            <div className="result-source-data">
                                                <span>{document.sourceName.replace(/"/g, "")}</span>
                                                <Link
                                                    className="result-title"
                                                    color="gray.500"
                                                    href={document.baseUrl}
                                                >
                                                    {document.baseUrl}
                                                </Link>
                                            </div>
                                        )}
                                    </div>
                                    <Link
                                        className="result-title"
                                        color="teal.600"
                                        fontSize="large"
                                        href={document.documentUrl}
                                    >
                                        {document.title}
                                    </Link>
                                    <span className="result-description">{document.summary}</span>
                                </div>
                            ))}
                        </>
                    )}
                    {loading && !error && (
                        <div className="results-page-loading-screen">
                            <Spinner size="xl" />
                        </div>
                    )}
                    {!!error && (
                        <div className="results-page-error-screen">
                            <Icon as={WarningTwoIcon} w={12} h={12} color="teal.600" mb={2} />
                            <Heading as="h2" size="xl" mb={2} color="teal.600">
                                Something went wrong
                            </Heading>
                            <span>{`An error occurred while searching. ${error}`}</span>
                            <Button colorScheme="teal" onClick={refreshDocuments} leftIcon={<FaRedo />}>
                                Retry search
                            </Button>
                        </div>
                    )}
                    {!loading && documents?.length && !error && (
                        <PageControl currentPage={page} setPage={setPage} />
                    )}
                </div>
            </div>
            <PageFooter />
        </div>
    );
};
