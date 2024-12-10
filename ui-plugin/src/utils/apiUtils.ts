const UNKNOWN_ERROR_MESSAGE = "Unknown error";

export const getApiErrorMessage = (error: unknown): string => {
    if (error instanceof Error) {
        return error.message || UNKNOWN_ERROR_MESSAGE;
    }

    if (typeof error === "string") {
        return error;
    }

    if (error && typeof error === "object") {
        if ("status" in error) {
            return `HTTP Error: ${(error as { status: number; statusText?: string }).status} ${(error as { statusText?: string }).statusText || ""}`;
        }

        try {
            if ("json" in error) {
                return JSON.stringify((error as { json: unknown }).json);
            }
        } catch (e) {
            return "Error parsing JSON response";
        }
    }

    return UNKNOWN_ERROR_MESSAGE;
};
