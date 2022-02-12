import React, { createContext, useState } from "react";

// this is the equivalent to the createStore method of Redux
// https://redux.js.org/api/createstore

// const [databases, setDatabases] = useState([])
let searchCardData = {}; //stores {params: cardData, params2: cardData2}
const updateSearchCardData = (x) => (searchCardData = x);
const addSearchCardData = (key, value) => (searchCardData[key]=value);

export const GlobalContext = createContext();

export const GlobalContextProvider = ({ children }) => {
  return (
    <GlobalContext.Provider
      value={{ searchCardData, updateSearchCardData, addSearchCardData }}
    >
      {children}
    </GlobalContext.Provider>
  );
};

// export default { GlobalContext, GlobalContextProvider };
