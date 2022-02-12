import React, { useState, useEffect, useRef, useContext } from "react";
import searchResultService from "services/main/searchResult";
import { GlobalContext } from "layouts/GlobalContext";

import TableCard from "./Table";
import Chart from "./Chart";

export default function DataDisplay({ params, isSnippet }) {
  const { searchCardData, addSearchCardData } = useContext(GlobalContext);
  const [cardData, setCardData] = useState();
  const [loadingData, setLoadingData] = useState(false);

  useEffect(() => {
    if (searchCardData[JSON.stringify(params)]) {
      setCardData(searchCardData[JSON.stringify(params)]);
    } else {
      setLoadingData(true);
      getSearchCardData();
    }
  }, []);

  const getSearchCardData = async () => {
    const response = await searchResultService.getSearchCardData(params);
    if (response.success) {
      setCardData(response.data);
      addSearchCardData([JSON.stringify(params)], response.data);
    }
    setLoadingData(false);
  };

  return (
    <div>
      {params.renderType == "table" ? (
        <TableCard
          cardData={cardData ? cardData.data : null}
          loadingData={loadingData}
          isSnippet={isSnippet}
        />
      ) : (
        <Chart
          cardData={cardData}
          loadingData={loadingData}
          isMiniChart={isSnippet}
          renderType={params.renderType}
        />
      )}
    </div>
  );
}
