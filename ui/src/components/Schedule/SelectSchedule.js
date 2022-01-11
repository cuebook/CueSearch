import React, { useState, useEffect, useRef } from "react";
import style from "./style.module.scss";
import {
    Modal,
    Input,
    Select,
    Icon,
    Tooltip,
    Popover,
    Form,
    message,
    Switch,
  } from "antd";
import AddSchedule from "./AddSchedule";

import scheduleService from "services/main/schedules.js"


const { Option } = Select;

export default function SelectSchedule(props) {
    const [schedules, setSchedules] = useState([]);
    const [isAddingSchedule, setIsAddingSchedule] = useState(false);
    const [selectedSchedule, setSelectedSchedule] = useState(props.schedule ? props.schedule : 'Select Cron Schedule');

    const getSchedules = async () => {
      const response = await scheduleService.getSchedules();
      setSchedules(response);
    };

    useEffect(() => {
      if (!schedules.length) {
        getSchedules();
      }
    }, []);

    const handleScheduleChange = (value) => {
      if(value === "Add Schedule"){
        setIsAddingSchedule(true)
        setSelectedSchedule('Select Cron Schedule')
      }
      else{
        setSelectedSchedule(value)
        props.onChange(value)
        // addNotebookSchedule(value)
      }
    }

    const addedSchedule = () => {
        setIsAddingSchedule(false)
        getSchedules()
    }

    let scheduleOptionsElement = []
    if(schedules){
      scheduleOptionsElement.push(<Option value={"Add Schedule"} key={"0"}>Add Schedule</Option>)
      schedules.forEach(schedule => {
        scheduleOptionsElement.push(<Option value={schedule.id} key={schedule.id}>{schedule.name}</Option>)
      })
    }

    return (
        <span>
            <Select value={selectedSchedule} style={{ width: 250 }} onChange={handleScheduleChange}>
              {scheduleOptionsElement}
            </Select>
            {isAddingSchedule ? <AddSchedule onCompletion={addedSchedule} /> : null}
        </span>
    )

}