import React, { useContext, useState, useEffect } from "react";
import { Router } from "react-router";
// import { ConnectedRouter } from "connected-react-router";

import { Switch, Route, Redirect } from "react-router-dom";
import ReactNotification from "react-notifications-component";
import { createHashHistory } from "history";

// components
import AdminNavbar from "components/Navbars/AdminNavbar.js";
import Sidebar from "components/Sidebar/Sidebar.js";
import HeaderStats from "components/Headers/HeaderStats.js";

// views
import Dataset from "views/admin/Dataset";
import Datasets from "views/admin/Datasets";
import Connections from "views/admin/Connections";
import Settings from "views/admin/Settings";
// Auth
import Login from "components/System/User/Login/index";

// contexts
import { GlobalContextProvider } from "./GlobalContext";
import userServices from "services/main/user.js";

// Search
import GlobalDimensionTable from "views/admin/GlobalDimension";
import SearchResultPage from "views/admin/SearchResults";
import SearchCardPage from "views/admin/SearchCard";

// CardTemplates
import CardTemplatesTable from "views/admin/CardTemplates";

// Telemetry
import installationServices from "services/main/installation";
import { telemetry } from "telemetry/index.js";

const history = createHashHistory();

export default function Admin() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [loader, setLoader] = useState(false);
  const [isAuthRequired, setIsAuthRequired] = useState(false);
  const [isLogout, setIsLogout] = useState(false);
  const [installationId, setInstallationId] = useState();

  useEffect(() => {
    if (!isLoggedIn) {
      getUser();
    }
    // if(!installationId){
    //   getInstallationIdForTelemetry()
    // }
  }, []);

  const getUser = async () => {
    const response = await userServices.currentAccount();
    if (response && response.success && response.isAuthenticationRequired) {
      setIsLogout(true);
      setIsAuthRequired(true);
      setIsLoggedIn(true);
      history.push("/");
    } else if (
      response &&
      !response.success &&
      response.isAuthenticationRequired
    ) {
      setIsLogout(true);
      setIsAuthRequired(true);
      setLoader(true);
    } else if (
      response &&
      !response.success &&
      !response.isAuthenticationRequired
    ) {
      setIsLoggedIn(true);
      setIsAuthRequired(true);
    }
  };
  const getLogOut = async () => {
    const response = await userServices.logout();
    if (response) {
      setLoader(true);
      setIsLoggedIn(false);
    }
  };

  const loggedIn = (val) => {
    setIsLoggedIn(val);
  };
  const logout = (val) => {
    if (val) {
      //val will be either true or false
      getLogOut();
    }
  };

  // const getInstallationIdForTelemetry = async() => {
  //   const res = await installationServices.getInstallationId()
  //   if (res && res.success == true){
  //     let id = res.data["installationId"]
  //     setInstallationId(id)
  //   }
  // }
  // let installId = installationId
  // if(installId){
  //   let title = window.location.hash
  //   title = title.replace("#/","")
  //   let url = window.location.href
  //   telemetry(title, url, installId)
  // }

  return (
    <>
      {isAuthRequired && isLoggedIn ? (
        <GlobalContextProvider>
          <Sidebar Logout={logout} authRequire={isLogout} />
          <ReactNotification />
          <div className="relative md:ml-64 bg-gray-200">
            {/* <AdminNavbar /> */}
            <HeaderStats />
            <div
              className="px-0 md:px-0 mx-auto w-full"
              style={{
                minHeight: "calc(100vh - 0px)",
                padding: "0.5rem 0rem 0 0rem",
              }}
            >
              <Router history={history}>
                <Route path="/dataset/create" exact component={Dataset} />
                <Route path="/dataset/:datasetId" exact component={Dataset} />
                <Route path="/datasets" exact component={Datasets} />
                <Route path="/connections" exact component={Connections} />
                <Route path="/settings" exact component={Settings} />
                <Route
                  path="/search/global-dimension"
                  exact
                  component={GlobalDimensionTable}
                />
                <Route
                  path="/search/templates"
                  exact
                  component={CardTemplatesTable}
                />
                <Route path="/search/" exact component={SearchResultPage} />
                <Route path="/search/card" exact component={SearchCardPage} />
                <Route
                  exact
                  path="/"
                  render={() => <Redirect to="/datasets" />}
                />
              </Router>
            </div>
          </div>
        </GlobalContextProvider>
      ) : (
        <div>
          {loader && isAuthRequired ? (
            <Switch>
              <Route
                path="/account/login"
                component={() => <Login loggedIn={loggedIn} />}
              />
              <Redirect from="/" to="/account/login" />
            </Switch>
          ) : (
            ""
          )}
        </div>
      )}
    </>
  );
}
