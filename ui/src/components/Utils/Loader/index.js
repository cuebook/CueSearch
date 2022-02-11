import React from "react";
import classNames from "classnames";
import styles from "./style.module.scss";

const Loader = ({ spinning = true, height = 180, fullScreen }) => (
  <div
    className={classNames(styles.loader, {
      [styles.hidden]: !spinning,
      [styles.fullScreen]: fullScreen,
    })}
    style={{ height: height }}
  />
);

export default Loader;
