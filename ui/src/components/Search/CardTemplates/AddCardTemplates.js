import React, { useState, useEffect, useRef } from "react";
import { Button, Form, Input, Switch, message, Select, textArea } from "antd";
import { Resizable } from "re-resizable";

import AceEditor from "react-ace";

import style from "./style.module.scss";

import cardTemplateService from "services/main/cardTemplate";
const { TextArea } = Input;

const { Option } = Select;

export default function AddCardTemplates(props) {
    const [form] = Form.useForm();
    const [renderType, setRenderType] = useState(null);

    useEffect(() => {
        console.log("add drawer open")
        if (!renderType) {
            setRenderType(["table", "line"])
        }
    }, []);
    var editorComponent;
    const renderTypeMap = {
        "table": "Table",
        "line": "Line"
    };
    const resizerStyle = {
        border: "solid 1px #ddd",
        background: "#f0f0f0",
        zIndex: "1"
    };
    const onSelectChange = (value) => {
        console.log("value", value)
        setRenderType(value);
    };

    const onEditorChange = (value) => {
        console.log("onEditorChangeValues", value)
    }
    const addCardTemplateFormSubmit = async (values) => {
        let payload = {};
        payload["templateName"] = values["templateName"]
        payload["title"] = values["title"]
        payload["sql"] = values["sql"]
        payload["bodyText"] = values["bodyText"]
        payload["renderType"] = values["renderType"][0]
        console.log("values form submit", values)

        const response = await cardTemplateService.addCardTemplates(payload);
        if (response.success) {
            props.onAddCardTemplateSuccess();
        } else {
            message.error(response.message);
        }
    };
    let renderTypeForSuggestion = [];
    renderTypeForSuggestion =
        renderType &&
        renderType.map((item) => (
            <Option
                value={
                    item
                }

                key={item}
            >
                {" "}
                {item}
            </Option>
        ));
    // let dimensionOptions = [];
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
                            name="renderType"
                            rules={[
                                {
                                    required: true,
                                    message: "Please select renderType !",
                                },
                            ]}
                        >
                            <Select
                                showSearch
                                mode="tags"
                                style={{ width: "100%" }}
                                placeholder="Select Render Type"
                                onChange={onSelectChange}
                            >
                                {renderTypeForSuggestion}
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
