import React, { useState, useEffect, useRef } from "react";
// import { Helmet } from "react-helmet";
import { Switch, Table, Button, Input, Drawer, Affix } from 'antd';
import {EditOutlined } from '@ant-design/icons';
import style from "./style.module.scss";
import {useHistory} from "react-router-dom"
import searchResultService from "services/main/searchResult.js"
import ErrorBoundary from "components/Utils/ErrorBoundary"
// import TrackVisibility from "react-on-screen";

import CardSnippet from "components/Search/Card/CardSnippet";

export default function SearchResultPage(props){
  const history = useHistory()
  const [searchCards, setSearchCards] = useState()
  const [searchPayload, setSearchPayload] = useState()
  useEffect(()=>{
        getSearchCard()
  }, []);

  const getSearchPayloadFromUrl = () =>{
    let params = new URLSearchParams(history.location.search);
    let searchQuery = JSON.parse(params.get("search"));
    setSearchPayload(searchQuery)
  }

  const getSearchCard = async () => {
    let params = new URLSearchParams(history.location.search);
    let searchPayload = JSON.parse(params.get("search"));
    const response = await searchResultService.getSearchCards(searchPayload)
    if(response.success){
      setSearchCards(response.data)
    }
  }

  let phantomCardsArray = []
  let cardsArray = []
  let loading = null
  let cardTypesArray = []

  if(searchCards){
    cardsArray = searchCards && searchCards.map((item, index)=>
      <ErrorBoundary>
        <div className={style.cardPanelWrapper}> < CardSnippet cardData={item} key={index} /> </div>
      </ErrorBoundary>
    )
  }

  return (
        <div>
          <div className="row" >
            <div className={`xl:w-8/12 ${style.searchResultsWrapper}`}>
              <h4>
                {searchCards ? 
                  cardsArray.length > 0 ? null : "No results found"
                 : "Loading.."}
              </h4>
              {cardsArray}
            </div>
          </div>
      </div>
    );

}