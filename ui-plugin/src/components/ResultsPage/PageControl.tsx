import React, { useCallback } from "react";
import { HStack, Link, Text } from "@chakra-ui/react";
import { useDataCache } from "../../hooks/useDataCache";
import { DEFAULT_PAGE_BLOCK_SIZE, DEFAULT_PAGE_SIZE } from "../../utils/constants";
import { getPaginationBlock } from "./utils";

export type PageControlProps = {
    currentPage: number;
    setPage: (newPage: number) => void;
};

export const PageControl: React.FC<PageControlProps> = ({ currentPage, setPage }) => {
    const { statistics } = useDataCache();

    if (!statistics) {
        return <></>;
    }

    const totalPages = Math.ceil(statistics.documentCount / DEFAULT_PAGE_SIZE);
    const paginationBlock = getPaginationBlock(currentPage, totalPages, DEFAULT_PAGE_BLOCK_SIZE);

    const changePage = (event: React.MouseEvent<HTMLAnchorElement, MouseEvent>, targetPage: number) => {
        event.preventDefault();
        if (targetPage < 1 || targetPage > totalPages) {
            return;
        }
        setPage(targetPage);
    };

    return (
        <HStack spacing={4} justify="center" py={4}>
            {currentPage - 1 < 1 ? (
                <Text color="gray.400">Previous</Text>
            ) : (
                <Link color="teal.600" fontWeight="bold" onClick={(e) => changePage(e, currentPage - 1)}>
                    Previous
                </Link>
            )}
            <div className="page-control-number-area">
                {paginationBlock[0] > 1 && (
                    <>
                        <Link color="gray.600" onClick={(e) => changePage(e, 1)}>
                            1
                        </Link>
                        <Text color="gray.600">...</Text>
                    </>
                )}
                {paginationBlock.map((pageNumber) => {
                    if (currentPage === pageNumber) {
                        return (
                            <Text key={pageNumber} fontWeight="bold" color="teal.600">
                                {pageNumber}
                            </Text>
                        );
                    }

                    return (
                        <Link color="gray.600" key={pageNumber} onClick={(e) => changePage(e, pageNumber)}>
                            {pageNumber}
                        </Link>
                    );
                })}
                {paginationBlock[paginationBlock.length - 1] < totalPages && (
                    <>
                        <Text color="gray.600">...</Text>
                        <Link color="gray.600" onClick={(e) => changePage(e, totalPages)}>
                            {totalPages}
                        </Link>
                    </>
                )}
            </div>
            {currentPage + 1 > totalPages ? (
                <Text color="gray.400">Next</Text>
            ) : (
                <Link color="teal.600" fontWeight="bold" onClick={(e) => changePage(e, currentPage + 1)}>
                    Next
                </Link>
            )}
        </HStack>
    );
};
