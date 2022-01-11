import React, { useState, useEffect } from "react";
import { Table, Button, Popconfirm, Input, message, Tooltip, Drawer } from "antd";
import style from "./style.module.scss";
import scheduleService from "services/main/schedules.js"
import EditSchedule from "components/Schedules/EditSchedule.js"
import AddSchedule from "components/Schedules/AddSchedule.js"
import { EyeOutlined, DeleteOutlined , EditOutlined} from '@ant-design/icons';



export default function Schedule(){

const [schedules, setSchedules] = useState([]);
const [selectedSchedule, setSelectedConnection] = useState('');
const [isAddConnectionDrawerVisible, setIsAddConnectionDrawerVisible] = useState('');
const [isViewConnectionDrawerVisible, setIsViewConnectionDrawerVisible] = useState('');

    useEffect(() => {
    if (!schedules.length) {
        fetchSchedules();
    }
  }, []);

  const fetchSchedules = async () => {
    const response = await scheduleService.getSchedules();
    setSchedules(response)
  }

  const deleteScheduleFunction = async (schedule) => {
    const response = await scheduleService.deleteSchedule(schedule.id);
    if(response.success){
        fetchSchedules()
    }
    else{
        message.error(response.message)
    }
  }

  const editSchedule = async (schedule) => {
    setSelectedConnection(schedule)
    setIsViewConnectionDrawerVisible(true)
  }

  const closeAddConnectionDrawer = () => {
    setIsAddConnectionDrawerVisible(false)
  }

  const closeViewConnectionDrawer = () => {
    setIsViewConnectionDrawerVisible(false)
  }

  const openAddConnectionForm = () => {
    setIsAddConnectionDrawerVisible(true)
  }

  const onAddScheduleSuccess = async () => {
    closeAddConnectionDrawer();
    fetchSchedules();
  }
  const onEditScheduleSuccess = async () => {
    closeViewConnectionDrawer();
    fetchSchedules();
  }

  const columns = [
    {
      title: "Name",
      dataIndex: "name",
      key: "name",
      sorter:(a,b)=>{return a.name.localeCompare(b.name)},
    },
    {
      title: "Schedule",
      dataIndex: "schedule",
      key: "schedule",
      sorter:(a,b)=>{return a.schedule.localeCompare(b.schedule)},
    },
    {
      title: "Assigned Anomaly Definition",
      dataIndex: "assignedSchedule",
      key: "assignedSchedule",
      align:"center",
      sorter:(a,b)=>  b.assignedSchedule - a.assignedSchedule,
    },
    {
      title: "",
      dataIndex: "",
      key: "",
      render: (text, schedule) => (
       <div className={style.actions}>
           
          <Tooltip title={"Edit Schedule"}>
            <EditOutlined onClick={() => editSchedule(schedule)} />
          </Tooltip>
          
          <Popconfirm
              title={"Are you sure to delete "+ schedule.name +"?"}
              onConfirm={() => deleteScheduleFunction(schedule)}
              // onCancel={cancel}
              disabled={(schedule.notebookCount > 0 || schedule.workflowCount > 0) ? true : false}
              okText="Yes"
              cancelText="No"
          >
              <Tooltip title={"Delete Schedule"}>
                  <DeleteOutlined />
              </Tooltip>
          </Popconfirm>
        </div>
      )
    }
  ];
  return (
    <div>
        <div className={`d-flex flex-column justify-content-center text-right mb-2`}>
            <Button
                key="createTag"
                type="primary"
                onClick={() => openAddConnectionForm()}
            >
                Add Schedule
            </Button>
        </div>
        <Table
            rowKey={"id"}
            scroll={{ x: "100%" }}
            columns={columns}
            size={"small"}
            dataSource={schedules}
            pagination={{
              defaultPageSize: 50,
              total: schedules ? schedules.length : 50
            }}
        />
        <Drawer
          title={"Add Schedule"}
          width={720}
          onClose={closeAddConnectionDrawer}
          visible={isAddConnectionDrawerVisible}
        >
          { isAddConnectionDrawerVisible 
            ? 
            <AddSchedule onAddScheduleSuccess={onAddScheduleSuccess} />
            :
            null
          }
        </Drawer> 
         <Drawer
          title={selectedSchedule.name}
          width={720}
          onClose={closeViewConnectionDrawer}
          visible={isViewConnectionDrawerVisible}
        >
        
          { isViewConnectionDrawerVisible 
            ? 
            <EditSchedule editSchedule={selectedSchedule}  onEditScheduleSuccess={onEditScheduleSuccess} />
            :
            null
          }
        </Drawer>
    </div>
    );



} 