import React, { useState, useEffect, useRef } from "react";
import { Button, Form, Input, Switch, message } from "antd";
import { LeftOutlined } from "@ant-design/icons";

import style from "./style.module.scss";
import connectionService from "services/main/connection.js";
const { TextArea } = Input;

export default function AddConnection(props) {
  const [connectionTypes, setConnectionTypes] = useState([]);
  const [selectedConnectionType, setSelectedConnectionType] = useState("");
  const [loader, setLoader] = useState(false);
  const [form] = Form.useForm();

  useEffect(() => {
    if (!connectionTypes.length) {
      fetchConnectionTypes();
    }
  }, []);

  const fetchConnectionTypes = async () => {
    const response = await connectionService.getConnectionTypes();
    setConnectionTypes(response.data);
  };

  const handleConnectionTypeSelect = (connectionType) => {
    setSelectedConnectionType(connectionType);
  };

  const addConnectionFormSubmit = async (values) => {
    setLoader(true);
    let params = { ...values };
    delete params["name"];
    let payload = {
      name: values["name"],
      description: "",
      connectionType_id: selectedConnectionType.id,
      params: params,
    };
    const response = await connectionService.addConnection(payload);
    if (response.success) {
      setLoader(false);
      props.onAddConnectionSuccess();
    } else {
      message.error(response.message);
      setLoader(false);
    }
  };

  const renderInputType = (field) => {
    switch (field.properties.type) {
      case "text":
        return (
          <Form.Item
            key={field.name}
            label={field.label}
            rules={field.properties.rules}
            name={field.name}
          >
            <Input
              type={field.isEncrypted ? "password" : "text"}
              className={style.inputArea}
            />
          </Form.Item>
        );
      case "boolean":
        return (
          <Form.Item
            key={field.name}
            label={field.label}
            rules={field.properties.rules}
            name={field.name}
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>
        );
      case "json":
        return (
          <Form.Item
            key={field.name}
            label={field.label}
            rules={field.properties.rules}
            name={field.name}
          >
            <TextArea rows={3} className={style.inputFileArea} />
          </Form.Item>
        );
      default:
        return (
          <Form.Item
            key={field.name}
            label={field.label}
            rules={field.properties.rules}
            name={field.name}
          >
            <Input
              type={field.isEncrypted ? "password" : "text"}
              className={style.inputArea}
            />
          </Form.Item>
        );
    }
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
          {renderInputType(item)}
        </div>
      );
    });
  }

  let addConnectionFormElement = (
    <div>
      {selectedConnectionType.id ? (
        <div className={style.selectedConnectionDiv}>
          <div
            className={style.connectionBackButton}
            onClick={() => setSelectedConnectionType({})}
          >
            <LeftOutlined />
            Back
          </div>
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
      <Form
        layout="vertical"
        className="mb-2"
        form={form}
        onFinish={addConnectionFormSubmit}
        name="addConnection"
        scrollToFirstError
        hideRequiredMark
      >
        <div className={style.addConnectionForm}>
          <div className={style.formItem} style={{ width: "100%" }}>
            <Form.Item
              hasFeedback
              name="name"
              label="Connection Name"
              rules={[
                {
                  required: true,
                  message: "Please input your Connection name!",
                },
              ]}
            >
              <Input className={style.inputArea} />
            </Form.Item>
          </div>
          {connectionParamElements}
        </div>
        <div className={style.submitButton}>
          <Button
            icon=""
            type="primary"
            className="mr-2"
            htmlType="submit"
            loading={loader}
          >
            Add Connection
          </Button>
        </div>
      </Form>
    </div>
  );

  // Code for rendering select connection type form
  let selectConnectionTypeElement = (
    <div className={style.items}>
      {connectionTypes.map((connectionType, index) => (
        <div
          className={style.connection}
          key={index}
          onClick={(e) => handleConnectionTypeSelect(connectionType)}
        >
          <div
            className={style.connectionLogo}
            style={{
              backgroundImage: `url(${require("assets/img/" +
                connectionType.name +
                ".svg")})`,
            }}
          ></div>
          <p>{connectionType.name}</p>
        </div>
      ))}
    </div>
  );

  return (
    <div>
      <div className="row">
        {selectedConnectionType.id ? (
          <div>{addConnectionFormElement}</div>
        ) : (
          selectConnectionTypeElement
        )}
      </div>
    </div>
  );
}
