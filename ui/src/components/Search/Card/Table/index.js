import React, { useState, useEffect, useRef } from "react";
import { message, Select, Table } from "antd";
import _ from "lodash";
import searchResultService from "services/main/searchResult.js";
import { calculateColumnsWidth } from "components/Utils/columnWidthHelper";
import style from "./style.module.scss";

export default function TableCard(props) {
  const [tableData, setSearchData] = useState();
  useEffect(() => {
    getSearchCardData();
  }, []);

  const getSearchCardData = async () => {
    const response = await searchResultService.getSearchCardsData(props.params);
    if (response.success) {
      setSearchData(response.data.data);
    }
  };

  const columns =
    !_.isEmpty(tableData) &&
    Object.keys(tableData[0]).map((col) => {
      return { title: col, dataIndex: col, key: col };
    });

  const styledTable = !_.isEmpty(tableData)
    ? calculateColumnsWidth(columns, tableData, 400)
    : {};

  const tableScroll = props.isSnippet
    ? { x: tableData ? 1200 : styledTable.tableWidth, y: 120 }
    : { x: tableData ? 1200 : styledTable.tableWidth, y: 480 };

  const dataTable = (
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

  return <div className="cardTable">{dataTable}</div>;
}
