import React, { useState, useEffect, useRef } from "react";
import { Button, Form, Input, Switch, message, Select } from "antd";
import style from "./style.module.scss";

import cardTemplateService from "services/main/cardTemplate";

const { Option } = Select;
const { TextArea } = Input

export default function EditCardTemplate(props) {
    const [form] = Form.useForm();
    const [renderType, setRenderType] = useState("table");

    const [selectedTemplate, setSelectedTemplate] = useState(null);

    useEffect(() => {

        let template = props && props.editCardTemplate
        setSelectedTemplate(template)
    }, []);

    console.log("selectedTemplate", selectedTemplate)
    let addCardTemplateFormElement = []


    const onSelectChange = (value) => { setRenderType(value) };


    let initialTemplateName = selectedTemplate && selectedTemplate["templateName"]
    let initialSQL = selectedTemplate && selectedTemplate["sql"]
    let initialTitle = selectedTemplate && selectedTemplate["title"]
    let initialBodyText = selectedTemplate && selectedTemplate["bodyText"]
    let initialRenderType = selectedTemplate && selectedTemplate["renderType"]
    let initialPublished = selectedTemplate && selectedTemplate["published"]

    const editCardTemplateFormSubmit = async (values) => {
        let payload = {};
        payload["id"] = props && props.editCardTemplate["id"]
        payload["templateName"] = values["templateName"]
        payload["sql"] = values["sql"]
        payload["title"] = values["title"]
        payload["bodyText"] = values["bodyText"]
        payload["renderType"] = values["renderType"]
        payload["published"] = values["published"]
        const response = await cardTemplateService.updateCardTemplate(
            payload["id"],
            payload
        );
        if (response.success) {
            props.onEditCardTemplateSuccess();
        }
    };

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
