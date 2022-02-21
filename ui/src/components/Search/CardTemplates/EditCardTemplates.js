import React, { useState, useEffect, useRef } from "react";
import { Button, Form, Input, Switch, message, Select } from "antd";
import style from "./style.module.scss";

import cardTemplateService from "services/main/cardTemplate";
import connectionService from "services/main/connection.js";

const { Option } = Select;
const { TextArea } = Input;

export default function EditCardTemplate(props) {
  const [form] = Form.useForm();
  const [renderType, setRenderType] = useState("table");
  const [allConnectionType, setAllConnectionType] = useState(null)
  const [connectionType, setConnectionType] = useState()
  const [publish, setPublish] = useState(false)
  const [selectedTemplate, setSelectedTemplate] = useState(null);

  useEffect(() => {

    let template = props && props.editCardTemplate
    let connection = template["connectionTypeId"] + "." + template["connectionTypeName"]
    let published = template["published"]
    setConnectionType(connection)
    setSelectedTemplate(template)
    setPublish(published)
    getConnectionType()
  }, []);

  let addCardTemplateFormElement = []


  const onSelectChange = (value) => { setRenderType(value) };
  const getConnectionType = async () => {
    const response = await connectionService.getConnectionTypes()
    if (response.success) {
      setAllConnectionType(response["data"])
    }
  }

  const onSelectConnectionTypeChange = (val) => {
    setConnectionType(val)
  }

  let initialTemplateName = selectedTemplate && selectedTemplate["templateName"]
  let initialSQL = selectedTemplate && selectedTemplate["sql"]
  let initialTitle = selectedTemplate && selectedTemplate["title"]
  let initialBodyText = selectedTemplate && selectedTemplate["bodyText"]
  let initialRenderType = selectedTemplate && selectedTemplate["renderType"]
  let initialPublished = selectedTemplate && selectedTemplate["published"]
  let initialConnectionType = selectedTemplate && selectedTemplate["connectionTypeName"]


  const editCardTemplateFormSubmit = async (values) => {

    let payload = {};
    payload["id"] = props && props.editCardTemplate["id"]
    let connType = connectionType && connectionType.split(".")
    payload["connectionTypeId"] = connType[0]
    payload["connectionTypeName"] = connType[1]
    payload["templateName"] = values["templateName"]
    payload["sql"] = values["sql"]
    payload["title"] = values["title"]
    payload["bodyText"] = values["bodyText"]
    payload["renderType"] = values["renderType"]
    payload["published"] = publish
    const response = await cardTemplateService.updateCardTemplate(
      payload["id"],
      payload
    );
    if (response.success) {
      props.onEditCardTemplateSuccess();
    }
  };

  let connectionTypeSuggestion = []
  connectionTypeSuggestion = allConnectionType && allConnectionType.map((item) => (
    <Option
      value={
        item["id"] + "." + item["name"]
      }
      key={item["id"]}
    >
      {" "}
      {item["name"]}{" "}
    </Option>
  ));
  let addCardTemplateParamElements = [];

  addCardTemplateFormElement = (
    <div>
      <Form
        layout="vertical"
        className="mb-2"
        form={form}
        onFinish={editCardTemplateFormSubmit}
        name="addSchedule"
        scrollToFirstError
        hideRequiredMark
      >
        <div className={style.addConnectionForm}>
          <div className={style.formItem} style={{ width: "100%" }}>
            <Form.Item
              hasFeedback
              name="templateName"
              initialValue={initialTemplateName}
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
              initialValue={initialTitle}
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
              initialValue={initialBodyText}
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
              initialValue={initialSQL}
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
              initialValue={initialConnectionType}
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
              initialValue={initialRenderType}
              rules={[
                {
                  required: true,
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
            </Form.Item> </div>
          {addCardTemplateParamElements}
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
        <div>{selectedTemplate ? addCardTemplateFormElement : null}</div>
      </div>
    </div>
  );
}
