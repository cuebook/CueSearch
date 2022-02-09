import React, { useState, useEffect, useRef } from "react";
import style from "./style.module.scss";
import { useParams, useHistory } from "react-router-dom";
import searchResultService from "services/main/searchResult";
import {
  Chart,
  Geom,
  Axis,
  Legend,
  Tooltip,
  track,
  G2,
  Guide,
} from "bizcharts";
const { Html } = Guide;

track(false);
G2.track(false);

const renderTypeMap = {
  line: "line",
  bar: "intervalStack",
  area: "areaStack",
};

class ChartCard extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      chartData: null,
      showPercentageChart: false,
      renderType: null,
      cardData: null,
    };
    this.chartRef = React.createRef();
    this.chart = null;
    this.getSearchCardData()
  }

  getSearchCardData = async () => {
    const response = await searchResultService.getSearchCardData(this.props.params);
    if (response.success) {
      this.setState({cardData: response.data});
    }
  };

  render() {
    const cardData = this.state.cardData;
    const showPercentageButton = cardData && cardData.rowsTotal;
    let data = [];
    let chartMetaData = {};
    let geomElements = null;
    let xAxisLabel = null;

    let renderType = this.state.renderType
      ? this.state.renderType
      : this.props.params.renderType;

    if (cardData) {
      if (cardData.data && cardData.chartMetaData) {
        data = JSON.parse(JSON.stringify(cardData.data));

        chartMetaData = cardData.chartMetaData;
        let numDict = { B: 1000000000, M: 1000000, K: 1000, O: 1 };
        let order = "O";
        order = order !== "O" ? order : "";
        if (chartMetaData.order && chartMetaData.order !== "O") {
          let denom = numDict[chartMetaData.order];
          chartMetaData.scale[chartMetaData.yColumn] = {
            ...chartMetaData.scale[chartMetaData.yColumn],
            formatter: (val) =>
              (val / denom).toLocaleString() + chartMetaData.order,
          };
        }

        geomElements = [
          <Geom
            key="chartDefault"
            type={renderTypeMap[renderType]}
            position={chartMetaData.xColumn + "*" + chartMetaData.yColumn}
            color={chartMetaData.color ? chartMetaData.color : ""}
          />,
          <Geom
            key="chartPoint"
            type={"point"}
            size={7}
            position={chartMetaData.xColumn + "*" + chartMetaData.yColumn}
            opacity={0}
          />,
        ];
      }
    }

    // Hiding X Axis Label for bar chart if more than 15 data points
    xAxisLabel =
      data.length && (renderType !== "bar" || data.length <= 15)
        ? { autoRotate: true }
        : null;
    this.chart = data.length ? (
      <Chart
        data={data}
        scale={chartMetaData.scale}
        forceFit={true}
        height={this.props.isMiniChart ? 120 : 400}
        width={this.props.isMiniChart ? 480 : undefined}
        padding="auto"
      >
        {this.props.isMiniChart ? (
          <Axis
            name={cardData.chartMetaData.yColumn}
            position="left"
            label={{ textStyle: { fill: "#888", fontSize: "10" } }}
          />
        ) : (
          <Axis name={cardData.chartMetaData.yColumn} />
        )}
        {this.props.isMiniChart ? (
          <Axis name={cardData.chartMetaData.xColumn} visible={false} />
        ) : (
          <Axis
            name={cardData.chartMetaData.xColumn}
            // label={xAxisLabel}
            title={{ textStyle: { fill: "#888" } }}
          />
        )}
        <Tooltip
          crosshairs={{
            type: "y",
          }}
          hideTime={1000}
        />
        {geomElements}
        {this.props.isMiniChart ? null : (
          <Legend name="annotate" visible={false} />
        )}
        {this.props.hasMarker ? this.props.markerElement : null}
      </Chart>
    ) : (
      <div
        className={`${style.loadingDiv} pt-5 mt-2`}
        style={{ height: this.props.isMiniChart ? 120 : 400 }}
      >
        <div>
          <i className="fa fa-exclamation-triangle"></i>
          <p>No Data</p>
        </div>
      </div>
    );

    return (
      <div>
        <div className={style.chartDiv}>{this.chart}</div>
      </div>
    );
  }
}

export default ChartCard;
