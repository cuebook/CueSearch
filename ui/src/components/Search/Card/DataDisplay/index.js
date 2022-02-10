import React, { useState, useEffect, useRef, useContext } from "react";

import TableCard from "./Table";
import Chart from "./Chart";

export default function DataDisplay({ params, isSnippet }) {
  return (
    <div>
      {params.renderType == "table" ? (
        <TableCard params={params} isSnippet={isSnippet} />
      ) : (
        <Chart
          params={params}
          isMiniChart={isSnippet}
        />
      )}

    </div>
  );
}
