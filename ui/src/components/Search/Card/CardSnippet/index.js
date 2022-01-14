import React, { useState, useEffect, useRef, useContext } from "react";
import { message, Select, Table } from "antd";

import style from "./style.module.scss";

import TableCard from "components/Search/Card/Table";

import { GlobalContext } from "layouts/GlobalContext"


export default function CardPanel(props) {

  const { searchCardData, updateSearchCardData } = useContext(GlobalContext)

	const { data: { data }, title, text } = props.searchCard

	const handleCardClick = () => {
		updateSearchCardData({data: data, title: title, text: text})
	} 

	return (
		<div>
		  <div className={style.searchSnippet}>
          <div className={style.chartSnippet}>

            <TableCard data={data} isSnippet={true} /> 
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
