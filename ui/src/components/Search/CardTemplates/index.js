import React, { useState, useEffect, useRef } from "react";
import {
    Switch,
    Table,
    Button,
    Input,
    Drawer,
    Popconfirm,
    Tooltip,
} from "antd";
import { EditOutlined, DeleteOutlined } from "@ant-design/icons";
import cardTemplateService from "services/main/cardTemplate";

import style from "./style.module.scss";
import AddCardTemplates from "./AddCardTemplates";

const { Search } = Input;
const ButtonGroup = Button.Group;

export default function CardTemplatesTable(props) {
    const [templates, setTemplates] = useState("");

    const [isAddDrawerVisible, setIsAddDrawerVisible] = useState(false);
    const [isEditDrawerVisible, setIsEditDrawerVisible] = useState(false);

    useEffect(() => {
        if (!templates) {
            console.log("something working")
            getTemplates()
        }
    }, []);
    const renderTypeMap = {
        "table": "Table",
        "line": "Line"
    };
    const getTemplates = async () => {
        const response = await cardTemplateService.getCardTemplates()
        setTemplates(response)
        console.log("response", response)
    }


    const closeAddDrawer = () => {
        setIsAddDrawerVisible(false);
        setIsEditDrawerVisible(false);
    };
    const openAddCardTemplate = () => {
        setIsAddDrawerVisible(true);
    };
    const onAddCardTemplateSuccess = () => {
        // getData();
        setIsAddDrawerVisible(false);
    };
    const columns = [
        {
            title: "Publish",
            dataIndex: "published",
            width: "8%",
            key: (arr) => arr.id,
            sorter: (a, b) => b.published - a.published,
            render: (text, entity) => {
                return (
                    <Switch
                        checked={entity.published}
                    // onChange={() => togglePublishState(entity.published, entity.id)}
                    />
                );
            },
        },
        {

            title: "Template Name",
            dataIndex: "templateName",
            // width: "10%",
        },

        {

            title: "Render Type",
            dataIndex: "renderType",
            render: (text, record) => {
                return (
                    <div>
                        {renderTypeMap[text]}
                    </div>
                )
            }
            // width: "10%",
        },

        {
            title: "",
            dataIndex: "action",
            key: "actions",
            className: "text-right",
            width: "8%",

            render: (text, record) => (
                <div className={style.actions}>
                    <Tooltip title={"Edit Templates"}>
                        {/* onClick={(e) => onClickEdit(record)} */}
                        <EditOutlined />
                    </Tooltip>

                    <Popconfirm
                        title={"Are you sure to delete " + record.templateName + " ?"}
                        // onConfirm={(e) => deleteGlobalDimension(record)}
                        okText="Yes"
                        cancelText="No"
                    >
                        <Tooltip title={"Delete Templates"}>
                            <DeleteOutlined />
                        </Tooltip>
                    </Popconfirm>
                </div>
            ),
        },
    ];

    return (
        <div>
            <div
                className={`d-flex flex-column justify-content-center text-right mb-2`}
            >
                <Button onClick={openAddCardTemplate} type="primary">
                    Add Templates
                </Button>

            </div>
            <Table
                rowKey={"id"}
                scroll={{ x: "100%" }}
                columns={columns}
                dataSource={templates}
                size={"small"}
                pagination={false}
            />
            <Drawer
                title={"Add Templates"}
                width={1000}
                onClose={closeAddDrawer}
                visible={isAddDrawerVisible}
            >
                {isAddDrawerVisible ? (
                    <AddCardTemplates
                        onAddCardTemplateSuccess={onAddCardTemplateSuccess}
                    />
                ) : null}
            </Drawer>

            <Drawer
                title={"Edit Templates"}
                width={1000}
                onClose={closeAddDrawer}
                visible={isEditDrawerVisible}
            >
                {/* {isEditDrawerVisible ? (
                    <EditGlobalDimension
                        editDimension={editDimension}
                        linkedDimension={linkedDimensionArray}
                        onEditGlobalDimensionSuccess={onEditGlobalDimensionSuccess}
                    />
                ) : null} */}
            </Drawer>


        </div>
    );
}
