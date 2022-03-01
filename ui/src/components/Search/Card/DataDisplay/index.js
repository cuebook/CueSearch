import React, { useState, useEffect, useRef, useContext } from "react";
import searchResultService from "services/main/searchResult";
import { GlobalContext } from "layouts/GlobalContext";
import { message } from "antd";

import TableCard from "./Table";
import Chart from "./Chart";
import ErrorDisplayCard from "../Error/ErrorDisplay";

export default function DataDisplay({ params, isSnippet }) {
  const { searchCardData, addSearchCardData } = useContext(GlobalContext);
  const [cardData, setCardData] = useState();
  const [loadingData, setLoadingData] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null)

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
    if (!response.success) {
      setCardData(null)
      setErrorMessage(response["data"])
    }
    setLoadingData(false);
  };
  return (
    <div>

      {
        params.renderType == "table" ? (
          <TableCard
            cardData={cardData ? cardData.data : null}
            loadingData={loadingData}
            isSnippet={isSnippet}
            errorMessage={errorMessage}
          />
        ) : (
          <Chart
            cardData={cardData}
            loadingData={loadingData}
            isMiniChart={isSnippet}
            renderType={params.renderType}
            errorMessage={errorMessage}

          />
        )
      }
    </div>
  );
}
