import React, { useState, useEffect } from "react";
import { Select } from "antd";
import connectionService from "services/main/connection.js";

const { Option } = Select;

export default function SelectConnection(props) {
  const [connections, setConnections] = useState(null);

  useEffect(() => {
    if (!connections) {
      getConnections();
    }
  }, []);

  const getConnections = async (record) => {
    const response = await connectionService.getConnections();
    setConnections(response.data);
  };

  const options =
    connections &&
    connections.map((connection) => (
      <Option value={connection.id}>{connection.name}</Option>
    ));

  return (
    <Select
      style={{ width: 200 }}
      placeholder="Select a connection"
      optionFilterProp="children"
      onChange={props.onChange}
      disabled={props.disabled ? props.disabled : false}
      value={props.value}
      filterOption={(input, option) =>
        option.children.toLowerCase().indexOf(input.toLowerCase()) >= 0
      }
    >
      {options}
    </Select>
  );
}
