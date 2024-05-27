import React from 'react';
import AlertArea from "../components/AlertArea";
import MainContent from "../components/MainContent";

const Overview = ({ businessDate }) => {
  return (
    <div>
      <MainContent businessDate={businessDate}/>
      <AlertArea />
    </div>
  );
};

export default Overview;
