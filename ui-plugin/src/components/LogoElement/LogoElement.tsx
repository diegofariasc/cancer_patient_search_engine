import React, { useEffect, useState } from "react";

import "./styles.less";

export enum LogoElementSize {
    Small = "small",
    Large = "large",
}

export type LogoElementProps = {
    size?: LogoElementSize;
    windowTrimSize?: number;
};

export const LogoElement: React.FC<LogoElementProps> = ({ size = LogoElementSize.Large, windowTrimSize }) => {
    const height = `var(--chakra-fontSizes-${size === LogoElementSize.Large ? 5 : 3}xl)`;

    const [hideLogoText, setHideLogoText] = useState<boolean>(
        !windowTrimSize || window.innerWidth >= windowTrimSize
    );

    useEffect(() => {
        const debounce = (func: Function, wait: number) => {
            let timeout: number;
            return (...args: any[]) => {
                clearTimeout(timeout);
                timeout = window.setTimeout(() => func(...args), wait);
            };
        };

        const handleResize = debounce(() => {
            setHideLogoText(window.innerWidth <= 768);
        }, 200);

        window.addEventListener("resize", handleResize);

        handleResize();

        return () => {
            window.removeEventListener("resize", handleResize);
        };
    }, []);

    return (
        <div className="title-wrapper">
            <svg
                xmlns="http://www.w3.org/2000/svg"
                viewBox="0 0 378 378"
                style={{ height, display: "block" }}
                overflow="hidden"
            >
                <g>
                    <rect x="0" y="0" width="378" height="378" fill="#FFFFFF" />
                    <path
                        d="M88.5001 154.5C88.5001 78.837 149.613 17.5001 225 17.5001 300.387 17.5001 361.5 78.837 361.5 154.5 361.5 230.163 300.387 291.5 225 291.5 149.613 291.5 88.5001 230.163 88.5001 154.5Z"
                        stroke="#248388"
                        strokeWidth="21.3333"
                        strokeMiterlimit="8"
                        fill="#FFFFFF"
                        fillRule="evenodd"
                    />
                    <path
                        d="M79.2258 263.135C84.8415 257.519 93.9464 257.519 99.5621 263.135L117.208 280.781C122.824 286.396 122.824 295.501 117.208 301.117L50.16 368.165C44.5443 373.781 35.4394 373.781 29.8237 368.165L12.1779 350.519C6.56215 344.903 6.56215 335.798 12.1779 330.183Z"
                        stroke="#248388"
                        strokeWidth="2"
                        strokeMiterlimit="8"
                        fill="#20868A"
                        fillRule="evenodd"
                    />
                    <path
                        d="M118.383 253.592 131.88 267.09 110.878 288.092 97.3805 274.594Z"
                        stroke="#248388"
                        strokeWidth="2"
                        strokeMiterlimit="8"
                        fill="#20868A"
                        fillRule="evenodd"
                    />
                    <path
                        d="M223.885 62.3827C253.436 61.494 281.7 73.1219 294.955 91.6208"
                        stroke="#248388"
                        strokeWidth="19.3333"
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeMiterlimit="10"
                        fill="none"
                        fillRule="evenodd"
                    />
                </g>
            </svg>
            {(!windowTrimSize || window.innerWidth > windowTrimSize) && (
                <div>
                    <span className="title-first-word" style={{ fontSize: height }}>
                        search
                    </span>
                    <span className="title-second-word" style={{ fontSize: height }}>
                        cancer
                    </span>
                </div>
            )}
        </div>
    );
};
