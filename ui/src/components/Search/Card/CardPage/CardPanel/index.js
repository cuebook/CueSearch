import React, { useState, useEffect, useRef } from "react";
import { useHistory } from "react-router-dom";
import { message, Select, Button } from "antd";
import _ from "lodash";

import DataDisplay from "components/Search/Card/DataDisplay";

import style from "./style.module.scss";

export default function CardPanel(props) {
  const history = useHistory();

  if (_.isEmpty(props.cardDetails)) {
    return (
      <div>
        <Button className="mr-2" type="primary" onClick={history.goBack}>
          {" "}
          Back{" "}
        </Button>
        <Button
          className="mr-2"
          type="primary"
          onClick={() => {
            history.push("/");
          }}
        >
          {" "}
          Home{" "}
        </Button>
      </div>
    );
  }

  const { title, text, params } = props.cardDetails;

  return (
    <div>
      <div className="flex">
        <div className={`w-9/12 ${style.chartPanel}`}>
          <div
            className={style.anomalyTitle}
            dangerouslySetInnerHTML={{ __html: title }}
          />
          <div
            className={style.anomalyText}
            dangerouslySetInnerHTML={{ __html: text }}
          />
          <div className={style.chartDiv}>
            <DataDisplay params={params} />
          </div>
        </div>
      </div>
    </div>
  );
}
