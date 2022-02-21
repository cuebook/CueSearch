import React, { useState, useEffect, useRef } from "react";
import { Button, Form, Input, Switch, message, Select, textArea } from "antd";

import style from "./style.module.scss";

import cardTemplateService from "services/main/cardTemplate";
import connectionService from "services/main/connection.js";

const { TextArea } = Input;

const { Option } = Select;

export default function AddCardTemplates(props) {
  const [form] = Form.useForm();
  const [renderType, setRenderType] = useState("table");
  const [connectionType, setConnectionType] = useState();
  useEffect(() => {
    getConnectionType();
  }, []);

  const onSelectChange = (value) => {
    setRenderType(value);
  };
  const onSelectConnectionTypeChange = (val) => {};
  const getConnectionType = async () => {
    const response = await connectionService.getConnectionTypes();
    if (response.success) {
      setConnectionType(response["data"]);
    }
  };
  const addCardTemplateFormSubmit = async (values) => {
    let payload = {};
    let connType = values["connectionType"].split(".");
    payload["connectionTypeId"] = connType[0];
    payload["connectionTypeName"] = connType[1];
    payload["templateName"] = values["templateName"];
    payload["title"] = values["title"];
    payload["sql"] = values["sql"];
    payload["bodyText"] = values["bodyText"];
    payload["renderType"] = values["renderType"];

    const response = await cardTemplateService.verifyCardTemplate(payload)
    if (response.success){
    const response = await cardTemplateService.addCardTemplate(payload);
    } else {
      message.error(response.message);
    }

    if (response.success) {
      props.onAddCardTemplateSuccess();
    } else {
      message.error(response.message);
    }
  };

  let connectionTypeSuggestion = [];
  connectionTypeSuggestion =
    connectionType &&
    connectionType.map((item) => (
      <Option value={item["id"] + "." + item["name"]} key={item["id"]}>
        {" "}
        {item["name"]}{" "}
      </Option>
    ));

  let addGlobalDimensionParamElements = [];

  let addCardTemplateFormElement = (
    <div>
      <Form
        layout="vertical"
        className="mb-2"
        form={form}
        onFinish={addCardTemplateFormSubmit}
        name="addSchedule"
        scrollToFirstError
        hideRequiredMark
      >
        <div className={style.addConnectionForm}>
          <div className={style.formItem} style={{ width: "100%" }}>
            <Form.Item
              hasFeedback
              name="templateName"
              rules={[
                {
                  required: true,
                  message: "Please input your Card Template Name !",
                  whitespace: true,
                },
              ]}
            >
              <Input
                className={style.inputArea}
                placeholder={"Template Name"}
              />
            </Form.Item>
            <Form.Item
              hasFeedback
              name="title"
              rules={[
                {
                  required: true,
                  message: "Please input your Card Template Title !",
                  whitespace: true,
                },
              ]}
            >
              <TextArea
                rows={2}
                className={style.inputArea}
                placeholder={"Title"}
              />
            </Form.Item>
            <Form.Item
              hasFeedback
              name="bodyText"
              rules={[
                {
                  required: true,
                  message: "Please input your Card Template Body Text !",
                  whitespace: true,
                },
              ]}
            >
              <TextArea
                rows={2}
                className={style.inputArea}
                placeholder={"Body Text"}
              />
            </Form.Item>
            <Form.Item
              hasFeedback
              name="sql"
              rules={[
                {
                  required: true,
                  message: "Please input your Card Template SQL !",
                  whitespace: true,
                },
              ]}
            >
              <TextArea
                rows={3}
                className={style.inputArea}
                width={"100%"}
                placeholder={"SQL"}
              />
            </Form.Item>
            <Form.Item
              name="connectionType"
              rules={[
                {
                  required: true,
                  message: "Please select connectionType !",
                },
              ]}
            >
              <Select
                style={{ width: "100%" }}
                placeholder="Card Template Connection Type"
                onChange={onSelectConnectionTypeChange}
              >
                {connectionTypeSuggestion}
              </Select>
            </Form.Item>

            <Form.Item
              name="renderType"
              initialValue={renderType}
              rules={[
                {
                  required: false,
                  message: "Please select renderType !",
                },
              ]}
            >
              <Select
                // showSearch
                // mode="tags"
                defaultValue="table"
                style={{ width: "100%" }}
                placeholder="Select Render Type"
                onChange={onSelectChange}
              >
                <Option value="table">Table</Option>
                <Option value="line"> Line</Option>
              </Select>
            </Form.Item>
          </div>
          {addGlobalDimensionParamElements}
        </div>
        <div className={style.submitButton}>
          <Button icon="" type="primary" className="mr-2" htmlType="submit">
            Save Card Template
          </Button>
        </div>
      </Form>
    </div>
  );

  return (
    <div>
      <div className="row">
        <div>{addCardTemplateFormElement}</div>
      </div>
    </div>
  );
}
