import React, { useState, useEffect, useRef } from "react";
import { message, Select, Table } from "antd";
import _ from "lodash";
import searchResultService from "services/main/searchResult.js";
import { calculateColumnsWidth } from "components/Utils/columnWidthHelper";
import Loader from "components/Utils/Loader"
import style from "./style.module.scss";

export default function TableCard(props) {
  const [tableData, setSearchData] = useState();
  const [loadingTableData, setLoadingTableData] = useState(false);

  useEffect(() => {
    setLoadingTableData(true)
    getSearchCardData();
  }, []);

  const getSearchCardData = async () => {
    const response = await searchResultService.getSearchCardData(props.params);
    if (response.success) {
      setSearchData(response.data.data);
    }
    setLoadingTableData(false)
  };

  const columns =
    !_.isEmpty(tableData) &&
    Object.keys(tableData[0]).map((col) => {
      return { title: col, dataIndex: col, key: col };
    });

  const styledTable = !_.isEmpty(tableData)
    ? calculateColumnsWidth(columns, tableData, 400)
    : {};

  const height = props.isSnippet ? 120 : 140;
  const tableScroll = { x: tableData ? 1200 : styledTable.tableWidth, y: height };

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

  return (
      <div className="cardTable">
        {loadingTableData ? 
          <div><Loader height={height}/></div>
          :
          dataTable
        }
      </div>
    )
}
