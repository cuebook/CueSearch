import React, { useState, useEffect, useRef } from "react";
import { Button, Form, Input, message } from "antd";
import { LeftOutlined } from "@ant-design/icons";

import style from "./style.module.scss";
import connectionService from "services/main/connection.js";

export default function ViewConnection(props) {
  const [connectionTypes, setConnectionTypes] = useState([]);
  const [selectedConnectionType, setSelectedConnectionType] = useState({});
  const [selectedConnection, setSelectedConnection] = useState({});
  const [initialFormValues, setInitialFormValues] = useState({});
  const [form] = Form.useForm();
  const { TextArea } = Input;

  useEffect(() => {
    if (!connectionTypes.length) {
      fetchConnectionTypes();
    }
    if (!selectedConnection.id) {
      fetchSelectedConnection();
    }
  }, []);

  const fetchConnectionTypes = async () => {
    const response = await connectionService.getConnectionTypes();
    setConnectionTypes(response.data);
    setSelectedConnectionTypeFromConnection(response.data);
  };

  const fetchSelectedConnection = async () => {
    const response = await connectionService.getConnection(props.connection.id);
    setSelectedConnection(response.data);
    setInitialFormValues({ name: response.data.name, ...response.data.params });
  };

  const setSelectedConnectionTypeFromConnection = (connectionTypes) => {
    let selectedConnectionType = connectionTypes.find(
      (ct) => ct.id === props.connection.connectionTypeId
    );
    setSelectedConnectionType(selectedConnectionType);
  };

  let connectionParamElements = [];
  if (selectedConnectionType.id) {
    selectedConnectionType.params.forEach((item) => {
      connectionParamElements.push(
        <div
          style={{ width: item.properties.width }}
          className={style.formItem}
          key={item.id}
        >
          {item.properties.type === "json" ? (
            <Form.Item
              key={item.name}
              label={item.label}
              rules={item.properties.rules}
              name={item.name}
            >
              <TextArea
                type={item.isEncrypted ? "password" : "text"}
                className={style.inputArea}
                disabled
              />
            </Form.Item>
          ) : (
            <Form.Item
              key={item.name}
              label={item.label}
              rules={item.properties.rules}
              name={item.name}
            >
              <Input
                type={item.isEncrypted ? "password" : "text"}
                className={style.inputArea}
                disabled
              />
            </Form.Item>
          )}
        </div>
      );
    });
  }

  let viewConnectionFormElement = (
    <div>
      {selectedConnectionType.id ? (
        <div className={style.selectedConnectionDiv}>
          <div className={`${style.connection} ${style.selectedConnection}`}>
            <div
              className={style.connectionLogo}
              style={{
                backgroundImage: `url(${require("assets/img/" +
                  selectedConnectionType.name +
                  ".svg")})`,
              }}
            ></div>
            <p>{selectedConnectionType.name}</p>
          </div>
        </div>
      ) : null}
      {initialFormValues.name ? (
        <Form
          layout="vertical"
          className="mb-2"
          form={form}
          initialValues={{ ...initialFormValues }}
          name="addConnection"
          scrollToFirstError
          hideRequiredMark
        >
          <div className={style.addConnectionForm}>
            <div className={style.formItem} style={{ width: "100%" }}>
              <Form.Item hasFeedback name="name" label="Connection Name">
                <Input disabled className={style.inputArea} />
              </Form.Item>
            </div>
            {connectionParamElements}
          </div>
        </Form>
      ) : null}
    </div>
  );

  // Code for rendering select connection type form
  // let selectConnectionTypeElement = (
  //   <div className={style.items}>
  //     {connectionTypes.map((connectionType, index) => (
  //         <div className={style.connection} key={index} onClick={e => handleConnectionTypeSelect(connectionType)}>
  //           <div className={style.connectionLogo} style={{backgroundImage: `url(${require("assets/img/" + connectionType.name + ".svg")})`}}>
  //           </div>
  //           <p>{connectionType.name}</p>
  //         </div>
  //     ))}
  //   </div>
  // );

  return (
    <div>
      <div className="row view-connection">
        {selectedConnectionType.id ? (
          <div>{viewConnectionFormElement}</div>
        ) : null}
      </div>
    </div>
  );
}
