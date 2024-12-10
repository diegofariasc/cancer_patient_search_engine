import React, { useCallback, useRef } from "react";
import { Input, Button, Text } from "@chakra-ui/react";
import { FaSearch } from "react-icons/fa";
import { PageFooter } from "../PageFooter/PageFooter";
import { LogoElement } from "../LogoElement/LogoElement";

import "./styles.less";

export const MainPage: React.FC = () => {
    const queryText = useRef<string>("");

    const search = useCallback(() => {
        if (queryText.current) {
            window.location.assign(`/search?query=${encodeURIComponent(queryText.current)}`);
        }
    }, []);

    const onInputChange = useCallback((event: React.ChangeEvent<HTMLInputElement>) => {
        queryText.current = event.currentTarget.value;
    }, []);

    const onInputKeyDown = useCallback((event: React.KeyboardEvent<HTMLInputElement>) => {
        if (event.key === "Enter") {
            search();
        }
    }, []);

    return (
        <div className="main-page-wrapper">
            <div className="main-page-content">
                <LogoElement />
                <Text color="gray.600" fontWeight="medium">
                    A reliable search engine for cancer patients
                </Text>
                <div className="main-search-bar-wrapper">
                    <Input
                        placeholder="Search for treatments, studies, and resources..."
                        w="100%"
                        bg="gray.100"
                        borderRadius="md"
                        focusBorderColor="teal.400"
                        mb={3}
                        onChange={onInputChange}
                        onKeyDown={onInputKeyDown}
                    />
                    <Button onClick={search} colorScheme="teal" borderRadius="md" leftIcon={<FaSearch />}>
                        Search
                    </Button>
                </div>
            </div>
            <PageFooter />
        </div>
    );
};
