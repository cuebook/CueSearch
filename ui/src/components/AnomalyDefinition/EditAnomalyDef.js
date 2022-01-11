import React, { useState, useEffect } from "react";
import style from "./style.module.scss";
import { components } from "react-select";
import CreatableSelect from "react-select/creatable";
import { Modal, Select, Spin, Switch, Button, Radio, message, Drawer } from "antd";
import datasetService from "services/main/datasets";
import anomalyDefService from "services/main/anomalyDefinitions.js";
import PercentageChange from "components/DetectionRuleParamSelector/PercentageChange";
import ValueThreshold from "components/DetectionRuleParamSelector/ValueThreshold";
import  _ from "lodash";

const { Option } = Select;

let options = [];
let allOptions = {};
let tempOption = {};


function getSelectedOptions(anomalyDef){
    let temp = []
    if(anomalyDef.metric){
        temp.push({
            value: anomalyDef.metric,
            label: anomalyDef.metric,
            optionType: "Measure",
            color: "#ffc71f",
            isFixed: true
          });
    }
    if(anomalyDef.dimension){
        temp.push({
            value: anomalyDef.dimension,
            label: anomalyDef.dimension,
            optionType: "dimension",
            color: "#12b1ff",
            isFixed: true
          });
          if(anomalyDef.operation){

            temp.push({
              value: anomalyDef.operation,
              label: anomalyDef.operation,
              optionType: "Top",
              color: "#12b1ff",
              isFixed: true
            });
            temp.push({
              value: anomalyDef.value,
              label: anomalyDef.value,
              optionType: "Dimension Values",
              color: "#12b1ff",
              isFixed: true
            });
          }
          
    }
    if(anomalyDef.highOrLow){
        temp.push({
            value: anomalyDef.highOrLow,
            label: anomalyDef.highOrLow,
            optionType: "High Or Low",
            color: "#02c1a3",
            isFixed: false
          });
    }
    return temp
}


function generateOptions() {
  allOptions = {};
  allOptions.highOrLow = [
    {
      value: "High",
      label: "High",
      optionType: "High Or Low",
      color: "#02c1a3",
      isFixed: false
    },
    {
      value: "Low",
      label: "Low",
      optionType: "High Or Low",
      color: "#02c1a3",
      isFixed: false
    }
  ];
  options = [...allOptions.highOrLow]

}

function updateHelpText(selectedOption) {
  let elements = document.getElementsByClassName("autocue-help");
  while (elements.length > 0) {
    elements[0].parentNode.removeChild(elements[0]);
  }
  if (selectedOption) {
    setTimeout(function() {
      let elements = document.getElementsByClassName("autoCueOptions");
      let element = elements[elements.length - 1];
      let helpText = getHelpText(selectedOption);
      if (element)
        element.innerHTML +=
          "<span class='autocue-help'>" + helpText + "</span>";
    }, 150);
  }
}

function getMetricHelpText(value, opts) {
    // options = []
    options = [
      ...allOptions.highOrLow
    ];
    return "";
  }

function getTopHelpText(value, opts) {
//   options = []
  options = [...allOptions.highOrLow]
  return ""
}

function getOperationHelpText(value, opts) {
//   options = []
  options = [...allOptions.highOrLow]
  return ""
}

function getHelpText(selectedOption) {
  if (selectedOption && selectedOption.length) {
    let length = selectedOption.length;
    let lastOption = selectedOption[length - 1];
    let text = "";
    switch (lastOption.optionType) {
      case "Measure":
        text = getMetricHelpText(lastOption.value, selectedOption);
        tempOption = lastOption
        break;
      case "High Or Low":
        options = [];
        break;
      case "Top":
        text = getTopHelpText(lastOption.value, selectedOption)
        tempOption = lastOption
        break;
      case "Dimension Values":
        text = getOperationHelpText(lastOption.value, selectedOption)
        tempOption = lastOption
        break;

    }
    return text;
  }
  else{
      options = []
      options = [...options, ...allOptions.metric]
      return options
  }
  // return "";
}

