import React from "react";
import { Text, Divider } from "@chakra-ui/react";

import "./styles.less";

export const PageFooter: React.FC = () => {
    return (
        <div className="page-footer">
            <Divider />
            <Text fontSize="sm" color="gray.500" mb={5}>
                CS-410: Text Information Systems - Final Project - Diego Farias Castro
            </Text>
        </div>
    );
};
