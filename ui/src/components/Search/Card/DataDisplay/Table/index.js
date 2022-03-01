import React, { useState, useEffect, useRef } from "react";
import { message, Select, Table, Button } from "antd";
import _ from "lodash";
import { calculateColumnsWidth } from "components/Utils/columnWidthHelper";
import Loader from "components/Utils/Loader";
import style from "./style.module.scss";
import ErrorDisplayCard from "../../Error/ErrorDisplay.js"

export default function TableCard(props) {
  const tableData = props.cardData;
  const loadingTableData = props.loadingData;
  const errorSqlMessage = props.errorMessage
  const columns =
    !_.isEmpty(tableData) &&
    Object.keys(tableData[0]).map((col) => {
      return { title: col, dataIndex: col, key: col };
    });

  const styledTable = !_.isEmpty(tableData)
    ? calculateColumnsWidth(columns, tableData, 400)
    : {};

  const height = props.isSnippet ? 120 : 480;
  const tableScroll = {
    x: tableData ? 1200 : styledTable.tableWidth,
    y: height,
  };

  const dataTable = (

    errorSqlMessage ? (
      <div>
        < ErrorDisplayCard
          loadingData={loadingTableData}
          errorMessage={errorSqlMessage}

        />
      </div >
    )
      :

      <Table
        className={style.antdTable}
        columns={columns}
        dataSource={tableData ? styledTable.source : tableData}
        pagination={false}
        size="xs"
        bordered={true}
        scroll={tableScroll}
      />
  );
  return (
    <div className="cardTable">
      {loadingTableData ? (
        <div>
          <Loader height={height} />
        </div>
      ) : (
        dataTable
      )}
    </div>
  );
}
