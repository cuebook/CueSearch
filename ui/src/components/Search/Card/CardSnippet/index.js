import React, { useState, useEffect, useRef, useContext } from "react";
import { message, Select, Table } from "antd";

import style from "./style.module.scss";

import TableCard from "components/Search/Card/Table";
import Chart from "components/Search/Card/Chart";

import { GlobalContext } from "layouts/GlobalContext"


export default function CardSnippet(props) {

  const { searchCardData, updateSearchCardData } = useContext(GlobalContext)

	const handleCardClick = () => {
		updateSearchCardData(props.cardData)
	} 

  const { title, text, params } = props.cardData;
  const data = props.cardData.data.data
  const tailoredCardData = { data: data, chartMetaData: props.cardData.chartMetaData, renderType: params.renderType }

	return (
		<div>
		  <div className={style.searchSnippet}>
          <div className={style.chartSnippet}>
            {
              params.renderType == "table" ? 
              <TableCard data={data} isSnippet={true} /> 
              :
              <Chart cardData={ tailoredCardData } isMiniChart={true} /> 
            }
          </div>
          <div className={style.contentSnippet}>
            <a
              onClick={handleCardClick}
              className={`header mb-0 ${style.cardLink}`}
              href={
                "#/search/card"
              }
            >
              <h4
                className={`mb-1 ${style.cardTitle}`}
                dangerouslySetInnerHTML={{ __html: title }}
              ></h4>
              {text ? (
                <p
                  className={style.cardText}
                  dangerouslySetInnerHTML={{ __html: text }}
                ></p>
              ) : null}
          </a></div></div>
		</div>
		)
}
