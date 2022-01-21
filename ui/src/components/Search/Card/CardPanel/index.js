import React, { useState, useEffect, useRef } from "react";
import { message, Select, Table } from "antd";
import _ from "lodash";

import TableCard from "components/Search/Card/Table";
import Chart from "components/Search/Card/Chart";

import style from "./style.module.scss";

export default function CardPanel(props) {

	if (_.isEmpty(props.cardData)){
		return <p>Please Go Back - ICON</p>
	}

	const data = props.cardData.data
	const title = props.cardData.title
	const text = props.cardData.text
	const params = props.cardData.params

	// checking if timeseries or not
	const dataColumns = Object.keys(data[0])
	let timestampColumn = null;
	let metric = null;
	let dimension = null;
	let mask = "M/D/H";
	let order = "0"

	if ( dataColumns.includes(params.timestampColumn) ) {
		timestampColumn = params.timestampColumn
	}
	if ( params.granularity == "day" ){
		mask = "M/D"
	}
	try {
		metric = params.metrics.filter(m=>dataColumns.includes(m))[0]
	} catch {}

	let metaData = {
		xColumn: timestampColumn,
		yColumn: metric,
		scale: {
			[timestampColumn]: {
				'type': 'time',
				'mask': mask
			},
		},
		order: "O"
	}

	try {
		dimension = params.dimensions.filter(d=>dataColumns.includes(d))[0]
		metaData.color = dimension
		metaData.scale[dimension] = { alias: dimension }
	} catch {
	}

	const cardData = { data: data, title: title, text: text, metaData: metaData, renderType: "line" }

	return (
		<div>
			<div className="flex">
			<div className={`w-9/12 ${style.chartPanel}`}>
			  <div className={style.anomalyTitle} dangerouslySetInnerHTML={{ __html: title }} />
			  <div className={style.anomalyText} dangerouslySetInnerHTML={{ __html: text }} />
			  {/* <div className={style.chartDiv}> <TableCard data={data} /> </div> */}
			  <div className={style.chartDiv}> <Chart data={data} cardData={cardData} renderType="line" /> </div>
			</div>
			</div>			
		</div>
		)
}
