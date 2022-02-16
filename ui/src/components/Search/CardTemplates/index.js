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
import style from "./style.module.scss";

const { Search } = Input;
const ButtonGroup = Button.Group;

export default function CardTemplatesTable(props) {
    const [templates, setTemplates] = useState("");

    const [isAddDrawerVisible, setIsAddDrawerVisible] = useState(false);
    const [isEditDrawerVisible, setIsEditDrawerVisible] = useState(false);

    useEffect(() => {
        if (!templates) {
            console.log("something working")
        }
    }, []);

    console.log("something working")
    const columns = [
        {
            title: "Publish",
            dataIndex: "published",
            width: "10%",
            // key: (arr) => "od",
            // sorter: (a, b) => b.published - a.published,
            render: (text, entity) => {
                return (
                    <Switch
                        checked={true}
                    // onChange={() => togglePublishState(entity.published, entity.id)}
                    />
                );
            },
        },
        {
            title: "",
            dataIndex: "action",
            key: "actions",
            className: "text-right",
            render: (text, record) => (
                <div className={style.actions}>
                    <Tooltip title={"Edit Templates"}>
                        {/* onClick={(e) => onClickEdit(record)} */}
                        <EditOutlined />
                    </Tooltip>

                    <Popconfirm
                        title={"Are you sure to delete " + "name" + " ?"}
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
                <Button type="primary">
                    Add Templates
                </Button>

            </div>
            <Table
                rowKey={"id"}
                scroll={{ x: "100%" }}
                columns={columns}
                dataSource={[]}
                size={"small"}
                pagination={false}
            />
            <Drawer
                title={"Add Templates"}
                width={720}
            // onClose={closeAddDrawer}
            // visible={isAddDrawerVisible}
            >
                {/* {isAddDrawerVisible ? (
                    <AddGlobalDimension
                        onAddGlobalDimensionSuccess={onAddGlobalDimensionSuccess}
                        linkedDimension={linkedDimensionArray}
                    />
                ) : null} */}
            </Drawer>

            <Drawer
                title={"Edit Templates"}
                width={720}
            // onClose={closeAddDrawer}
            // visible={isEditDrawerVisible}
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
