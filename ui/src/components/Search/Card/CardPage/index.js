import React, { useState, useEffect, useRef, useContext } from "react";
import { useHistory } from "react-router-dom";

import { GlobalContext } from "layouts/GlobalContext";

// import style from "./style.module.scss";

import CardPanel from "./CardPanel";

export default function CardPage(props) {
  const history = useHistory();

  let params = new URLSearchParams(history.location.search);
  console.log(params.get("searchCardDetails"))
  let searchCardDetails = JSON.parse(params.get("searchCardDetails"));

  return (
    <div>
      <CardPanel cardDetails={searchCardDetails} />
    </div>
  );
}
