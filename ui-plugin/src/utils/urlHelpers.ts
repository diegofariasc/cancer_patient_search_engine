import { Location } from "react-router-dom";
import { isDefined } from "./helpers";

export const readUrlParam = (paramName: string, location: Location) => {
    const params = new URLSearchParams(location.search);
    const param = params.get(paramName);
    return isDefined(param) ? param : undefined;
};
