import React, { useState, useEffect, useRef } from "react";
import _ from "lodash";
import Loader from "components/Utils/Loader";
import style from "./style.module.scss";

export default function ErrorDisplayCard(props) {
    const errorSqlMessage = props.errorMessage
    const loadingData = props.loadingData

    const dataTable = (

        <div
            className={`${style.loadingDiv} pt-5 mt-2`}
        >
            <div className={style.errorMessageStyle}>
                <h2 style={{ color: "black", textSizeAdjust: "20px" }}> No Data </h2>
                <p style={{ maxWidth: "300px", wordWrap: "break-word" }}> {errorSqlMessage}</p>
            </div>

        </div>
    );
    return (
        <div className={style.ErrorDiv}>
            {loadingData ? (
                <div>
                    <Loader />
                </div>
            ) : (
                dataTable
            )}
        </div>
    );
}
