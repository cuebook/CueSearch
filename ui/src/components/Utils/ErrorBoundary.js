import React, { Component } from "react";

class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
    };
  }
  static getDerivedStateFromError(error) {
    console.error("ERROR IN LOADING COMPONENT: ERROR: ", error);
    return {
      hasError: true,
    };
  }
  render() {
    if (this.state.hasError) {
      return <div></div>;
    }
    return this.props.children;
  }
}

export default ErrorBoundary;
