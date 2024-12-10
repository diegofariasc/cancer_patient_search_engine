export const parseNumber = (value: string | undefined, defaultValue = 1): number => {
    const parsedValue = Number(value);
    return isNaN(parsedValue) ? defaultValue : parsedValue;
};

export const isDefined = <T>(value: T | null | undefined): value is T => {
    return value !== null && value !== undefined;
};
