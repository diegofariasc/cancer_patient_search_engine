export const getPaginationBlock = (currentPage: number, totalPages: number, pageBlockSize: number) => {
    const startBlock = Math.floor((currentPage - 1) / pageBlockSize) * pageBlockSize + 1;
    const endBlock = Math.min(startBlock + pageBlockSize - 1, totalPages);

    const pagesInBlock = [];
    for (let i = startBlock; i <= endBlock; i++) {
        pagesInBlock.push(i);
    }

    return pagesInBlock;
};