export default function EditAnomalyDef(props){
  const [selectedOption, setSelectedOption] = useState([]);
  const [isFocused, setIsFocused] = useState(false);
  const [initialDataset, setInitialDataset] = useState([])
  const [detectionRule, setDetectionRule] = useState()
  const [updatedParams, setUpdatedParams] = useState({})
  const [anomalyDefId, setAnomalyDefId] = useState(0)

  useEffect(()=>{
    

    if(props)
    {
        let anomalyDef = props.editAnomalyDef["anomalyDef"]
        let datasetName = props.editAnomalyDef["datasetName"]
        setDetectionRule(props.editAnomalyDef.detectionRule)
        setInitialDataset(datasetName)
        let selected = getSelectedOptions(anomalyDef)
        setSelectedOption(selected)
        setAnomalyDefId(anomalyDef["id"])
        generateOptions()
    }

  }, []);

 const handelEditAnomaly = () => {

    var payload = {
      anomalyDefId: anomalyDefId,
      measure: selectedOption[0].value
    };

    selectedOption.forEach(item => {
      if (item.optionType === "High Or Low") {
        payload.highOrLow = item.value;
      }
    });

    let paramsUpdated = true
    for(let param in detectionRule.params)
    {
      if(!updatedParams[param])
      {
        paramsUpdated = false
      }
    }

    if(!paramsUpdated)
    {
      message.error("Update parameter values for detection rule");
      return
    }
    payload.detectionRuleParams = updatedParams

    getEditAnomaly(payload)

  };

  const getEditAnomaly = async (payload) =>{
  const response = await anomalyDefService.editAnomalyDef(payload)
  if(response.success){
    props.onEditAnomalyDefSuccess(true)
  }
  setSelectedOption([])
  }
  

 const handleDatasetChange = value => {
    setSelectedOption([])
  };
  const handleChange = (selectedOption,{action, removedValue}) => {
    switch(action){
        case "pop-value":
            if(removedValue.isFixed){
                return 
            }
    }
    setSelectedOption(selectedOption)
    setIsFocused(false)
    // updateOptions(selectedOption);
    // generateOptions()
    updateHelpText(selectedOption);
    setTimeout(() => {
      setIsFocused(true)
    }, 200);
  };

  const  singleOption = props => {
    if (props && props.label && props.label.indexOf("Create ") !== -1) {
      return (
        <components.Option {...props}>
          <div className={style.optionWrapper}>
            <span className={style.subText}>{props.data.optionType}</span>
            <p style={{ color: props.data.color }} className={style.option}>
              {props.value}
            </p>
          </div>
        </components.Option>
      );
    } else {
      return (
        <components.Option {...props}>
          <div className={style.optionWrapper}>
            <p style={{ color: props.data.color }} className={style.option}>
              {props.label}
            </p>
            <span className={style.subText}>{props.data.optionType}</span>
          </div>
        </components.Option>
      );
    }
  };

  const multiValue = props => {
    return (
      <components.MultiValue {...props}>
        <div style={{ background: "white" }}></div>
      </components.MultiValue>
    );
  };

  const  multiValueContainer = props => {
    return (
      <components.MultiValueContainer {...props}>
        <div
          className={`autoCueOptions ${style.selectedOption}`}
          style={{ color: props.data.color }}
        >
          {props.data.label}
        </div>
      </components.MultiValueContainer>
    );
  };
  const handleOnCancel = () =>{
      props.onEditAnomalyDefSuccess(false)
      setSelectedOption([])
  }

  const handleIsFocused = (val) => {
    setIsFocused(val)
  }


    let detectionRuleElem = null

    if(detectionRule)
    {
      let paramSelector = null
      //add values in param selector
      if(detectionRule.detectionRuleType.name == "Percentage Change")
      {
        paramSelector = <PercentageChange submitParams={setUpdatedParams} defaultParams={detectionRule.params} />
      }
      if(detectionRule.detectionRuleType.name == "Value Threshold")
      {
        paramSelector = <ValueThreshold submitParams={setUpdatedParams} defaultParams={detectionRule.params} />
      }

      detectionRuleElem = (
        <div className="mb-6">
          <Select
            className={`${style.selectEditor}`}
            showSearch
            disabled
            placeholder="Create a detection rule"
            value={detectionRule.detectionRuleType.name}
            optionFilterProp="children"
            filterOption={(input, option) =>
              option.props.children
                .toLowerCase()
                .indexOf(input.toLowerCase()) >= 0
            }
          >
          </Select>
          <span style={{opacity: 0.6, paddingLeft: 5}}>{detectionRule.detectionRuleType.description}</span>
          {paramSelector}
        </div>
      )
    }


    return (
      <div>
          <Drawer
            title="Edit Anomaly Definition"
            width="50%"
            centered
            visible={true}
            key="editAnomalyModal"
            centered="true"
            onClose={handleOnCancel}
          >
            <div>
              <div className="mb-6">
                <Select
                  className={`${style.selectEditor}`}
                  showSearch
                  // style={{ width: 200, float: "left" }}
                  placeholder="Select a dataset"
                  optionFilterProp="children"
                  value={initialDataset}
                  disabled={true}
                  onChange={handleDatasetChange}
                //   notFoundContent={
                //     this.props.cubes.loading ? <Spin size="small" /> : null
                //   }
                  filterOption={(input, option) =>
                    option.props.children
                      .toLowerCase()
                      .indexOf(input.toLowerCase()) >= 0
                  }
                >
                  {/* {datasetOption} */}
                </Select>
              </div>
              <div className="mb-6">
              <CreatableSelect
                styles={{
                  indicatorSeparator: () => {}, // removes the "stick"
                  dropdownIndicator: defaultStyles => ({
                    ...defaultStyles,
                    "& svg": { display: "none" }
                  })
                }}
                isMulti
                value={selectedOption}
                className={`${style.filterEditor}`}
                onChange={handleChange}
                onFocus={()=>handleIsFocused(true)}
                onBlur={() => handleIsFocused(false)}
                menuIsOpen={isFocused}
                isClearable={false}
                
                disabled={true}
                components={{
                  Option: singleOption,
                  MultiValue: multiValue,
                  MultiValueContainer: multiValueContainer
                }}
                options={options}
                placeholder={`Measure [Dimension] [Top N / Min % Contribution X / Min Avg Value Y] [High/Low] `}
              />

            </div>
            {detectionRuleElem}
            <div className="mb-6">
            <Button
                key="save"
                type="primary"
                onClick={() => handelEditAnomaly()}
              >
                Save Anomaly Definition 
              </Button>
              </div>
            </div>
            
          </Drawer>
      </div>
    );
  }
// }
