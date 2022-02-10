import React, { useState, useEffect, useRef, useContext } from "react";
import { message, Select, Table } from "antd";
import { useHistory } from "react-router-dom";

import TableCard from "components/Search/Card/Table";
import Chart from "components/Search/Card/Chart";

import { GlobalContext } from "layouts/GlobalContext";

import style from "./style.module.scss";

export default function CardSnippet(props) {
  const history = useHistory();

  const handleCardClick = () => {
    history.push({
      pathname: "/search/card/",
      search: "?searchCardDetails=" + encodeURIComponent(JSON.stringify(props.cardData))
    })
  };

  const { title, text, params } = props.cardData;

  return (
    <div>
      <div className={style.searchSnippet}>
        <div className={style.chartSnippet}>
          {params.renderType == "table" ? (
            <TableCard params={params} isSnippet={true} />
          ) : (
            <Chart
              params={params}
              isMiniChart={true}
            />
          )}
        </div>
        <div className={style.contentSnippet}>
          <a
            onClick={handleCardClick}
            className={`header mb-0 ${style.cardLink}`}
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
          </a>
        </div>
      </div>
    </div>
  );
}
