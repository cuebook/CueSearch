import React, { useState, useEffect, useRef } from "react";
import style from "./style.module.scss";
import { useParams, useHistory } from 'react-router-dom';
import {
  Chart,
  Geom,
  Axis,
  Legend,
  Tooltip,
  track,
  G2,
  Guide
} from "bizcharts";
const { Html } = Guide;

track(false);
G2.track(false);

const renderTypeMap = {
  line: "line",
  bar: "intervalStack",
  area: "areaStack"
};

class ChartCard extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      chartData: null,
      showPercentageChart: false,
      renderType: null
    };
    this.chartRef = React.createRef();
    this.chart = null;
  }

  render() {
    const { cardData } = this.props;
    const showPercentageButton = cardData && cardData.rowsTotal;
    let data = [];
    let metaData = {};
    let geomElements = null;
    let xAxisLabel = null;

    let renderType = this.state.renderType
      ? this.state.renderType
      : this.props.renderType;

    if (cardData) {
      if (cardData.data && cardData.metaData) {
        data = JSON.parse(JSON.stringify(cardData.data));

        metaData = cardData.metaData;
        let numDict = { B: 1000000000, M: 1000000, K: 1000, O: 1 };
        let order = "O";
        order = order !== "O" ? order : "";
        if (metaData.order && metaData.order !== "O") {
          let denom = numDict[metaData.order];
          metaData.scale[metaData.yColumn] = {
            ...metaData.scale[metaData.yColumn],
            formatter: val => (val / denom).toLocaleString() + metaData.order
          };
        }

          geomElements = [
            <Geom
              key="chartDefault"
              type={renderTypeMap[renderType]}
              position={metaData.xColumn + "*" + metaData.yColumn}
              color={metaData.color ? metaData.color : ""}
            />,
            <Geom
              key="chartPoint"
              type={"point"}
              size={7}
              position={metaData.xColumn + "*" + metaData.yColumn}
              opacity={0}
              active={[
                true,
                {
                  highlight: true,
                  style: {
                    cursor: "crosshair"
                  }
                }
              ]}
            />
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
        scale={metaData.scale}
        forceFit={true}
        height={this.props.height ? this.props.height : 400}
        width={this.props.width}
        padding="auto"
      >
        {this.props.isMiniChart ? (
          <Axis
            name={cardData.metaData.yColumn}
            position="left"
            label={{ textStyle: { fill: "#888", fontSize: "10" } }}
          />
        ) : (
          <Axis name={cardData.metaData.yColumn} />
        )}
        {this.props.isMiniChart ? (
          <Axis name={cardData.metaData.xColumn} visible={false} />
        ) : (
          <Axis
            name={cardData.metaData.xColumn}
            // label={xAxisLabel}
            title={{ textStyle: { fill: "#888" } }}
          />
        )}
        <Tooltip
          crosshairs={{
            type: "y"
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
      <div className={`${style.loadingDiv} pt-5 mt-2`}>
        <i className="fa fa-exclamation-triangle"></i>
        <p>No Data</p>
      </div>
    );

    return (
      <div>
        <div className={style.chartDiv}>
          {this.props.loading ? (
            <div className={` ${style.loadingDiv} pt-5 mt-2`}>
              {" "}
              <Spin />{" "}
            </div>
          ) : (
            this.chart
          )}
        </div>

      </div>
    );
  }
}

export default ChartCard;
