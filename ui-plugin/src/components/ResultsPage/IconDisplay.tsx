import React from "react";

export type Base64IconDisplayProps = {
    base64String: string;
};

export const Base64IconDisplay: React.FC<Base64IconDisplayProps> = ({ base64String }) => {
    const iconUrl = `data:image/jpeg;base64,${base64String}`;
    return <img src={iconUrl} alt="icon" />;
};

export default Base64IconDisplay;
