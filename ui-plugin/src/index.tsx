import "@fontsource/inter/400.css";
import "@fontsource/inter/700.css";

import React from "react";
import ReactDOM from "react-dom/client";

import { createBrowserHistory } from "history";
import { ChakraProvider, ColorModeScript, extendTheme } from "@chakra-ui/react";
import { Router, Route, Routes } from "react-router-dom";
import { ResultsPage } from "./components/ResultsPage/ResultsPage";
import { MainPage } from "./components/MainPage/MainPage";

const rootElement = document.getElementById("root");

const theme = extendTheme({
    fonts: {
        heading: `'Inter', sans-serif`,
        body: `'Inter', sans-serif`,
    },
});

if (rootElement) {
    const root = ReactDOM.createRoot(rootElement);
    const history = createBrowserHistory();

    root.render(
        <React.StrictMode>
            <ChakraProvider theme={theme}>
                <ColorModeScript
                    initialColorMode={theme.config.initialColorMode}
                />
                <Router location={history.location} navigator={history}>
                    <Routes>
                        <Route path="/" element={<MainPage />} />
                        <Route path="/search" element={<ResultsPage />} />
                    </Routes>
                </Router>
            </ChakraProvider>
        </React.StrictMode>
    );
}
