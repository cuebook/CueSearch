import React, { useState, useEffect, useRef, useContext } from "react";
import searchResultService from "services/main/searchResult";

import TableCard from "./Table";
import Chart from "./Chart";

export default function DataDisplay({ params, isSnippet }) {
  const [ cardData, setCardData ] = useState();
  const [ loadingData, setLoadingData ] = useState(false);

  useEffect(() => {
    setLoadingData(true)
    getSearchCardData();
  }, []);

  const getSearchCardData = async () => {
    const response = await searchResultService.getSearchCardData(params);
    if (response.success) {
      setCardData(response.data);
    }
    setLoadingData(false)
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
