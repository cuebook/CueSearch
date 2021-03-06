import React, { useState, useEffect, useRef } from "react";
import { Switch, Table, Button, Input, Drawer, Affix } from "antd";
import { EditOutlined } from "@ant-design/icons";
import style from "./style.module.scss";
import { useHistory } from "react-router-dom";
import _ from "lodash";

import searchResultService from "services/main/searchResult.js";
import ErrorBoundary from "components/Utils/ErrorBoundary";
import CardSnippet from "components/Search/Card/CardSnippet";
import Loader from "components/Utils/Loader";

export default function SearchResultPage(props) {
  const history = useHistory();
  const [searchCards, setSearchCards] = useState();
  const [searchPayload, setSearchPayload] = useState();
  useEffect(() => {
    syncResultsWithURL();
  });

  const isPayloadSame = (a, b) => {
    if (_.isEmpty(a) && _.isEmpty(b)) {
      return true;
    } else if (_.isEmpty(a) || _.isEmpty(b)) {
      return false;
    } else if (
      a
        .map((x) => x.value)
        .sort()
        .join() ==
      b
        .map((x) => x.value)
        .sort()
        .join()
    )
      return true;
    return false;
  };

  const syncResultsWithURL = () => {
    let params = new URLSearchParams(history.location.search);
    let searchPayloadNew = JSON.parse(params.get("search"));
    if (!isPayloadSame(searchPayload, searchPayloadNew)) {
      getSearchCard(searchPayloadNew);
      setSearchCards();
      setSearchPayload(searchPayloadNew);
    }
  };

  const getSearchCard = async (searchPayloadNew) => {
    const response = await searchResultService.getSearchCards(searchPayloadNew);
    if (response.success) {
      setSearchCards(response.data);
    }
  };

  let phantomCardsArray = [];
  let cardsArray = [];
  let loading = null;
  let cardTypesArray = [];

  if (searchCards) {
    cardsArray =
      searchCards &&
      searchCards.map((item, index) => (
        <ErrorBoundary>
          <div className={style.cardPanelWrapper}>
            {" "}
            <CardSnippet cardData={item} key={index} />{" "}
          </div>
        </ErrorBoundary>
      ));
  }

  return (
    <div>
      <div className="row">
        <div className={`xl:w-8/12 ${style.searchResultsWrapper}`}>
          <div className={`xl:w-8/12 ${style.loadingDiv}`}>
            {searchCards ? (
              cardsArray.length > 0 ? null : (
                <>
                  {" "}
                  <i className="fa fa-exclamation-triangle"></i> <p>No Data</p>{" "}
                </>
              )
            ) : (
              <Loader />
            )}
          </div>
          {cardsArray}
        </div>
      </div>
    </div>
  );
}
